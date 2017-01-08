FROM alpine:latest
RUN apk add --no-cache openssh-client python3
RUN adduser -S rfcm
USER rfcm
COPY ./src /home/rfcm/
CMD ["python3", "/home/rfcm/rfcm.py"]