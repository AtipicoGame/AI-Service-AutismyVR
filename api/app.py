from flask import Flask
from flasgger import Swagger
from src.auth import init_firebase
from api.routes import api_bp

def create_app():
    app = Flask(__name__)
    
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
    
    try:
        init_firebase()
    except Exception as e:
        print(f"Firebase initialization skipped (will initialize on first auth): {e}")
    
    app.register_blueprint(api_bp)
            
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
