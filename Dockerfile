FROM python:3.10-alpine

WORKDIR /app

# Install requirements
COPY ./requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm requirements.txt

COPY /app /app

CMD python /app/main.py