from setuptools import setup, find_packages

setup(
    name="revobank-backend",
    version="0.1.0",
    packages=find_packages(include=['app', 'app.*']),
    python_requires=">=3.13",
    install_requires=[
        "flask>=3.1.1",
        "flask-bcrypt>=1.0.1",
        "flask-jwt-extended>=4.7.1",
        "flask-sqlalchemy>=3.1.1",
        "python-dotenv>=1.1.0",
        "psycopg2-binary>=2.9.10",
        "gunicorn>=23.0.0",
        "flask-swagger-ui>=4.11.1",
        "sqlalchemy-utils>=0.41.1",
        "flask-migrate>=4.0.5",
    ],
)
