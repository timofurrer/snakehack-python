import bottle
import os
import itertools
import math

import numpy as np

from bstar import PathFinder


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    head_url = '%s://%s/static/william_snakespeare.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#910052',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'William Snakespeare'
    }


def create_matrix(width, height, snakes):
    """
    Create two dim array with snakes
    """
    snakes_coords = itertools.chain(*[x['coords'] for x in snakes])
    matrix = np.zeros(shape=(width, height))
    for x, y in snakes_coords:
        matrix[y][x] = 1
    return matrix


def get_move(start, end):
    # check single move
    x = end[0] - start[0]
    if x > 0:
        return 'right'
    elif x < 0:
        return 'left'

    y = end[1] - start[1]
    if y > 0:
        return 'down'
    elif y > 0:
        return 'up'

    print('Choose random move')
    return 'up'


def get_closest_food(head, foods):
    min_d = 20000000000000
    closest_food = foods[0]
    for x, y in foods:
        d = math.fabs(head[0] - x)**2 + math.fabs(head[1] - y)**2
        if d < min_d:
            min_d = d
            closest_food = x, y
    return closest_food


@bottle.post('/move')
def move():
    data = bottle.request.json

    print(data)

    matrix = create_matrix(data['width'], data['height'], data['snakes'])
    print(matrix)

    our_snake = next((x for x in data['snakes'] if x['id'] == data['you']), None)
    # our_head = tuple(reversed(fix_y_coord(our_snake['coords'][0])))
    our_head = tuple(our_snake['coords'][0])
    print(our_snake)

    finder = PathFinder(data['width'], data['height'], matrix)

    next_food = tuple(get_closest_food(our_head, data['food']))

    print('Head', our_head)
    print('Food', next_food)

    astar_path = list(finder.astar(our_head, next_food))
    print(astar_path)

    next_coord = astar_path[1]
    move = get_move(our_head, next_coord)

    print(move)

    # TODO: Do things with data
    directions = ['up', 'down', 'left', 'right']

    return {
        # 'move': random.choice(directions),
        'move': move,
        'taunt': 'snakehack-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
