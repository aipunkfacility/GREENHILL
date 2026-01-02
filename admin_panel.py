import os
import json
import secrets
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn

import config

security = HTTPBasic()
templates = Jinja2Templates(directory="templates")
app = FastAPI()

AUDIT_LOG = "/data/audit.log"
AUTH_FILE = "/data/admin_auth.json"


def _client_ip(request: Request) -> str:
    return (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.headers.get("x-real-ip", "").strip()
        or (request.client.host if request.client else "-")
    )


def audit(request: Request, action: str, ok: bool = True, details: str = ""):
    # ВАЖНО: сюда не передавать пароли/токены
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    line = f"{ts}\tip={_client_ip(request)}\taction={action}\tok={int(ok)}\t{details}".strip() + "\n"
    os.makedirs("/data", exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(line)


def _load_auth():
    # если файла нет — создаём из .env (или дефолтов)
    if not os.path.exists(AUTH_FILE):
        os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
        data = {"user": config.ADMIN_USER, "pass": config.ADMIN_PASS}
        with open(AUTH_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return data

    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "user" not in data or "pass" not in data:
            return {"user": config.ADMIN_USER, "pass": config.ADMIN_PASS}
        return data
    except:
        return {"user": config.ADMIN_USER, "pass": config.ADMIN_PASS}


def _save_auth(user: str, password: str):
    os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump({"user": user, "pass": password}, f)


def verify_credentials(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
):
    auth = _load_auth()
    correct_user = auth["user"]
    correct_pass = auth["pass"]

    # сравнение bytes (устойчиво к non-ASCII)
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        str(correct_user).encode("utf-8"),
    )
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        str(correct_pass).encode("utf-8"),
    )

    if not (is_correct_username and is_correct_password):
        audit(request, "login", ok=False, details=f"user={credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    audit(request, "login", ok=True, details=f"user={credentials.username}")
    return credentials.username


def clean_int(value: str) -> int:
    clean_value = str(value).replace(".", "").replace(",", "").replace(" ", "")
    if not clean_value:
        return 0
    return int(clean_value)


@app.get("/state")
def get_state(request: Request, username: str = Depends(verify_credentials)):
    rates = config.get_rates()
    admins = config.get_admins()
    return {"rate": rates["rub_rate"], "admins": admins}


@app.post("/save_rates")
async def save_rates(
    request: Request,
    rub: str = Form(...),
    usdt: str = Form(...),
    usd: str = Form(...),
    username: str = Depends(verify_credentials),
):
    rub_int = clean_int(rub)
    usdt_int = clean_int(usdt)
    usd_int = clean_int(usd)

    config.update_rates(rub_int, usdt_int, usd_int)
    audit(request, "save_rates", ok=True, details=f"rub={rub_int} usdt={usdt_int} usd={usd_int}")

    return RedirectResponse("/", status_code=303)


@app.post("/add_admin")
async def add_admin(
    request: Request,
    admin_id: int = Form(...),
    username: str = Depends(verify_credentials),
):
    config.add_admin_id(admin_id)
    audit(request, "add_admin", ok=True, details=f"admin_id={admin_id}")
    return RedirectResponse("/", status_code=303)


@app.get("/delete_admin/{admin_id}")
async def delete_admin(
    request: Request,
    admin_id: int,
    username: str = Depends(verify_credentials),
):
    config.remove_admin_id(admin_id)
    audit(request, "delete_admin", ok=True, details=f"admin_id={admin_id}")
    return RedirectResponse("/", status_code=303)


@app.get("/", response_class=HTMLResponse)
def admin_page(request: Request, username: str = Depends(verify_credentials)):
    rates = config.get_rates()
    admins = config.get_admins()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "rates": rates, "admins": admins},
    )


@app.get("/auth", response_class=HTMLResponse)
def auth_page(request: Request, username: str = Depends(verify_credentials)):
    return templates.TemplateResponse("auth.html", {"request": request})


@app.post("/auth")
async def auth_save(
    request: Request,
    new_user: str = Form(...),
    new_pass: str = Form(...),
    new_pass2: str = Form(...),
    username: str = Depends(verify_credentials),
):
    if new_pass != new_pass2:
        audit(request, "change_password", ok=False, details="reason=password_mismatch")
        return templates.TemplateResponse(
            "auth.html",
            {"request": request, "error": "Passwords do not match"},
            status_code=400,
        )

    _save_auth(new_user.strip(), new_pass)
    audit(request, "change_password", ok=True, details=f"new_user={new_user.strip()}")
    return RedirectResponse("/", status_code=303)


@app.get("/logs", response_class=HTMLResponse)
def logs_page(request: Request, username: str = Depends(verify_credentials)):
    try:
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()[-200:]
        log_text = "".join(lines) if lines else "Лог пока пуст."
    except FileNotFoundError:
        log_text = "Лог пока пуст."

    return templates.TemplateResponse(
        "logs.html",
        {"request": request, "log_text": log_text},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
