# Simplified Refactoring for UV Clothing Advisor

## Hobbyist-Friendly Structure

```
uv-clothing-advisor/
├── app/
│   ├── __init__.py                 # Flask app factory (simple)
│   ├── config.py                   # Environment-based config
│   ├── database.py                 # SQLite database setup
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py               # User model
│   │   ├── routes.py               # Login/register routes
│   │   └── utils.py                # Password hashing, etc.
│   ├── main/
│   │   ├── __init__.py
│   │   ├── routes.py               # Main app routes
│   │   └── forms.py                # WTForms for user input
│   ├── api/
│   │   ├── __init__.py
│   │   ├── weather.py              # Weather API endpoints
│   │   ├── recommendations.py      # AI recommendation endpoints
│   │   └── clients.py              # External API clients (NIWA, OpenWeather)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── weather_service.py      # Your existing weather logic (cleaned up)
│   │   ├── recommendation_service.py # AI recommendations
│   │   └── user_service.py         # User-related business logic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                 # User database model
│   │   ├── recommendation.py       # Recommendation history model
│   │   └── weather_cache.py        # Cache weather data
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   └── dashboard.html          # User dashboard
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── tests/
│   ├── __init__.py
│   ├── test_weather.py             # Test weather services
│   ├── test_auth.py                # Test authentication
│   ├── test_recommendations.py     # Test AI recommendations
│   └── fixtures/                   # Test data
├── migrations/                     # Flask-Migrate files
├── instance/                       # SQLite database goes here
├── requirements.txt
├── .env.example
├── .env
├── run.py                         # Development server
├── wsgi.py                        # Production deployment
└── config.py                      # Config classes
```

## Key Design Principles for Hobbyists

### 1. **Keep It Simple** - Flask Blueprints
```python
# app/__init__.py - Simple app factory
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.main import bp as main_bp
    from app.auth import bp as auth_bp
    from app.api import bp as api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
```

### 2. **Simple Database Models** - SQLite + SQLAlchemy
```python
# app/models/user.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(100))  # For future multi-location support
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# app/models/recommendation.py
class RecommendationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    uv_index = db.Column(db.Float)
    weather_condition = db.Column(db.String(50))
    recommendation = db.Column(db.Text)
    ai_enhanced = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

### 3. **Clean Up Existing Services** - Keep Your Logic
```python
# app/services/weather_service.py - Your existing code, just organized
import requests
from app.config import Config

class WeatherService:
    def __init__(self):
        self.niwa_key = Config.NIWA_KEY
        self.openweather_key = Config.OPENWEATHER_KEY
    
    def get_uv_index(self, location="auckland"):  # Your existing logic
        try:
            # Your NIWA API code here
            pass
        except Exception as e:
            return None
    
    def get_weather_data(self, location="auckland"):  # Your existing logic
        try:
            # Your OpenWeather API code here
            pass
        except Exception as e:
            return None
    
    def get_clothing_advice(self, uv_index, is_cloudy=None):
        # Your existing advice function - just moved here
        if uv_index is None:
            return "UV data unavailable."
        # ... rest of your existing logic
```

### 4. **Simple AI Integration** - Start Basic
```python
# app/services/recommendation_service.py
import openai  # or use free alternatives like Hugging Face
from app.config import Config

class AIRecommendationService:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY  # Optional
    
    def enhance_recommendation(self, basic_recommendation, user_context=None):
        """Enhance basic recommendation with AI if available"""
        if not self.api_key:
            return basic_recommendation  # Fallback to your existing logic
        
        try:
            # Simple AI enhancement
            prompt = f"""
            Basic UV recommendation: {basic_recommendation}
            User context: {user_context or 'General user'}
            
            Provide a more personalized and detailed recommendation:
            """
            
            # AI API call here (optional)
            return basic_recommendation  # Fallback for now
        except:
            return basic_recommendation  # Always fallback
```

### 5. **Easy Testing** - Start Simple
```python
# tests/test_weather.py
import unittest
from app import create_app, db
from app.services.weather_service import WeatherService

class WeatherTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
    def test_clothing_advice_low_uv(self):
        service = WeatherService()
        advice = service.get_clothing_advice(uv_index=1, is_cloudy=True)
        self.assertIn("Low UV", advice)
        
    def test_clothing_advice_high_uv(self):
        service = WeatherService()
        advice = service.get_clothing_advice(uv_index=8, is_cloudy=False)
        self.assertIn("Very High UV", advice)
```

### 6. **Simple Config for All Environments**
```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///uv_advisor.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # APIs
    NIWA_KEY = os.environ.get('NIWA_KEY')
    OPENWEATHER_KEY = os.environ.get('OPENWEATHER_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')  # Optional
    
    # Deployment (Render, Heroku, etc.)
    PORT = int(os.environ.get('PORT', 5000))
```

## Migration Steps (Easy Weekend Project)

### Step 1: Create New Structure (30 mins)
```bash
mkdir -p app/{auth,main,api,services,models,templates/auth}
mkdir tests migrations instance
touch app/{__init__.py,config.py,database.py}
# Create all the __init__.py files
```

### Step 2: Move Existing Code (1 hour)
- Move your `route_logic/advice.py` → `app/services/weather_service.py`
- Move your `route_logic/uv_service.py` → `app/api/clients.py`
- Keep your existing logic, just organize it better

### Step 3: Add Simple Auth (1 hour)
- Install `flask-login` and `flask-wtf`
- Create basic User model
- Add login/register forms

### Step 4: Add Database (30 mins)
- Install `flask-sqlalchemy` and `flask-migrate`
- Create models
- Run first migration

### Step 5: Simple Tests (1 hour)
- Test your existing advice function
- Test basic routes
- Test user registration

## Deployment on Render

```python
# wsgi.py
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

```txt
# requirements.txt (add to existing)
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
Flask-Migrate==4.0.4
Flask-WTF==1.1.1
WTForms==3.0.1
gunicorn==21.2.0
```

## Benefits of This Approach

✅ **Easy to understand** - Clear separation without over-engineering  
✅ **Your existing code mostly stays** - Just organized better  
✅ **Room to grow** - Easy to add AI, more features later  
✅ **Production ready** - Works on Render/Heroku out of the box  
✅ **Testable** - Simple unit tests you can actually write  
✅ **Database ready** - SQLite for dev, PostgreSQL for production  

This structure lets you keep your current simplicity while preparing for the features you want to add. You can implement each piece gradually without breaking what already works!