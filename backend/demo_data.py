from datetime import datetime, timezone, timedelta
import random

def get_demo_data(user_id: str):
    """Generate demo data for a user"""
    
    # Demo passengers
    passengers = [
        {
            "id": "demo-passenger-1",
            "user_id": user_id,
            "full_name": "María González López",
            "email": "maria.gonzalez@email.com",
            "phone": "+34612345678",
            "passport_number": "ES123456789",
            "passport_expiry": (datetime.now(timezone.utc) + timedelta(days=730)).strftime("%Y-%m-%d"),
            "date_of_birth": "1985-03-15",
            "nationality": "Española",
            "address": "Calle Mayor 123, Madrid, España",
            "notes": "Cliente VIP. Prefiere vuelos directos y hoteles 5 estrellas.",
            "documents": [],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=180)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        },
        {
            "id": "demo-passenger-2",
            "user_id": user_id,
            "full_name": "Carlos Rodríguez Martín",
            "email": "carlos.rodriguez@email.com",
            "phone": "+34687654321",
            "passport_number": "ES987654321",
            "passport_expiry": (datetime.now(timezone.utc) + timedelta(days=900)).strftime("%Y-%m-%d"),
            "date_of_birth": "1978-07-22",
            "nationality": "Española",
            "address": "Avenida Diagonal 456, Barcelona, España",
            "notes": "Viaja frecuentemente por negocios. Necesita facturas detalladas.",
            "documents": [],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=150)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        },
        {
            "id": "demo-passenger-3",
            "user_id": user_id,
            "full_name": "Ana Fernández Torres",
            "email": "ana.fernandez@email.com",
            "phone": "+34655123789",
            "passport_number": "ES456789123",
            "passport_expiry": (datetime.now(timezone.utc) + timedelta(days=1095)).strftime("%Y-%m-%d"),
            "date_of_birth": "1990-11-08",
            "nationality": "Española",
            "address": "Plaza España 78, Valencia, España",
            "notes": "Luna de miel planeada para el próximo año. Busca destinos románticos.",
            "documents": [],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=90)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        },
        {
            "id": "demo-passenger-4",
            "user_id": user_id,
            "full_name": "José Luis Sánchez García",
            "email": "joseluis.sanchez@email.com",
            "phone": "+34699887766",
            "passport_number": "ES789456123",
            "passport_expiry": (datetime.now(timezone.utc) + timedelta(days=600)).strftime("%Y-%m-%d"),
            "date_of_birth": "1982-05-30",
            "nationality": "Española",
            "address": "Calle Sevilla 34, Málaga, España",
            "notes": "Familia de 4 personas. Prefiere todo incluido y destinos con playa.",
            "documents": [],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=200)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
        },
        {
            "id": "demo-passenger-5",
            "user_id": user_id,
            "full_name": "Laura Martínez Ruiz",
            "email": "laura.martinez@email.com",
            "phone": "+34622334455",
            "passport_number": "ES321654987",
            "passport_expiry": (datetime.now(timezone.utc) + timedelta(days=450)).strftime("%Y-%m-%d"),
            "date_of_birth": "1995-09-12",
            "nationality": "Española",
            "address": "Gran Vía 89, Madrid, España",
            "notes": "Mochilera. Busca experiencias auténticas y presupuesto ajustado.",
            "documents": [],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=60)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        }
    ]
    
    # Demo trips
    trips = [
        {
            "id": "demo-trip-1",
            "user_id": user_id,
            "passenger_id": "demo-passenger-1",
            "title": "Vacaciones en París",
            "destination": "París, Francia",
            "start_date": (datetime.now(timezone.utc) + timedelta(days=45)).strftime("%Y-%m-%d"),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=52)).strftime("%Y-%m-%d"),
            "status": "upcoming",
            "details": [
                {
                    "type": "Vuelo",
                    "description": "Madrid (MAD) - París (CDG)",
                    "date": (datetime.now(timezone.utc) + timedelta(days=45)).strftime("%Y-%m-%d"),
                    "time": "10:30",
                    "reference_number": "AF2845",
                    "provider": "Air France",
                    "cost": 450.00,
                    "notes": "Asiento ventana confirmado"
                },
                {
                    "type": "Hotel",
                    "description": "Hotel Plaza Athénée - Suite Deluxe",
                    "date": (datetime.now(timezone.utc) + timedelta(days=45)).strftime("%Y-%m-%d"),
                    "reference_number": "HPA789456",
                    "provider": "Booking.com",
                    "cost": 2100.00,
                    "notes": "7 noches, desayuno incluido"
                },
                {
                    "type": "Vuelo",
                    "description": "París (CDG) - Madrid (MAD)",
                    "date": (datetime.now(timezone.utc) + timedelta(days=52)).strftime("%Y-%m-%d"),
                    "time": "18:45",
                    "reference_number": "AF2846",
                    "provider": "Air France",
                    "cost": 450.00,
                    "notes": "Vuelo de regreso"
                }
            ],
            "total_cost": 3000.00,
            "notes": "Viaje romántico. Incluye cena en la Torre Eiffel el segundo día.",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        },
        {
            "id": "demo-trip-2",
            "user_id": user_id,
            "passenger_id": "demo-passenger-2",
            "title": "Conferencia en Nueva York",
            "destination": "Nueva York, USA",
            "start_date": (datetime.now(timezone.utc) + timedelta(days=15)).strftime("%Y-%m-%d"),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=18)).strftime("%Y-%m-%d"),
            "status": "upcoming",
            "details": [
                {
                    "type": "Vuelo",
                    "description": "Madrid (MAD) - Nueva York (JFK)",
                    "date": (datetime.now(timezone.utc) + timedelta(days=15)).strftime("%Y-%m-%d"),
                    "time": "14:00",
                    "reference_number": "IB6251",
                    "provider": "Iberia",
                    "cost": 850.00,
                    "notes": "Clase Business"
                },
                {
                    "type": "Hotel",
                    "description": "Hilton Midtown - Habitación Ejecutiva",
                    "date": (datetime.now(timezone.utc) + timedelta(days=15)).strftime("%Y-%m-%d"),
                    "reference_number": "HNY456789",
                    "provider": "Hilton.com",
                    "cost": 600.00,
                    "notes": "3 noches cerca del centro de convenciones"
                }
            ],
            "total_cost": 1450.00,
            "notes": "Viaje de negocios. Requiere factura detallada.",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        },
        {
            "id": "demo-trip-3",
            "user_id": user_id,
            "passenger_id": "demo-passenger-4",
            "title": "Vacaciones Familiares en Cancún",
            "destination": "Cancún, México",
            "start_date": (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d"),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=104)).strftime("%Y-%m-%d"),
            "status": "upcoming",
            "details": [
                {
                    "type": "Vuelo",
                    "description": "Madrid (MAD) - Cancún (CUN) - 4 pasajeros",
                    "date": (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d"),
                    "time": "22:30",
                    "reference_number": "AM0458",
                    "provider": "Aeroméxico",
                    "cost": 3200.00,
                    "notes": "Familia de 4: 2 adultos, 2 niños"
                },
                {
                    "type": "Hotel",
                    "description": "Resort Todo Incluido - Grand Palladium",
                    "date": (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d"),
                    "reference_number": "GP789123",
                    "provider": "Palladium Hotels",
                    "cost": 4500.00,
                    "notes": "14 noches, todo incluido, 2 habitaciones familiares"
                }
            ],
            "total_cost": 7700.00,
            "notes": "Vacaciones de verano en familia. Incluye actividades para niños.",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=45)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
        },
        {
            "id": "demo-trip-4",
            "user_id": user_id,
            "passenger_id": "demo-passenger-1",
            "title": "Crucero por el Mediterráneo",
            "destination": "Mediterráneo (Barcelona - Roma - Atenas)",
            "start_date": (datetime.now(timezone.utc) - timedelta(days=120)).strftime("%Y-%m-%d"),
            "end_date": (datetime.now(timezone.utc) - timedelta(days=113)).strftime("%Y-%m-%d"),
            "status": "completed",
            "details": [
                {
                    "type": "Crucero",
                    "description": "MSC Cruceros - 7 días Mediterráneo",
                    "date": (datetime.now(timezone.utc) - timedelta(days=120)).strftime("%Y-%m-%d"),
                    "reference_number": "MSC456789",
                    "provider": "MSC Cruceros",
                    "cost": 1800.00,
                    "notes": "Camarote balcón, pensión completa"
                }
            ],
            "total_cost": 1800.00,
            "notes": "Viaje completado. Cliente muy satisfecho.",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=150)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=110)).isoformat()
        }
    ]
    
    # Demo calls
    calls = [
        {
            "id": "demo-call-1",
            "user_id": user_id,
            "passenger_id": "demo-passenger-1",
            "call_date": (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%d"),
            "duration": 15,
            "notes": "Confirmación de reserva de hotel en París. Cliente satisfecho con la elección.",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        },
        {
            "id": "demo-call-2",
            "user_id": user_id,
            "passenger_id": "demo-passenger-2",
            "call_date": (datetime.now(timezone.utc) - timedelta(days=12)).strftime("%Y-%m-%d"),
            "duration": 25,
            "notes": "Consulta sobre requisitos de visa para Estados Unidos. Enviados documentos necesarios.",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=12)).isoformat()
        },
        {
            "id": "demo-call-3",
            "user_id": user_id,
            "passenger_id": "demo-passenger-3",
            "call_date": (datetime.now(timezone.utc) - timedelta(days=8)).strftime("%Y-%m-%d"),
            "duration": 30,
            "notes": "Planificación inicial de luna de miel. Discutiendo opciones: Maldivas vs Bali.",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
        },
        {
            "id": "demo-call-4",
            "user_id": user_id,
            "passenger_id": "demo-passenger-4",
            "call_date": (datetime.now(timezone.utc) - timedelta(days=20)).strftime("%Y-%m-%d"),
            "duration": 20,
            "notes": "Reserva de vacaciones familiares en Cancún. Confirmado resort todo incluido.",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
        },
        {
            "id": "demo-call-5",
            "user_id": user_id,
            "passenger_id": "demo-passenger-5",
            "call_date": (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%d"),
            "duration": 18,
            "notes": "Consulta sobre mochilero en sudeste asiático. Enviadas recomendaciones de hostels.",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        }
    ]
    
    # Demo WhatsApp messages
    whatsapp_messages = [
        {
            "id": "demo-wa-1",
            "user_id": user_id,
            "passenger_id": "demo-passenger-1",
            "direction": "inbound",
            "message": "Hola! Me gustaría confirmar los horarios del vuelo a París",
            "phone_number": "+34612345678",
            "status": "received",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=3)).isoformat()
        },
        {
            "id": "demo-wa-2",
            "user_id": user_id,
            "passenger_id": "demo-passenger-1",
            "direction": "outbound",
            "message": "¡Hola María! Claro, tu vuelo sale el 15 de marzo a las 10:30 desde Madrid (Terminal 4) con Air France. Llegas a París a las 13:00 hora local. ¿Necesitas algo más?",
            "phone_number": "+34612345678",
            "status": "sent",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=2, minutes=45)).isoformat()
        },
        {
            "id": "demo-wa-3",
            "user_id": user_id,
            "passenger_id": "demo-passenger-1",
            "direction": "inbound",
            "message": "Perfecto! Y el hotel tiene desayuno incluido verdad?",
            "phone_number": "+34612345678",
            "status": "received",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=2, minutes=30)).isoformat()
        },
        {
            "id": "demo-wa-4",
            "user_id": user_id,
            "passenger_id": "demo-passenger-1",
            "direction": "outbound",
            "message": "Sí, el Hotel Plaza Athénée incluye desayuno buffet todas las mañanas. También tienes acceso al spa y gimnasio. 😊",
            "phone_number": "+34612345678",
            "status": "sent",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=2, minutes=25)).isoformat()
        },
        {
            "id": "demo-wa-5",
            "user_id": user_id,
            "passenger_id": "demo-passenger-2",
            "direction": "inbound",
            "message": "Necesito la factura del viaje a Nueva York para la empresa",
            "phone_number": "+34687654321",
            "status": "received",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=4, hours=5)).isoformat()
        },
        {
            "id": "demo-wa-6",
            "user_id": user_id,
            "passenger_id": "demo-passenger-2",
            "direction": "outbound",
            "message": "Hola Carlos! Te envío la factura detallada por email en los próximos 10 minutos con todos los conceptos desglosados.",
            "phone_number": "+34687654321",
            "status": "sent",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=4, hours=4, minutes=55)).isoformat()
        }
    ]
    
    return {
        "passengers": passengers,
        "trips": trips,
        "calls": calls,
        "whatsapp_messages": whatsapp_messages
    }
