FROM python:3.10.11-bullseye

# Install ps to allow nextflow to collect task metrics
RUN apt-get update && apt-get -y install procps

# Create workdir
WORKDIR /app 
COPY requirements.txt requirements.txt

# Python library 
RUN pip3 install -r requirements.txt

# Environments
ENV PATH="$PATH:/usr/bin:/usr/local/bin"    
