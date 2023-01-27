from flask import Flask, Response, request
from flask import render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import os
import time
import eventlet
from GameClass import Game
import uuid


app = Flask(__name__, template_folder="public")
app.config["SECRET_KEY"] = 'ThisIsASecret?!'
eventlet.monkey_patch()  # This allows socket emits happen in the middle of functions
socketio = SocketIO(app, logger=False, engineio_logger=False, manage_session=True)
socketio.gamesInfo = {}
socketio.playerGameMap = {}


@app.route("/", methods=["GET"])
def getIndex():
    return render_template("views/pages/index.html")


def root_dir(): # Return files that lie in the public directory 
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "public/"))


def get_file(filename):  # Return files that lie in the public directory 
    try:
        src = os.path.join(root_dir(), filename)
        return open(src, encoding="utf8").read()

    except IOError as exc:
        return str(exc)
    

# default route for requests to files in the public directory
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_resource(path):  # pragma: no cover
    mimetypes = {
        ".css": "text/css",
        ".html": "text/html",
        ".js": "application/javascript",
        ".png": "image/svg+xml",
        ".svg": "image/svg+xml"
    }
    complete_path = os.path.join(root_dir(), path)
    ext = os.path.splitext(path)[1]
    mimetype = mimetypes.get(ext, "text/html")
    content = get_file(complete_path)
    return Response(content, mimetype=mimetype)


#--------Socket IO interaction-----------
@socketio.on('disconnect')
def endConnection():
    requestSid = request.sid
    del socketio.gamesInfo[requestSid]
    # TODO: Delete game instance for the player who left.


# When a player joins a game, create the game object and initialize variables
@socketio.on('joinGame')
def joinGame(playerName):  

    sid=request.sid
    foundAvailableGame = False
    for gameId in socketio.gamesInfo.keys():
        if socketio.gamesInfo[gameId]["isStarted"] == False:
            foundAvailableGame = True
            socketio.playerGameMap[sid] = gameId
            join_room(gameId)
            socketio.gamesInfo[gameId]["numPlayers"] += 1
            socketio.gamesInfo[gameId]["players"][sid] = {}
            socketio.gamesInfo[gameId]["players"][sid]["name"] = playerName
            socketio.gamesInfo[gameId]["players"][sid]["id"] = socketio.gamesInfo[gameId]["numPlayers"]
            emit("gameJoined", socketio.gamesInfo[gameId]["numPlayers"], room=gameId)
            return

    # If a game has not been found then generate a new game.
    gameId = uuid.uuid4()
    join_room(gameId)
    print(f"generated UUID {gameId}")
    socketio.playerGameMap[sid] = gameId 
    socketio.gamesInfo[gameId] = {}
    socketio.gamesInfo[gameId]["isStarted"] = False
    socketio.gamesInfo[gameId]["numPlayers"] = 1
    socketio.gamesInfo[gameId]["players"] = {}
    socketio.gamesInfo[gameId]["players"][sid] = {}
    socketio.gamesInfo[gameId]["players"][sid]["name"] = playerName
    socketio.gamesInfo[gameId]["players"][sid]["id"] = 1
    emit("gameJoined", socketio.gamesInfo[gameId]["numPlayers"], room=gameId)
    


@socketio.on('startGame')
def startGame():
    requestSid = request.sid
    gameId = socketio.playerGameMap[requestSid]
    firstPlayObj = {}
    firstPlayObj["playFromId"] = -1
    firstPlayObj["playerName"] = None
    firstPlayObj["cardsPlayed"] = [-1]
    firstPlayObj["cardsOnTable"] = []
    firstPlayObj["nextId"] = 1
    firstPlayObj["isBurn"] = False
    firstPlayObj["isFinished"] = False
    firstPlayObj["passed"] = False

    emit("gamePending") # removed broadcast from here
    socketio.gamesInfo[gameId]["isStarted"] = True
    # Deal cards and initilize variables
    game_obj = Game(6, numHumanPlayers=socketio.gamesInfo[gameId]["numPlayers"], socketio=socketio)

    # Get the init object
    initObject = game_obj.initSocketGame()
    socketio.gamesInfo[gameId]["gameObj"] = game_obj

    print(f"initObject {initObject}")
    emit("gameStarted", initObject, room = gameId)
    emit("promptPlay", {"playerId" : 1, "notFirstAttempt": False}, room=gameId) # Prompt the first player for their lead


# When a client emits that they have selected a play
@socketio.on("playSelected")
def receivePlay(playObj):

    # Recieve playObj:
    #   - "playerId": The id who submitted the play
    #   - "play": The play that was submitted
    requestSid = request.sid
    gameId = socketio.playerGameMap[requestSid]

    if playObj["playerId"] != socketio.gamesInfo[gameId]["gameObj"].turnId:
        print("**An invalid player tried to submit a turn")
        return

    # StepObj from socketGameStep()
    #   "validPlay": Bool if the play was valid or not.
    #   "playFromId": the id who played last
    #   "cardsPlayed": Cards played by the last player
    #   "NextId": The id of the next player to play
    stepObj = socketio.gamesInfo[gameId]["gameObj"].socketGameStep(playObj, True)

    # reprompt the player and return if the play selected was invalid
    if stepObj["validPlay"] == False:
        print(f"+=+=+=+INVALID PLAY: Refrompting {playObj['playerId']}")
        emit("promptPlay", {"playerId": playObj["playerId" ], "notFirstAttempt": True}, room=gameId)
        return
    
    emit("newPlay", stepObj, room=gameId)

    # This will need to be updated for multiplayer
    isSocketPlayer = stepObj["nextId"] <= socketio.gamesInfo[gameId]["numPlayers"]

    if stepObj["isFinished"]:
        gameFinished()
        return

    while not isSocketPlayer:
        stepObj = socketio.gamesInfo[gameId]["gameObj"].socketGameStep(None, False)
        emit("newPlay", stepObj, room=gameId)
        time.sleep(0.75)

        if stepObj["isFinished"]:
            gameFinished()
            return

        # This will need to be updated for multiplayer
        isSocketPlayer = stepObj["nextId"] <= socketio.gamesInfo[gameId]["numPlayers"]
        #isSocketPlayer = stepObj["nextId"] == 1

    emit("promptPlay", {"playerId" : stepObj["nextId"], "notFirstAttempt": False}, room=gameId)


# When a game finishes:
# - Display the standins
# - Delete variables that are no longer used.
def gameFinished():
    requestSid = request.sid
    gameId = socketio.playerGameMap[requestSid]
    positions = ["President", "Vice President", "Neutral 1", "Neutral 2", "Vice Ass", "Ass"]

    results, autoAssIds = socketio.gamesInfo[gameId]["gameObj"].getResults()

    standings = []
    for i, player in enumerate(results):
        result = {}
        result["id"] = player.id

        if player.id <= socketio.gamesInfo[gameId]["numPlayers"]: # This will need to be changed for multiplayer
            result["name"] = socketio.gamesInfo[gameId]["players"][requestSid]["name"]
        else:
            result["name"] = f"AI ({player.id})"

        result["position"] = positions[i]
        standings.append(result)
    
    emit("gameFinished", standings, room=gameId)
    
    del socketio.gamesInfo[gameId]
    
# I don't think this is necessary anymore.
#@socketio.on('helloServer')
#def helloServer():
#    print("The client says hello, responding with hello")
#    emit("helloClient")

def createApp(): 
    ssl_cert = "/etc/letsencrypt/live/dawsontheroux.ca/fullchain.pem"
    ssl_cert_key = "/etc/letsencrypt/live/dawsontheroux.ca/privkey.pem"
    context = (ssl_cert, ssl_cert_key)

    # Uncomment for HTTPS
    #socketio.run(app, port=8081, debug=True, certfile=ssl_cert, keyfile=ssl_cert_key) 

    # Uncomment for HTTP
    socketio.run(app, port=8081, debug=True) 


if __name__ == "__main__":
    createApp()
