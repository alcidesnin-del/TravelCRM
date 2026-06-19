# Guía de Despliegue - TravelCRM

Esta guía asume que es tu primera vez desplegando una aplicación web completa
(frontend + backend + base de datos). Sigue los pasos en orden.

---

## 1. Qué necesitas crear (todo es gratis para empezar)

| Servicio | Para qué | Plan gratuito |
|---|---|---|
| MongoDB Atlas | Base de datos | Sí (512MB, suficiente para validar) |
| Railway o Render | Backend (FastAPI) | Sí (con límites de horas/mes) |
| Vercel | Frontend (React) | Sí (generoso para proyectos chicos) |

**Por qué esta combinación:** Vercel es excelente y gratuito para frontends
React. Railway/Render son más simples que AWS para correr un backend Python
sin pelear con configuración de servidores.

---

## 2. Base de datos: MongoDB Atlas

1. Crea cuenta en https://www.mongodb.com/cloud/atlas/register
2. Crea un cluster gratuito (M0)
3. En "Database Access", crea un usuario con contraseña
4. En "Network Access", agrega `0.0.0.0/0` (permite conexión desde cualquier
   lugar; lo normal para empezar, lo puedes restringir después)
5. Click en "Connect" → "Drivers" → copia la URL de conexión, se ve así:
   ```
   mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```
6. Guarda esa URL, la necesitas en el paso 3

---

## 3. Backend: Railway

1. Crea cuenta en https://railway.app (puedes usar tu GitHub)
2. "New Project" → "Deploy from GitHub repo" → selecciona tu repo TravelCRM
3. Railway detecta que es Python. En **Settings**, configura:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. En la pestaña **Variables**, agrega (usa los valores de tu `.env.example`):
   ```
   MONGO_URL=<la URL que copiaste de Atlas>
   DB_NAME=travelcrm
   JWT_SECRET=<genera uno nuevo, ver abajo>
   CORS_ORIGINS=<lo configuras en el paso 4, déjalo vacío por ahora>
   FRONTEND_URL=<lo configuras en el paso 4>
   OPENAI_API_KEY=<opcional, solo si quieres OCR de pasaportes>
   ```
5. Para generar un `JWT_SECRET` seguro, corre esto en tu computadora:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
6. Click en "Deploy". Railway te da una URL pública, algo como:
   `https://travelcrm-production.up.railway.app`
7. Guarda esa URL, la necesitas en el paso 4

---

## 4. Frontend: Vercel

1. Crea cuenta en https://vercel.com (usa tu GitHub)
2. "Add New Project" → selecciona tu repo TravelCRM
3. En **Root Directory**, selecciona `frontend`
4. En **Environment Variables**, agrega:
   ```
   REACT_APP_BACKEND_URL=https://travelcrm-production.up.railway.app/api
   ```
   (usa la URL real que te dio Railway, con `/api` al final)
5. Click en "Deploy". Vercel te da una URL, algo como:
   `https://travelcrm.vercel.app`

---

## 5. Conectar ambos lados (paso que la gente olvida)

Vuelve a Railway y actualiza estas dos variables con la URL real de Vercel:

```
CORS_ORIGINS=https://travelcrm.vercel.app
FRONTEND_URL=https://travelcrm.vercel.app
```

Sin este paso, el backend rechazará las peticiones del frontend por seguridad
(CORS). Railway redesplegará automáticamente al guardar.

---

## 6. Probar que todo funciona

1. Abre `https://travelcrm.vercel.app`
2. Deberías ver la landing page
3. Prueba el botón de demo o regístrate con un usuario nuevo
4. Si algo falla, revisa los logs en Railway (pestaña "Deployments" → click
   en el deploy → "View Logs")

---

## 7. Funcionalidades opcionales (actívalas solo si las vas a usar)

**OCR de pasaportes** (requiere `OPENAI_API_KEY`):
- Crea cuenta en https://platform.openai.com
- Genera una clave en https://platform.openai.com/api-keys
- Carga saldo (mínimo $5 USD); GPT-4o cobra por uso, no es caro para volúmenes
  bajos (~$0.01-0.03 por escaneo)

**WhatsApp vía Twilio** (requiere `TWILIO_*`):
- Más complejo de configurar (requiere número verificado de WhatsApp Business)
- Te recomiendo dejarlo para cuando tengas el primer cliente pagando, no antes

**Google Drive** (requiere `GOOGLE_CLIENT_*`):
- Necesitas crear un proyecto en Google Cloud Console y configurar OAuth
- También recomendable dejarlo para después de validar

---

## 8. Dominio propio (opcional, cuando ya tengas tracción)

Cuando quieras verte más profesional, en vez de `travelcrm.vercel.app`:
1. Compra un dominio (ej: en Namecheap, ~$10-15 USD/año)
2. En Vercel, ve a tu proyecto → Settings → Domains → agrega tu dominio
3. Sigue las instrucciones de Vercel para configurar los DNS

---

## Resumen de costos para validar (mes 1)

| Servicio | Costo |
|---|---|
| MongoDB Atlas (M0) | $0 |
| Railway (plan gratuito, ~500 horas) | $0 (luego ~$5/mes) |
| Vercel (plan Hobby) | $0 |
| OpenAI (si usas OCR) | ~$5-10 según uso |
| **Total** | **$0 a $15 USD** |

No necesitas gastar nada para tener el CRM corriendo y mostrárselo a
clientes potenciales.
