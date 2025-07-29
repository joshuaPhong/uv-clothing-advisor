# UV Clothing Advisor

A Python Flask web application that provides personalized clothing and accessory recommendations based on real-time UV index and weather conditions. The app helps users make informed decisions about sun protection by analyzing current UV levels and cloud cover.

## Features

- **Real-time UV Index**: Fetches current UV data from the NIWA UV API
- **Weather Integration**: Uses OpenWeather API to determine cloud cover conditions
- **Smart Recommendations**: Provides tailored clothing and accessory advice based on UV levels and weather
- **User-friendly Interface**: Clean web interface for easy access to recommendations
- **Error Handling**: Graceful handling of API failures with informative messages

## How It Works

1. **UV Data Collection**: Retrieves the current UV index using the NIWA API for accurate sun exposure measurements
2. **Weather Analysis**: Fetches cloud cover data from OpenWeather API (0-100 scale, divided by 2) to determine if conditions are sunny (≥50) or cloudy (<50)
3. **Smart Advisory**: Combines UV index and weather conditions to generate appropriate clothing and accessory recommendations
4. **User Display**: Presents recommendations through a clean web interface

### UV Index Classifications & Recommendations

The app provides specific advice based on UV index levels and weather conditions:

#### Cloudy Conditions (<50 cloud index)
- **UV 0-2 (Low)**: Minimal sun risk - regular clothing is fine
- **UV 3-5 (Moderate)**: Some UV penetrates - cover shoulders, consider a hat
- **UV 6-7 (High)**: UV can still be strong - use sunscreen and wear sunglasses
- **UV 8-10 (Very High)**: Clouds offer partial protection - cover up and limit exposure
- **UV 11+ (Extreme)**: Dangerous even with clouds - stay indoors or fully cover up

#### Sunny Conditions (≥50 cloud index)
- **UV 0-2 (Low)**: No special protection needed - light clothing is fine
- **UV 3-5 (Moderate)**: Wear a hat and cover exposed skin
- **UV 6-7 (High)**: Sunglasses, hat, and long sleeves recommended
- **UV 8-10 (Very High)**: Avoid midday sun - full coverage and SPF 30+ sunscreen needed
- **UV 11+ (Extreme)**: Stay indoors if possible - maximum sun protection required

## Requirements

- Python 3.8 or higher
- pip package manager
- Internet connection for API access
- Valid API keys for NIWA and OpenWeather services

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

## Project Structure

```
uv-clothing-advisor/
├── app.py                  # Main Flask application
├── .env                    # Environment variables (create this)
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── route_logic/           # Business logic modules
│   ├── __init__.py       # Package initialization
│   ├── uv_service.py     # UV index data retrieval
│   ├── weather_service.py # Weather data retrieval
│   └── advice.py         # Recommendation logic
└── templates/             # HTML templates
    └── index.html        # Main web interface
```

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Access the application**:
   Open your web browser and navigate to `http://localhost:5000`

3. **Get recommendations**:
   The application will automatically fetch current UV and weather data to provide clothing advice

## Configuration

The application uses the following environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `NIWA_KEY` | API key for NIWA UV service | Yes |
| `OPEN_WEATHER_KEY` | API key for OpenWeather service | Yes |

## Error Handling

The application includes comprehensive error handling for:
- API connection failures
- Invalid API responses
- Missing environment variables
- Network connectivity issues

When APIs are unavailable, users receive clear error messages explaining the situation.

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
python app.py
```

### Testing
```bash
# Run tests (if test suite exists)
python -m pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Known Limitations

- Requires active internet connection for API calls
- API rate limits may apply depending on your subscription tier
- Weather conditions are currently simplified to sunny/cloudy based on 50% cloud cover threshold (more precision planned for future updates)
- Cloud cover index is divided by 2 from the original 0-100 scale for current threshold determination

## Future Enhancements

- [ ] Add support for multiple locations
- [ ] Include hourly UV forecasts
- [ ] Implement more precise weather condition thresholds beyond the current 50% cloud cover split
- [ ] Add more detailed weather conditions (partly cloudy, overcast, etc.)
- [ ] Implement user preferences and settings
- [ ] Add mobile-responsive design improvements
- [ ] Include wind and humidity factors in recommendations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [NIWA](https://niwa.co.nz) for UV index data
- [OpenWeather](https://openweathermap.org) for weather information
- Flask community for the excellent web framework

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.

---

**Note**: Make sure to never commit your `.env` file containing API keys to version control. The `.env` file should be added to your `.gitignore` file.
