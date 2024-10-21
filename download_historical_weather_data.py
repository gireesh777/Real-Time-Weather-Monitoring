import sqlite3
import requests
from datetime import datetime, timedelta
from config import API_KEY
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']

def get_db_connection():
    conn = sqlite3.connect('weather.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_weather_summary_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            city TEXT NOT NULL,
            avg_temp REAL NOT NULL,
            max_temp REAL NOT NULL,
            min_temp REAL NOT NULL,
            dominant_condition TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def initialize_database():
    create_weather_summary_table()

def fetch_weather_data(city, date):
    """Fetch historical weather data for a specific city and date."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&date={date}&appid={API_KEY}"
    response = requests.get(url)
    return response.json()

def kelvin_to_celsius(temp_kelvin):
    return temp_kelvin - 273.15

def save_daily_summary(city, avg_temp, max_temp, min_temp, dominant_condition, date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO weather_summary (date, city, avg_temp, max_temp, min_temp, dominant_condition)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, city, avg_temp, max_temp, min_temp, dominant_condition))
    conn.commit()
    conn.close()

def download_historical_weather_data(start_date, end_date):
    date_format = "%Y-%m-%d"
    current_date = start_date

    while current_date <= end_date:
        for city in CITIES:
            data = fetch_weather_data(city, current_date.strftime(date_format))
            if 'main' in data:
                avg_temp = kelvin_to_celsius(data['main']['temp'])
                max_temp = kelvin_to_celsius(data['main']['temp_max'])
                min_temp = kelvin_to_celsius(data['main']['temp_min'])
                dominant_condition = data['weather'][0]['main']
                save_daily_summary(city, avg_temp, max_temp, min_temp, dominant_condition, current_date.strftime(date_format))
                print(f"Weather data for {city} on {current_date.strftime(date_format)} saved.")
            else:
                print(f"Could not retrieve data for {city} on {current_date.strftime(date_format)}.")
        current_date += timedelta(days=1)

if __name__ == '__main__':
    initialize_database()

    # Get user input for date range
    start_date_str = input("Enter the start date (YYYY-MM-DD): ")
    end_date_str = input("Enter the end date (YYYY-MM-DD): ")

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    download_historical_weather_data(start_date, end_date)
