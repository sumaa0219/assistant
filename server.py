from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from routers import observ, pcinfo
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

app = FastAPI()

# 許可するオリジンのリストを指定します
origins = [
    "http://localhost:3000",
    "https://sssumaa.com",
    "http://192.168.1.4:3000"
    # 必要に応じて他の許可するオリジンを追加します
]

# CORSミドルウェアを追加してCORS設定を行います
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 許可するオリジンを指定します
    allow_credentials=True,
    allow_methods=["*"],  # 許可するHTTPメソッドを指定します
    allow_headers=["*"],  # 許可するHTTPヘッダーを指定します
)
# # Permissions-Policyヘッダーを追加するミドルウェア


app.include_router(observ.router)
app.include_router(pcinfo.router)


@app.get("/")
async def root():
    return {"message": "Hello World from FastAPI"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
