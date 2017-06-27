from datetime import datetime, timezone
from flatlib import aspects, const
from models import *
from pprint import pprint

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

if __name__ == "__main__":
    kasra_time = datetime(1992, 3, 14, 20, 0, 0, tzinfo=timezone.utc)
    today_time = datetime(2017, 6, 27, 12, 0, 0, tzinfo=timezone.utc)

    kasra = NatalChart(Person("Kasra", kasra_time, 31.3183272, 48.6706187, '+04:30'))
    today = NatalChart(Person("Today", today_time, 31.3183272, 48.6706187, '+04:30'))

    allAspects = []
    for i in range(len(LIST_PLANETS)):
        p = LIST_PLANETS[i]

        for a in get_chart_aspects_for_planet(p, kasra.chart, today.chart):
            if LIST_PLANETS.index(a['second']) < i:
                # We already have it !
                continue
            allAspects.append(a)
    
    pprint(allAspects)
