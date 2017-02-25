from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

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

    date = Datetime(person.birth_date_str(), person.birth_time_str(), person.birth_utc_offset)
    pos = GeoPos(person.birth_lat, person.birth_lon)
    chart = Chart(date, pos)

    for body in const.LIST_SEVEN_PLANETS:
      self.planets[body] = NatalPlanet(chart, body)

    for house in const.LIST_HOUSES:
      self.houses[house] = NatalHouse(chart, house)

  def to_dict(self):
    output = {
      'person': {
        'name': self.person.name,
        'birthdate': self.person.birthdate.timestamp(),
        'birth_geo': [self.person.birth_lat, self.person.birth_lon],
        'birth_utc_offset': self.person.birth_utc_offset
      },
      'chart': {
        'planets': {k: self.planets[k].to_dict() for k in self.planets},
        'houses': {k: self.houses[k].to_dict() for k in self.houses}
      }
    }

    return output


class NatalPlanet:
  """Positioning for planets"""
  def __init__(self, chart, body):
    self.planet = chart.get(body)
    self.house = chart.houses.getObjectHouse(self.planet).id

  def to_dict(self):
    return {
      'planet': self.planet.__dict__,
      'house': self.house
    }

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