FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
CMD ["sh", "-c", "python backend/manage.py migrate && python manage.py create_super_user --unique_code='admin1' --center='Centro1' --username='admin1' --password='1234' && gunicorn backend.wsgi:application --bind 0.0.0.0:8000"]