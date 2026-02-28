# 🧩 Bitespeed Identity Reconciliation Service

A high-performance backend service built with FastAPI that implements identity reconciliation logic. It links multiple contact points (email, phone) into a single unified customer identity.

🌐 **Live Demo:** [https://bitespeed-identity-29am.onrender.com/docs](https://bitespeed-identity-29am.onrender.com/docs)  
*(Note: Please allow ~60 seconds for the initial spin-up on the Render free tier.)*

---

## 📌 Overview
This service solves the problem of "fragmented" identities. When a customer uses different contact information across multiple orders, this service:
1.  **Identifies** if the new information belongs to an existing user.
2.  **Links** new emails or phone numbers as "secondary" contacts.
3.  **Merges** two previously separate primary contacts if a new order links them together.

## 🚀 Tech Stack
* **Framework:** FastAPI (Python 3.12)
* **Database:** SQLite (SQLAlchemy ORM)
* **Validation:** Pydantic
* **Deployment:** Render (CI/CD via GitHub)

---

## 🧠 Identity Resolution Logic
The service uses a **Graph Traversal (BFS)** strategy to ensure 100% accuracy in complex linking scenarios:
1.  **Search:** Queries the database for any records matching the incoming email or phoneNumber.
2.  **Cluster Discovery:** Uses a Breadth-First Search (BFS) to find every connected contact in the database (handling "chain-links").
3.  **Primary Selection:** The **oldest** record in the entire cluster (based on `createdAt`) is automatically designated as the **Primary** contact.
4.  **Demotion:** Any other "primary" records in the cluster are demoted to **Secondary** and linked to the oldest record.
5.  **New Information:** If the request contains a new email or phone number not seen in the cluster, a new **Secondary** record is created.



---

## 📥 API Endpoint

### `POST /identify`
Consolidates contact information.

**Request Body:**
```json
{
  "email": "mcfly@hillvalley.edu",
  "phoneNumber": "123456"
}
```

> At least one field is required.

---

## 📤 Response

```json
{
  "contact": {
    "primaryContactId": 1,
    "emails": ["doc@future.com", "mcfly@hillvalley.edu"],
    "phoneNumbers": ["123456"],
    "secondaryContactIds": [2]
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

### 1️⃣ 1️⃣ Clone and Setup

```bash
git clone [https://github.com/codingbetas/bitespeed-identity.git](https://github.com/codingbetas/bitespeed-identity.git)
cd bitespeed-identity
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
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
├── app/
│   ├── main.py        # API Routes & BFS Logic
│   ├── models.py      # SQLAlchemy Database Models
│   ├── schemas.py     # Pydantic Validation Models
│   └── database.py    # Database Configuration
├── requirements.txt   # Project Dependencies
├── .gitignore         # venv and SQLite exclusion
└── README.md          # Documentation
```

---

## ✅ Features Implemented

- New contact creation
- Primary-secondary linking
- Multiple primary merge handling
- Chain linking
- Deterministic primary selection
- Response validation with Pydantic
- [x] BFS-based Graph Traversal for Identity Mapping
- [x] Automated Primary-to-Secondary demotion (Merging)
- [x] Handling of null/missing fields
- [x] Deterministic Primary selection based on seniority
- [x] Live deployment with automated CI/CD

---

## ⚠️ Note on Persistence
Since this service is hosted on **Render's Free Tier** using **SQLite**, the database is ephemeral. Data will be reset periodically when the instance spins down due to inactivity or during new deployments.
