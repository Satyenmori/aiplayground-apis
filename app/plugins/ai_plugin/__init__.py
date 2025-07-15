from .routes import ai_bp

def register_plugin(app):
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
