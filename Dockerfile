FROM python:3
ADD main.py .
COPY . /app
WORKDIR /app

# Install any necessary dependencies
RUN pip install uvicorn fastapi mysql-connector-python python-multipart aiofiles passlib python-jose jwt tortoise

# Command to run the FastAPI server when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]