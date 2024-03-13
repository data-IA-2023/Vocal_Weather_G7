import json
from flask import Flask, render_template, request, abort, Response
import urllib
from dotenv import load_dotenv
import os
from datetime import datetime

from voice import recognize_from_microphone
from camembert import NLP
from geocoding import city_to_coordinates


load_dotenv('.env')
app = Flask(__name__)


@app.route('/forecast', methods=['GET'])
def get_weather():
    city = request.args.get('ville')
    date_str = request.args.get('date')
    
    if city is None or date_str is None:
        abort(400, 'Missing argument city or date')
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        abort(400, 'Invalid date format. Please use YYYY-MM-DD')
    
    data = {}
    # data['q'] = city
    location=city_to_coordinates(city)
    data['lat'] = location['lat']  
    data['lon'] = location['lon']   
    data['appid'] = os.environ['METEOKEY']
    data['units'] = 'metric'
    data['lang'] = 'fr'
    data['dt'] = int(date.timestamp())  # Convert date to Unix timestamp
    
    url_values = urllib.parse.urlencode(data)
    url = 'https://api.openweathermap.org/data/3.0/onecall/timemachine'

    full_url = url + '?' + url_values
    print(full_url)
    response = urllib.request.urlopen(full_url)
    
    resp = Response(response)
    resp.status_code = 200
    titre= f'La météo à {city} le {date_str} est:'
    datajson=json.loads(response.read().decode('utf8'))
  
    datajson["data"][0]["dt"] = datetime.fromtimestamp(datajson["data"][0]["dt"]) # Convert date a au format normal
    print(datajson)
    return render_template('index.html', titre=titre, data=datajson)

@app.route('/speech-to-text', methods=['post'])
def speechToText():
    result= recognize_from_microphone()
    return render_template('index.html', result = result)

@app.route('/decode', methods=['GET'])
def decode():
    phrase = request.args.get('speech_text')
    data= NLP(phrase=phrase)
    ville = data.get('ville', [''])[0]
    date = data.get('date', [''])[0]
    return render_template('index.html', ville = ville, date= date)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)