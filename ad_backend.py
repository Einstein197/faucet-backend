from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import secrets
import time

app = FastAPI()

# ⭐ CORS FIX — allows GitHub Pages to call your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://einstein197.github.io"],  # your GitHub Pages domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = "ad_sessions.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_token TEXT PRIMARY KEY,
            user_id TEXT,
            created_at INTEGER,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/ad", response_class=HTMLResponse)
def ad_page(user_id: str):
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()
        # Inject user_id into the page
        html = html.replace("{{USER_ID}}", user_id)
        return HTMLResponse(content=html)
    except Exception as e:
        return HTMLResponse(content=f"Error loading ad page: {e}", status_code=500)

@app.get("/start_ad", response_class=HTMLResponse)
def start_ad(user_id: str):
    session_token = secrets.token_urlsafe(16)
    created_at = int(time.time())

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO sessions (session_token, user_id, created_at) VALUES (?, ?, ?)",
              (session_token, user_id, created_at))
    conn.commit()
    conn.close()

    return f"""
    <html>
    <body>
        <p>session_token={session_token}</p>
    </body>
    </html>
    """

@app.get("/ad_complete")
def ad_complete(session_token: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE sessions SET completed = 1 WHERE session_token = ?", (session_token,))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/check")
def check(user_id: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT completed FROM sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return {"completed": False}

    return {"completed": bool(row[0])}
