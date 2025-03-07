FROM python:3.10-slim
USER root

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

RUN apt install -y git gcc libasound2-dev

RUN mkdir -p /assistant
COPY ./requirements.txt /assistant

WORKDIR /assistant
RUN pip install -r requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools


CMD ["python", "main.py"]