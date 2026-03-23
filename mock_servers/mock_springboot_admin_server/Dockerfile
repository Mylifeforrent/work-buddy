# Stage 1: Build React UI
FROM node:20-slim AS ui-builder
WORKDIR /build
COPY mock_servers/ui/package*.json ./
RUN npm install
COPY mock_servers/ui ./
RUN npm run build

# Stage 2: Python Server
FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn pydantic python-multipart
COPY --from=ui-builder /build/dist /app/ui/dist
COPY mock_servers/mock_springboot_admin_server/main.py /app/main.py
EXPOSE 9300
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9300"]
