FROM python:3.7

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir python-telegram-bot tinydb requests

RUN mkdir /src
ADD . /src
WORKDIR /src

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]