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


## Online Swagger Documentation

You can also explore the API documentation online here:  
[https://banking-system-revou.onrender.com/api/docs/#/](https://banking-system-revou.onrender.com/api/docs/#/)

---

# Project Dependencies

This project uses the following Python packages, managed via `pyproject.toml` and compiled into `requirements.txt` using `uv pip compile`.

| Package           | Version  | Notes / Source                                |
|-------------------|----------|----------------------------------------------|
| **alembic**       | 1.15.2   | Database migrations (via `flask-migrate`)    |
| **bcrypt**        | 4.3.0    | Password hashing (via `flask-bcrypt`)         |
| **blinker**       | 1.9.0    | Flask signaling support (via `flask`)         |
| **click**         | 8.2.0    | Command line interface (via `flask`)           |
| **flask**         | 3.1.1    | Web framework (core dependency)                |
| **flask-bcrypt**  | 1.0.1    | Bcrypt integration for Flask                    |
| **flask-jwt-extended** | 4.7.1 | JWT authentication support                      |
| **flask-migrate** | 4.1.0    | Database migrations for Flask                   |
| **flask-sqlalchemy** | 3.1.1  | SQLAlchemy integration for Flask                |
| **flask-swagger-ui** | 4.11.1 | Swagger UI for API documentation                 |
| **greenlet**      | 3.2.2    | Dependency of SQLAlchemy                         |
| **gunicorn**      | 23.0.0   | Production WSGI HTTP Server                      |
| **itsdangerous**  | 2.2.0    | Security helpers for Flask                       |
| **jinja2**        | 3.1.6    | Templating engine used by Flask                  |
| **mako**          | 1.3.10   | Template rendering engine (used by Alembic)     |
| **markupsafe**    | 3.0.2    | Safe string handling (used by Flask & Jinja2)  |
| **packaging**     | 25.0     | Utilities for package version handling          |
| **psycopg2-binary** | 2.9.10 | PostgreSQL database adapter                      |
| **pyjwt**         | 2.10.1   | JSON Web Token implementation                    |
| **python-dotenv** | 1.1.0    | Loads environment variables from `.env` files  |
| **sqlalchemy**    | 2.0.40   | SQL toolkit and ORM                              |
| **sqlalchemy-utils** | 0.41.2 | Additional utilities for SQLAlchemy              |
| **typing-extensions** | 4.13.2 | Backports of typing features                      |
| **werkzeug**      | 3.1.3    | WSGI utility library used by Flask               |

---

## Notes

- This list was generated automatically by running:  
  ```bash
  uv pip compile pyproject.toml -o requirements.txt
  ```
- Versions are locked to ensure consistent environments.
- Many packages are dependencies of Flask extensions used in this project.

---