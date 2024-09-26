# Bike Shop

# Testing:

```bash
PYTHONPATH=. pytest --cov
```

# Frontend

Create an .env.local file with:

NEXT_PUBLIC_API_URL=http://localhost:8000

```bash
cd frontend
yarn run dev
```

# Backend

```bash
uvicorn backend.app.main:app --reload
PYTHONPATH=. python backend/app/models/fixtures.py
```

# TODO:

organize models in different files
Add authentication
Implement add to cart in frontend
