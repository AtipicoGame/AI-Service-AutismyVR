from flask import Flask
from flasgger import Swagger
from src.db import init_db
from src.auth import init_firebase
from api.routes import api_bp

def create_app():
    app = Flask(__name__)
    
    # Swagger Config with Firebase Auth
    app.config['SWAGGER'] = {
        'title': 'AutismyVR AI Service API',
        'uiversion': 3,
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'Firebase ID token. Format: Bearer <token>'
            }
        }
    }
    Swagger(app)
    
    # Initialize Firebase (optional - will be initialized on first use if not done here)
    try:
        init_firebase()
    except Exception as e:
        print(f"Firebase initialization skipped (will initialize on first auth): {e}")
    
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
