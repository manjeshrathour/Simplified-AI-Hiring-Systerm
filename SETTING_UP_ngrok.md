# 🚀 Multi-Agent AI Hiring System – Demo Setup (ngrok + Vercel + Google Form)

This guide explains how to run the system locally and expose it using **ngrok** for demo purposes.

Architecture:

Vercel Frontend  
        ↓  
   ngrok tunnel  
        ↓  
   Local FastAPI Backend  
        ↓  
     MongoDB  

---

# 📦 1️⃣ Backend Setup (FastAPI)

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Start Backend

```bash
uvicorn main:app --reload
```

Verify backend is running:

Open in browser:

```
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

# 🌍 2️⃣ ngrok Setup

## Install ngrok

Download from:

https://ngrok.com/download

Verify installation:

```bash
ngrok version
```

---

## Add Authentication Token (First Time Only)

```bash
ngrok config add-authtoken YOUR_NGROK_TOKEN
```

---

## Start ngrok Tunnel

```bash
ngrok http 8000
```

You will get something like:

```
https://abcd-1234.ngrok-free.app
```

⚠️ IMPORTANT:
- This URL changes every time you restart ngrok.
- Keep ngrok running during demo.

---

# 🔧 3️⃣ Required Backend Changes (main.py)

Ensure CORS is configured correctly.

Replace existing middleware with:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://multiagent-ai-hiring-system.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Restart backend after making changes.

---

# 🖥️ 4️⃣ Frontend Configuration (Vercel)

## Update API Base URL

In `script.js`:

```js
const API_BASE = "https://abcd-1234.ngrok-free.app";
const WS_BASE  = "wss://abcd-1234.ngrok-free.app";
```

Replace with your current ngrok URL.

---

## Add ngrok Header to ALL Fetch Requests

For GET requests:

```js
fetch(`${API_BASE}/stats`, {
  headers: {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
  }
})
```

For POST with FormData:

```js
fetch(`${API_BASE}/upload-resume/`, {
  method: "POST",
  headers: {
    "ngrok-skip-browser-warning": "true"
  },
  body: formData
})
```

⚠️ Do NOT manually set `Content-Type` when using FormData.

---

# 🔌 5️⃣ WebSocket Configuration

Backend endpoint:

```python
@app.websocket("/ws/interview/{interview_id}")
```

Frontend must use:

```js
const socketUrl = `wss://abcd-1234.ngrok-free.app/ws/interview/${interviewId}`;
```

Important:
- Use `wss://`
- Do NOT use `ws://`
- Must match ngrok domain

---

# 📝 6️⃣ Google Form → Apps Script Configuration

In Google Apps Script:

## Update ngrok URL

```javascript
const NGROK_URL = "https://abcd-1234.ngrok-free.app";
```

---

## Update API Call Example

```javascript
const response = UrlFetchApp.fetch(NGROK_URL + "/apply-for-job/", {
  method: "post",
  payload: formData,
  headers: {
    "x-secret-key": "YOUR_SECRET_KEY",
    "ngrok-skip-browser-warning": "true"
  }
});
```

---

## Important: Header Must Match Backend

In `main.py`:

```python
x_secret_key: str = Header(None)
```

So Apps Script must send header:

```
x-secret-key
```

NOT:
- SECRET_KEY
- Authorization
- api-key

---

# 🧪 7️⃣ Demo Checklist (Before Presentation)

### Backend
- [ ] MongoDB running
- [ ] FastAPI running
- [ ] `/health` endpoint working

### ngrok
- [ ] ngrok running
- [ ] Correct URL copied
- [ ] URL updated in frontend
- [ ] URL updated in Apps Script

### Frontend
- [ ] Redeployed on Vercel
- [ ] `/stats` working
- [ ] Resume upload working
- [ ] WebSocket interview working

---

# ⚠️ Important Demo Notes

Free ngrok limitations:

- URL changes every restart
- Must update frontend + Apps Script each time
- Laptop must stay ON
- Backend must stay running

If ngrok stops → demo stops.

---

# 🛠️ Common Errors & Fixes

## ❌ CORS Error
Fix CORS origins in `main.py`.

---

## ❌ 502 Bad Gateway
Backend not running.

---

## ❌ WebSocket Failed
Using `ws://` instead of `wss://`.

---

## ❌ ERR_NGROK_3200
Using old ngrok URL.

---

# 🔄 Complete Demo Flow

1. Start MongoDB  
2. Start FastAPI  
3. Start ngrok  
4. Copy ngrok URL  
5. Update:
   - script.js  
   - interview.js  
   - Google Apps Script  
6. Redeploy frontend  
7. Test `/health`  
8. Test `/stats`  
9. Start demo 🎉  

---

# 📌 Production Recommendation (After Demo)

For production deployment, use:

- Render  
- Railway  
- Fly.io  

This removes the need for ngrok and manual updates.

---

# 👨‍💻 Maintainer

Deepesh Yadav  
B.Tech – AI / ML / Data Science  
Multi-Agent AI Hiring System
