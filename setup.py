from setuptools import setup, find_packages

setup(
    name="parliament_scraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "cachetools>=5.3.2",
        "pydantic>=2.5.2",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.7",
)
