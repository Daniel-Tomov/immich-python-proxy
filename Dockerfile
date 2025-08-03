FROM python:3.13.1-bookworm

WORKDIR /src/

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . /src/

EXPOSE 3000

CMD [ "gunicorn", "--bind", "0.0.0.0:3000",  "-w", "4", "--threads", "4" ,"main:http", "--certfile=cert.pem", "--keyfile=key.pem" ]