import bottle
import os
import random
import itertools

import numpy as np

from astar import astar


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


def create_matrix(width, height, snakes_coords):
    """
    Create two dim array with snakes
    """
    matrix = np.zeros(shape=(width, height))
    for x, y in snakes_coords:
        matrix[y - 1, x] = 1
    return matrix

def fix_y_coord(point):
    return (point[0], point[1] - 1)


def get_move(start, end):
    # check single move
    if start[0] == end[0]:
        if end[1] > start[1]:
            return 'right'
        else:
            return 'left'

    if start[1] == end[1]:
        if end[0] > start[1]:
            return 'down'
        else:
            return 'up'

    # double stage move


@bottle.post('/move')
def move():
    data = bottle.request.json

    print(data)

    snakes_coords = itertools.chain(*[x['coords'] for x in data['snakes']])
    matrix = create_matrix(data['width'], data['height'], snakes_coords)
    print(matrix)

    our_snake = next((x for x in data['snakes'] if x['id'] == data['you']), None)
    our_head = reversed(fix_y_coord(our_snake['coords'][0]))
    print(our_snake)

    next_food = reversed(fix_y_coord(data['food'][0]))

    astar_path = astar(matrix, tuple(our_head), tuple(next_food))
    print(astar_path)
    next_coord = astar_path[-1]
    move = get_move(our_head, next_coord)

    # TODO: Do things with data
    directions = ['up', 'down', 'left', 'right']

    return {
        # 'move': random.choice(directions),
        'move': 'up',
        'taunt': 'snakehack-python!'
    }


# def create_matrix(width, height,


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
