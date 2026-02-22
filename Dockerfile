# syntax=docker/dockerfile:1-labs

# Use the official Python runtime image
FROM python:3.14.3-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container, excluding the database
COPY --exclude=db.sqlite3 . /app/

# Copy the database separately into its own layer
COPY db.sqlite3 /app/

# Expose the port Django runs on
EXPOSE 8000

# Command to run the Django development server on all interfaces
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
