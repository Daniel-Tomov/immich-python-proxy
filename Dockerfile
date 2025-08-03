FROM python:3.13.1-bookworm

WORKDIR /src/

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . /src/

EXPOSE 3000

CMD [ "gunicorn", "-c", "server/gunicorn.conf.py", "app:app" ]