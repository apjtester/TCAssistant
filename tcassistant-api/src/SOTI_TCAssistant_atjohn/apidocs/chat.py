
from flask_restful import Api, Resource
from flasgger import swag_from
from flask import Response, request, stream_with_context
from ..singleton import singleton

# def register_chat_routes(app):
#     @app.route('/chat', methods=['POST'])
#     def status():
#         return {"status": "API 1 is working!"}
def GenerateURLText(urls):
    urlText="**Source URLS used for the test case**\n"
    urlMap={}
    for url in urls:
        if not urlMap.get(url):            
            urlMap[url]=True
            urlText+=f"- [{url}]({url})\n"
    return urlText+'\n'

class Chat(Resource):
    @swag_from({
        "parameters": [
            {
            "name": "body",
            "in": "body",
            "type": "string",
            "required": "true",
            "default": "{\"model\":\"gemma:2b\", \"question\":\"Create a test case to test device group creation.\"}",
            }
        ],
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
    def post(self):
        """
        This endpoint accepts a JSON body with 'model' and 'question' keys and returns a response.
        """
        data = request.get_json()
        model = data.get('model')
        question = data.get('question')
        if not model or not question:
            return {'message': 'Both model and question are required.'}, 400
        if not singleton.rag.changeModel(model):
            return {'message': 'Invalid Model name'}, 400
        sourceUrls , docStream= singleton.rag.answerQuestion(question)
        def generate():
            yield GenerateURLText(sourceUrls)
            for chunk in docStream:
                yield f"{chunk}"

        # Process the model and question here
        # response_message = f"Model: {model}, Question: {response}"

        return Response(generate(),content_type='text/event-stream',headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})
