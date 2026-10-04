FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/srv/apps
WORKDIR /srv
COPY apps/requirements.txt /srv/apps/requirements.txt
RUN pip install --no-cache-dir -r /srv/apps/requirements.txt
COPY apps/backend /srv/apps/backend
COPY apps/data /srv/apps/data
ENV BITHEALTH_DATA_DIR=/srv/apps/data/candidate_package
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
