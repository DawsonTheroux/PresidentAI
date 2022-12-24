
let socket = null;

joinedGame = false
joinedWaitingRoom = false
playerID = undefined
hand = []
cardsOnTable = []

// Once the users name has been inputted, the socket is created
function joinGame(){
    let playerName = document.getElementById("txtPlayerName").value;
    console.log("Joining a game");
    //setupGameScreen();
    if(playerName.length > 0 || socket == null){
        joinedGame = true
        socket=io();
        socket.on("helloClient", displayClientHello);
        socket.on("gameJoined", joinWaitingRoom);
        socket.on("gamePending", gamePending);
        socket.on("gameStarted",gameStarted); 
        socket.on("newPlay", newPlayReceived);
        socket.emit("joinGame", playerName);
    }

}


/*
function setupGameScreen(){
    let gameDiv = document.getElementById("gameDiv");
    while(gameDiv.children.length > 0){
        gameDiv.removeChild(gameDiv.firstChild)
    }
    gameDiv.appendChild(document.createTextNode("Hello Socket"));
    button = document.createElement("a");
    button.classList.add("button1");
    button.appendChild(document.createTextNode("Say Hello to the server"));
    button.onclick = sayHelloToServer;
    gameDiv.appendChild(button);
}
*/

function joinWaitingRoom(numPlayers){
    if(joinedWaitingRoom){
        playersString = document.getElementById("waitingLi");
        playersString.innerHTML = "Waiting for other players... (" + numPlayers + "/6)"; 
    }else{
        playerID = numPlayers
        let gameDiv = document.getElementById("gameDiv");
        while(gameDiv.children.length > 0){
            gameDiv.removeChild(gameDiv.firstChild)
        }
        playersString = document.createElement("li");
        playersString.id = "waitingLi";
        playersString.innerHTML = "Waiting for other players... (" + numPlayers + "/6)";
        gameDiv.appendChild(playersString)
        button = document.createElement("a");
        button.classList.add("button1");
        button.appendChild(document.createTextNode("Start Game"))
        button.onclick = startTheGame
        gameDiv.append(button)
    }

}

function startTheGame(){
    socket.emit("startGame")
}

    


function sayHelloToServer(){
    socket.emit("helloServer")
}

function gamePending(){
    let gameDiv = document.getElementById("gameDiv");
    let titleHeader = document.getElementById("titleHeader");
    titleHeader.innerHTML = "Loading Game..."
    while(gameDiv.children.length > 0){
        gameDiv.removeChild(gameDiv.firstChild);
    }
}

function gameStarted(handObject){
    let gameDiv = document.getElementById("gameDiv");
    let titleHeader = document.getElementById("titleHeader");
    titleHeader.innerHTML = "President (ID) " + playerID
    while(gameDiv.children.length > 0){
        gameDiv.removeChild(gameDiv.firstChild);
    }
    /*
    for (const [key,value] of Object.entries(handObject)){
        let pDesc = document.createElement("p");
        pDesc.innerHTML = "Player(" + key + "):" + value;
        gameDiv.appendChild(pDesc);
    }
    */
    // Add the hand paragraph object
    hand = handObject[playerID]
    pDesc = document.createElement("p");
    pDesc.innerHTML = "\n\nMY HAND: " + hand;
    pDesc.id = "pHand"
    gameDiv.appendChild(pDesc);

    // Add the Table paragraph object
    pTable = document.createElement("p");
    pTable.innerHTML = "TABLE: " + cardsOnTable;
    pTable.id = "pTable"
    gameDiv.appendChild(pTable);

    // Add the text input
    textInput = document.createElement("input")
    textInput.type="textbox"
    textInput.id="inputPlay"
    gameDiv.appendChild(textInput)

    // Add the button to submit the play
    button = document.createElement("a");
    button.classList.add("button1");
    button.appendChild(document.createTextNode("Submit play"));
    button.onclick = submitPlay;
    button.disabled = false;
    gameDiv.append(button)
}

function submitPlay(){
    let playSelected = document.getElementById("inputPlay").value;
    console.log("Submitting play " + playSelected);
}

function newPlayReceived(playObject){
    // "playerID": The playerID of the player who played the new cards
    // "playerName": The playername of the player who played the cards
    // "cardsPlayed": The cards played by the player
    // "cardsOnTable": The cards on table after the play
    
    
}

function displayClientHello(){
    let outputDiv = document.getElementById("gameDiv");
    outputDiv.removeChild(outputDiv.firstChild);
    li = document.createElement("li");
    li.appendChild(document.createTextNode("ServerSaysHello"));
    outputDiv.appendChild(li);
}