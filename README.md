# UV Clothing Advisor

A modern Python Flask web application that provides personalized clothing and accessory recommendations based on real-time UV index, weather conditions, and AI-powered advice. The app helps users make informed decisions about sun protection by analyzing current UV levels, cloud cover, and location-specific conditions with intelligent caching for optimal performance.

## Features

- **Real-time UV Index**: Fetches current UV data from the NIWA UV API
- **Weather Integration**: Uses OpenWeather API to determine cloud cover conditions and weather status
- **AI-Powered Recommendations**: Integrates with local Ollama (OpenHermes model) for personalized, context-aware clothing advice
- **Location Services**: GPS-based location detection with manual location selection fallback
- **Smart Caching**: Intelligent caching system that reduces API calls and improves performance
- **Day/Night Awareness**: Automatically detects nighttime conditions and adjusts recommendations
- **User Authentication**: Secure login/logout system with user sessions
- **Responsive Design**: Modern, dark-themed interface with mobile-responsive design
- **Error Handling**: Graceful handling of API failures with informative messages

## How It Works

1. **Location Detection**: Automatically detects user location via GPS or allows manual selection from predefined cities
2. **Smart Data Fetching**: Uses intelligent caching to minimize API calls - only fetches new data when location changes or cache expires (5 minutes)
3. **Concurrent API Calls**: Simultaneously fetches UV index and weather data for optimal performance
4. **Day/Night Detection**: Uses sunrise/sunset data to determine if UV protection is needed
5. **AI Advisory**: Will generate personalized recommendations using local Ollama (OpenHermes) when fully implemented
6. **User Display**: Presents comprehensive recommendations through a clean, modern web interface

### UV Index Classifications & Recommendations

The app provides specific advice based on UV index levels, weather conditions, and time of day:

#### Nighttime Conditions
- **Any UV Level**: No UV protection needed - enjoy your evening activities safely

#### Daytime - Cloudy Conditions (<50% cloud cover)
- **UV 0-2 (Low)**: Minimal sun risk - regular clothing is fine
- **UV 3-5 (Moderate)**: Some UV penetrates - cover shoulders, consider a hat
- **UV 6-7 (High)**: UV can still be strong - use sunscreen and wear sunglasses
- **UV 8-10 (Very High)**: Clouds offer partial protection - cover up and limit exposure
- **UV 11+ (Extreme)**: Dangerous even with clouds - stay indoors or fully cover up

#### Daytime - Sunny Conditions (≥50% cloud cover)
- **UV 0-2 (Low)**: No special protection needed - light clothing is fine
- **UV 3-5 (Moderate)**: Wear a hat and cover exposed skin
- **UV 6-7 (High)**: Sunglasses, hat, and long sleeves recommended
- **UV 8-10 (Very High)**: Avoid midday sun - full coverage and SPF 30+ sunscreen needed
- **UV 11+ (Extreme)**: Stay indoors if possible - maximum sun protection required

## Requirements

- Python 3.8 or higher
- pip package manager
- Internet connection for API access
- Valid API keys for NIWA, OpenWeather, and AI language model services

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd uv-clothing-advisor
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root directory:
   ```env
   NIWA_KEY=your_niwa_api_key_here
   OPEN_WEATHER_KEY=your_openweather_api_key_here
   SECRET_KEY=your_flask_secret_key_here
   OLLAMA_BASE_URL=http://localhost:11434  # Default Ollama URL
   OLLAMA_MODEL=openhermes  # Model name in Ollama
   ```

## API Keys Setup

### NIWA API Key
1. Visit [NIWA's UV API documentation](https://niwa.co.nz)
2. Register for an API key
3. Add the key to your `.env` file

### OpenWeather API Key
1. Visit [OpenWeather API](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key
4. Add the key to your `.env` file

### Ollama Setup (for AI recommendations)
1. Install [Ollama](https://ollama.ai) on your local machine
2. Pull the OpenHermes model:
   ```bash
   ollama pull openhermes
   ```
3. Start Ollama service:
   ```bash
   ollama serve
   ```
4. Verify it's running at `http://localhost:11434`

### Flask Secret Key
Generate a secure random string for session management:
```python
import secrets
print(secrets.token_hex(16))
```

## Project Structure

```
uv-clothing-advisor/
├── app.py                     # Flask application factory
├── run.py                     # Application entry point
├── .env                       # Environment variables (create this)
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── routes/                    # Route blueprints
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Main application routes with caching
│   └── auth.py               # Authentication routes
├── route_logic/              # Business logic modules
│   ├── __init__.py          # Package initialization
│   ├── uv_service.py        # UV index data retrieval
│   ├── weather_service.py   # Weather data retrieval
│   ├── advice.py            # Traditional recommendation logic
│   └── bot_advice.py        # AI-powered logic (Ollama integration - in development)
├── templates/                # HTML templates
│   ├── base.html            # Base template with navigation
│   ├── home.html            # Main application interface
│   ├── login.html           # User login page
│   └── register.html        # User registration page
├── static/                   # Static assets
│   └── css/
│       └── style.css        # Modern dark theme styling
└── models/                   # Database models (if using database)
    └── user.py              # User model for authentication
```

## Usage

1. **Start the application**:
   ```bash
   python run.py
   ```

2. **Access the application**:
   Open your web browser and navigate to `http://localhost:5000`

3. **Create an account or login**:
   Register a new account or login with existing credentials

4. **Set your location**:
   - Allow GPS location access for automatic detection, or
   - Manually select your city from the dropdown menu

5. **Get recommendations**:
   The application will automatically fetch current UV and weather data to provide:
   - Traditional clothing advice based on UV levels
   - Weather-specific guidance
   - AI-powered personalized recommendations (when fully implemented)

## Performance Optimizations

### Intelligent Caching System
- **Location-based caching**: API calls only made when location changes
- **Time-based expiration**: Cache expires after 5 minutes for fresh data
- **Session storage**: Uses Flask sessions for user-specific caching
- **Automatic cache clearing**: Cache clears when user changes location

### Optimized AI Processing
- **Local AI model**: Uses Ollama with OpenHermes for privacy and speed
- **Smart AI calls**: Only generates AI advice during daytime hours (when implemented)
- **Offline capability**: AI runs locally without external API dependencies

## Configuration

The application uses the following environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `NIWA_KEY` | API key for NIWA UV service | Yes |
| `OPEN_WEATHER_KEY` | API key for OpenWeather service | Yes |
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `OLLAMA_BASE_URL` | Ollama server URL | No (defaults to localhost:11434) |
| `OLLAMA_MODEL` | Ollama model name | No (defaults to openhermes) |
| `FLASK_ENV` | Flask environment (development/production) | No |

## Error Handling

The application includes comprehensive error handling for:
- API connection failures and timeouts
- Invalid API responses and malformed data
- Missing or invalid environment variables
- Network connectivity issues
- AI service unavailability (Ollama server down)
- Local AI model loading failures
- User authentication errors

When services are unavailable, users receive clear error messages and fallback recommendations.

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
python run.py
```

### Starting Ollama
Ensure Ollama is running before starting the Flask app:
```bash
# In a separate terminal
ollama serve

# Verify the model is available
ollama list
```

### Testing Location Changes
Test the caching system by:
1. Setting an initial location
2. Refreshing the page (should use cached data)
3. Changing location (should fetch fresh data)
4. Waiting 5+ minutes and refreshing (should fetch fresh data)

## API Rate Limits and Costs

### NIWA API
- Free tier available with reasonable limits
- Commercial tiers for high-volume usage

### OpenWeather API
- Free tier: 1,000 calls/day
- Paid tiers available for higher volumes

### Ollama (Local AI)
- **No API costs**: Runs entirely on your local machine
- **Privacy**: All AI processing happens locally
- **Performance**: Depends on your hardware specifications
- **Models**: Free access to various open-source models

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Known Limitations

- Requires active internet connection for initial data fetching
- AI recommendations only available during daytime hours (when implemented)
- Requires Ollama to be running locally for AI features
- AI performance depends on local hardware capabilities
- Weather conditions simplified to sunny/cloudy based on 50% cloud cover threshold

## Recent Updates

### Version 2.0 Features
- ✅ Intelligent caching system for reduced API calls
- 🚧 Local AI integration with Ollama (OpenHermes model) - in development
- ✅ User authentication and session management
- ✅ GPS location detection with manual fallback
- ✅ Day/night awareness and sunrise/sunset calculations
- ✅ Modern responsive UI with dark theme
- ✅ Concurrent API processing for better performance

### In Development
- 🚧 AI-powered personalized recommendations via Ollama
- 🚧 Integration with OpenHermes model for context-aware advice

## Future Enhancements

- [ ] **Complete AI integration**: Finish implementing Ollama-based personalized recommendations
- [ ] Database integration for persistent user preferences
- [ ] Hourly UV forecasts and historical data
- [ ] More granular weather condition analysis
- [ ] Push notifications for UV alerts
- [ ] Offline mode with cached recommendations
- [ ] User-customizable advice preferences
- [ ] Multiple AI model support (Llama, Mistral, etc.)
- [ ] Integration with wearable devices
- [ ] Multi-language support
- [ ] Social sharing features
- [ ] UV exposure tracking

## Security Considerations

- Environment variables for sensitive API keys
- Flask session security with secret key
- Input validation for location data
- HTTPS recommended for production deployment
- Rate limiting consideration for production use

## Deployment

### Production Checklist
- [ ] Set `FLASK_ENV=production`
- [ ] Configure proper secret key
- [ ] Set up HTTPS/SSL
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure database (if using persistent storage)
- [ ] Set up backup strategies

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [NIWA](https://niwa.co.nz) for UV index data
- [OpenWeather](https://openweathermap.org) for weather information
- [Ollama](https://ollama.ai) for local AI model hosting
- [OpenHermes](https://huggingface.co/teknium/OpenHermes-2.5-Mistral-7B) for the AI model
- Flask community for the excellent web framework
- Contributors and testers who helped improve the application

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section below
2. Review existing GitHub issues
3. Open a new issue with detailed information about your problem

### Troubleshooting

**Common Issues:**
- **Location not detected**: Ensure GPS permission is granted or use manual location selection
- **No AI recommendations**: Check if Ollama is running and OpenHermes model is installed
- **Cache not working**: Verify session storage is enabled in your browser
- **API errors**: Verify all API keys are correctly set in `.env` file
- **Ollama connection failed**: Ensure Ollama service is running on localhost:11434

---

**Note**: Always keep your `.env` file secure and never commit it to version control. Add `.env` to your `.gitignore` file to prevent accidental exposure of API keys.
