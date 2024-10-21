from flask import Flask, render_template, jsonify
import sqlite3
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import matplotlib
import threading
from config import API_KEY


matplotlib.use('Agg')

CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
ALERT_THRESHOLD_TEMP = 35

app = Flask(__name__)
CORS(app)  

scheduler = BackgroundScheduler()
scheduler.start()

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

def fetch_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    response = requests.get(url)
    return response.json()

def kelvin_to_celsius(temp_kelvin):
    return temp_kelvin - 273.15

def save_daily_summary(city, avg_temp, max_temp, min_temp, dominant_condition):
    conn = get_db_connection()
    cursor = conn.cursor()
    date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO weather_summary (date, city, avg_temp, max_temp, min_temp, dominant_condition)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, city, avg_temp, max_temp, min_temp, dominant_condition))
    conn.commit()
    conn.close()

def gather_weather_data():
    for city in CITIES:
        data = fetch_weather_data(city)
        avg_temp = kelvin_to_celsius(data['main']['temp'])
        max_temp = kelvin_to_celsius(data['main']['temp_max'])
        min_temp = kelvin_to_celsius(data['main']['temp_min'])
        dominant_condition = data['weather'][0]['main']
        save_daily_summary(city, avg_temp, max_temp, min_temp, dominant_condition)

scheduler.add_job(gather_weather_data, 'interval', hours=24)

@app.route('/api/weather/current')
def get_all_cities_weather():
    weather_data = []
    for city in CITIES:
        data = fetch_weather_data(city)
        avg_temp = kelvin_to_celsius(data['main']['temp'])
        max_temp = kelvin_to_celsius(data['main']['temp_max'])
        min_temp = kelvin_to_celsius(data['main']['temp_min'])
        weather_data.append({
            'city': city,
            'temperature': round(avg_temp, 2),
            'max_temp': round(max_temp, 2),
            'min_temp': round(min_temp, 2),
            'condition': data['weather'][0]['main']
        })
    return jsonify(weather_data)

@app.route('/api/weather/<city_name>', methods=['GET'])
def get_specific_city_weather(city_name):
    """Get weather for a specific city by name"""
    data = fetch_weather_data(city_name)
    if data:
        weather_data = []
        avg_temp = kelvin_to_celsius(data['main']['temp'])
        max_temp = kelvin_to_celsius(data['main']['temp_max'])
        min_temp = kelvin_to_celsius(data['main']['temp_min'])
        weather_data.append({
            'city': city_name,
            'temperature': round(avg_temp, 2),
            'max_temp': round(max_temp, 2),
            'min_temp': round(min_temp, 2),
            'condition': data['weather'][0]['main']
        })
        return jsonify(weather_data)
    
    return jsonify({'error': 'Failed to fetch weather data'}), 500

@app.route('/api/alerts')
def check_temperature_alerts():
    alerts = []
    for city in CITIES:
        data = fetch_weather_data(city)
        temp_celsius = kelvin_to_celsius(data['main']['temp'])
        if temp_celsius > ALERT_THRESHOLD_TEMP:
            alerts.append({
                'city': city,
                'message': f"ALERT: {city}'s temperature exceeds {ALERT_THRESHOLD_TEMP}°C with {temp_celsius:.2f}°C"
            })
    return jsonify(alerts)

@app.route('/api/trends/<city>')
def visualize_temperature_trends(city):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        data = cursor.execute('''
            SELECT date, avg_temp, max_temp, min_temp FROM weather_summary WHERE city = ?
        ''', (city,)).fetchall()
        conn.close()

        if not data:
            return jsonify({'error': 'No data available for this city'}), 404

        dates = [row['date'] for row in data]
        avg_temps = [row['avg_temp'] for row in data]
        max_temps = [row['max_temp'] for row in data]
        min_temps = [row['min_temp'] for row in data]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, avg_temps, label='Avg Temp', marker='o')
        plt.plot(dates, max_temps, label='Max Temp', linestyle='--', marker='x')
        plt.plot(dates, min_temps, label='Min Temp', linestyle='--', marker='x')
        plt.xticks(rotation=45)
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        plt.title(f'Temperature Trends for {city}')
        plt.legend()
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close()

        return jsonify({'image': img_base64})
    except Exception as e:
        print(f"Error visualizing trends for {city}: {e}")
        return jsonify({'error': 'An error occurred while processing the request'}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    initialize_database()  
    threading.Thread(target=gather_weather_data).start()
    app.run(debug=True)
