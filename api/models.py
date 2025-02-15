from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const, aspects
import os
import site
import sys
from importlib import resources
import flatlib.resources

def find_swefiles_path():
    """Find the Swiss Ephemeris files path that works in both prod and dev"""
    try:
        # First try using importlib.resources (most reliable, works in prod)
        with resources.path('flatlib.resources', 'swefiles') as swefiles_path:
            if os.path.exists(os.path.join(swefiles_path, 'seas_18.se1')):
                return str(swefiles_path)

        # Try Heroku-specific paths first (based on runtime.txt)
        heroku_paths = [
            # Main Heroku Python path for 3.11
            '/app/.heroku/python/lib/python3.11/site-packages/flatlib/resources/swefiles',
            # Fallback Heroku paths
            f'/app/.heroku/python/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages/flatlib/resources/swefiles',
            '/app/venv/lib/python3.11/site-packages/flatlib/resources/swefiles',
        ]
        
        for path in heroku_paths:
            if os.path.exists(os.path.join(path, 'seas_18.se1')):
                return path

        # Try development paths (venv)
        venv_base = os.path.dirname(os.path.dirname(__file__))
        dev_paths = [
            # Look for Python 3.11 first
            os.path.join(venv_base, 'venv/lib/python3.11/site-packages/flatlib/resources/swefiles'),
            # Then try current Python version
            os.path.join(venv_base, 'venv/lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 
                        'site-packages/flatlib/resources/swefiles'),
            # Try env instead of venv
            os.path.join(venv_base, 'env/lib/python3.11/site-packages/flatlib/resources/swefiles'),
        ]

        for path in dev_paths:
            if os.path.exists(os.path.join(path, 'seas_18.se1')):
                return path

        # Try standard system paths
        system_paths = [
            # General site-packages for 3.11
            *[os.path.join(p, 'flatlib', 'resources', 'swefiles') for p in site.getsitepackages()],
            '/usr/local/lib/python3.11/site-packages/flatlib/resources/swefiles',
            '/usr/lib/python3.11/site-packages/flatlib/resources/swefiles',
        ]

        for path in system_paths:
            if os.path.exists(os.path.join(path, 'seas_18.se1')):
                return path

        # Check environment variable as last resort
        env_path = os.getenv('EPHE_PATH')
        if env_path and os.path.exists(os.path.join(env_path, 'seas_18.se1')):
            return env_path

        raise FileNotFoundError("Could not find Swiss Ephemeris files in any expected location")
            
    except Exception as e:
        print(f"Warning: Error finding ephemeris files: {str(e)}")
        return os.getcwd()

# Set up ephemeris path before importing swisseph
ephe_path = find_swefiles_path()
os.environ['SE_EPHE_PATH'] = ephe_path
print(f"Using ephemeris path: {ephe_path}")

import swisseph as swe
swe.set_ephe_path(ephe_path)

ASPECT_LABELS = {0: 'conjunction', 60: 'sextile', 90: 'square', 120: 'trine', 180: 'opposition'}
LIST_PLANETS = const.LIST_SEVEN_PLANETS + [const.URANUS, const.NEPTUNE, const.PLUTO, const.ASC]

class Person:
  """Wrapper for API query input, person and birth info"""
  def __init__(self, name, birthdate, birth_lat, birth_lon, birth_utc_offset):
    self.name = name
    self.birthdate = birthdate
    self.birth_lat = birth_lat
    self.birth_lon = birth_lon
    self.birth_utc_offset = birth_utc_offset

  def birth_date_str(self):
    return "{:%Y/%m/%d}".format(self.birthdate)

  def birth_time_str(self):
    return "{:%H:%M}".format(self.birthdate)

  def __repr__(self):
    return "<Person {} Born {:%y-%m-%d}>".format(self.name, self.birthdate)
  
  def __eq__(self, other):
    return self.name == other.name and self.birthdate == other.birthdate

  def __hash__(self):
    return hash("{}_{}".format(self.name, self.birthdate.timestamp()))


class NatalChart:
  """Calculator and wrapper for results of natal charts, per Person"""
  def __init__(self, person):
    self.planets = {}
    self.houses = {}
    self.person = person

    self.date = Datetime(person.birth_date_str(), person.birth_time_str(), person.birth_utc_offset)
    self.pos = GeoPos(person.birth_lat, person.birth_lon)
    self.chart = Chart(self.date, self.pos, IDs=const.LIST_OBJECTS, hsys=const.HOUSES_PLACIDUS)

    for body in LIST_PLANETS:
      self.planets[body] = NatalPlanet(self.chart, body)

    for house in const.LIST_HOUSES:
      self.houses[house] = NatalHouse(self.chart, house)

  def to_dict(self):
    output = {
      'person': {
        'name': self.person.name,
        'birthdate': self.person.birthdate.timestamp(),
        'birth_geo': [self.person.birth_lat, self.person.birth_lon],
        'birth_utc_offset': self.person.birth_utc_offset
      },
      'chart': {
        'planets': {self.planets[k].name: self.planets[k].to_dict() for k in self.planets},
        'houses': {k: self.houses[k].to_dict() for k in self.houses}
      }
    }

    return output


class NatalPlanet:
  """Positioning for planets"""
  def __init__(self, chart, body):
    self.planet = chart.get(body)
    self.house = chart.houses.getObjectHouse(self.planet).id
    self.aspects = []
    self.name = body if body != 'Asc' else 'Ascendant'

    for house_id in const.LIST_HOUSES:
      house = chart.get(house_id)
      if house.sign == self.planet.sign:
        self.house = house_id
        break

    for other_body in LIST_PLANETS:
      other_planet = chart.get(other_body)
      aspect = aspects.getAspect(self.planet, other_planet, const.MAJOR_ASPECTS)
      if aspect.type != -1:
        aspect_part = aspect.active if aspect.active.id != body else aspect.passive
        if aspect_part.id not in LIST_PLANETS:
          # don't care about Lilith and nodes
          continue
        if aspect.orb > 10:
          # maybe #TODO: use different values per type?
          continue
        self.aspects.append({
          'first': self.name, 'second': aspect_part.id,
          'type': aspect.type, 'type_name': ASPECT_LABELS[aspect.type],
          'orb': aspect.orb
        })

  def to_dict(self):
    obj = {
      'planet': self.planet.__dict__,
      'house': self.house,
    }
    if self.aspects:
      obj['aspects'] = [x for x in self.aspects]
    return obj

  def __repr__(self):
    return "<Natal Planet {} in {}>".format(self.planet, self.house)

class NatalHouse:
  """Whose who for the houses at moment of birth"""
  def __init__(self, chart, body):
    self.house = chart.get(body)

  def to_dict(self):
    return self.house.__dict__

  def __repr__(self):
    return "<Natal House {}>".format(self.house)