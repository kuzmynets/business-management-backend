Business Management — Backend

REST API for a web application for managing a small business: clients, orders, tasks, team roles and basic finance tracking in one place.

This is my diploma project (Junior Bachelor's in Software Engineering, Khmelnytskyi Polytechnic College). The frontend is built with React; this repository contains the FastAPI backend.

Features
Auth and roles — Firebase Authentication; each user has a role inside a business: OWNER, MANAGER or EMPLOYEE
Businesses — an owner registers and gets a new business; team members join by invitation
Clients and orders — keep a client base per business, create orders linked to a client
Tasks — create tasks from orders, assign them to people, track status
Finance — income and expenses, paginated transaction history, totals for income, expenses and profit. Income is created automatically from orders (and never duplicated for the same order)
Analytics — revenue by month, profit, order and task completion rate, active orders and tasks, average order value, top performers
Access control — every endpoint checks the user's role (for example, finance is OWNER only, analytics is OWNER and MANAGER)
Tech stack

Python 3.10+ · FastAPI · Pydantic · Firebase Authentication · Firebase Firestore · Uvicorn · pytest

Roles
Role	What they can do
OWNER	Everything: business, team, finance, analytics
MANAGER	Create orders, work with clients and tasks, view analytics
EMPLOYEE	Work on assigned tasks
Example endpoints

Full interactive documentation (Swagger UI) is available at /docs when the server is running.

Method & path	Access	Description
GET /finance?page=1&limit=10	OWNER	Transactions page with income, expenses and profit summary
POST /finance/sync-orders	OWNER	Create income transactions from orders
POST /finance/expense	OWNER	Add an expense (amount > 0, category required)
GET /analytics	OWNER, MANAGER	Business analytics
Project structure
app/
  core/              # security: current user and role checks
  modules/           # business modules (finance, analytics, ...), each with router + service
  firebase.py        # Firebase / Firestore initialization
pytest.ini
requirements.txt
Getting started
Clone the repo and install dependencies:
bash
   git clone https://github.com/kuzmynets/business-management-backend.git
   cd business-management-backend
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
Create a Firebase project (Authentication + Firestore), download a service account key and configure it as described in app/firebase.py. Never commit the key file — add it to .gitignore.
Run the server:
bash
   uvicorn app.main:app --reload

The API is available at http://localhost:8000 and the docs at http://localhost:8000/docs.

Tests
bash
pytest
Next steps
Add more unit tests for the finance and analytics services
Add Docker support and a CI pipeline that runs the tests
