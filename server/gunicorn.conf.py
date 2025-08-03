bind = '0.0.0.0:3000'
#accesslog = 'gunicornaccess.log'
#errorlog = 'gunicornerror.log'
module="app:app"
loglevel = 'WARN'
timeout = 240000
pidfile = 'server/gunicorn.pid'
debug = False
workers = 8
threads = 4
#keyfile="server/key.pem"
#certfile="server/cert.pem"

def post_worker_init(worker):
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context