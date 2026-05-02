FROM python:3.12-slim

WORKDIR /app

COPY requirements-dashboard.txt .
RUN pip install --no-cache-dir -r requirements-dashboard.txt

COPY unifi_dashboard.py .
COPY .streamlit/config.toml /app/.streamlit/config.toml

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "unifi_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
