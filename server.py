from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from routers import observ, pcinfo, wallpaper
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)
# Permissions-Policyヘッダーを追加するミドルウェア


app.include_router(observ.router)
app.include_router(pcinfo.router)
app.include_router(wallpaper.router)


@app.get("/")
async def root():
    return {"message": "Hello World from FastAPI"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
