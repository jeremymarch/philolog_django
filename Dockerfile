# Stage 1: Build the frontend (if it were part of the build process)
# For now, we assume frontend assets are pre-built and in the repo.

# Stage 2: Final application image
FROM python:3.14.3-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies, including nginx and supervisor
RUN apt-get update && apt-get install -y nginx supervisor && rm -rf /var/lib/apt/lists/*

# Create directory for supervisor and gunicorn socket
RUN mkdir -p /var/log/supervisor && \
    mkdir -p /run/ && \
    chown www-data:www-data /run/

# Set the working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Copy Nginx and Supervisor configurations
# Remove the default nginx config and then copy our config.
RUN rm /etc/nginx/sites-enabled/default
COPY nginx/nginx.conf /etc/nginx/sites-available/default
RUN ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy the entrypoint script
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose port 80 for Nginx
EXPOSE 80

# Run the entrypoint script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
