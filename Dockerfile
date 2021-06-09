FROM python:3.9

WORKDIR /usr/src/cv-server

COPY pip.conf /etc/pip.conf
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "-c", "./gunicorn.conf.py"]