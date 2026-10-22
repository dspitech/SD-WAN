FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    iproute2 iputils-ping tcpdump tshark iperf3 curl traceroute procps jq iptables \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "cryptography>=43,<47"
WORKDIR /lab
COPY app.py controller.py edge.py /lab/
COPY scripts/ /usr/local/bin/
# Tolere les fins de ligne Windows (CRLF) et rend les outils executables.
RUN sed -i 's/\r$//' /usr/local/bin/* /lab/*.py && chmod +x /usr/local/bin/*
