FROM python:3.11

RUN mkdir /pdf && chmod 777 /pdf
WORKDIR /pdf

# Install dependencies for wkhtmltopdf + OCRmyPDF
RUN apt-get update && apt-get install -y \
    wget \
    xfonts-75dpi \
    xfonts-base \
    ocrmypdf \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf from official .deb package
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb \
    && apt install -y ./wkhtmltox_0.12.6-1.bionic_amd64.deb \
    && rm wkhtmltox_0.12.6-1.bionic_amd64.deb

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY libgenesis/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y tree && rm -rf /var/lib/apt/lists/*
RUN tree

CMD ["python3", "-u", "__main__.py"]
