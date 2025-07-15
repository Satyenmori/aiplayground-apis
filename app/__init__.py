import os
import importlib
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py', silent=True)

    plugin_folder = os.path.join(os.path.dirname(__file__), 'plugins')
    for plugin_name in os.listdir(plugin_folder):
        plugin_path = os.path.join(plugin_folder, plugin_name)
        if os.path.isdir(plugin_path) and '__init__.py' in os.listdir(plugin_path):
            module = importlib.import_module(f'app.plugins.{plugin_name}')
            if hasattr(module, 'register_plugin'):
                module.register_plugin(app)

    return app
