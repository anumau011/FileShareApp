# 🔐 File Share App

A Flask-based secure file sharing system that supports operations and client users, email verification, role-based access, and secure token-based downloads.

---

## 🚀 Features

- JWT Authentication with Role-based Access Control
- Email Verification for Clients
- Secure, Time-limited Download Links
- File Upload (Ops Only): `.pptx`, `.docx`, `.xlsx`
- MD5 File Integrity Check
- Password Hashing with Werkzeug
- Comprehensive Error Handling

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
https://github.com/anumau011/FileShareApp.git
cd FileShareApp
```
### 2. Install Dependencies
```
pip install -r requirements.txt

```
## 🎥 Demo

[![Demo Video]]
https://github.com/user-attachments/assets/a17e2842-afce-480e-8ea7-6785d2f87ba5

### 3. Environment Configuration

```
# Security Keys (Change in Production)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'

# Email Configuration
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'  # Use app password
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

```

### 5. Run The Appliction 
```
python app.py
```

# 📡 API Endpoints

## 1. Admin
### Create Operations User
```
POST /admin/create-ops-user

```
### Body 
```
{
  "email": "ops@example.com",
  "password": "securepassword",
  "name": "Operations User"
}

```
## 2. Operations User Endpoints

### Login 
```
POST: /admin/create-ops-user
```
### BODY 
```
{
  "email": "ops@example.com",
  "password": "securepassword",
  "name": "Operations User"
}

```
### Upload File

```
POST /ops/upload
Headers: Authorization: Bearer <access_token>

```
### Body: Form-data with file field
### Allowed Types: .pptx, .docx, .xlsx

# 3. Client User

## Sign Up
```
POST /client/signup

```

### Body 
```
{
  "email": "client@example.com",
  "password": "password123",
  "name": "Client Name"
}

```

### Verify Email

```
GET /client/verify-email/<token>
```
## Login

```
POST /client/login

```
### Body 
```
{
  "email": "client@example.com",
  "password": "password123"
}
```
### List All Files
```
GET /client/files
Headers: Authorization: Bearer <access_token>

```
### Request Download Link

```
GET /client/download-file/<file_id>
Headers: Authorization: Bearer <access_token>

```

### Response

```{
  "download_link": "http://localhost:5000/download-file/secure_token_here",
  "message": "success",
  "expires_in": "1 hour"
}
```
### Download File

```
GET /download-file/<secure_token>
Headers: Authorization: Bearer <access_token>
```

## 🛡️ Security Features

🔐 JWT Authentication
👤 Role-based Access (Ops, Client)
✉️ Email Verification
🔗 Secure, Time-limited Download Tokens
📁 File Type Whitelisting
🧮 MD5 File Integrity Check
🔒 Password Hashing (Werkzeug)
