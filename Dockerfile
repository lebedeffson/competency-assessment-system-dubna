FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

RUN echo '#!/bin/bash\n\
set -e\n\
mkdir -p /app/data\n\
if [ ! -f /app/data/competencies.db ]; then\n\
    echo "Инициализация базы данных..."\n\
    python init_db.py\n\
    echo "База данных инициализирована!"\n\
fi\n\
echo "Запуск приложения..."\n\
exec python app.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

