FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy nginx configuration
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 8000

# Run migrations and create superuser
CMD [ "sh", "-c", "\
    python3 manage.py makemigrations && \
    python3 manage.py migrate && \
    python3 manage.py create_super_user \
        --unique_code='admin' \
        --center='centro1' \
        --username='admin' \
        --password='123' && \
    gunicorn backend.wsgi:application --bind 0.0.0.0:8000 \
"]