FROM semaphoreui/semaphore:v2.18.4

USER root
RUN apk add --no-cache pass gnupg

COPY --chown=1001:1001 semaphore-init.sh /home/semaphore/semaphore-init.sh
RUN chmod +x /home/semaphore/semaphore-init.sh

USER 1001
CMD ["/home/semaphore/semaphore-init.sh"]
