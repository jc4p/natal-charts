from flask import Flask, request, jsonify
from datetime import datetime, timezone
from models import *
from utils import get_chart_aspects_for_planet, crossdomain
import geocoder
import os

app = Flask(__name__)
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

@app.route('/')
def index():
  return "Hello"

@app.route('/geocode', methods=['POST'])
def geocode():
  query = request.form.get('q')
  if not query:
    return jsonify({'error': "Invalid input: query"})
  g = geocoder.google(query, key=GOOGLE_API_KEY)
  if not g or g.status != 'OK':
    return jsonify({'error': "Unable to find location"})

  time_year = request.form.get('time_year', -1, type=int)
  time_month = request.form.get('time_month', -1, type=int)
  time_day = request.form.get('time_day', -1, type=int)
  time_hour = request.form.get('time_hour', -1, type=int)

  timezone_time = None
  for el in [time_year, time_month, time_day, time_hour]:
    if el == -1:
      timezone_time = datetime.utcnow()
      break

  if not timezone_time:
    timezone_time = datetime(time_year, time_month, time_day, time_hour, 0, 0, tzinfo=timezone.utc)

  tz = geocoder.google([g.lat, g.lng], timestamp=timezone_time.timestamp(),
          method="timezone", key=GOOGLE_API_KEY)

  # E.g. -18000 --> -05:00 // 12600 --> +3:30
  tz_offset = tz.rawOffset + tz.dstOffset  # we want to ignore daylight savings for this
  tz_offset_negative = tz_offset < 0
  tz_offset_hours = int(abs(tz_offset)/60//60)
  tz_offset_minutes = int((abs(tz_offset)/60/60 - tz_offset_hours) * 60)

  return jsonify({
    'query': query,
    'location': g.address,
    'geo': [g.lat, g.lng],
    'utc_offset': '{}{:02d}:{:02d}'.format("-" if tz_offset_negative else "+",
        tz_offset_hours, tz_offset_minutes)
  })


@app.route('/chart', methods=['POST'])
@crossdomain(origin='*')
def chart():
  name = request.form.get('name')
  if not name:
    return jsonify({'error': "Invalid input: name"})
  
  birth_year = request.form.get('date_year', -1, type=int)
  birth_month = request.form.get('date_month', -1, type=int)
  birth_day = request.form.get('date_day', -1, type=int)
  birth_hour = request.form.get('date_hour', -1, type=int)
  birth_min = request.form.get('date_min', 0, type=int)

  for el in [birth_year, birth_month, birth_day, birth_hour]:
    if el == -1:
      return jsonify({'error': "Invalid input: birthdate"})

  birth_lat = request.form.get('location_lat', 0.0, type=float)
  birth_lon = request.form.get('location_lon', 0.0, type=float)

  if birth_lon == 0.0 or birth_lat == 0.0:
    return jsonify({'error': "Invalid input: birth geo"})

  birth_utc_offset = request.form.get('location_utc_offset', '+00:00')
  
  birthdate = datetime(birth_year, birth_month, birth_day, birth_hour, birth_min, 0, tzinfo=timezone.utc)
  person = Person(name, birthdate, birth_lat, birth_lon, birth_utc_offset)
  chart = NatalChart(person)

  return jsonify(chart.to_dict())


@app.route('/day', methods=['POST'])
def day():
  location_lat = request.form.get('location_lat', 0.0, type=float)
  location_lon = request.form.get('location_lon', 0.0, type=float)

  if location_lat == 0.0 or location_lon == 0.0:
    return jsonify({'error': "Invalid input: birth location"})

  #TODO: The location's daylight savings might be different at the moment vs birth time !
  location_offset = request.form.get('location_utc_offset', '+00:00')

  moment_timestamp = request.form.get('moment_time', 0, type=int)

  if moment_timestamp == 0 :
    return jsonify({'error': "Invalid input: timestamp"})

  moment_time = datetime.utcfromtimestamp(moment_timestamp)

  person = Person(moment_timestamp, moment_time, location_lat, location_lon, location_offset)
  chart = NatalChart(person)

  return jsonify(chart.to_dict())


@app.route('/person-aspects', methods=['POST'])
def person_aspects():
  first_timestamp = request.form.get('first_time', 0, type=int)
  second_timestamp = request.form.get('second_time', 0, type=int)

  if first_timestamp == 0 or second_timestamp == 0:
    return jsonify({'error': "Invalid input: timestamps"})

  first_time = datetime.utcfromtimestamp(first_timestamp)
  second_time = datetime.utcfromtimestamp(second_timestamp)

  first_lat = request.form.get('first_lat', 0.0, type=float)
  first_lon = request.form.get('first_lon', 0.0, type=float)

  second_lat = request.form.get('second_lat', 0.0, type=float)
  second_lon = request.form.get('second_lon', 0.0, type=float)

  if first_lat == 0.0 or first_lon == 0.0 or second_lat == 0.0 or second_lon == 0.0:
    return jsonify({'error': "Invalid input: locations"})

  first_offset = request.form.get('first_utc_offset', '+00:00')
  second_offset = request.form.get('second_utc_offset', '+00:00')

  first = NatalChart(Person("First", first_time, first_lat, first_lon, first_offset))
  second = NatalChart(Person("Second", second_time, second_lat, second_lon, second_offset))

  all_aspects = []
  for i in range(len(LIST_PLANETS)):
      p = LIST_PLANETS[i]

      for a in get_chart_aspects_for_planet(p, first.chart, second.chart):
          if LIST_PLANETS.index(a['second']) < i:
              # We already have it !
              continue
          all_aspects.append(a)

  return jsonify(all_aspects)


@app.route('/transits', methods=['POST'])
def transits():
  person_timestamp = request.form.get('person_time', 0, type=int)
  moment_timestamp = request.form.get('moment_time', 0, type=int)

  if person_timestamp == 0 or moment_timestamp == 0:
    return jsonify({'error': "Invalid input: timestamps"})

  person_time = datetime.utcfromtimestamp(person_timestamp)
  moment_time = datetime.utcfromtimestamp(moment_timestamp)

  location_lat = request.form.get('location_lat', 0.0, type=float)
  location_lon = request.form.get('location_lon', 0.0, type=float)

  if location_lat == 0.0 or location_lon == 0.0:
    return jsonify({'error': "Invalid input: birth location"})

  #TODO: The location's daylight savings might be different at the moment vs birth time !
  location_offset = request.form.get('location_utc_offset', '+00:00')

  person = NatalChart(Person("Person", person_time, location_lat, location_lon, location_offset))
  moment = NatalChart(Person("Moment", moment_time, location_lat, location_lon, location_offset))

  all_aspects = []
  for i in range(len(LIST_PLANETS)):
      p = LIST_PLANETS[i]
      all_aspects_for_planet = []
      for a in get_chart_aspects_for_planet(p, moment.chart, person.chart):
          # if LIST_PLANETS.index(a['second']) < i:
          #     # We already have it !
          #     continue
          all_aspects_for_planet.append(a)
      smallest_orb_index = -1
      conjunction_index = -1
      smallest_orb_amount = 100
      # Only add the aspect with the smallest orb
      for i, aspect in enumerate(all_aspects_for_planet):
        if aspect['orb'] < smallest_orb_amount:
          smallest_orb_amount = aspect['orb']
          smallest_orb_index = i
      # If there's another conjunction aspet, add that too
      for i, aspect in enumerate(all_aspects_for_planet):
        if aspect['type'] == 0 and smallest_orb_index != i:
          conjunction_index = i
      if smallest_orb_index > -1:
        all_aspects.append(all_aspects_for_planet[smallest_orb_index])
      if conjunction_index > -1:
        all_aspects.append(all_aspects_for_planet[conjunction_index])


  # from flatlib.ephem import ephem
  # Next sunrise might be tomorrow, but last sunrise might be 10 min ago!
  # lastSunrise = ephem.lastSunrise(moment.date, moment.pos)
  # nextSunset = ephem.nextSunset(lastSunrise, moment.pos)
  # nextSunrise = ephem.nextSunrise(moment.date, moment.pos)
  # print("Last sunrise: ", lastSunrise)
  # print("Next sunset: ", nextSunset)
  # print("Next sunrise: ", nextSunrise)

  return jsonify(all_aspects)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
