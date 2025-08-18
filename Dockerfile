FROM python:3.11

# إنشاء مجلد
RUN mkdir /pdf && chmod 777 /pdf
WORKDIR /pdf

# تثبيت بايثون requirements
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY libgenesis/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# تثبيت ocrmypdf + wkhtmltopdf من .deb
RUN apt-get update && apt-get install -y \
    ocrmypdf \
    wget \
    xfonts-75dpi \
    xfonts-base \
    tree \
    && wget -O /tmp/wkhtmltopdf.deb https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && apt-get install -y /tmp/wkhtmltopdf.deb \
    && rm /tmp/wkhtmltopdf.deb \
    && rm -rf /var/lib/apt/lists/*

# نسخ باقي الملفات
COPY . .

# تأكد أن wkhtmltopdf مثبت
RUN wkhtmltopdf --version

CMD ["python3", "-u", "__main__.py"]
