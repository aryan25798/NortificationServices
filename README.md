# 📢 Notification Service

A simple, beginner-friendly notification system supporting **Email**, **SMS**, and **In-App** notifications. Includes message queueing (RabbitMQ), MongoDB for storage, and real-time delivery simulation.

---

## 🚀 Features

- ✅ **Send Notification** – `POST /notifications`
- 📬 **Get All Notifications for a User** – `GET /users/{id}/notifications`
- 📦 **Queued Processing** with RabbitMQ (CloudAMQP)
- 🔁 **Retry Failed Notifications**
- 🗂 **In-App Notifications** stored in MongoDB (MongoDB Atlas)
- 🟢 **Real-time Background Processing** using FastAPI
- ☁️ **Deployable on [Railway](https://railway.app)**

---

## ⚙️ Tech Stack

| Layer       | Technology              |
|-------------|--------------------------|
| Backend     | FastAPI                  |
| Database    | MongoDB Atlas            |
| Queue       | RabbitMQ (CloudAMQP)     |
| Frontend    | HTML + Bootstrap 5       |
| Async Tasks | `aio-pika`, `asyncio`    |

---

## 🧪 Local Setup (Dev)

### 1. Clone the Repository

```bash
git clone https://github.com/aryan25798/NortificationServices.git
cd NotificationServices


Create a Virtual Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

 Install Dependencies
pip install -r requirements.txt

Create a .env File in root
MONGO_URI=mongodb+srv://aryan911793:p3ZY6KNR5Lm367H3@cluster0.bvpegfo.mongodb.net/notifications_db?retryWrites=true&w=majority&appName=Cluster0
RABBITMQ_URL=amqps://lkgffasn:ZGd7DCDe9EP1n1r_BEIjL1dUHgQH2aYo@fuji.lmq.cloudamqp.com/lkgffasn

Run the app:
uvicorn app.main:app --reload



## 🌐 Frontend Features

- 📤 **Submit new notifications**
- 🔍 **Fetch notifications by user ID**
- 🎨 **Dark mode toggle**
- 🔄 **Auto-update status** (`pending → sent`)
- 📄 **Export to CSV**
- 🧹 **Delete notifications**
- 🎉 **Confetti on successful submission**


