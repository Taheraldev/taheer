FROM python:3.11

RUN mkdir /pdf && chmod -R 755 /pdf
WORKDIR /pdf

RUN apt update && apt install -y ocrmypdf wkhtmltopdf tree

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /tmp/requirements.txt

COPY libgenesis/requirements.txt /tmp/libgenesis-requirements.txt
RUN pip install --no-cache-dir -r /tmp/libgenesis-requirements.txt

COPY . .

# تحديد استخدام المعالج والذاكرة
CMD ["python3", "-u", "__main__.py"]
