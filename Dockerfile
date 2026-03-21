# Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Копируем requirements и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🔒 Копируем .env (для dev — в prod лучше использовать secrets)
COPY .env .

# Копируем код
COPY app/ ./app/

# Создаём папку для лицензий
RUN mkdir -p /app/app/licenses

EXPOSE 8080

CMD ["python", "app/server.py"]