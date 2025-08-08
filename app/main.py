import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from .db import init_db
from .utils.crypto import encrypt_obj
from .settings import settings
from .worker import run_job
import app.beat  # carga schedule de Celery Beat

app = FastAPI(title=settings.APP_NAME)
init_db()

HTML_FORM = '''
<!doctype html><html><body style="font-family:sans-serif;max-width:760px;margin:auto;padding:20px">
<h2>LeadBot Sheet — Ejecutar búsqueda</h2>
<p><small>Nota: LinkedIn scraping puede violar TOS. Actívalo en el .env solo si lo aceptas.</small></p>
<form method="post" action="/run" style="display:grid;gap:8px">
  <label>Tenant/Cliente <input name="tenant_name" required></label>
  <label>Email admin <input name="email" required></label>
  <fieldset><legend>Credenciales LinkedIn (opcional)</legend>
    <label>User <input name="li_user"></label>
    <label>Pass <input name="li_pass" type="password"></label>
    <label>Chrome profile path <input name="li_profile" placeholder="C:\\Users\\...\\User Data"></label>
    <label>Chrome binary path <input name="li_binary" placeholder="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"></label>
  </fieldset>
  <fieldset><legend>Query</legend>
    <label>Keywords <input name="query" placeholder="java backend 5 años ecommerce" required></label>
    <label>Perfiles objetivo <input name="target" type="number" value="30" min="1"></label>
    <label>Mín score <input name="min_score" type="number" value="6" min="0"></label>
    <label>Mín grupos <input name="min_groups" type="number" value="2" min="1"></label>
    <label>Mín años <input name="min_years" type="number" value="0" min="0"></label>
  </fieldset>
  <button type="submit">Ejecutar</button>
</form>
</body></html>
'''

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_FORM

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
def run(
    tenant_name: str = Form(...),
    email: str = Form(...),
    li_user: str = Form(""),
    li_pass: str = Form(""),
    li_profile: str = Form(""),
    li_binary: str = Form(""),
    query: str = Form(...),
    target: int = Form(30),
    min_score: int = Form(6),
    min_groups: int = Form(2),
    min_years: int = Form(0),
):
    tenant_creds_map = {}
    if settings.ENABLE_LINKEDIN and li_user and li_pass:
        tenant_creds_map["linkedin"] = {
            "user": li_user, "pass": li_pass,
            "chrome_profile": li_profile or None,
            "chrome_binary": li_binary or None,
        }
    if settings.ENABLE_COMPUTRABAJO:
        tenant_creds_map["computrabajo"] = {}

    token = encrypt_obj(tenant_creds_map)
    async_result = run_job.delay(token, query, target, min_score, min_groups, min_years)
    return JSONResponse({"task_id": async_result.id})

@app.get("/result/{task_id}")
def result(task_id: str):
    from .worker import celery
    res = celery.AsyncResult(task_id)
    if not res.ready():
        return {"status": res.status}
    if res.failed():
        return {"status": "error", "reason": str(res.result)}
    data = res.result
    path = data.get("xlsx_path")
    if not path or not os.path.exists(path):
        return {"status": "error", "reason": "output not found"}
    return FileResponse(path, filename=os.path.basename(path), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
