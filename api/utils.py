from flatlib import const, aspects
from models import *
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper


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
            if not aspect.inOrb(planet.id):
                continue
            if not aspect.mutualAspect():
                continue

            if planetName in ['Sun', 'Moon', 'Asc']:
                if aspect.orb > 2.5:
                    continue
            elif aspect.orb > 2:
                continue

            res.append({
                'first': planetName, 'second': aspect_part.id,
                'type': aspect.type, 'type_name': ASPECT_LABELS[aspect.type],
                'orb': aspect.orb
            })
  
    return res


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator
