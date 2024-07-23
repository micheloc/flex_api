import os
import importlib
from flask import Blueprint

def register_blueprints(app):
    project_root = os.path.abspath(os.path.dirname(__file__) + '../../../')
    controllers_dir = os.path.join(project_root, 'src', 'controllers')

    if os.path.isdir(controllers_dir):
        for filename in os.listdir(controllers_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = f'controllers.{filename[:-3]}'
                module = importlib.import_module(module_name)
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if isinstance(attribute, Blueprint):
                        app.register_blueprint(attribute)