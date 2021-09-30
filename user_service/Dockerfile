FROM python:3.10-rc-bullseye

ENV USER_SERVICE_HOST=0.0.0.0
ENV USER_SERVICE_PORT=9000
EXPOSE 9000

WORKDIR /usr/local/user-service

#RUN apt update
#RUN apt install -y build-essential libssl-dev libffi-dev python3-dev

COPY ./common ./common
COPY ./user_service ./user_service
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

CMD python -m user_service
