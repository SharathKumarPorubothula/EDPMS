# ==========================================
# Base Image
# ==========================================
FROM ubuntu:22.04

LABEL maintainer="EDPMS"
ENV DEBIAN_FRONTEND=noninteractive

# ==========================================
# Install OS Packages
# ==========================================
RUN apt-get update && apt-get install -y \
    apache2=2.4.52-1ubuntu4.16 \
    apache2-utils=2.4.52-1ubuntu4.16 \
    software-properties-common \
    python3=3.10.6-1~22.04 \
    python3-pip=22.0.2+dfsg-1ubuntu0.7\
    python3-dev \
    libapache2-mod-wsgi-py3 \
    build-essential \
    curl \
    wget \
    unzip \
    git \
    vim \
    nano \
    net-tools \
    iputils-ping \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# Upgrade pip
# ==========================================
#RUN python3 -m pip install --upgrade pip

# ==========================================
# Install Common Python Packages
# ==========================================
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# Enable Apache Modules
# ==========================================
RUN a2enmod rewrite && \
    a2enmod headers && \
    a2enmod proxy && \
    a2enmod proxy_http && \
    a2enmod ssl && \
    a2enmod wsgi

# ==========================================
# Create Application Directory
# ==========================================

WORKDIR /app
COPY . .

# ==========================================
# Expose Apache Port
# ==========================================
EXPOSE 80

# ==========================================
# Start Apache
# ==========================================
CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]