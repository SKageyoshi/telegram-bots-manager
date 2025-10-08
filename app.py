from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Telegram Bots Manager", version="1.0.0")

@app.get("/")
def read_root():
    return {
        "message": "Telegram Bots Manager funcionando!",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/bots")
def get_bots():
    return []

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
