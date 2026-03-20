# 👁️ Retinex Pro — Deployment Guide

> Hackathon build: Colorblindness Awareness & Inclusive Design

---

## 🏗️ Project Structure (Fixed)

```
retinex-pro/
├── backend/                  ← Deploy this on Render
│   ├── app.py                ← Fixed Flask app
│   ├── requirements.txt      ← Fixed dependencies
│   ├── templates/
│   │   ├── entry.html        ← Login / Signup page
│   │   ├── landing.html      ← Welcome page (post-login)
│   │   └── kalai.html        ← Main app interface
│   └── static/               ← Put any CSS/JS files here
│
├── frontend/                 ← (Optional) Static-only Vercel version
│   ├── entry.html
│   ├── landing.html
│   └── kalai.html
│
├── render.yaml               ← Render auto-config
├── vercel.json               ← Vercel config (frontend only)
└── README.md
```

---

## 🚀 Deployment Steps

### STEP 1 — Push your project to GitHub

Make sure your repo looks like the structure above.

```bash
git init
git add .
git commit -m "fix: restructure for Render + Vercel deployment"
git remote add origin https://github.com/YOUR_USERNAME/retinex-pro.git
git push -u origin main
```

---

### STEP 2 — Deploy Backend on Render (Free)

1. Go to **https://render.com** → Sign up / Log in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Fill in these settings:

| Setting | Value |
|---|---|
| **Name** | `retinex-pro-backend` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120` |
| **Instance Type** | `Free` |

5. Add these **Environment Variables** (in the Render dashboard):

| Key | Value |
|---|---|
| `SECRET_KEY` | Click "Generate" — Render will create a random one |
| `DB_PATH` | `/tmp/users.db` |

6. Click **"Create Web Service"**
7. Wait ~2 minutes. You'll get a URL like:
   ```
   https://retinex-pro-backend.onrender.com
   ```
8. Test it: visit `https://retinex-pro-backend.onrender.com/health` — should return `{"status": "ok"}`

---

### STEP 3 — Test your backend URL

Visit your Render URL in the browser:
```
https://retinex-pro-backend.onrender.com
```
You should see your **Login page** — that means it works! ✅

> ⚠️ **Free Render services sleep after 15 minutes of inactivity.**
> First load may take 30–60 seconds to wake up. This is normal on the free tier.

---

### STEP 4 — (Optional) Deploy Frontend on Vercel

Only needed if you want the frontend on a separate Vercel URL.

1. Go to **https://vercel.com** → Sign up / Log in
2. Click **"Add New Project"** → Import your GitHub repo
3. Set **Root Directory** to `frontend`
4. Click **Deploy**

Then update `entry.html` in the frontend folder:
```html
<script>
  // Replace this with your actual Render backend URL
  window.BACKEND_URL = "https://retinex-pro-backend.onrender.com";
</script>
```

> **Note:** Since your Flask app already serves HTML, you DON'T need Vercel.
> Render handles everything — Flask serves the pages, handles auth, and runs the API.
> Just use your Render URL directly. ✅

---

## ⚠️ Important Notes

### SQLite on Render (Free Tier)
- The DB is stored at `/tmp/users.db`
- `/tmp` is **ephemeral** — it resets when the service restarts or sleeps
- For a hackathon demo, this is fine
- For production, switch to **PostgreSQL** (Render offers a free Postgres instance)

### How to upgrade to PostgreSQL later
1. In Render, create a free **PostgreSQL** database
2. Copy the connection string
3. `pip install psycopg2-binary`
4. Replace `sqlite3` with `psycopg2` in `app.py`

---

## 🧪 Local Development

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/retinex-pro.git
cd retinex-pro/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file
echo "SECRET_KEY=local-dev-secret" > .env
echo "DB_PATH=users.db" >> .env

# Run
python app.py
```

Visit **http://localhost:5000**

---

## 🔗 Why Not Vercel for Flask?

| Platform | What it's for |
|---|---|
| **Vercel** | Static sites + serverless functions only |
| **Render** | Full web servers — Flask, Django, Node, etc. |
| **Railway** | Same as Render, also great |

Flask needs a persistent server process. Vercel kills processes after each request.
That's why you were getting `FUNCTION_INVOCATION_FAILED`.

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| Auth | bcrypt (password hashing) |
| Database | SQLite (→ PostgreSQL for production) |
| Hosting | Render (backend) |
| CORS | flask-cors |
