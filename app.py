from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from checker import check_username

app = FastAPI(title="Social Username Checker", version="1.0.0")

class UsernameRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"status": "error", "message": "Erro interno do servidor"})

@app.get("/")
async def home():
    return {"status": "ok", "message": "Social Username Checker API"}

@app.get("/username/{username}")
async def get_username(username: str):
    return await check_username(username)

@app.post("/username")
async def post_username(data: UsernameRequest):
    return await check_username(data.username)
