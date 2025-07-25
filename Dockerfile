# Use a slim Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project into the container
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose FastAPI's default port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
