from flatlib import const, aspects
from models import *

def get_chart_aspects_for_planet(planetName, baseChart, chart):
  planet = baseChart.get(planetName)
  res = []

  for other_body in LIST_PLANETS:
    other_planet = chart.get(other_body)
    aspect = aspects.getAspect(planet, other_planet, const.MAJOR_ASPECTS)

    if aspect.type != -1:
      aspect_part = aspect.active if aspect.active.id != planetName else aspect.passive
      if aspect_part.id not in LIST_PLANETS:
        # don't care about Lilith and nodes
        continue
      if aspect.orb > 5:
        continue
      res.append({
        'first': planetName, 'second': aspect_part.id,
        'type': aspect.type, 'type_name': ASPECT_LABELS[aspect.type],
        'orb': aspect.orb
      })
  
  return res
