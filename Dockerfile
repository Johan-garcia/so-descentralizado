FROM python:3.9-slim

# ESTA ES LA LÍNEA MÁGICA QUE ARREGLA LOS LOGS VACÍOS
ENV PYTHONUNBUFFERED=1

LABEL description="SO Descentralizado con Librerías Propias de IA"

# Herramientas de sistema
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/os-decentralized

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/opt/os-decentralized

CMD ["python", "kernel/boot.py"]
