FROM python:3.7-alpine AS base
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY ./module/requirements.txt /usr/src/app
RUN apk update
RUN apk add --virtual .py_deps build-base python3-dev libffi-dev gcc musl-dev openssl-dev
RUN pip install -r /usr/src/app/requirements.txt
RUN apk del .py_deps &&\
    apk add -U tzdata &&\
    apk add curl &&\
    echo "Asia/Taipei" > /etc/timezone
COPY ./module /usr/src/app
HEALTHCHECK --interval=60s --timeout=5s --retries=5 CMD curl -fs "http://localhost:8333/healthCheck" || exit 1 
CMD ["python", "server.py"]
