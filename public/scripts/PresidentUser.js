
let socket = null;

joinedGame = false
joinedWaitingRoom = false
playerId = undefined
hand = []
cardsOnTable = []
isTurn = false;
oponentHands = {}

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
        socket.on("promptPlay", promptPlay);
        socket.on("newPlay", newPlayReceived);
        socket.on("gameFinished", gameFinished);
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
        playerId = numPlayers
        let gameDiv = document.getElementById("gameDiv");
        while(gameDiv.children.length > 0){
            gameDiv.removeChild(gameDiv.firstChild)
        }
        playersString = document.createElement("li");
        playersString.id = "waitingLi";
        playersString.innerHTML = "Waiting for other players... (" + numPlayers + "/6)";
        gameDiv.appendChild(playersString)
        button = document.createElement("button");
        button.classList.add("button1");
        button.appendChild(document.createTextNode("Start Game"))
        button.onclick = startTheGame
        gameDiv.appendChild(button)
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


function cardSelected(){
    if(this.classList.contains("active")){
        this.classList.remove("active");
    }else if(this.classList.contains("disabled") == false){
        this.classList.add("active");
    }
}

function drawHand(){
				//	<button class="card">
				//		<img class="card" src="img/playingCards/spades_3.svg"></img>
				//	</button>

    cardPath = "img/playingCards/"
    divHand = document.getElementById("divHand");
    left = 0;
    while(divHand.children.length > 0){
        divHand.removeChild(divHand.firstChild);
    }
    for(let i=0;i<hand.length;i++){
        card = ""
        cardNames = {'14' : 'joker_black', '1': 'spades_ace', '11': 'spades_jack', '12': 'spades_queen', '13': 'spades_king'}
        if(hand[i] in cardNames){
            card = cardNames[hand[i]] +  ".svg"
        }else{
            card = "spades_" + hand[i] + ".svg"
        }
        iCard = document.createElement("img");
        iCard.classList.add("card");
        iCard.src = cardPath + card;
        iCard.style.left= left + "px";
        iCard.onclick = cardSelected;
        iCard.cardValue = hand[i];
        left += 20;

        
        divHand.appendChild(iCard);

    }
}

function clearTable(){
    divTable = document.getElementById("divTable");
    left = 0;
    while(divTable.children.length > 0){
        divTable.removeChild(divTable.firstChild);
    }
}

function addCardsToTable(cardsToAdd){
    cardPath = "img/playingCards/"

    console.log("Drawing cards on table: " + cardsToAdd);

    clearTable()


    let left = 10;
    for(let i=0;i<cardsToAdd.length;i++){
        card = ""
        cardNames = {'14' : 'joker_black', '1': 'spades_ace', '11': 'spades_jack', '12': 'spades_queen', '13': 'spades_king'}
        if(cardsToAdd[i] in cardNames){
            card = cardNames[cardsToAdd[i]] +  ".svg"
        }else{
            card = "spades_" + cardsToAdd[i] + ".svg"
        }
        iCard = document.createElement("img");
        iCard.classList.add("card");
        iCard.classList.add("display");
        iCard.src = cardPath + card;
        iCard.style.left= left + "px";
        iCard.onclick = cardSelected;
        iCard.cardValue = cardsToAdd[i];
        iCard.style.transform = "rotate(-4deg);"
        left += 20;

        
        divTable.appendChild(iCard);
    }

}

function disableHand(){
    divHand = document.getElementById("divHand");
    for(let i=0;i<divHand.children.length;i++){
        let child = divHand.children[i];
        if(child.classList.contains("active")){
            child.classList.remove("active");
        }
        
        child.classList.add("disabled");
    }
}

function enableCards(){
    divHand = document.getElementById("divHand");
    for(let i=0;i<divHand.children.length;i++){
        let child = divHand.children[i]
        if(child.classList.contains("disabled")){
            child.classList.remove("disabled");
        }
    }

}

function initializeOponentHands(){

    gameDiv = document.getElementById("gameDiv")
    for(let i=2;i<7;i++){
        opStatus = document.createElement("p3");
        opStatus.id = "opStatus" + i;
        opStatus.style.height="1.8em";
        opStatus.style.margin=0;
        opStatus.style.padding=0;
        divOpSeat = document.createElement("div");
        
        divOpSeat.append(opStatus);
        //divOpSeat.classList.add("oponentHand");
        divOpSeat.classList.add("seat" + i);
        divOpHand = document.createElement("div");
        divOpHand.id="opSeat" + i;
        divOpHand.classList.add("oponentHand");
        divOpSeat.append(divOpHand);
        
        gameDiv.appendChild(divOpSeat);
        drawOponentCards(i)
    }

}

function getSeat(oponentId){
    seat = (oponentId-playerId);
    if(seat <= 0){
        seat = 6 + seat;
    }
    seat = seat + 1;
    return seat
}

function drawOponentCards(oponentId){
    cardPath = "img/playingCards/"

    // Loop through each oponent.
    console.log("Drawing cards for oponent: " + oponentId + " num cards: " + oponentId["numCards"]);
    oponentObj = oponentHands[oponentId];
    let divOpSeat = document.getElementById("opSeat" + oponentObj["seat"]);
    let opSteat = document.getElementById("opStatus" + oponentObj["seat"]);
    opSteat.innerHTML = " "
    //console.log("Oponent(" + oponentId + ") Getting the seat: " + oponentObj["seat"])

    while(divOpSeat.children.length > 0){
        divOpSeat.removeChild(divOpSeat.firstChild);
    }

    left = 0;
    for(let i=0;i<oponentObj["numCards"];i++){
        card = "red.svg"
        iCard = document.createElement("img");
        iCard.classList.add("oponentCard");
        iCard.src = cardPath + card;
        iCard.style.left= left + "px";
        left += 10;


        divOpSeat.appendChild(iCard);

    }
}

function clearAllOponentStatus(){
    for(key in oponentHands){
        let opStatus = document.getElementById("opStatus" + oponentHands[key]["seat"])
        opStatus.innerHTML = "\00 ";
    }
}

function gameStarted(handObject){
    let gameDiv = document.getElementById("gameDiv");
    let titleHeader = document.getElementById("titleHeader");
    //titleHeader.innerHTML = "President (ID) " + playerId
    titleHeader.innerHTML = "President"
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
    //Initialize oponent hands
    for(let i=1; i<7;i++){
        if(i == playerId){
            continue;
        }
        seat = getSeat(i);
        oponentHands[i] = {};
        oponentHands[i]["numCards"] = handObject[i].length;
        oponentHands[i]["seat"] = seat;
        
    }
    //for(key in oponentHands){
    //   console.log("Player(" + key + ") in seat: " + oponentHands[key]["seat"]);
    //}
    initializeOponentHands();
    tableDiv = document.createElement("div");
    tableDiv.id = "divTable";
    tableDiv.classList.add("table");
    gameDiv.appendChild(tableDiv);

    hand = handObject[playerId]
    let playerArea = document.createElement("div");
    let divHand = document.createElement("div");
    divHand.id = "divHand";

    //divHand.classList.add("hand");
    playerArea.classList.add("hand");
    playerArea.appendChild(divHand);
    gameDiv.appendChild(playerArea);
    drawHand();
    disableHand();



    // This has been changed to have player statuses instead.
    //pStatus = document.createElement("p3");
    //pStatus.id = "pStatus";
    //gameDiv.appendChild(pStatus);


    // Add the button to submit the play
    button = document.createElement("button");
    button.classList.add("button1");
    button.appendChild(document.createTextNode("Submit play"));
    button.onclick = submitPlay;
    button.id = "submitButton"
    button.disabled = true;
    button.style.position="absolute"
    button.style.bottom="0px"
    button.style.left="40%;"
    playerArea.appendChild(button)
    //gameDiv.append(button)
}

function promptPlay(promptObj){
    if(promptObj["playerId"] != playerId){
        console.log("You where prompted out of order")
        //console.log("Prompting this socket for card");
        return;
    }
    if(promptObj["notFirstAttempt"]){
        //alert("Play inputted is invalid, please try again")
        //let pStatus = document.getElementById("pStatus");
        //pStatus.innerHTML = "INAVLID PLAY, please try again"
    }
    enableCards();
    let submitButton = document.getElementById("submitButton")
    submitButton.disabled=false;
    submitButton.bottom="0px;"
    submitButton.left="40%;"
    submitButton.position="absolute;"
    isTurn = true;
}


function submitPlay(){
    if(isTurn){
        let playObject={}
        playObject["playerId"] = playerId
        let divHand = document.getElementById("divHand");
        let play = []
        for(let i=0;i<divHand.children.length;i++){
            let child = divHand.children[i];
            if(child.classList.contains("active")){
                play.push(child.cardValue);
            }
        }

        play = play.toString();
        if(play.length == 0){
            play = [0].toString();
        }
        playObject["play"] = play

        socket.emit("playSelected", playObject)
        disableHand();
    }
}

function helloButton(){
    console.log("hello");
}


function newPlayReceived(playObject){
    // "playFromId": The playerId of the player who played the new cards
    // "playerName": The playername of the player who played the cards
    // "cardsPlayed": The cards played by the player
    // "cardsOnTable": The cards on table after the play
    // "validPlay": Is the play valid
    // "nextId": The id of the next person to play
    // "isBurn": is the play a burn
    // "isFinished": is the game finished
    // "passed": Did the player pass

    if(isTurn && playObject["playFromId"] == playerId){
        for(let i=0; i<playObject["cardsPlayed"].length;i++){
            for(let j=0;j<hand.length; j++){
                if(playObject["cardsPlayed"][i] == hand[j]){
                    delete hand[j];
                    break;
                }
            }

        }
        // Get the hand text box and update.
        hand = hand.filter(n=>n)
        drawHand();
        disableHand();
    }else{
        oponentId = playObject["playFromId"]
        oponentHands[oponentId]["numCards"] = oponentHands[oponentId]["numCards"] - playObject["cardsPlayed"].length  
        drawOponentCards(oponentId);    // The status text for the oponent is cleared when drawing the cards.
        clearAllOponentStatus();
        opSeatId = "opStatus" + oponentHands[oponentId]["seat"];
        opStatus = document.getElementById(opSeatId);

        if(playObject["isBurn"]){
            //opStatus.innerHTML = "Player(" + playObject["playFromId"] + ") BURNED!";
            opStatus.innerHTML = "BURN!";
        }else if(playObject["passed"]){
            //pStatus.innerHTML = "Player(" + playObject["playFromId"] + ") Passed!";
            opStatus.innerHTML = "Pass...";
        }else{
            //pStatus.innerHTML = "Player(" + playObject["playFromId"] + ") Played: " + playObject["play"];
            opStatus.innerHTML = "Played: " + playObject["play"];
        }
    }
    // Set the turn to false because it was accepted
    if(isTurn){
        isTurn = false;
    }
    // Get the table text box and update.
    if(cardsOnTable == playObject["cardsOntable"]){
        return
    }
    cardsOnTable = playObject["cardsOnTable"];
    if (cardsOnTable.length == 0 && playObject["isBurn"] == false){
        clearTable();
    }else if(playObject["burn"]){

            addCardsToTable(playObject["play"]);
            setTimeout(function() {
            clearTable();
                
            }, delayInMilliseconds);
    }else{
        addCardsToTable(cardsOnTable)

    }

    
    
}

function displayClientHello(){
    let outputDiv = document.getElementById("gameDiv");
    outputDiv.removeChild(outputDiv.firstChild);
    li = document.createElement("li");
    li.appendChild(document.createTextNode("ServerSaysHello"));
    outputDiv.appendChild(li);
}       

function gameFinished(standings){
    let gameDiv = document.getElementById("gameDiv");
    let titleHeader = document.getElementById("titleHeader");
    titleHeader.innerHTML = "Game Over!"
    while(gameDiv.children.length > 0){
        gameDiv.removeChild(gameDiv.firstChild);
    }

    let standingsItem  = document.createElement("ol");
    for(let i=0;i<6;i++){

        let positionItem = document.createElement("li");
        positionItem.appendChild(document.createTextNode(standings[i]["name"])); 
        standingsItem.appendChild(positionItem);
    }
    gameDiv.appendChild(standingsItem);
    button = document.createElement("a");
    button.classList.add("button1");
    button.appendChild(document.createTextNode("New Game"))
    button.href = "/"
    gameDiv.appendChild(button);


}



