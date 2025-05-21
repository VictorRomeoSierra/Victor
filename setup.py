from setuptools import setup, find_packages

setup(
    name="victor",
    version="0.1.0",
    description="AI coding assistant for DCS Lua development",
    author="VRS Community",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.6",
        "pgvector>=0.2.0",
        "pydantic>=2.0.0",
        "tree-sitter>=0.20.1",
        "numpy>=1.24.0",
        "httpx>=0.24.0",
    ],
    python_requires=">=3.9",
)