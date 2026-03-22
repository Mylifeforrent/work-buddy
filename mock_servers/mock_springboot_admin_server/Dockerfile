FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn pydantic python-multipart
COPY mock_servers/mock_springboot_admin_server/main.py /app/main.py
EXPOSE 9300
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9300"]
