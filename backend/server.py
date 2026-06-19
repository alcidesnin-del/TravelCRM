from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header, UploadFile, File, Query
from fastapi.responses import JSONResponse, RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from twilio.rest import Client as TwilioClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import io
import tempfile

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

SECRET_KEY = os.environ.get('JWT_SECRET')
if not SECRET_KEY or SECRET_KEY == 'your-secret-key-change-in-production':
    raise RuntimeError(
        "JWT_SECRET no está configurado o usa el valor por defecto inseguro. "
        "Genera uno con: python -c \"import secrets; print(secrets.token_hex(32))\" "
        "y agrégalo a tu archivo .env como JWT_SECRET=<valor>"
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== MODELS =====

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Passenger(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    passport_number: Optional[str] = None
    passport_expiry: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    documents: List[dict] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PassengerCreate(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    passport_number: Optional[str] = None
    passport_expiry: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class PassengerUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    passport_number: Optional[str] = None
    passport_expiry: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class Call(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    passenger_id: str
    call_date: str
    duration: Optional[int] = None
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CallCreate(BaseModel):
    passenger_id: str
    call_date: str
    duration: Optional[int] = None
    notes: Optional[str] = None

class TripDetail(BaseModel):
    type: str
    description: str
    date: Optional[str] = None
    time: Optional[str] = None
    reference_number: Optional[str] = None
    provider: Optional[str] = None
    cost: Optional[float] = None
    notes: Optional[str] = None

class Trip(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    passenger_id: str
    title: str
    destination: str
    start_date: str
    end_date: str
    status: str
    details: List[TripDetail] = Field(default_factory=list)
    total_cost: Optional[float] = None
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class TripCreate(BaseModel):
    passenger_id: str
    title: str
    destination: str
    start_date: str
    end_date: str
    status: str = "upcoming"
    details: List[TripDetail] = Field(default_factory=list)
    total_cost: Optional[float] = None
    notes: Optional[str] = None

class TripUpdate(BaseModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    details: Optional[List[TripDetail]] = None
    total_cost: Optional[float] = None
    notes: Optional[str] = None

# ===== AUTH UTILITIES =====

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace('Bearer ', '')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user_doc:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user_doc)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ===== AUTH ENDPOINTS =====

@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_data.email,
        name=user_data.name
    )
    
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user_data.password)
    
    await db.users.insert_one(user_dict)
    
    token = create_access_token({"sub": user.id})
    return {"token": token, "user": user}

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc or not verify_password(credentials.password, user_doc["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = User(id=user_doc["id"], email=user_doc["email"], name=user_doc["name"], created_at=user_doc["created_at"])
    token = create_access_token({"sub": user.id})
    return {"token": token, "user": user}

@api_router.get("/auth/me", response_model=User)
async def get_me(user: User = Depends(get_current_user)):
    return user

# ===== PASSENGER ENDPOINTS =====

@api_router.get("/passengers", response_model=List[Passenger])
async def get_passengers(user: User = Depends(get_current_user)):
    passengers = await db.passengers.find({"user_id": user.id}, {"_id": 0}).to_list(1000)
    return passengers

@api_router.get("/passengers/{passenger_id}", response_model=Passenger)
async def get_passenger(passenger_id: str, user: User = Depends(get_current_user)):
    passenger = await db.passengers.find_one({"id": passenger_id, "user_id": user.id}, {"_id": 0})
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")
    return passenger

@api_router.post("/passengers", response_model=Passenger)
async def create_passenger(data: PassengerCreate, user: User = Depends(get_current_user)):
    passenger = Passenger(user_id=user.id, **data.model_dump())
    await db.passengers.insert_one(passenger.model_dump())
    return passenger

@api_router.put("/passengers/{passenger_id}", response_model=Passenger)
async def update_passenger(passenger_id: str, data: PassengerUpdate, user: User = Depends(get_current_user)):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.passengers.update_one(
        {"id": passenger_id, "user_id": user.id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passenger not found")
    
    passenger = await db.passengers.find_one({"id": passenger_id}, {"_id": 0})
    return passenger

@api_router.delete("/passengers/{passenger_id}")
async def delete_passenger(passenger_id: str, user: User = Depends(get_current_user)):
    result = await db.passengers.delete_one({"id": passenger_id, "user_id": user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Passenger not found")
    return {"message": "Passenger deleted successfully"}

# ===== CALL ENDPOINTS =====

@api_router.get("/calls", response_model=List[Call])
async def get_calls(passenger_id: Optional[str] = None, user: User = Depends(get_current_user)):
    query = {"user_id": user.id}
    if passenger_id:
        query["passenger_id"] = passenger_id
    calls = await db.calls.find(query, {"_id": 0}).to_list(1000)
    return calls

@api_router.post("/calls", response_model=Call)
async def create_call(data: CallCreate, user: User = Depends(get_current_user)):
    call = Call(user_id=user.id, **data.model_dump())
    await db.calls.insert_one(call.model_dump())
    return call

@api_router.delete("/calls/{call_id}")
async def delete_call(call_id: str, user: User = Depends(get_current_user)):
    result = await db.calls.delete_one({"id": call_id, "user_id": user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Call not found")
    return {"message": "Call deleted successfully"}

# ===== TRIP ENDPOINTS =====

@api_router.get("/trips", response_model=List[Trip])
async def get_trips(passenger_id: Optional[str] = None, status: Optional[str] = None, user: User = Depends(get_current_user)):
    query = {"user_id": user.id}
    if passenger_id:
        query["passenger_id"] = passenger_id
    if status:
        query["status"] = status
    trips = await db.trips.find(query, {"_id": 0}).to_list(1000)
    return trips

@api_router.get("/trips/{trip_id}", response_model=Trip)
async def get_trip(trip_id: str, user: User = Depends(get_current_user)):
    trip = await db.trips.find_one({"id": trip_id, "user_id": user.id}, {"_id": 0})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@api_router.post("/trips", response_model=Trip)
async def create_trip(data: TripCreate, user: User = Depends(get_current_user)):
    trip = Trip(user_id=user.id, **data.model_dump())
    await db.trips.insert_one(trip.model_dump())
    return trip

@api_router.put("/trips/{trip_id}", response_model=Trip)
async def update_trip(trip_id: str, data: TripUpdate, user: User = Depends(get_current_user)):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.trips.update_one(
        {"id": trip_id, "user_id": user.id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip = await db.trips.find_one({"id": trip_id}, {"_id": 0})
    return trip

@api_router.delete("/trips/{trip_id}")
async def delete_trip(trip_id: str, user: User = Depends(get_current_user)):
    result = await db.trips.delete_one({"id": trip_id, "user_id": user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip deleted successfully"}

# ===== GOOGLE DRIVE ENDPOINTS =====

async def get_drive_service(user: User = Depends(get_current_user)):
    creds_doc = await db.drive_credentials.find_one({"user_id": user.id})
    if not creds_doc:
        raise HTTPException(
            status_code=400, 
            detail="Google Drive not connected. Please connect your Drive first."
        )
    
    creds = Credentials(
        token=creds_doc["access_token"],
        refresh_token=creds_doc.get("refresh_token"),
        token_uri=creds_doc["token_uri"],
        client_id=creds_doc["client_id"],
        client_secret=creds_doc["client_secret"],
        scopes=creds_doc["scopes"]
    )
    
    if creds.expired and creds.refresh_token:
        logger.info(f"Refreshing expired token for user {user.id}")
        creds.refresh(GoogleRequest())
        
        await db.drive_credentials.update_one(
            {"user_id": user.id},
            {"$set": {
                "access_token": creds.token,
                "expiry": creds.expiry.isoformat() if creds.expiry else None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    
    return build('drive', 'v3', credentials=creds)

@api_router.get("/drive/connect")
async def connect_drive(user: User = Depends(get_current_user)):
    try:
        redirect_uri = os.getenv("GOOGLE_DRIVE_REDIRECT_URI")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        if not all([redirect_uri, client_id, client_secret]):
            raise HTTPException(status_code=500, detail="Google Drive credentials not configured")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=['https://www.googleapis.com/auth/drive.file'],
            redirect_uri=redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=user.id
        )
        
        logger.info(f"Drive OAuth initiated for user {user.id}")
        return {"authorization_url": authorization_url}
    
    except Exception as e:
        logger.error(f"Failed to initiate OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate OAuth: {str(e)}")

@api_router.get("/drive/callback")
async def drive_callback(code: str = Query(...), state: str = Query(...)):
    try:
        redirect_uri = os.getenv("GOOGLE_DRIVE_REDIRECT_URI")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=None,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        logger.info(f"Drive credentials obtained for user {state}, scopes: {credentials.scopes}")
        
        required_scopes = {"https://www.googleapis.com/auth/drive.file"}
        granted_scopes = set(credentials.scopes or [])
        if not required_scopes.issubset(granted_scopes):
            missing = required_scopes - granted_scopes
            logger.error(f"Missing required Drive scopes: {missing}")
            raise HTTPException(
                status_code=400,
                detail=f"Missing required Drive scopes: {', '.join(missing)}"
            )
        
        await db.drive_credentials.update_one(
            {"user_id": state},
            {"$set": {
                "user_id": state,
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
        logger.info(f"Drive credentials stored for user {state}")
        
        frontend_url = os.getenv("FRONTEND_URL", os.getenv("REACT_APP_BACKEND_URL", "").replace("/api", ""))
        return RedirectResponse(url=f"{frontend_url}/dashboard?drive_connected=true")
    
    except Exception as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        frontend_url = os.getenv("FRONTEND_URL", os.getenv("REACT_APP_BACKEND_URL", "").replace("/api", ""))
        return RedirectResponse(url=f"{frontend_url}/dashboard?drive_error=true")

@api_router.get("/drive/status")
async def check_drive_status(user: User = Depends(get_current_user)):
    creds_doc = await db.drive_credentials.find_one({"user_id": user.id})
    return {"connected": creds_doc is not None}

@api_router.post("/drive/upload/{passenger_id}")
async def upload_to_drive(
    passenger_id: str,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    try:
        service = await get_drive_service(user)
        
        passenger = await db.passengers.find_one({"id": passenger_id, "user_id": user.id})
        if not passenger:
            raise HTTPException(status_code=404, detail="Passenger not found")
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        file_metadata = {
            'name': file.filename,
            'parents': []
        }
        
        media = MediaFileUpload(tmp_path, mimetype=file.content_type)
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, webViewLink'
        ).execute()
        
        os.unlink(tmp_path)
        
        doc_info = {
            "id": uploaded_file['id'],
            "name": uploaded_file['name'],
            "mimeType": uploaded_file['mimeType'],
            "webViewLink": uploaded_file.get('webViewLink'),
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.passengers.update_one(
            {"id": passenger_id},
            {"$push": {"documents": doc_info}}
        )
        
        return doc_info
    
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@api_router.delete("/drive/files/{file_id}")
async def delete_drive_file(
    file_id: str,
    passenger_id: str = Query(...),
    user: User = Depends(get_current_user)
):
    try:
        service = await get_drive_service(user)
        
        service.files().delete(fileId=file_id).execute()
        
        await db.passengers.update_one(
            {"id": passenger_id, "user_id": user.id},
            {"$pull": {"documents": {"id": file_id}}}
        )
        
        return {"message": "File deleted successfully"}
    
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

# ===== DASHBOARD STATS =====

@api_router.get("/stats")
async def get_stats(user: User = Depends(get_current_user)):
    total_passengers = await db.passengers.count_documents({"user_id": user.id})
    total_trips = await db.trips.count_documents({"user_id": user.id})
    upcoming_trips = await db.trips.count_documents({"user_id": user.id, "status": "upcoming"})
    total_calls = await db.calls.count_documents({"user_id": user.id})
    
    return {
        "total_passengers": total_passengers,
        "total_trips": total_trips,
        "upcoming_trips": upcoming_trips,
        "total_calls": total_calls
    }

# ===== WHATSAPP MODELS =====

class WhatsAppMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    passenger_id: str
    direction: str
    message: str
    phone_number: str
    status: str = "sent"
    twilio_sid: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class WhatsAppMessageCreate(BaseModel):
    passenger_id: str
    message: str

class WhatsAppWebhook(BaseModel):
    MessageSid: str
    From: str
    To: str
    Body: str

# ===== WHATSAPP ENDPOINTS =====

def get_twilio_client():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not account_sid or not auth_token:
        raise HTTPException(status_code=500, detail="Twilio credentials not configured")
    return TwilioClient(account_sid, auth_token)

@api_router.post("/whatsapp/send")
async def send_whatsapp_message(data: WhatsAppMessageCreate, user: User = Depends(get_current_user)):
    try:
        passenger = await db.passengers.find_one({"id": data.passenger_id, "user_id": user.id}, {"_id": 0})
        if not passenger:
            raise HTTPException(status_code=404, detail="Passenger not found")
        
        if not passenger.get("phone"):
            raise HTTPException(status_code=400, detail="Passenger has no phone number")
        
        phone_number = passenger["phone"]
        if not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
        
        twilio_client = get_twilio_client()
        twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        message = twilio_client.messages.create(
            from_=f"whatsapp:{twilio_whatsapp_number}",
            to=f"whatsapp:{phone_number}",
            body=data.message
        )
        
        whatsapp_msg = WhatsAppMessage(
            user_id=user.id,
            passenger_id=data.passenger_id,
            direction="outbound",
            message=data.message,
            phone_number=phone_number,
            status="sent",
            twilio_sid=message.sid
        )
        
        await db.whatsapp_messages.insert_one(whatsapp_msg.model_dump())
        
        return whatsapp_msg
    
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@api_router.get("/whatsapp/messages/{passenger_id}", response_model=List[WhatsAppMessage])
async def get_whatsapp_messages(passenger_id: str, user: User = Depends(get_current_user)):
    messages = await db.whatsapp_messages.find(
        {"passenger_id": passenger_id, "user_id": user.id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    return messages

@api_router.post("/whatsapp/webhook")
async def whatsapp_webhook(
    MessageSid: str = Query(...),
    From: str = Query(...),
    To: str = Query(...),
    Body: str = Query(...)
):
    try:
        phone_number = From.replace("whatsapp:", "")
        
        passenger = await db.passengers.find_one({"phone": {"$regex": phone_number.replace("+", "")}})
        
        if passenger:
            whatsapp_msg = WhatsAppMessage(
                user_id=passenger["user_id"],
                passenger_id=passenger["id"],
                direction="inbound",
                message=Body,
                phone_number=phone_number,
                status="received",
                twilio_sid=MessageSid
            )
            
            await db.whatsapp_messages.insert_one(whatsapp_msg.model_dump())
            
            logger.info(f"Received WhatsApp message from {phone_number}: {Body}")
        else:
            logger.warning(f"Received message from unknown number: {phone_number}")
        
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

@api_router.get("/whatsapp/status")
async def check_whatsapp_status():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    configured = bool(account_sid and auth_token and whatsapp_number)
    
    return {
        "configured": configured,
        "whatsapp_number": whatsapp_number if configured else None
    }

# ===== NOTIFICATIONS =====

@api_router.get("/notifications")
async def get_notifications(user: User = Depends(get_current_user)):
    notifications = []
    now = datetime.now(timezone.utc)
    today = now.date()

    # Check passport expiry for all passengers
    passengers = await db.passengers.find({"user_id": user.id}, {"_id": 0}).to_list(1000)
    for p in passengers:
        expiry_str = p.get("passport_expiry")
        if not expiry_str:
            continue
        try:
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        days_left = (expiry_date - today).days
        if days_left < 0:
            notifications.append({
                "id": f"passport-expired-{p['id']}",
                "type": "passport_expired",
                "severity": "critical",
                "title": "Pasaporte vencido",
                "message": f"El pasaporte de {p['full_name']} venció hace {abs(days_left)} días.",
                "passenger_id": p["id"],
                "passenger_name": p["full_name"],
                "date": expiry_str,
            })
        elif days_left <= 30:
            notifications.append({
                "id": f"passport-30-{p['id']}",
                "type": "passport_expiry",
                "severity": "high",
                "title": "Pasaporte por vencer (30 días)",
                "message": f"El pasaporte de {p['full_name']} vence en {days_left} días ({expiry_str}).",
                "passenger_id": p["id"],
                "passenger_name": p["full_name"],
                "date": expiry_str,
            })
        elif days_left <= 60:
            notifications.append({
                "id": f"passport-60-{p['id']}",
                "type": "passport_expiry",
                "severity": "medium",
                "title": "Pasaporte por vencer (60 días)",
                "message": f"El pasaporte de {p['full_name']} vence en {days_left} días ({expiry_str}).",
                "passenger_id": p["id"],
                "passenger_name": p["full_name"],
                "date": expiry_str,
            })
        elif days_left <= 90:
            notifications.append({
                "id": f"passport-90-{p['id']}",
                "type": "passport_expiry",
                "severity": "low",
                "title": "Pasaporte por vencer (90 días)",
                "message": f"El pasaporte de {p['full_name']} vence en {days_left} días ({expiry_str}).",
                "passenger_id": p["id"],
                "passenger_name": p["full_name"],
                "date": expiry_str,
            })

    # Check upcoming trips (within 7 days)
    trips = await db.trips.find({"user_id": user.id, "status": "upcoming"}, {"_id": 0}).to_list(1000)
    for t in trips:
        start_str = t.get("start_date")
        if not start_str:
            continue
        try:
            start_date = datetime.strptime(start_str[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        days_until = (start_date - today).days
        if 0 <= days_until <= 7:
            # Find passenger name
            passenger = await db.passengers.find_one({"id": t.get("passenger_id")}, {"_id": 0})
            pax_name = passenger["full_name"] if passenger else "Desconocido"
            notifications.append({
                "id": f"trip-soon-{t['id']}",
                "type": "trip_upcoming",
                "severity": "info",
                "title": "Viaje próximo",
                "message": f"El viaje '{t['title']}' de {pax_name} a {t['destination']} inicia en {days_until} día(s).",
                "passenger_id": t.get("passenger_id"),
                "passenger_name": pax_name,
                "date": start_str,
            })

    # Check trips ending soon (within 3 days)
    ongoing_trips = await db.trips.find({"user_id": user.id, "status": "ongoing"}, {"_id": 0}).to_list(1000)
    for t in ongoing_trips:
        end_str = t.get("end_date")
        if not end_str:
            continue
        try:
            end_date = datetime.strptime(end_str[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        days_until_end = (end_date - today).days
        if 0 <= days_until_end <= 3:
            passenger = await db.passengers.find_one({"id": t.get("passenger_id")}, {"_id": 0})
            pax_name = passenger["full_name"] if passenger else "Desconocido"
            notifications.append({
                "id": f"trip-ending-{t['id']}",
                "type": "trip_ending",
                "severity": "info",
                "title": "Viaje finalizando",
                "message": f"El viaje '{t['title']}' de {pax_name} finaliza en {days_until_end} día(s).",
                "passenger_id": t.get("passenger_id"),
                "passenger_name": pax_name,
                "date": end_str,
            })

    # Filter out dismissed notifications
    dismissed = await db.dismissed_notifications.find({"user_id": user.id}, {"_id": 0}).to_list(1000)
    dismissed_ids = {d["notification_id"] for d in dismissed}
    notifications = [n for n in notifications if n["id"] not in dismissed_ids]

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    notifications.sort(key=lambda n: severity_order.get(n["severity"], 5))

    return {"notifications": notifications, "count": len(notifications)}


@api_router.post("/notifications/dismiss/{notification_id}")
async def dismiss_notification(notification_id: str, user: User = Depends(get_current_user)):
    await db.dismissed_notifications.update_one(
        {"user_id": user.id, "notification_id": notification_id},
        {"$set": {
            "user_id": user.id,
            "notification_id": notification_id,
            "dismissed_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    return {"message": "Notification dismissed"}


@api_router.delete("/notifications/dismissed")
async def clear_dismissed(user: User = Depends(get_current_user)):
    await db.dismissed_notifications.delete_many({"user_id": user.id})
    return {"message": "Dismissed notifications cleared"}


# ===== OCR DOCUMENT SCANNING =====

import base64
import json as json_module
from openai import AsyncOpenAI

OCR_SYSTEM_PROMPT = "Eres un experto en OCR de documentos de identidad. Extraes información de pasaportes y carnets de identidad con precisión."

OCR_USER_PROMPT = """Analiza esta imagen de pasaporte o documento de identidad. Extrae la siguiente información y devuelve ÚNICAMENTE un objeto JSON válido con estos campos:
{
  "full_name": "Nombre completo tal como aparece en el documento",
  "passport_number": "Número del documento",
  "date_of_birth": "Fecha de nacimiento en formato YYYY-MM-DD",
  "passport_expiry": "Fecha de vencimiento en formato YYYY-MM-DD",
  "nationality": "Nacionalidad",
  "gender": "M o F",
  "document_type": "passport o id_card"
}

Si un campo no es visible o no se puede leer, usa null.
Devuelve SOLO el JSON, sin texto adicional, sin markdown, sin backticks."""


async def run_ocr_on_image(b64_image: str) -> dict:
    """Calls OpenAI's vision model directly (replaces the Emergent-only proxy)."""
    openai_key = os.environ.get('OPENAI_API_KEY')
    if not openai_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY no configurada")

    client_ai = AsyncOpenAI(api_key=openai_key)

    response = await client_ai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": OCR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": OCR_USER_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                ]
            }
        ],
        max_tokens=500,
    )

    response_text = response.choices[0].message.content.strip()
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    return json_module.loads(response_text)


class OCRScanResponse(BaseModel):
    full_name: Optional[str] = None
    passport_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    passport_expiry: Optional[str] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    document_type: Optional[str] = None

@api_router.post("/ocr/scan")
async def scan_document(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    try:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máx 10MB)")

        b64_image = base64.b64encode(content).decode('utf-8')
        extracted_data = await run_ocr_on_image(b64_image)

        return {
            "success": True,
            "data": extracted_data,
            "message": "Datos extraídos exitosamente"
        }

    except json_module.JSONDecodeError:
        logger.error("Failed to parse OCR response")
        return {
            "success": False,
            "data": {},
            "message": "No se pudo extraer datos del documento. Intenta con una imagen más clara."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR scan error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al escanear documento: {str(e)}")


@api_router.post("/ocr/scan-and-create")
async def scan_and_create_passenger(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    """Scan a document and create a new passenger with extracted data"""
    try:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máx 10MB)")

        b64_image = base64.b64encode(content).decode('utf-8')
        extracted_data = await run_ocr_on_image(b64_image)

        return {
            "success": True,
            "data": extracted_data,
            "message": "Datos extraídos exitosamente. Revisa y confirma antes de guardar."
        }

    except json_module.JSONDecodeError:
        return {
            "success": False,
            "data": {},
            "message": "No se pudo extraer datos del documento. Intenta con una imagen más clara."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR scan-and-create error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al escanear documento: {str(e)}")


# ===== PDF EXPORT =====

from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER


@api_router.get("/passengers/{passenger_id}/pdf")
async def export_passenger_pdf(passenger_id: str, user: User = Depends(get_current_user)):
    passenger = await db.passengers.find_one({"id": passenger_id, "user_id": user.id}, {"_id": 0})
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")

    trips = await db.trips.find({"passenger_id": passenger_id, "user_id": user.id}, {"_id": 0}).sort("start_date", -1).to_list(1000)
    calls = await db.calls.find({"passenger_id": passenger_id, "user_id": user.id}, {"_id": 0}).sort("call_date", -1).to_list(1000)
    messages = await db.whatsapp_messages.find({"passenger_id": passenger_id, "user_id": user.id}, {"_id": 0}).sort("created_at", -1).to_list(100)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm, leftMargin=20*mm, rightMargin=20*mm)

    dark = HexColor("#0f172a")
    amber = HexColor("#d97706")
    slate600 = HexColor("#475569")
    slate200 = HexColor("#e2e8f0")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=22, textColor=dark, spaceAfter=2*mm, fontName="Helvetica-Bold")
    section_style = ParagraphStyle("SectionCustom", parent=styles["Heading2"], fontSize=14, textColor=amber, spaceBefore=8*mm, spaceAfter=4*mm, fontName="Helvetica-Bold")
    normal_style = ParagraphStyle("NormalCustom", parent=styles["Normal"], fontSize=10, textColor=dark, leading=14)
    small_style = ParagraphStyle("SmallCustom", parent=styles["Normal"], fontSize=8, textColor=slate600, leading=11)

    elements = []

    # Header
    elements.append(Paragraph("Ficha de Pasajero", title_style))
    elements.append(Paragraph(passenger.get("full_name", "Sin nombre"), ParagraphStyle("NameStyle", parent=styles["Heading1"], fontSize=18, textColor=dark, spaceAfter=1*mm)))
    elements.append(Paragraph(f"Generado: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')} UTC", small_style))
    elements.append(Spacer(1, 4*mm))
    elements.append(HRFlowable(width="100%", thickness=1, color=slate200))

    # Personal Info
    elements.append(Paragraph("Informacion Personal", section_style))

    info_data = []
    fields = [
        ("Email", passenger.get("email")),
        ("Telefono", passenger.get("phone")),
        ("Pasaporte", passenger.get("passport_number")),
        ("Vencimiento", passenger.get("passport_expiry")),
        ("Nacimiento", passenger.get("date_of_birth")),
        ("Nacionalidad", passenger.get("nationality")),
        ("Direccion", passenger.get("address")),
    ]
    for label, value in fields:
        if value:
            info_data.append([
                Paragraph(f"<b>{label}</b>", small_style),
                Paragraph(str(value), normal_style)
            ])

    if info_data:
        info_table = Table(info_data, colWidths=[35*mm, 130*mm])
        info_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LINEBELOW", (0, 0), (-1, -2), 0.5, slate200),
        ]))
        elements.append(info_table)

    if passenger.get("notes"):
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph("<b>Notas:</b>", small_style))
        elements.append(Paragraph(passenger["notes"], normal_style))

    # Trips
    elements.append(Paragraph(f"Historial de Viajes ({len(trips)})", section_style))
    if trips:
        trip_header = [
            Paragraph("<b>Viaje</b>", small_style),
            Paragraph("<b>Destino</b>", small_style),
            Paragraph("<b>Fechas</b>", small_style),
            Paragraph("<b>Estado</b>", small_style),
            Paragraph("<b>Costo</b>", small_style),
        ]
        trip_rows = [trip_header]
        status_map = {"upcoming": "Proximo", "ongoing": "En curso", "completed": "Completado", "cancelled": "Cancelado"}
        for t in trips:
            trip_rows.append([
                Paragraph(t.get("title", ""), normal_style),
                Paragraph(t.get("destination", ""), normal_style),
                Paragraph(f"{t.get('start_date', '')[:10]} a {t.get('end_date', '')[:10]}", small_style),
                Paragraph(status_map.get(t.get("status", ""), t.get("status", "")), normal_style),
                Paragraph(f"${t.get('total_cost', 0):,.2f}" if t.get("total_cost") else "-", normal_style),
            ])
        trip_table = Table(trip_rows, colWidths=[38*mm, 38*mm, 38*mm, 25*mm, 26*mm])
        trip_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f8fafc")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, slate200),
            ("LINEBELOW", (0, 0), (-1, 0), 1, dark),
        ]))
        elements.append(trip_table)
    else:
        elements.append(Paragraph("No hay viajes registrados.", small_style))

    # Calls
    elements.append(Paragraph(f"Historial de Llamadas ({len(calls)})", section_style))
    if calls:
        call_header = [
            Paragraph("<b>Fecha</b>", small_style),
            Paragraph("<b>Duracion</b>", small_style),
            Paragraph("<b>Notas</b>", small_style),
        ]
        call_rows = [call_header]
        for c in calls:
            call_rows.append([
                Paragraph(c.get("call_date", "")[:10], normal_style),
                Paragraph(f"{c.get('duration', '-')} min" if c.get("duration") else "-", normal_style),
                Paragraph(c.get("notes", "") or "-", small_style),
            ])
        call_table = Table(call_rows, colWidths=[30*mm, 25*mm, 110*mm])
        call_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f8fafc")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, slate200),
            ("LINEBELOW", (0, 0), (-1, 0), 1, dark),
        ]))
        elements.append(call_table)
    else:
        elements.append(Paragraph("No hay llamadas registradas.", small_style))

    # WhatsApp
    if messages:
        elements.append(Paragraph(f"Ultimos Mensajes WhatsApp ({len(messages)})", section_style))
        for m in messages[:20]:
            direction = "Enviado" if m.get("direction") == "outbound" else "Recibido"
            dt = m.get("created_at", "")[:16].replace("T", " ")
            elements.append(Paragraph(f"<b>[{direction}] {dt}</b>", small_style))
            elements.append(Paragraph(m.get("message", ""), normal_style))
            elements.append(Spacer(1, 2*mm))

    # Footer
    elements.append(Spacer(1, 10*mm))
    elements.append(HRFlowable(width="100%", thickness=1, color=slate200))
    elements.append(Paragraph("TravelCRM - Gestion de Viajes", ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=slate600, alignment=TA_CENTER)))

    doc.build(elements)
    buffer.seek(0)

    safe_name = passenger.get("full_name", "pasajero").replace(" ", "_")
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="ficha_{safe_name}.pdf"'}
    )


# ===== DEMO ACCOUNT =====

from demo_data import get_demo_data

@api_router.post("/demo/reset")
async def reset_demo_account():
    """Create or reset demo account with sample data"""
    try:
        # Check if demo user exists
        demo_user = await db.users.find_one({"email": "demo@travelcrm.com"})
        
        if demo_user:
            user_id = demo_user["id"]
            # Delete existing demo data
            await db.passengers.delete_many({"user_id": user_id})
            await db.trips.delete_many({"user_id": user_id})
            await db.calls.delete_many({"user_id": user_id})
            await db.whatsapp_messages.delete_many({"user_id": user_id})
        else:
            # Create demo user
            user_id = str(uuid.uuid4())
            hashed_pw = hash_password("demo123")
            demo_user_data = {
                "id": user_id,
                "email": "demo@travelcrm.com",
                "name": "Usuario Demo",
                "password": hashed_pw,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.insert_one(demo_user_data)
        
        # Get demo data
        demo_data = get_demo_data(user_id)
        
        # Insert demo data
        if demo_data["passengers"]:
            await db.passengers.insert_many(demo_data["passengers"])
        if demo_data["trips"]:
            await db.trips.insert_many(demo_data["trips"])
        if demo_data["calls"]:
            await db.calls.insert_many(demo_data["calls"])
        if demo_data["whatsapp_messages"]:
            await db.whatsapp_messages.insert_many(demo_data["whatsapp_messages"])
        
        # Generate demo token
        token = create_access_token({"sub": user_id})
        
        return {
            "message": "Demo account created successfully",
            "credentials": {
                "email": "demo@travelcrm.com",
                "password": "demo123"
            },
            "token": token,
            "stats": {
                "passengers": len(demo_data["passengers"]),
                "trips": len(demo_data["trips"]),
                "calls": len(demo_data["calls"]),
                "whatsapp_messages": len(demo_data["whatsapp_messages"])
            }
        }
    except Exception as e:
        logger.error(f"Error creating demo account: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating demo account: {str(e)}")

@api_router.get("/demo/credentials")
async def get_demo_credentials():
    """Get demo account credentials"""
    return {
        "email": "demo@travelcrm.com",
        "password": "demo123",
        "note": "Use these credentials to access the demo account"
    }

# ===== CONTACT FORM =====

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    message: Optional[str] = None

@api_router.post("/contact")
async def submit_contact_form(data: ContactForm):
    """Handle contact form submissions"""
    try:
        contact_data = data.model_dump()
        contact_data["id"] = str(uuid.uuid4())
        contact_data["created_at"] = datetime.now(timezone.utc).isoformat()
        contact_data["status"] = "new"
        
        await db.contacts.insert_one(contact_data)
        
        logger.info(f"New contact form submission from {data.email}")
        
        return {"message": "Contact form submitted successfully"}
    except Exception as e:
        logger.error(f"Error submitting contact form: {str(e)}")
        raise HTTPException(status_code=500, detail="Error submitting contact form")

app.include_router(api_router)

_cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
if _cors_origins == ['*']:
    logger.warning(
        "CORS_ORIGINS no está configurado: aceptando peticiones de CUALQUIER origen. "
        "Esto es aceptable en desarrollo local, pero antes de producción agrega "
        "CORS_ORIGINS=https://tu-dominio.com a tu .env"
    )

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()