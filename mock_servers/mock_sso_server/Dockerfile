FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn pydantic python-multipart
COPY mock_servers/mock_sso_server/main.py /app/main.py
EXPOSE 8090
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
