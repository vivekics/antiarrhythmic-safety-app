# Antiarrhythmic Medication Safety & Monitoring Application

Cloud-based application for assessing medication safety using **synthetic clinical profiles only** (no real patient data).

## Features
- Create / edit / view synthetic patient profiles
- Rules-based safety engine (Sotalol, Flecainide, Amiodarone + general checks)
- Automatic warnings & monitoring recommendations
- Simple JWT authentication
- Audit logging of assessments
- Docker-ready for easy deployment on AWS EC2

---

## Project Structure

```
antiarrhythmic-safety-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── database.py          # DB connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── rules_engine.py      # Core safety rules
│   │   ├── auth.py              # JWT authentication
│   │   └── routers/
│   │       ├── auth.py
│   │       └── patients.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── services/api.js
│   │   ├── components/
│   │   └── pages/
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Quick Start (Local with Docker)

1. Copy `.env.example` → `.env` and edit if needed
2. Run:
   ```bash
   docker-compose up --build
   ```
3. Backend: http://localhost:8000  
   Frontend: http://localhost:5173  
   API Docs: http://localhost:8000/docs

Default login (created on first run):
- Username: `admin`
- Password: `admin123`

---

## Deploy on AWS EC2 (Simple Method)

1. Launch Ubuntu 22.04 EC2 instance (t3.medium recommended)
2. Install Docker & Docker Compose
3. Upload this entire folder to the server
4. Create `.env` from `.env.example`
5. Run `docker-compose up -d --build`
6. Open security group ports 80, 443, 8000, 5173 (or put Nginx in front)

---

## Next Steps (Recommended)
- Replace JWT with AWS Cognito
- Move PostgreSQL to AWS RDS
- Add email alerts (SES)
- Add dashboard charts
- Add role-based access (doctor / nurse / admin)
