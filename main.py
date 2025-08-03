from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    make_response,
    session,
    redirect,
    url_for,
    send_file,
    Response
)
from flask_compress import Compress

from utils import error_404, get_url
from share import Share
from environment import config

class Main:
    def __init__(self):
        # log = logging.getLogger('werkzeug')
        # log.setLevel(logging.ERROR)

        # use flask_compress to minify resources to make page loading faster on slower networks

        # various flask settings to remove whitespace in the HTML file sent to the client after the templating is done.
        # also has various security settings to ensure hackers can not use XSS attacks to get a user's session cookie
        self.app = self.start_app()
        # app = Flask(__name__)
        
        self.app.jinja_env.trim_blocks = True
        self.app.jinja_env.lstrip_blocks = True
        self.app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
        self.app.config["TEMPLATES_AUTO_RELOAD"] = True
        self.app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
        self.app.config["SESSION_PERMANENT"] = False
        self.app.config["SESSION_TYPE"] = "filesystem"
        self.app.config.update(
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE="Strict",
        )
        self.register_routes()
        Share(self.app)
        #S(self.app)
        
        #self.app.run(host="0.0.0.0", port=5555, debug=False, use_reloader=False) # development server

    def start_app(self):
        compress = Compress()
        app = Flask(__name__, static_url_path='/share/static')
        compress.init_app(app)
        return app

    def register_routes(self):
        @self.app.route("/", methods=["GET"])
        def index():
            if not config['ipp']['showHomePage']:
                return error_404()
            return render_template("index.html")
        
        @self.app.route('/healthcheck', methods=['GET'])
        def healthcheck():
            r = get_url('/api/server/config')
            if r.status_code == 200:
                return "Success. Immich is reachable."
            print(f'Got response code {r.status_code} from Immich.')
            return error_404()
        
        @self.app.errorhandler(404)
        def not_found(error):
            return error_404()
        
        
http = Main().app

