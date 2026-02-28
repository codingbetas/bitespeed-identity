# 🧩 Bitespeed Identity Reconciliation Service

## 📌 Overview

This service implements identity reconciliation logic similar to the backend task from Bitespeed.

It links contacts based on shared email addresses and/or phone numbers.

If multiple records belong to the same person, they are grouped under a single **primary contact**.

---

## 🚀 Tech Stack

- FastAPI
- SQLAlchemy
- SQLite
- Python 3.12

---

## ⚙️ How It Works

- Each contact is stored in a `contacts` table.
- If two contacts share the same email or phone number, they are linked.
- A graph traversal (**BFS**) is used to collect all related contacts.
- The **oldest contact** in the group becomes the primary.
- All others are marked as secondary.
- New records are created only when new email/phone information appears.

---

## 📥 API Endpoint

### `POST /identify`

### Request Body

```json
{
  "email": "string (optional)",
  "phoneNumber": "string (optional)"
}
```

> At least one field is required.

---

## 📤 Response

```json
{
  "contact": {
    "primaryContactId": 1,
    "emails": ["email1@example.com", "email2@example.com"],
    "phoneNumbers": ["1234567890"],
    "secondaryContactIds": [2, 3]
  }
}
```

---

## 🧠 Identity Resolution Logic

1. Search existing contacts matching email or phone.
2. Use BFS traversal to find full connected component.
3. Select oldest contact as primary.
4. Demote other primaries to secondary.
5. Create new secondary if new information appears.
6. Return consolidated response.

---

## ▶️ Running Locally

### 1️⃣ Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Start server

```bash
uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

---

## 📂 Project Structure

```
bitespeed-identity/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ✅ Features Implemented

- New contact creation
- Primary-secondary linking
- Multiple primary merge handling
- Chain linking
- Deterministic primary selection
- Response validation with Pydantic