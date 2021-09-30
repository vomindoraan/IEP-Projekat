FROM python:3.10-rc-bullseye

WORKDIR /usr/local/app

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

ARG SERVICE=user_service

COPY ./common ./common
COPY ./$SERVICE ./$SERVICE

CMD python -m $SERVICE
