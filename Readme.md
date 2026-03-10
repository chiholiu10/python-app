# Books API

Een RESTful API gebouwd met Flask en PostgreSQL - perfect voor developers met frontend ervaring die backend willen leren.

## Features

- Full CRUD operations for books
- PostgreSQL database
- Search functionality
- Pagination
- Error handling
- Clean code structure

## Installatie

### 1. PostgreSQL installeren

```bash
brew install postgresql@16
brew services start postgresql@16
```

## How to run Python app

# 1. Clone repository

git clone <your-repo-url>
cd <project-folder>

# 2. Set up virtual environment

python -m venv venv
source venv/bin/activate # Mac/Linux

# venv\Scripts\activate # Windows

# 3. Install dependencies

pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure environment

cp .env.example .env

# Edit .env with your database credentials

# 5. Install and start PostgreSQL

# Mac:

brew install postgresql@16
brew services start postgresql@16

# Linux:

sudo apt install postgresql
sudo systemctl start postgresql

# Windows:

# Download from https://www.postgresql.org/download/windows/

net start postgresql

# 6. Create database

createdb -U postgres book_api_dev

# Or: psql -U postgres -c "CREATE DATABASE book_api_dev;"

# 7. Run the app

# For Flask:

python app.py

# For FastAPI:

uvicorn main:app --reload --port 5000

# 8. Open in browser

http://127.0.0.1:5000

# FastAPI docs: http://127.0.0.1:5000/docs
