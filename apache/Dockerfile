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
    apache2 \
    apache2-utils \
    software-properties-common \
    python3 \
    python3-pip \
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
