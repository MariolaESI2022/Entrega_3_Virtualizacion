FROM alpine:latest
LABEL maintainer=juliancaba email=julian.caba@uclm.es

RUN apk add mosquitto
COPY broker.conf /mosquitto/mosquitto.conf

WORKDIR /mosquitto
EXPOSE 2883/tcp

CMD mosquitto -c mosquitto.conf