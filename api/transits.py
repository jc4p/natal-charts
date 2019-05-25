from datetime import datetime, timezone, timedelta
from flatlib import aspects, const, angle
from models import *
from pprint import pprint

def get_aspects_for_transits(planetName, baseChart, chart, debug=False):
  planet = baseChart.get(planetName)
  res = []

  if debug:
    print(f"------ get_chart_aspects_for_planet: {planetName} ------")
    print(f"  lat: {planet.lat} lon: {planet.lon}")

  for other_body in LIST_PLANETS:
    # We don't use Ascendant on the transit's chart when looking at these
    if other_body == 'Asc':
      continue

    other_planet = chart.get(other_body)
    aspect = aspects.getAspect(planet, other_planet, const.MAJOR_ASPECTS)

    if aspect.type != -1:
      aspect_part = aspect.active if aspect.active.id != planetName else aspect.passive

      if aspect_part.id not in LIST_PLANETS:
        # i don't care about Lilith and nodes
        continue

      if debug:
        print(f"{other_planet} - {ASPECT_LABELS[aspect.type]}")
      
      sep = angle.closestdistance(planet.lon, other_planet.lon)
      diff_to_aspect_exact = abs(aspect.type - abs(sep))

      orb_limit = 2
      if aspect_part.id == 'Moon':
        orb_limit = 5

      if diff_to_aspect_exact > orb_limit:
        if debug:
          print(f"  Skipping, orb {diff_to_aspect_exact} out of limit of {orb_limit}")
        continue

      date_range = calculate_date_range_for_transit(planetName, other_planet, aspect, sep)
      if not date_range['already_ended']:
        res.append({
          'natal': planetName, 'transit': aspect_part.id,
          'type': aspect.type, 'type_name': ASPECT_LABELS[aspect.type],
          'orb': aspect.orb, 'date_start': date_range['start'],
          'date_end': date_range['end'], 'date_exact': date_range['exact_on']
        })
    
  return res

def calculate_date_range_for_transit(planetName, otherPlanet, aspect, sep):
  max_sep = aspect.type + 1.4
  min_sep = aspect.type - 1.4

  degrees_til_exact = aspect.type - abs(sep)
  exact_degrees = otherPlanet.lon + degrees_til_exact

  today = datetime.utcnow().astimezone(timezone.utc)

  days_til_exact = degrees_til_exact / abs(otherPlanet.lonspeed)
  exact = today + timedelta(days = days_til_exact)

  degrees_til_max = max_sep - abs(sep)
  degrees_til_min = abs(min_sep - abs(sep))

  days_til_max = degrees_til_max / abs(otherPlanet.lonspeed)
  days_til_min = degrees_til_min / abs(otherPlanet.lonspeed)

  start = today + timedelta(days = -days_til_min)
  end = today + timedelta(days = days_til_max)

  return {
    'start': start.isoformat(),
    'end': end.isoformat(),
    'exact_on': exact.isoformat(),
    'already_ended': degrees_til_max < 0
  }

if __name__ == "__main__":
  kasra_time = datetime(1992, 3, 14, 20, 0, 0, tzinfo=timezone.utc)
  today_time = datetime(2019, 5, 25, 12, 0, 0, tzinfo=timezone.utc)

  kasra = NatalChart(Person("Kasra", kasra_time, 31.3183272, 48.6706187, '+03:30'))
  today = NatalChart(Person("Today", today_time, 31.3183272, 48.6706187, '+03:30'))

  allAspects = []

  for i in range(len(LIST_PLANETS)):
    p = LIST_PLANETS[i]

    for a in get_aspects_for_transits(p, kasra.chart, today.chart, debug=False):
      allAspects.append(a)

  pprint(allAspects)