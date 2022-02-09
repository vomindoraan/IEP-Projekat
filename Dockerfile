FROM python:3.10-bullseye

WORKDIR /usr/local/app

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./common ./common
COPY ./auth_service ./auth_service
COPY ./admin_service ./admin_service
COPY ./voting_service ./voting_service
