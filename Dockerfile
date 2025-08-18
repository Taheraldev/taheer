FROM python:3.11

# إنشاء مجلد
RUN mkdir /pdf && chmod 777 /pdf
WORKDIR /pdf

# تثبيت بايثون requirements
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY libgenesis/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# تحديث وتنصيب الحزم
RUN apt-get update && apt-get install -y \
    ocrmypdf \
    wkhtmltopdf \
    tree \
    && rm -rf /var/lib/apt/lists/*

# نسخ باقي الملفات
COPY . .

# تنفيذ tree كاختبار
RUN tree

CMD ["python3", "-u", "__main__.py"]
