FROM postgres:18.1

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libpq-dev \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 2. Set up a Virtual Environment
# Modern Linux (Debian 12+) blocks global pip installs (PEP 668). 
# We create a virtual environment in /opt/venv and add it to the PATH.
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# ENV PATH="$PATH:/usr/bin:/usr/local/bin"    
# 3. Install Python Libraries
# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies (upgrade pip first)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 4. Cleanup (Optional but recommended to keep image size down)
# We remove the heavy build tools now that packages are installed.
# (Comment this out if you need to compile more things later)
# RUN apt-get purge -y --auto-remove build-essential python3-dev

# 5. Default Command
# We stick to the default postgres entrypoint so it still behaves like a DB
CMD ["postgres"]