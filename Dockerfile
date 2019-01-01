FROM python:3

RUN apt-get update \
    && apt-get install -y \
    git \
    wget \
    sqlite3 \
    supervisor \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download and install Gophish
WORKDIR /usr/src/gophish
RUN wget -O gophish.zip https://getgophish.com/releases/latest/linux/64
RUN unzip gophish.zip
RUN rm gophish.zip
RUN chmod +x gophish

# Expose the admin port to the host
RUN sed -i 's/127.0.0.1/0.0.0.0/g' config.json

WORKDIR /usr/src/gophish-demo/
COPY . .
RUN mv docker/* .
RUN chmod +x run_demo.sh

# Install depenedencies
RUN pip install --no-cache-dir -r requirements.txt

# Setup the supervisor
RUN mv supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]