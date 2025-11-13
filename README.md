# Asset Allocation Backend (FastAPI)

The **Backend** is the core service of the Asset Allocation/Management System.  
It manages user authentication, asset tracking, allocations, return requests, and notifications — all through a secure RESTful API built with **FastAPI**, **PostgreSQL**, and **JWT authentication**.

---

## 🚀 Tech Stack

| Layer | Technology |
|--------|-------------|
| **Backend Framework** | FastAPI |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Authentication** | JWT (Access + Refresh Tokens) |
| **Testing** | Pytest |
| **Email Service** | (Future) Amazon SES or SMTP |
| **Containerization** | Docker (Planned) |

---

## Tech Stack

backend/
├── api/
│   ├── models/
│   ├── routes/
│   ├── schemas/
├── core/
│   ├── auth.py
│   └── config.py
├── main.py
├── venv
├── requirements.txt
└── README.md


## **Setup Instructions**

## Clone the Repository

git clone https://github.com/<your-username>/<your-backend-repo>.git
cd <your-backend-repo>

## Create a Virtual Environment

python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

## Install Dependencies

pip install -r requirements.txt

## Run the FastAPI Server

uvicorn main:app --reload
