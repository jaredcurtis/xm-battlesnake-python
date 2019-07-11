import bottle
import os
import random
import json
import sys


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']


    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': 'Get your neck chopped!',
        'head_url': head_url,
        'name': 'NinjaGaiden Snake'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
    return {
        'move': findNextMove(data),
        'taunt': 'Come get some!'
    }

def findNextMove(data):
    move = findHead(data)
    if move is None:
        return findFood(data, None)
    else:
        return move

def getSnake(gameState, id):
   for snake in gameState["snakes"]:
       if snake["id"] == id :
        return snake

def getOtherSnakeHeads(gameState, id):
   snakeHeads = []
   for snake in gameState["snakes"]:
       if snake["id"] != id :
           snakeHeads.append(snake["coords"][0])
   return snakeHeads

def findHead(gameState):
  mySnake = getSnake(gameState, gameState["you"])
  head = mySnake["coords"][0]
  snakeHeads = getOtherSnakeHeads(gameState, gameState["you"])
  if isSnakeHead(gameState, "left", head, snakeHeads):
    return "left"
  if isSnakeHead(gameState, "right", head, snakeHeads):
    return "right"
  if isSnakeHead(gameState, "up", head, snakeHeads):
    return "up"
  if isSnakeHead(gameState, "down", head, snakeHeads):
    return "down"
  else:
    return None

def isSnakeHead(gameState, move, head, snakeHeads):
  nextCoord = transformMove(move, head)
  if nextCoord in snakeHeads:
    return True
  else:
    return False

def findFood(gameState, invalidMoves):
  if invalidMoves is None:
        invalidMoves = []
  mySnake = getSnake(gameState, gameState["you"])
  head = mySnake["coords"][0]
  move = None
  if gameState["food"][0][0] < head[0] and isValidMove(gameState, "left", head):
        move = "left"
        invalidMoves.append("left")

  if gameState["food"][0][0] > head[0] and isValidMove(gameState, "right", head):
        move = "right"
        invalidMoves.append("right")

  if gameState["food"][0][1] < head[1] and isValidMove(gameState, "up", head):
        move = "up"
        invalidMoves.append("up")

  if gameState["food"][0][1] > head[1] and isValidMove(gameState, "down", head):
        move = "down"
        invalidMoves.append("down")

  if move is None:
      move = pickNextMove(gameState, invalidMoves, head)

  print ("chosen move ", move)
  sys.stdout.flush()
  return move

def pickNextMove(gameState, invalidMoves, head):
  if "left" not in invalidMoves:
      if isValidMove(gameState, "left", head):
          return "left"
  if "right" not in invalidMoves:
      if isValidMove(gameState, "right", head):
          return "right"
  if "up" not in invalidMoves:
      if isValidMove(gameState, "up", head):
          return "up"
  return "down"

def transformMove(move, head):
  if move == "left":
      return [head[0] - 1, head[1]]
  if move == "right":
      return [head[0] + 1, head[1]]
  if move == "up":
      return [head[0], head[1] - 1]
  if move == "down":
      return [head[0], head[1] + 1]

def isValidMove(gameState, move, head):
  return isNotCollidingSnake(gameState, move, head) and isNotCollidingWall(gameState, move, head)

def isNotCollidingSnake(gameState, move, head):
  realMove = transformMove(move, head)
  isValid = True
  for snake in gameState["snakes"]:
        for coord in snake["coords"]:
                if coord[0] == realMove[0] and coord[1] == realMove[1]:
                    isValid = False
  print ("checking snake collision ",move, realMove[0], realMove[1], isValid)
  sys.stdout.flush()
  return isValid

def isNotCollidingWall(gameState, move, head):
  realMove = transformMove(move, head)
  isValid = True
  if realMove[0] >= gameState["height"] or realMove[0] < 0:
      isValid = False
  if realMove[1] >= gameState["width"] or realMove[1] < 0:
      isValid = False
  print ("checking walls ", realMove[0], realMove[1], isValid)
  return isValid

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
