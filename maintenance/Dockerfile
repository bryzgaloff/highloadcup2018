FROM postgres

RUN echo 'deb http://ftp.de.debian.org/debian testing main' \
        >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y python3.7 python3-pip nginx supervisor

WORKDIR /usr/src/app
COPY maintenance/requirements.txt .
RUN python3.7 -m pip install -r requirements.txt

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN mkdir -p /var/sockets/ --mode=755 && chown www-data:www-data /var/sockets/
COPY maintenance/nginx-site.conf /etc/nginx/sites-enabled/
EXPOSE 80

ENTRYPOINT ["/bin/bash", "maintenance/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]

COPY maintenance/init-db.sql /docker-entrypoint-initdb.d/
COPY . .
