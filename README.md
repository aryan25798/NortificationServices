# 📢 Notification Service

A simple, beginner-friendly notification system supporting **Email**, **SMS**, and **In-App** notifications. Includes message queueing (RabbitMQ) and retry handling.

---

## 🚀 Features

- ✅ Send Notification – `POST /notifications`
- 📬 Get All Notifications for a User – `GET /users/{id}/notifications`
- 📦 Queued processing with RabbitMQ (CloudAMQP)
- 🔁 Retry failed notifications
- 🗂 In-App notifications saved in PostgreSQL (Supabase)
- 🟢 Real-time background processing using FastAPI
- ☁️ Deployable on [Railway](https://railway.app)

---

## ⚙️ Tech Stack

- ⚡ FastAPI
- 🐘 PostgreSQL (Supabase)
- 🐇 RabbitMQ (CloudAMQP)
- 🌐 HTML + Bootstrap Frontend
- 🐳 No Docker required for deployment

---

## 🧪 Local Setup (Dev)

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/notification-service.git
cd notification-service


python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows


pip install -r requirements.txt

create .env file in root directory
DATABASE_URL=postgresql://postgres:12345@db.xfuwgcarhhwyxkxutkoo.supabase.co:5432/postgres
RABBITMQ_URL=amqps://lkgffasn:ZGd7DCDe9EP1n1r_BEIjL1dUHgQH2aYo@fuji.lmq.cloudamqp.com/lkgffasn


Run the app: uvicorn app.main:app --reload
