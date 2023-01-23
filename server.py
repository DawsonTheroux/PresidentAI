from flask import Flask, Response, request
from flask import render_template
from flask_socketio import SocketIO, send, emit
import os
import time
import eventlet
from GameClass import Game


app = Flask(__name__, template_folder="public")
app.config["SECRET_KEY"] = 'ThisIsASecret?!'
eventlet.monkey_patch() 
socketio = SocketIO(app, logger=False, engineio_logger=False, manage_session=True)
#socketio.numPlayers = 0
#socketio.gameActive = False
#socketio.lobbyCreated = False
#socketio.players = {}



@app.route("/", methods=["GET"])
def getIndex():
    return render_template("views/pages/index.html")


'''
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    fileEnding = path.split('.')[-1]
    if 
    return render_template(path)
'''
def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "public/"))

def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src, encoding="utf8").read()
    except IOError as exc:
        return str(exc)
    
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
@socketio.on('connect')
def startConnection(sid):

    print("Received a socket connection")

@socketio.on('disconnect')
def endConnection():
    requestSid = request.sid
    del socketio.gamesInfo[requestSid]
    print("A player has left")

@socketio.on('joinGame')
def joinGame(playerName):  
    sid=request.sid
    print(f"id: {sid}")
    print(f"player name: {playerName}")
    socketio.gamesInfo = {}
    socketio.gamesInfo[sid] = {}
    socketio.gamesInfo[sid]["numPlayers"] = 1
    #socketio.numPlayers += 1
    socketio.gamesInfo[sid]["numPlayers"] = 1
    #socketio.lobbyCreated = True
    socketio.gamesInfo[sid]["players"] = {}
    socketio.gamesInfo[sid]["players"][sid] = {}
    #socketio.players[socketio.numPlayers] = {}
    #socketio.players[socketio.numPlayers]["name"] = playerName
    socketio.gamesInfo[sid]["players"][sid]["name"] = playerName
    socketio.gamesInfo[sid]["players"][sid]["id"] = 1
    #socketio.players[socketio.numPlayers]["socketID"] = request.sid 
    emit("gameJoined", socketio.gamesInfo[sid]["numPlayers"], broadcast = True)


@socketio.on('startGame')
def startGame():
    requestSid = request.sid
    firstPlayObj = {}
    firstPlayObj["playFromId"] = -1
    firstPlayObj["playerName"] = None
    firstPlayObj["cardsPlayed"] = [-1]
    firstPlayObj["cardsOnTable"] = []
    firstPlayObj["nextId"] = 1
    firstPlayObj["isBurn"] = False
    firstPlayObj["isFinished"] = False
    firstPlayObj["passed"] = False

    emit("gamePending", broadcast = True) 
    
    # Deal cards and initilize variables
    #game_obj = Game(6, numHumanPlayers=socketio.numPlayers, socketio=socketio)
    game_obj = Game(6, numHumanPlayers=socketio.gamesInfo[requestSid]["numPlayers"], socketio=socketio)

    # Get the init object
    initObject = game_obj.initSocketGame()
    socketio.gamesInfo[requestSid]["gameObj"] = game_obj
    #socketio.gameObj = game_obj
    emit("gameStarted", initObject)
    #emit("newPlay", firstPlayObj)
    emit("promptPlay", {"playerId" : 1, "notFirstAttempt": False})

@socketio.on("playSelected")
def receivePlay(playObj):
    requestSid = request.sid
    # Recieve playObj:
    #   - "playerId": The id who submitted the play
    #   - "play": The play that was submitted
    #if playObj["playerId"] != socketio.gameObj.turnId:
    if playObj["playerId"] != socketio.gamesInfo[requestSid]["gameObj"].turnId:
        print("**An invalid player tried to submit a turn")
        return
    # StepObj from socketGameStep()
    #   "validPlay": Bool if the play was valid or not.
    #   "playFromId": the id who played last
    #   "cardsPlayed": Cards played by the last player
    #   "NextId": The id of the next player to play
    #stepObj = socketio.gameObj.socketGameStep(playObj, True)
    stepObj = socketio.gamesInfo[requestSid]["gameObj"].socketGameStep(playObj, True)

    # return if the play selected was invalid
    if stepObj["validPlay"] == False:
        print(f"+=+=+=+INVALID PLAY: Refrompting {playObj['playerId']}")
        emit("promptPlay", {"playerId": playObj["playerId" ], "notFirstAttempt": True})
        return
    
    print(f"emitting New play {stepObj}")
    emit("newPlay", stepObj, broadcast=True)

    #isSocketPlayer = stepObj["nextId"] in socketio.players
    #isSocketPlayer = stepObj["nextId"] in socketio.gamesInfo[requestSid]["players"].keys()
    isSocketPlayer = stepObj["nextId"] == 1

    if stepObj["isFinished"]:
        gameFinished()
        return

    while not isSocketPlayer:
        #stepObj = socketio.gameObj.socketGameStep(None, False)
        stepObj = socketio.gamesInfo[requestSid]["gameObj"].socketGameStep(None, False)
        print(f"emitting New play {stepObj}")
        emit("newPlay", stepObj, broadcast=True)
        time.sleep(0.75)
        if stepObj["isFinished"]:
            gameFinished()
            return
        #isSocketPlayer = stepObj["nextId"] in socketio.gamesInfo[requestSid]["players"].keys()
        isSocketPlayer = stepObj["nextId"] == 1
    emit("promptPlay", {"playerId" : stepObj["nextId"], "notFirstAttempt": False})

def gameFinished():
    requestSid = request.sid
    positions = ["President", "Vice President", "Neutral 1", "Neutral 2", "Vice Ass", "Ass"]

    #results, autoAssIds = socketio.gameObj.getResults()
    results, autoAssIds = socketio.gamesInfo[requestSid]["gameObj"].getResults()

    standings = []
    for i, player in enumerate(results):
        result = {}
        result["id"] = player.id
        #if player.id in socketio.players:
        #if player.id in socketio.gamesInfo["players"][requestSid]["id"]:
        if player.id == 1: 
            #result["name"] = socketio.players[player.id]["name"]
            result["name"] = socketio.gamesInfo[requestSid]["players"][requestSid]["name"]
        else:
            result["name"] = f"AI ({player.id})"
        result["position"] = positions[i]
        standings.append(result)
    
    emit("gameFinished", standings, broadcast = True)
    #for playerId in socketio.gamesInfo["players"].keys():
        #socketio.disconnect(playerId)
    
    del socketio.gamesInfo[requestSid]


    
    # Check to see if the next player is a bot or not.

    


    # Call the next step function.
    # If the step function returns that the play is invalid, re-emit prompt play
    # else: emit the next play



    
    

@socketio.on('helloServer')
def helloServer():
    print("The client says hello, responding with hello")
    emit("helloClient")

def createApp():
    
    ssl_cert = "/etc/letsencrypt/live/dawsontheroux.ca/fullchain.pem"
    ssl_cert_key = "/etc/letsencrypt/live/dawsontheroux.ca/privkey.pem"
    context = (ssl_cert, ssl_cert_key)
    socketio.run(app, port=8081, debug=True, certfile=ssl_cert, keyfile=ssl_cert_key) 
    #socketio.run(app, port=8081, debug=True) 
    #return socketio


if __name__ == "__main__":
    createApp()

    #app.run(port=8081)
    #socketio.numPlayers = 0
    #socketio.gameActive = False
    #socketio.lobbyCreated = False
    #socketio.players = {}

    #socketio.run(app, port=8081, debug=True)
