import bottle
import os
import itertools
import random
import math
import time

import numpy as np

from bstar import PathFinder

EAT = 0x01
ATTACK = 0x02


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
        'head_type': 'sand-worm',
        'tail_type': "curled",
        'secondary_color': '#fefefe',
        'name': 'William Snakespeare'
    }


def create_matrix(width, height, our_snake, enemy_snakes):
    """
    Create two dim array with snakes
    """
    # add possible next head points to enemy snakes
    for enemy in (e for e in enemy_snakes if len(e['coords']) >= len(our_snake['coords'])):
        x, y = enemy['coords'][0]
        enemy['coords'] = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)] + enemy['coords']

    print('Our snake', our_snake)
    print('enemy snakes', enemy_snakes)

    snakes_coords = itertools.chain(*[x['coords'][0:-1] for x in [our_snake] + enemy_snakes])
    matrix = np.ones(shape=(width, height))

    center = [math.ceil(height/2), math.ceil(width/2)]
    maxcost = math.floor(calc_dist([0, 0], center))
    bordercostvalue=5
    for x, row in enumerate(matrix):
        for y, col in enumerate(row):
            matrix[y][x] += math.floor(calc_dist([y, x], center) / maxcost * bordercostvalue) + 1

    HEATMAP=2
    for x, y in snakes_coords:
        if 0 <= x < width and 0 <= y < height:
            if (x, y) in [e['coords'][-1] for e in enemy_snakes]:
                matrix[y][x] = 1
            else:
                matrix[y][x] = 0
                for j in range(HEATMAP):
                    i = j + 1
                    set_heap_map(matrix, width, height, x+1, y)
                    set_heap_map(matrix, width, height, x-1, y)
                    set_heap_map(matrix, width, height, x, y+i)
                    set_heap_map(matrix, width, height, x, y-i)
                    set_heap_map(matrix, width, height, x-i, y-i)
                    set_heap_map(matrix, width, height, x+i, y+i)
                    set_heap_map(matrix, width, height, x-i, y+i)
                    set_heap_map(matrix, width, height, x+i, y-i)
    return matrix

def set_heap_map(matrix, width, height, x, y):
    if x >= 0 and y >= 0 and x < width and y < height and matrix[y][x] != 0:
        matrix[y][x] += 1



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


def calc_dist(a, b):
    return math.fabs(a[0] - b[0])**2 + math.fabs(a[1] - b[1])**2


def get_closest_point(head, foods):
    return sorted(foods, key=lambda p: calc_dist(head, p))


def go_for_food(finder, head, foods):
    astar_path = None
    sorted_foods = get_closest_point(head, foods)
    for food in sorted_foods:
        astar_path = finder.astar(head, tuple(food))
        if astar_path is not None:
            break
    try:
        return list(astar_path)[1], 'eat'
    except TypeError:
        return None, None


def go_for_attack(finder, our_head, our_snake, enemies):
    astar_path = None
    enemy_heads = [x['coords'][0:2] for x in enemies if (len(x['coords']) + 3) < len(our_snake['coords'])]
    sorted_enemies = sorted(enemy_heads, key=lambda p: calc_dist(our_head, p[0]))

    for enemy in sorted_enemies:
        enemy_head, enemy_body = enemy
        own_head, own_body = our_snake['coords'][0:2]

        enemy_vector = (enemy_head[0] - enemy_body[0], enemy_head[1] - enemy_body[1])
        own_vector = (own_head[0] - own_body[0], own_head[1] - own_body[1])
        print("Own Vector: {}".format(own_vector))
        print("Enemy Vector: {}".format(enemy_vector))

        predicted_enemy_pos = (enemy_head[0] + enemy_vector[0], enemy_head[1] + enemy_vector[1])
        # don't attack this enemy if they look in the same direction
        distance_vector = (own_vector[0] - enemy_vector[0], own_vector[1] - enemy_vector[1])
        print("Distance Vector: {}".format(distance_vector))
        if distance_vector[0] == 0 and distance_vector[1] == 0:
            print("Enemy and Snake look in the same direction skip this enemy!!")
            break
        astar_path = finder.astar(our_head, predicted_enemy_pos)
        if astar_path is not None:
            break

    try:
        return list(astar_path)[1], 'attack!'
    except Exception:
        return None, None


@bottle.post('/move')
def move():
    starttime = time.time()
    data = bottle.request.json

    print(data)

    our_snake = next((x for x in data['snakes'] if x['id'] == data['you']), None)
    enemies = [x for x in data['snakes'] if x['id'] != data['you']]
    our_head = tuple(our_snake['coords'][0])
    print(our_snake)
    print('Head', our_head)

    # check health
    next_coord = None
    health = our_snake['health_points']
    snake_length = len(our_snake['coords'])

    matrix = create_matrix(data['width'], data['height'], our_snake, enemies)
    finder = PathFinder(data['width'], data['height'], matrix)
    print(matrix)

    if snake_length >= 10 and int(health) >= 70:
        print('Health point >= 60 -> TRY TO ATTACK')
        next_coord, taunt = go_for_attack(finder, our_head, our_snake, enemies)
        # check distance
        if next_coord is not None:
            dist = calc_dist(our_head, next_coord)
            print('enemy dist is:', dist)
            if dist > 3:
                next_coord = None

    # fallback to food
    if next_coord is None:
        next_coord, taunt = go_for_food(finder, our_head, data['food'])

    # fallback
    i = 0
    while next_coord is None and i <= 300:
        print('Do random shit as fallback')
        random_target = random.randint(0, data['width'] - 1), random.randint(0, data['height'] - 1)
        try:
            next_coord = list(finder.astar(our_head, random_target))[1]
        except Exception:
            next_coord = None
        taunt = 'do random shit'
        i += 1

    move = get_move(our_head, next_coord)
    print('move from {0} to {1} with {2}'.format(
        our_head, next_coord, move))

    print('Duration', (time.time() - starttime) / 1000.0)

    return {
        # 'move': random.choice(directions),
        'move': move,
        'taunt': taunt
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
