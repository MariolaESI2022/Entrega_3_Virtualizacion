FROM alpine:latest
LABEL maintainer=juliancaba email=julian.caba@uclm.es


RUN apk add mosquitto-clients

WORKDIR /mosquitto
COPY pub.sh /mosquitto


ENTRYPOINT ["./pub.sh"]
