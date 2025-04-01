from flask_restful import Api, Resource
from flasgger import swag_from
from flask import make_response
class Items(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'A status code 200 means successful and returns a list of items.',
                'content': {
                    'application/json': {
                        'examples': {
                            'example1': {
                                'summary': 'Successful response',
                                'value': {'items': ['Item 1', 'Item 2', 'Item 3']}
                            }
                        }
                    }
                }
            }
        }
    })
    def get(self):
        """
        This endpoint returns a list of items.
        """
        items = ['Item 1', 'Item 2', 'Item 3']
        return {'items': items}


class Welcome(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'A status code 200 means successful and returns a welcome HTML page.',
                'content': {
                    'text/html': {
                        'examples': {
                            'example1': {
                                'summary': 'Successful response',
                                'value': '<html><head><title>Welcome to the TCAssitant BOT API</title></head><body><h1>Welcome to the TCAssitant BOT API</h1><p>Navigate to <a href="/apidocs">/apidocs</a> for more API details.</p></body></html>'
                            }
                        }
                    }
                }
            }
        }
    })
    def get(self):
        """
        This endpoint returns a welcome HTML page.
        """
        html_content = """
        <html>
            <head>
                <title>Welcome to the TCAssitant BOT API</title>
            </head>
            <body>
                <h1>Welcome to the TCAssitant BOT API</h1>
                <p>Navigate to <a href="/apidocs">/apidocs</a> for more API details.</p>
            </body>
        </html>
        """
        return make_response(html_content, 200, {'Content-Type': 'text/html'})
