# 🚀 Deployment Guide — ThyroAI

## Local Development (Recommended to start with)

### Requirements
- Python 3.10+
- Node.js 18+
- pip, npm

### Step 1: Train ML Models
```bash
cd ml_models
python generate_dataset.py  # ~5 seconds
python train.py             # ~2-5 minutes
```
This creates model files in `ml_models/saved_models/`.

### Step 2: Start Backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Start Frontend
```bash
cd frontend
npm run dev
```

Open: http://localhost:5173

---

## Production Deployment

### Docker Setup

**Dockerfile (Backend):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ .
COPY ml_models/ ../ml_models/
COPY datasets/ ../datasets/
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Dockerfile (Frontend):**
```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY frontend/ .
RUN npm install && npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports: ["8000:8000"]
    volumes:
      - ./uploads:/app/../uploads
      - ./reports:/app/../reports
    env_file: ./backend/.env

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports: ["80:80"]
    depends_on: [backend]
```

### Environment Variables
```
SECRET_KEY=<strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASS=your-app-password
DATABASE_URL=sqlite:///./thyroid.db
```

---

## Tesseract OCR Installation

**Windows:**
```
Download: https://github.com/UB-Mannheim/tesseract/wiki
Add to PATH: C:\Program Files\Tesseract-OCR
```

**Linux/Ubuntu:**
```bash
sudo apt install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

---

## Performance Notes

- **SQLite** is used for simplicity. For production with >1000 concurrent users, migrate to **PostgreSQL**.
- **ML models** are loaded into memory at startup. First prediction may take 1–2s.
- **PDF generation** is synchronous; consider background tasks for high load.
