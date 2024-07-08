FROM python:3.10

# Установка необходимых пакетов и локалей
RUN apt-get update

# Установка зависимостей
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

# Копирование остального кода приложения
COPY . /app

RUN chmod +x update_cont.sh
# Запуск приложения
CMD ["python", "main.py"]
