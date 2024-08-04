from typing import Optional
from fastapi import FastAPI, Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from unfollowers import obtain_unfollowers, obtain_session_id
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SessionData(BaseModel):
    session_id: str

class LoginData(BaseModel):
    username: str
    password: str

@app.post("/api/v1/data")
async def get_data(session_data: SessionData) -> dict:
    unfollowers_list = await obtain_unfollowers(session_data.session_id)
    return unfollowers_list

@app.post("/api/v2/data")
async def login(login_data: LoginData) -> dict:
    session_id = await obtain_session_id(login_data.username, login_data.password)
    unfollowers_list = await obtain_unfollowers(session_id)
    return unfollowers_list

@app.get("/proxy")
async def proxy(url: str) -> Response:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": response.headers.get("Content-Type"),
            }
            return Response(content=response.content, headers=headers, media_type=response.headers.get("Content-Type"))
        else:
            return Response(content="Error fetching image", status_code=500)
