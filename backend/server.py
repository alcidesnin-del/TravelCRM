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

SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
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

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

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

from twilio.rest import Client

def get_twilio_client():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not account_sid or not auth_token:
        raise HTTPException(status_code=500, detail="Twilio credentials not configured")
    return Client(account_sid, auth_token)

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()