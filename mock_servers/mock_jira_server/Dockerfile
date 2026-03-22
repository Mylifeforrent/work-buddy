FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn pydantic python-multipart
COPY mock_servers/mock_jira_server/main.py /app/main.py
EXPOSE 8081
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
