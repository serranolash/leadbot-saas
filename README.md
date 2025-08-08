# LeadBot Sheet SaaS (MVP)

SaaS multi-tenant con FastAPI + Celery + Redis. Adaptadores: LinkedIn (opcional, Selenium) y Computrabajo (requests+bs4).
Exporta a Excel y trae un **blueprint para Render** y configuración para **Railway**.

## 1) Arranque rápido con Docker Compose

```bash
cp .env.example .env
# Genera CRYPTO_FERNET_KEY:
python - <<<'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
docker compose up --build
```

Web: http://localhost:8000  
Trabajador y Beat se levantan solos. Descarga el Excel vía `GET /result/{task_id}`.

## 2) Deploy en Render (Blueprint)

1. Sube este repo a GitHub/GitLab.
2. En Render: **New + Blueprint** → apunta al repo.
3. Render detectará `render.yaml` y creará automáticamente:
   - `leadbot-api` (FastAPI)
   - `leadbot-celery-worker`
   - `leadbot-celery-beat`
   - `leadbot-redis`
4. En `leadbot-api` configura envs si quieres habilitar LinkedIn:
   - `ENABLE_LINKEDIN=true`
   - (Opcional) `DEMO_QUERY` y `DEMO_CREDS_JSON` para cron de demo.
5. Deploy. Visita la URL pública del servicio web.

## 3) Deploy en Railway (Nixpacks)

1. Crea un proyecto y conecta el repo.
2. Railway/Nixpacks detecta `Procfile` y creará procesos:
   - `web` (uvicorn)
   - `worker` (celery worker)
   - `beat` (celery beat)
3. Añade un **plugin Redis** en Railway y define variables:
   - `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
4. Añade `CRYPTO_FERNET_KEY` (usa el comando de arriba para generarla).
5. Despliega. Abre la URL para usar el formulario.

## 4) Configurar CRON (Celery Beat)

- Beat corre con un **heartbeat** cada 5 min.
- Para una tarea demo diaria a las 9 AM:
  - `DEMO_QUERY="java backend 5 años ecommerce"`
  - `DEMO_CREDS_JSON` con credenciales (JSON) para `linkedin` y/o `{}` para computrabajo.
- En el próximo sprint puedes:
  - Crear endpoints para guardar JobConfigs por tenant y construir schedule dinámico desde DB.

## 5) Notas sobre LinkedIn

- **Habilitado a voluntad** (por defecto desactivado).
- Usar **tu cuenta** y **Chrome profile path** reduce 2FA/captchas.
- Respeta TOS, usa delays y volumen moderado.

## 6) Monetización

- Planes por cuota de leads/mes y fuentes activas.
- Add-ons: proxies, enriquecimiento de email, CRM integrations (HubSpot/Pipedrive).
- Stripe Checkout (no incluido en este MVP) + webhooks para activar límites por tenant.

## 7) Roadmap

- Endpoints CRUD para Tenants/Jobs/Schedules.
- Más adaptadores (Indeed, Bumeran, Zonajobs, etc.).
- Panel admin y métricas.
