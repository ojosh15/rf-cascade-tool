FROM python:3.10-alpine

WORKDIR /workspace

# Install requirements
COPY ./requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm requirements.txt

RUN mkdir -p /static

COPY /app /workspace/app
COPY static/* /static
COPY ./entrypoint.sh .

ENV PYTHONPATH="/workspace"

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]

# CMD python /workspace/app/main.py
CMD ash