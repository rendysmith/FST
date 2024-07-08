FROM python:3.10

# Установка необходимых пакетов и локалей
RUN apt-get update && \
    apt-get install -y locales locales-all && \
    locale-gen ru_RU.UTF-8

# Установка локали
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8

# Установка зависимостей
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

# Копирование остального кода приложения
COPY . /app

RUN chmod +x update_cont.sh
# Запуск приложения
CMD ["python", "main.py"]
