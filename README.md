# UV Clothing Advisor

This project is a Python Flask application that provides clothing accessory advice based on the UV index and weather conditions. It fetches the UV data from the NIWA UV API and cloud cover from OPEN WEATHER API to determine if it is cloudy or sunny. The advice is adjusted accordingly.

## Requirements

- Python 3.x
- pip

## Setup

1. Clone the project repository.
2. Create and activate a virtual environment.
3. Install the dependencies:
    
    ```bash
    pip install -r requirements.txt
    ```
    
4. Create a `.env` file in the project root with the following keys:

    ```
    NIWA_KEY=your_niwa_key
    OPEN_WEATHER_KEY=your_openweather_key
    ```

## Project Structure
```
├── app.py 
├── .env 
├── README.md 
├── route_logic   
    ├── uv_service.py    
    ├── weather_service.py 
    └── advice.py 
└── templates 
    └── index.html
```
## Running the Application

Start the application by executing:

```bash
python app.py
```
Then open your browser at http://localhost:5000 to view the advisory page.



How It Works
UV Data: The app fetches the current UV index using the NIWA API.
Weather Check: The app fetches the current cloud index from OPEN WEATHER API.
It determines if the weather is cloudy or sunny,less than or greater than 50.
Clothing Advice: Based on the combination of the UV index and the weather condition, the app provides tailored advice.
Error Handling
If the UV or weather data is not available, the application displays an appropriate error message.


Licence
[Include project licence information here]
This README provides a brief overview, setup instructions, file structure,
and explanation of how the application works.uv app for clothing accessory advice
