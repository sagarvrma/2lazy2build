from backend.app import app
from serverless_wsgi import handle_request

def main(event, context):
    return handle_request(app, event, context)
