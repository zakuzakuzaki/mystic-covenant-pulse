"""FastAPIメインアプリケーション"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from pathlib import Path

from .core.config import settings
from .api.models import SummonRequest, SummonResponse, AttackRequest, AttackResponse, FinishRequest, FinishResponse
from .api.summons import router as summons_router
from .api.battle import router as battle_router

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
app.mount("/assets", StaticFiles(directory=str(settings.ASSETS_DIR)), name="assets")

# APIルーターの登録
app.include_router(summons_router, prefix="/api")
app.include_router(battle_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def root():
    """メインページ"""
    static_path = Path("static/index.html")
    if static_path.exists():
        return static_path.read_text(encoding="utf-8")
    return """
    <html>
        <head><title>召喚獣バトル</title></head>
        <body>
            <h1>召喚獣バトルアプリ</h1>
            <p>APIサーバーが起動しています</p>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/static/index.html">ゲーム開始</a></li>
            </ul>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok", "message": "召喚獣バトルAPIは正常に動作しています"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )