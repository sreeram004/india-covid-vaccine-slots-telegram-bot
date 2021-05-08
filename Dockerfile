FROM python:3.7

RUN pip install python-telegram-bot
RUN pip install tinydb

RUN mkdir /src
ADD . /src
WORKDIR /src

CMD python src/bot.py