FROM python:3.12
LABEL authors="Semyon"

WORKDIR /shop
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY shop_api/ ./shop_api/
CMD ["uvicorn", "shop_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]