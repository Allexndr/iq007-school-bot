import os
import sys
import logging

# Ensure the app module can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from aiogram import Bot, Dispatcher, types
from app.handlers import router
from app.config import TOKEN

# Set up logging for Vercel
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Initialize Bot and Dispatcher
# Note: In a serverless environment, global variables are not guaranteed to persist across requests,
# but for the webhook handler it works as initialized per invocation (or reused if warm).
bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>IQ007 Bot</title>
            <style>
                body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5; }
                .container { text-align: center; padding: 2rem; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                p { color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>IQ007 Bot is Running</h1>
                <p>The webhook is active.</p>
            </div>
        </body>
    </html>
    """

@app.post("/api/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = types.Update(**data)
        await dp.feed_webhook_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Error handling webhook: {e}")
        return {"status": "error", "message": str(e)}
