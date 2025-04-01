from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from .apidocs.chat import Chat
from .apidocs.welcome import Items, Welcome
from .apidocs.update_data import Revise
from .RAG.rag import RAGBot
from werkzeug.middleware.proxy_fix import ProxyFix
from .singleton import singleton

def create_app():

    app = Flask(__name__)

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    api = Api(app)

    # Configuring Swagger
    app.config['SWAGGER'] = {
        'title': 'My API',
        'uiversion': 3
    }
    swagger = Swagger(app)
    singleton.rag=RAGBot()


    api.add_resource(Welcome, '/')
    api.add_resource(Chat, '/chat')
    api.add_resource(Revise, '/revise')
    api.add_resource(Items, '/items')
    return app
