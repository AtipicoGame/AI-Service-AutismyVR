from flask import Flask
from flasgger import Swagger
from src.db import init_db
from api.routes import api_bp

def create_app():
    app = Flask(__name__)
    
    # Swagger Config
    app.config['SWAGGER'] = {
        'title': 'AutismyVR AI Service API',
        'uiversion': 3
    }
    Swagger(app)
    
    # Register Blueprints
    app.register_blueprint(api_bp)
    
    # Initialize DB (if needed here, or in entrypoint)
    # init_db() # Better to run via migration script or entrypoint, but for now:
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            print(f"DB Init failed (expected during build if db not ready): {e}")
            
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
