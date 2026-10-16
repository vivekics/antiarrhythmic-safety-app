# Step-by-Step Guide – From Zero to Running on AWS

## 1. Prerequisites on your laptop
- Docker Desktop installed (or Docker Engine + Docker Compose)
- Git (optional)

## 2. Download / Copy the project
Copy the entire `antiarrhythmic-safety-app` folder to your computer.

## 3. Run locally first (recommended)
```bash
cd antiarrhythmic-safety-app
docker-compose up --build
```

Wait until you see:
- Backend running on http://localhost:8000
- Frontend running on http://localhost:5173

Open http://localhost:5173  
Login with: **admin** / **admin123**

## 4. Test the system
1. Click **+ New Profile**
2. Fill in a synthetic patient (example values below)
3. Save → Click **Run Safety Assessment**
4. You should see warnings based on the rules engine

### Example high-risk profile (Sotalol)
- Age: 72
- Diagnosis: AF
- LVEF: 55
- Heart Rate: 58
- QTc: 510
- Potassium: 3.2
- eGFR: 38
- Antiarrhythmic: Sotalol 80 mg BD
- Other meds: Bisoprolol 2.5 mg

This should trigger multiple high/critical alerts.

## 5. Deploy to AWS EC2

### 5.1 Launch EC2
- AMI: Ubuntu 22.04 LTS
- Instance type: t3.medium (or t3.small for testing)
- Storage: 20 GB
- Security Group: allow inbound
  - 22 (SSH)
  - 80, 443 (optional – for later Nginx)
  - 8000 (backend)
  - 5173 (frontend)

### 5.2 Connect & install Docker
```bash
ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>

sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker ubuntu
# log out and log back in
```

### 5.3 Upload the project
From your laptop:
```bash
scp -i your-key.pem -r antiarrhythmic-safety-app ubuntu@<EC2-PUBLIC-IP>:~/
```

### 5.4 Run on the server
```bash
cd antiarrhythmic-safety-app
# (optional) edit .env if you want a stronger SECRET_KEY
docker compose up -d --build
```

### 5.5 Access
- Frontend: http://<EC2-PUBLIC-IP>:5173
- Backend API docs: http://<EC2-PUBLIC-IP>:8000/docs

## 6. Recommended next improvements (for your project report)
1. Put Nginx in front and serve frontend on port 80
2. Move PostgreSQL to **AWS RDS**
3. Replace simple JWT with **AWS Cognito**
4. Add email alerts using **Amazon SES**
5. Add a proper dashboard with charts (risk distribution)
6. Add unit tests for the rules engine
7. Add HTTPS with Let’s Encrypt

## 7. Project Report Tips
- Emphasize that **only synthetic data** is used
- Show the rules engine as the clinical decision support core
- Document the cloud architecture (diagram)
- Include screenshots of alerts for Sotalol / Flecainide / Amiodarone cases
- Discuss security (auth, audit logs, no real patient data)
