FROM alpine:latest
#Install required packages
RUN apk add --no-cache openssh-client python3 ca-certificates

#Install Reachmail API for Python
COPY ./assets/reachmailapi /tmp/reachmailapi
WORKDIR /tmp/reachmailapi
RUN python3 setup.py install
RUN rm  -fr /tmp
#Fix permissions on cacerts.txt
RUN find /usr/lib/python3.5/site-packages/httplib2* -name "cacerts.txt" -exec chmod a+r {} \;

#Create non-privilaged user
RUN adduser -S rfcm

#Copy application data
COPY ./src /home/rfcm/

#Prepare for running applicaton
USER rfcm
WORKDIR /home/rfcm
CMD ["python3", "rfcm.py"]
#CMD /bin/ash