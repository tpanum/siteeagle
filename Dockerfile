FROM python:3.10-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

# Run the application:
COPY main.py .
ENTRYPOINT ["python", "main.py"]
