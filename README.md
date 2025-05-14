# Revobank Backend

A Flask-based REST API backend for the Revobank banking application.

## API Documentation

The API documentation is available via Swagger UI at `/api/docs` when the server is running.
Once the development server is running, you can access the API documentation at:
http://localhost:5000/api/docs

## Authentication

- JWT access token validity: 1 hour
- JWT refresh token validity: 30 days

## Development Setup

1. Generate a secret key:

```python
import uuid
print(uuid.uuid4().hex)
```

2. Create `.env` file with the required environment variables:

```
SECRET_KEY=your_generated_secret
POSTGRESQL_URL=postgresql://username:password@localhost:5432/revobank
FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=1
```

3. Install dependencies:

```
uv pip install -e .
```

4. Run the development server:

```
flask run
```
