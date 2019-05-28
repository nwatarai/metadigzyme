From python:3.7.0-slim

####################################
# INSTALL COMMANDLINE REQUIREMENTS #
####################################

WORKDIR /root

RUN apt-get update \
    && apt-get install -y \
        gcc \
        git \
        wget \
        zlib1g-dev \
        build-essential \
        libmysql++-dev \
        libfreetype6-dev \
        libpng-dev \
        python-setuptools \
        python-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


###############################
# INSTALL PYTHON REQUIREMENTS #
###############################

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip; \
    pip install -r requirements.txt; \
    rm requirements.txt


###############################
# INSTALL PYTHON REQUIREMENTS #
###############################

COPY . /opt/metadigzyme
RUN bash /opt/metadigzyme/script/shell/download_references.sh


########################
# SETUP FOR DOCKER RUN #
########################

VOLUME ["/var/lib/docker", "/data"]

WORKDIR /data

CMD /bin/bash
