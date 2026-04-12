FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cp entrypoint.sh /start.sh && sed -i 's/\r$//' /start.sh && chmod +x /start.sh

EXPOSE 8000

ENTRYPOINT ["/start.sh"]
