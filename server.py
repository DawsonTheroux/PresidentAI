from flask import Flask, Response, request
from flask import render_template
from flask_socketio import SocketIO, send, emit
import os
from GameClass import Game


app = Flask(__name__, template_folder="public")
app.config["SECRET_KEY"] = 'ThisIsASecret?!'
socketio = SocketIO(app, logger=True, engineio_logger=True)



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
        return open(src).read()
    except IOError as exc:
        return str(exc)
    
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_resource(path):  # pragma: no cover
    mimetypes = {
        ".css": "text/css",
        ".html": "text/html",
        ".js": "application/javascript",
    }
    complete_path = os.path.join(root_dir(), path)
    ext = os.path.splitext(path)[1]
    mimetype = mimetypes.get(ext, "text/html")
    content = get_file(complete_path)
    return Response(content, mimetype=mimetype)



#--------Socket IO interaction-----------
@socketio.on('connect')
def startConnection():
    print("Received a socket connection")

@socketio.on('disconnect')
def endConnection():
    print("A player has left")

@socketio.on('joinGame')
def joinGame(playerName):  
    socketio.numPlayers += 1
    socketio.lobbyCreated = True
    socketio.players[socketio.numPlayers] = {}
    socketio.players[socketio.numPlayers]["name"] = playerName
    socketio.players[socketio.numPlayers]["socketID"] = request.sid 
    emit("gameJoined", socketio.numPlayers, broadcast = True)


@socketio.on('startGame')
def startGame():
    emit("gamePending", broadcast = True) 
    game_obj = Game(6, socketio.numPlayers)
    
    

@socketio.on('helloServer')
def helloServer():
    print("The client says hello, responding with hello")
    emit("helloClient")

if __name__ == "__main__":
    #app.run(port=8081)
    socketio.numPlayers = 0
    socketio.gameActive = False
    socketio.lobbyCreated = False
    socketio.players = {}

    socketio.run(app, port=8081, debug=True)