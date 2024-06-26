FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV OPENAI_API_KEY=<your_openai_api_key>
ENV ASSISTANT_ID=<your_assistant_id>
ENV VS_STORAGE=<your_vector_storage_id>

EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
