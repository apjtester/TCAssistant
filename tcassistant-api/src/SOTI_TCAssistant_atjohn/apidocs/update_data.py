
from flask_restful import Api, Resource
from flasgger import swag_from
from flask import request
from ..singleton import singleton
class Revise(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'A status code 200 means successful and returns a message.',
                'content': {
                    'application/json': {
                        'examples': {
                            'example1': {
                                'summary': 'Successful response',
                                'value': {'message': 'Welcome GeeksforGeeks!!'}
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'A status code 400 means invalid message and returns a message.',
                'content': {
                    'application/json': {
                        'examples': {
                            'example1': {
                                'summary': 'Successful response',
                                'value': {'message': 'Welcome GeeksforGeeks!!'}
                            }
                        }
                    }
                }
            }
        }
    })
    def get(self):
        """
        This endpoint updates the Knowledge base with the latest MC Help page.
        """
        url = request.args.get('url',default='https://www.soti.net/mc/help/v2025.0/en/start.html')
        singleton.rag.vstoreConnection.fetch_all_links(url)
        return {'message': "Updated VectorStore"}, 200
