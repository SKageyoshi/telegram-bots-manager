from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="Telegram Bots Manager", version="1.1.0")

# Configurar templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Telegram Bots Manager",
        "version": "1.1.0"
    })

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/bots")
def get_bots():
    return []

@app.get("/api/stats")
def get_stats():
    return {
        "total_bots": 0,
        "active_bots": 0,
        "total_messages": 0,
        "uptime": "99.9%"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
