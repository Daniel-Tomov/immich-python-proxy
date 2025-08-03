import ssl
import logging
from gunicorn.workers.sync import SyncWorker

_original_handle = SyncWorker.handle

def handle_with_ssl_filter(self, listener, client, addr):
    try:
        return _original_handle(self, listener, client, addr)
    except ssl.SSLError as e:
        if 'sslv3 alert certificate unknown' in str(e).lower():
            # Suppress this specific warning
            logging.getLogger("gunicorn.error").debug("Suppressed SSL error from %s: %s", addr, e)
        else:
            raise

SyncWorker.handle = handle_with_ssl_filter
