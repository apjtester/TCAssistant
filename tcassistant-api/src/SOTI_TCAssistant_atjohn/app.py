from flask import Flask, request
from flask_restful import Api
from flasgger import Swagger
from flask_cors import CORS
from .apidocs.chat import Chat
from .apidocs.welcome import Items, Welcome
from .apidocs.update_data import Revise
from .RAG.rag import RAGBot
# from werkzeug.middleware.proxy_fix import ProxyFix
from .singleton import singleton

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
# app.wsgi_app = ProxyFix(
#     app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
# )
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

if __name__ == '__main__':
    app.run(debug=True)
