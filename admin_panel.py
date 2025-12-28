import os
import secrets
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
import config

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = config.ADMIN_USER
    correct_pass = config.ADMIN_PASS
    is_correct_username = secrets.compare_digest(credentials.username, correct_user)
    is_correct_password = secrets.compare_digest(credentials.password, correct_pass)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Вспомогательная функция: превращает "3.090.000" -> 3090000
def clean_int(value: str) -> int:
    # Удаляем точки, запятые и пробелы
    clean_value = str(value).replace('.', '').replace(',', '').replace(' ', '')
    if not clean_value:
        return 0
    return int(clean_value)

app = FastAPI()
@app.get("/state")
def get_state():
    rates = config.get_rates()
    admins = config.get_admins()

    return {
        "rate": rates["rub_rate"],
        "admins": admins
    }




# ИСПРАВЛЕНО: принимаем str, очищаем, сохраняем как int
@app.post("/save_rates")
async def save_rates(
    rub: str = Form(...), 
    usdt: str = Form(...), 
    usd: str = Form(...)
):
    rub_int = clean_int(rub)
    usdt_int = clean_int(usdt)
    usd_int = clean_int(usd)
    
    config.update_rates(rub_int, usdt_int, usd_int)
    return RedirectResponse("/", status_code=303)

@app.post("/add_admin")
async def add_admin(admin_id: int = Form(...)):
    config.add_admin_id(admin_id)
    return RedirectResponse("/", status_code=303)

@app.get("/delete_admin/{admin_id}")
async def delete_admin(admin_id: int):
    config.remove_admin_id(admin_id)
    return RedirectResponse("/", status_code=303)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def admin_page(
    request: Request,
    username: str = Depends(verify_credentials)
):
    rates = config.get_rates()
    admins = config.get_admins()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "rates": rates,
            "admins": admins
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

