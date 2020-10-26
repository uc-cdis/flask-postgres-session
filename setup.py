from setuptools import setup, find_packages

setup(
    name="flask_postgres_session",
    install_requires=[
        "Flask==1.0",
        "psycopg2>=2.7",
        "sqlalchemy==0.9.9",
        "Flask-SQLAlchemy-Session==1.1",
    ],
    packages=find_packages(),
)
