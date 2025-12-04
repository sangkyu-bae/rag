# FastAPI Project Skeleton

This repository provides a minimal FastAPI project structure to help you get started quickly.

## Project Layout

```
.
├── app
│   ├── api
│   │   ├── deps.py
│   │   └── v1
│   │       ├── endpoints
│   │       │   └── health.py
│   │       └── router.py
│   ├── core
│   │   └── config.py
│   ├── main.py
│   ├── models
│   └── schemas
├── requirements.txt
└── tests
    └── test_health.py
```

## Getting Started

1. Create and activate your virtual environment.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Start the development server:
   ```
   uvicorn app.main:app --reload
   ```
4. Visit the interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Running Tests

```
pytest
```

