# TravelCRM - PRD (Product Requirements Document)

## Problema Original
Construir un CRM basico para agentes de viajes, con fichas completas de pasajeros (con apartado de imagenes para registrar fotos de pasaporte a traves de Google Drive), registro de llamadas, historial de viajes pasados, presentes y futuros, y un calendario interactivo. Adicionalmente, integracion con WhatsApp para interaccion y registro de chat en la ficha del pasajero, y funcionalidades para vender el CRM como SaaS (Landing page, cuenta Demo).

## Usuarios Objetivo
- Agentes de viajes independientes y agencias de viajes
- Usuarios demo para probar la plataforma

## Stack Tecnologico
- **Frontend**: React 19, React Router v6, Tailwind CSS, Shadcn/UI, React-Big-Calendar
- **Backend**: FastAPI, MongoDB (Motor Async), PyJWT, bcrypt
- **Integraciones**: Twilio (WhatsApp), Google Drive API (Documentos)

## Arquitectura de Rutas
- Publica: `/` (Landing Page), `/login`
- Privada: `/app/*` (Dashboard, Pasajeros, Calendario)

## Funcionalidades Implementadas

### Autenticacion (DONE)
- Registro y Login con JWT
- Proteccion de rutas privadas

### Dashboard (DONE)
- Estadisticas: Total pasajeros, viajes proximos, total viajes, llamadas registradas
- Proximos viajes y llamadas recientes

### Gestion de Pasajeros (DONE)
- CRUD completo de pasajeros
- Fichas detalladas con pestanas: Info, Documentos, Llamadas, Viajes, WhatsApp
- Busqueda y filtrado

### Registro de Llamadas (DONE)
- Crear/eliminar llamadas por pasajero
- Fecha, duracion y notas

### Historial de Viajes (DONE)
- CRUD de viajes con estados: upcoming, ongoing, completed, cancelled
- Detalles: destino, fechas, costo, notas

### Calendario Interactivo (DONE)
- Vista mensual/semanal/diaria con react-big-calendar
- Visualizacion de viajes en el calendario

### Integracion Google Drive (DONE)
- OAuth para conectar Drive
- Subida de documentos (pasaportes, etc.) por pasajero
- Eliminacion de archivos

### Integracion WhatsApp - Twilio (DONE)
- Envio de mensajes WhatsApp desde la ficha del pasajero
- Recepcion de mensajes via webhook
- Historial de conversacion por pasajero

### Landing Page Comercial (DONE)
- Pagina de presentacion del producto
- Boton "Probar Demo Gratis"
- Formulario de contacto "Solicitar Informacion"

### Cuenta Demo (DONE)
- Endpoint `/api/demo/reset` genera datos de prueba
- Credenciales: demo@travelcrm.com / demo123
- 5 pasajeros, 4 viajes, 5 llamadas, mensajes WhatsApp de ejemplo

## Backlog (Pendiente)

### P1 - SaaS Setup (Opcion B)
- Integracion de sistema de pagos (Stripe)
- Arquitectura Multi-Tenant (Multi-agencia)
- Onboarding automatizado por email
- Panel de administracion para gestionar clientes/agencias

### P2 - Mejoras
- Aislamiento de credenciales OAuth/Drive por agencia
- Mejoras de UI/UX
- Reportes y analiticas avanzadas
- Exportacion de datos

## Esquema de Base de Datos
- `users`: {id, email, password, name, created_at}
- `passengers`: {id, user_id, full_name, email, phone, passport_number, passport_expiry, date_of_birth, nationality, address, notes, documents[], created_at, updated_at}
- `trips`: {id, user_id, passenger_id, title, destination, start_date, end_date, status, details[], total_cost, notes, created_at, updated_at}
- `calls`: {id, user_id, passenger_id, call_date, duration, notes, created_at}
- `whatsapp_messages`: {id, user_id, passenger_id, direction, message, phone_number, status, twilio_sid, created_at}
- `drive_credentials`: {user_id, access_token, refresh_token, token_uri, client_id, client_secret, scopes, expiry}
- `contacts`: {id, name, email, phone, company, message, status, created_at}

## Endpoints API
- Auth: POST /api/auth/register, POST /api/auth/login, GET /api/auth/me
- Passengers: GET/POST /api/passengers, GET/PUT/DELETE /api/passengers/{id}
- Trips: GET/POST /api/trips, GET/PUT/DELETE /api/trips/{id}
- Calls: GET/POST /api/calls, DELETE /api/calls/{id}
- WhatsApp: POST /api/whatsapp/send, GET /api/whatsapp/messages/{passenger_id}, POST /api/whatsapp/webhook, GET /api/whatsapp/status
- Drive: GET /api/drive/connect, GET /api/drive/callback, GET /api/drive/status, POST /api/drive/upload/{passenger_id}, DELETE /api/drive/files/{file_id}
- Demo: POST /api/demo/reset, GET /api/demo/credentials
- Contact: POST /api/contact
- Stats: GET /api/stats
- Notifications: GET /api/notifications, POST /api/notifications/dismiss/{id}, DELETE /api/notifications/dismissed
- OCR: POST /api/ocr/scan, POST /api/ocr/scan-and-create

## Integraciones
- Twilio (WhatsApp Messaging) - Credenciales en .env
- Google Drive API (File Uploads) - OAuth configurado
- OpenAI GPT-4o (OCR de documentos) - via Emergent LLM Key
