# Real-Time Weather Monitoring App

## Overview

This project is an assignment for the Zeotap internship. It is a Flask-based web application designed to provide real-time weather monitoring for various cities in India. The app fetches weather data from the OpenWeatherMap API and displays current conditions, alerts for high temperatures, and visualizes temperature trends over time.

### File Descriptions

- **index.html**: The main HTML frontend of the application, styled with Bootstrap. It includes JavaScript functions to interact with the Flask API.
- **app.py**: The core Flask application. It handles routing, fetching weather data, saving it to a SQLite database, and managing alerts.
- **config.py**: Configuration file containing the API key for the OpenWeatherMap API.
- **weather.db**: SQLite database file used to store weather summaries.
- **download_historical_weather_data.py**: A script for downloading and populating historical weather data into the database.

## Requirements

To run this application, you will need:

- Python 3.x
- Flask
- Flask-CORS
- Requests
- SQLite3
- Matplotlib
- APScheduler

## Installation

1. **Clone the Repository**:

```
   git clone https://github.com/gireesh777/Real-Time-Weather-Monitoring.git
   cd Real-Time-Weather-Monitoring
```

2. **Install Required Packages**:

```
pip install Flask Flask-CORS requests matplotlib APScheduler
```

3. **Configure API Key**:

Add your OpenWeatherMap API key in config.py

```
API_KEY = 'your_api_key_here'
```

## Usage

**Run the Application**:

```
python app.py
```

**Access the App**:

Open your web browser and navigate to:

```
http://127.0.0.1:5000/
```

## API Documentation

This section provides details about the API endpoints available in the Real-Time Weather Monitoring app.

### Endpoints

#### 1. Get Current Weather for All Cities

- **Endpoint:** `/weather/current`
- **Method:** `GET`
- **Description:** Fetches current weather data for all predefined cities.

**Response:**

- **Status:** 200 OK
- **Body:**
  ```json
  [
      {
          "city": "Delhi",
          "temperature": 25.00,
          "max_temp": 28.00,
          "min_temp": 22.00,
          "condition": "Clear"
      },
      ...
  ]
  ```

---

#### 2. Get Weather for a Specific City

- **Endpoint:** `/weather/<city_name>`
- **Method:** `GET`
- **Parameters:**
  - `city_name`: The name of the city (e.g., `Delhi`).

**Response:**

- **Status:** 200 OK
- **Body:**

  ```json
  [
    {
      "city": "Delhi",
      "temperature": 25.0,
      "max_temp": 28.0,
      "min_temp": 22.0,
      "condition": "Clear"
    }
  ]
  ```

- **Status:** 500 Internal Server Error
- **Body:**
  ```json
  {
    "error": "Failed to fetch weather data"
  }
  ```

---

#### 3. Check Temperature Alerts

- **Endpoint:** `/alerts`
- **Method:** `GET`
- **Description:** Checks if any cities exceed the defined temperature alert threshold.

**Response:**

- **Status:** 200 OK
- **Body:**
  ```json
  [
      {
          "city": "Delhi",
          "message": "ALERT: Delhi's temperature exceeds 35°C with 36.50°C"
      },
      ...
  ]
  ```

---

#### 4. Visualize Temperature Trends for a City

- **Endpoint:** `/trends/<city>`
- **Method:** `GET`
- **Parameters:**
  - `city`: The name of the city (e.g., `Delhi`).

**Response:**

- **Status:** 200 OK
- **Body:**

  ```json
  {
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAB..."
  }
  ```

- **Status:** 404 Not Found
- **Body:**

  ```json
  {
    "error": "No data available for this city"
  }
  ```

- **Status:** 500 Internal Server Error
- **Body:**
  ```json
  {
    "error": "An error occurred while processing the request"
  }
  ```

## Features:

**Current Weather**: Enter a city name to fetch and display current weather information.

**Temperature Trends**: Select a city from the dropdown menu to visualize its temperature trends over time.

**Temperature Alerts**: The application checks and displays alerts for cities where the temperature exceeds a specified threshold.

**Scheduled Data Collection**:The application automatically gathers daily weather data for a predefined list of cities every 24 hours. You can modify the list of cities in the CITIES variable within app.py.

## Additional Scripts

`download_historical_weather_data.py`: Use this script to download and insert historical weather data into weather.db.

### Notes

- Ensure you have the correct API key configured in `config.py`.
- The app runs on a local server, and the base URL should be adjusted accordingly when deployed.
