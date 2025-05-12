FROM python:3.13.3
FROM postgres:15

RUN apt-get update && apt-get install -y postgresql-server-dev-15 make gcc \
    && git clone https://github.com/pgvector/pgvector.git \
    && cd pgvector && make && make install

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/app
WORKDIR $APP_HOME

COPY requirements.txt $APP_HOME/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . $APP_HOME

ENTRYPOINT ["/app/entrypoint.sh"]
