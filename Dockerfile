FROM python:3.10.6-buster

COPY requirements_prod.txt /requirements_prod.txt

RUN pip install --upgrade pip
RUN pip install -r requirements_prod.txt

COPY api /api
COPY setup.py /setup.py

RUN pip install .

CMD uvicorn Safety-Map.api.fastapi.fast:app --host 0.0.0.0 --port $PORT
