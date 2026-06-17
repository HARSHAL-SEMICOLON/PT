![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Supabase](https://img.shields.io/badge/Supabase-Database-brightgreen)
![Vercel](https://img.shields.io/badge/Vercel-Frontend-black)
![Render](https://img.shields.io/badge/Render-Backend-purple)
![License](https://img.shields.io/badge/License-Educational-orange)

# 🏥 CarePulse - Clinic Appointment Management System

CarePulse is a full-stack Clinic Appointment Management System that enables patients to book appointments, doctors to manage appointments, and maintain digital medical records through a secure and user-friendly platform.

## 🚀 Live Demo

* **Frontend:** https://pt-zeta-vert.vercel.app/.
* **Backend API:**  https://pt-clinic-backend.onrender.com

---

## 📌 Features

### 👨‍⚕️ Doctor Features

* Secure Registration & Login
* View Assigned Appointments
* Mark Appointments as Completed
* Cancel Appointments
* Create Medical Records
* Access Patient Information

### 🧑‍🤝‍🧑 Patient Features

* Secure Registration & Login
* Book Appointments
* Reschedule Appointments
* Cancel Appointments
* View Appointment History
* Access Medical Records & Prescriptions

### 🔐 Security Features

* JWT Authentication
* Password Hashing using Bcrypt
* Role-Based Access Control (RBAC)
* Protected API Routes

---

## 🏗️ System Architecture

```text
Frontend (HTML, CSS, JavaScript)
            │
            ▼
      FastAPI Backend
            │
            ▼
 JWT Authentication Layer
            │
            ▼
    Supabase PostgreSQL
```

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* Vanilla JavaScript

### Backend

* Python
* FastAPI
* Uvicorn
* JWT Authentication
* Bcrypt

### Database

* Supabase PostgreSQL

### Deployment

* Vercel
* Render
* GitHub

---

## 📂 Project Structure

```text
CarePulse/
│
├── frontend/
│   ├── index.html
│   ├── index.css
│   └── app.js
│
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── model.py
│   └── requirements.txt
│
├── README.md
└── .gitignore
```

---

## 🗄️ Database Schema

### Users

* id
* name
* email
* password
* role
* created_at

### Doctors

* id
* user_id
* specialization
* created_at

### Patients

* id
* user_id
* phone
* created_at

### Appointments

* id
* patient_id
* doctor_id
* appointment_date
* appointment_time
* status
* created_at

### Medical Records

* id
* patient_id
* doctor_id
* diagnosis
* prescription
* created_at

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/your-username/carepulse.git
cd carepulse
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Run Backend

```bash
uvicorn main:app --reload
```

---

## 📡 API Endpoints

### Authentication

```http
POST /auth/register
POST /auth/login
GET  /auth/me
```

### Doctors

```http
GET /doctors
```

### Patients

```http
GET /patients
```

### Appointments

```http
POST   /appointments
GET    /appointments
GET    /appointments/{id}
PATCH  /appointments/{id}
DELETE /appointments/{id}
```

### Medical Records

```http
POST /medical-records
GET  /medical-records
GET  /medical-records/{id}
```

---
## 📸 Application Screenshots

### 🔐 Login Page

<p align="center">
  <img src="screenshots/login-page.png" alt="Login Page" width="900">
</p>

---

### 📝 Registration Page

<p align="center">
  <img src="screenshots/register-page.png" alt="Registration Page" width="900">
</p>

---

### 👨‍⚕️ Doctor Dashboard

<p align="center">
  <img src="screenshots/doctor-dashboard.png" alt="Doctor Dashboard" width="900">
</p>

---

### 🩺 Add Medical Record

<p align="center">
  <img src="screenshots/add-medical-record.png" alt="Medical Record Page" width="900">
</p>

---

### 👤 Patient Dashboard

<p align="center">
  <img src="screenshots/patient-dashboard.png" alt="Patient Dashboard" width="900">
</p>

---

### 📅 Appointment Booking

<p align="center">
  <img src="screenshots/book-appointment.png" alt="Appointment Booking" width="900">
</p>

---

### 📋 Medical History

<p align="center">
  <img src="screenshots/medical-history.png" alt="Medical History" width="900">
</p>

## 🎯 Learning Outcomes

* Full Stack Web Development
* FastAPI REST APIs
* JWT Authentication
* Role-Based Access Control
* Database Design
* CRUD Operations
* Frontend-Backend Integration
* Cloud Deployment

---

## 🔮 Future Enhancements

* Email Notifications
* Appointment Slot Validation
* Doctor Availability Scheduling
* Admin Dashboard
* Prescription PDF Generation
* Video Consultation Support
* Search & Filter Functionality

---

## 👨‍💻 Authors

Developed by Team CarePulse

* Prathmesh Bhokare

---

## 📜 License

This project is developed for educational and academic purposes.
