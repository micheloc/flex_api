from flask import abort, request, Blueprint

## Blueprint não pode conter nomes repetidos. ("Então sé eu criar um novo Blueprint o nome deve ser diferente.")
REQUEST_API = Blueprint('swagger', __name__)

def get_swagger():
    """Return the blueprint for the main app module"""
    return REQUEST_API


    