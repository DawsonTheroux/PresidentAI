let socket = null;

joinedGame = false          // Is the client in a game
joinedWaitingRoom = false   // Is the client in the waiting room
playerId = undefined        // What is the id of player (as seen by the gameClass)
hand = []                   // The cards in your hand
cardsOnTable = []           // The cards on the table
isTurn = false;             // Is it the clients turn
oponentHands = {}           // Object with oponent information like numcards, their seats, etc.


// Once the users name has been inputted, the socket is created
function joinGame(){
    let playerName = document.getElementById("txtPlayerName").value;

    // If the player actually inputted a name, then allow it to join a game
    if(playerName.length > 0 || socket == null){
        joinedGame = true;
        socket=io();
        //socket.on("helloClient", displayClientHello);
        socket.on("gameJoined", joinWaitingRoom);
        socket.on("gamePending", gamePending);
        socket.on("gameStarted",gameStarted); 
        socket.on("promptPlay", promptPlay);
        socket.on("newPlay", newPlayReceived);
        socket.on("gameFinished", gameFinished);
        socket.emit("joinGame", playerName);
    }
}


// Draw the waiting room HTML 
function joinWaitingRoom(numPlayers){
    if(joinedWaitingRoom){
        playersString = document.getElementById("waitingLi");
        playersString.innerHTML = "Waiting for other players... (" + numPlayers + "/6)"; 
    }else{
        playerId = numPlayers;
        let gameDiv = document.getElementById("gameDiv");

        // Clear the gamediv.
        while(gameDiv.children.length > 0){
            gameDiv.removeChild(gameDiv.firstChild)
        }

        // Draw all of the waiting room HTML in the gameDiv
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


// Emite that the game has started (onlick of waiting room button)
function startTheGame(){
    socket.emit("startGame")
}

    

//function sayHelloToServer(){
//    socket.emit("helloServer")
//}

// Show loading screen while waiting for the initial game object from the server
function gamePending(){
    let gameDiv = document.getElementById("gameDiv");
    let titleHeader = document.getElementById("titleHeader");
    titleHeader.innerHTML = "Loading Game..."
    while(gameDiv.children.length > 0){
        gameDiv.removeChild(gameDiv.firstChild);
    }
}


// When a card is selected add the "active" class so that it is translated 10px up.
function cardSelected(){
    if(this.classList.contains("active")){
        this.classList.remove("active");
    }else if(this.classList.contains("disabled") == false){
        this.classList.add("active");
    }
}


// Draw the cards using images using the global "hand" Array.
function drawHand(){
    left = 0;
    cardPath = "img/playingCards/"
    divHand = document.getElementById("divHand");

    // Remove all elements from the hand div.
    while(divHand.children.length > 0){
        divHand.removeChild(divHand.firstChild);
    }

    // Go through all the cards and draw them.
    for(let i=0;i<hand.length;i++){
        card = ""
        cardNames = {'14' : 'joker_black', '1': 'spades_ace', '11': 'spades_jack', '12': 'spades_queen', '13': 'spades_king'}

        if(hand[i] in cardNames){
            card = cardNames[hand[i]] +  ".svg"
        }else{
            card = "spades_" + hand[i] + ".svg"
        }

        // Create the HTML for the card.
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


// Remove all cards from the table div.
function clearTable(){
    divTable = document.getElementById("divTable");
    left = 0;
    while(divTable.children.length > 0){
        divTable.removeChild(divTable.firstChild);
    }
}


// Add the cards to the table that were received from the server.
function addCardsToTable(cardsToAdd){
    cardPath = "img/playingCards/"

    clearTable() // Remove old cards from the table

    let left = 10; // The amount that the cards are shifted when creating the overlap
    for(let i=0;i<cardsToAdd.length;i++){
        let card = ""
        cardNames = {'14' : 'joker_black', '1': 'spades_ace', '11': 'spades_jack', '12': 'spades_queen', '13': 'spades_king'}
        if(cardsToAdd[i] in cardNames){
            card = cardNames[cardsToAdd[i]] +  ".svg"
        }else{
            card = "spades_" + cardsToAdd[i] + ".svg"
        }

        // Create HTML for the card.
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


// Remove active class from all cards in hand and adding the disabled tag
// - The disabled tag add transparency to the cards to show that it is not the clients turn.
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


// Remove the disabled class from the hand
function enableCards(){
    divHand = document.getElementById("divHand");
    for(let i=0;i<divHand.children.length;i++){
        let child = divHand.children[i]
        if(child.classList.contains("disabled")){
            child.classList.remove("disabled");
        }
    }
}


// Initialize the display elements of the oponent hands
// - This includes the cards themselves and the status'
function initializeOponentHands(){
    gameDiv = document.getElementById("gameDiv")
    for(let i=2;i<7;i++){
        // Generate the status paragraph for the oponent
        opStatus = document.createElement("p3");
        opStatus.id = "opStatus" + i;
        opStatus.style.height="1.8em";
        opStatus.style.margin=0;
        opStatus.style.padding=0;

        // Generate the seat div for the oponent
        divOpSeat = document.createElement("div"); 
        divOpSeat.append(opStatus);
        divOpSeat.classList.add("seat" + i);

        // Generate the hand div for the oponent
        divOpHand = document.createElement("div");
        divOpHand.id="opSeat" + i;
        divOpHand.classList.add("oponentHand");
        divOpSeat.append(divOpHand);
        
        gameDiv.appendChild(divOpSeat);
        drawOponentCards(i);  // Addds the corrent number of card back images to each oponents hand div
    }
}

// Returns the seat number corresponding to certain oponent id.
function getSeat(oponentId){
    seat = (oponentId-playerId);
    if(seat <= 0){
        seat = 6 + seat;
    }
    seat = seat + 1;
    return seat
}


// Adds the card images to the oponent hand div.
function drawOponentCards(oponentId){
    let cardPath = "img/playingCards/"
    let oponentObj = oponentHands[oponentId];
    let divOpSeat = document.getElementById("opSeat" + oponentObj["seat"]);
    let opSteat = document.getElementById("opStatus" + oponentObj["seat"]);
    opSteat.innerHTML = ""

    // Clear the hand div of elements.
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


// Set all the oponents status to empty strings.
// - This is called on every new play so that only 1 player has a status at a time.
function clearAllOponentStatus(){
    for(key in oponentHands){
        let opStatus = document.getElementById("opStatus" + oponentHands[key]["seat"])
        opStatus.innerHTML = "";
    }
}


// Initialize all of the game HTML elements with the object given by the server.
function gameStarted(handObject){
    let gameDiv = document.getElementById("gameDiv");
    let titleHeader = document.getElementById("titleHeader");
    titleHeader.innerHTML = "President";

    // Clear the game div of all its HTML elements.
    while(gameDiv.children.length > 0){
        gameDiv.removeChild(gameDiv.firstChild);
    }

    //Initialize oponent hands with the info from the server.
    for(let i=1; i<7;i++){
        if(i == playerId){
            continue;
        }
        seat = getSeat(i);
        oponentHands[i] = {};
        oponentHands[i]["numCards"] = handObject[i].length;
        oponentHands[i]["seat"] = seat;
        
    }

    initializeOponentHands();  // Add all the elements to the oponent hands. 

    // Create the div that holds the Table cards.
    tableDiv = document.createElement("div");
    tableDiv.id = "divTable";
    tableDiv.classList.add("table");
    gameDiv.appendChild(tableDiv);

    // Create the div that client play area.
    hand = handObject[playerId]
    let playerArea = document.createElement("div");
    let divHand = document.createElement("div");
    divHand.id = "divHand";
    playerArea.classList.add("hand");
    playerArea.appendChild(divHand);
    gameDiv.appendChild(playerArea);

    drawHand();     // Draw the cards in the client hand
    disableHand();  // Start the hand as disabled. The hand will be enabled when its the players turn.

    // Add the submit button to the Player area 
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
}


// Prompt the client for the play.
//  - If it is not the clients turn, this will be ignored.
function promptPlay(promptObj){
    if(promptObj["playerId"] != playerId){
        console.log("You where prompted out of order")
        return;
    }
    
    // If the player is prompted with the "notFirstAttempt" flag,
    // their last play was invalid and they should try again.
    if(promptObj["notFirstAttempt"]){
        alert("Play inputted is invalid, please try again")
    }

    enableCards();

    let submitButton = document.getElementById("submitButton")
    submitButton.disabled=false;
    submitButton.bottom="0px;"
    submitButton.left="40%;"
    submitButton.position="absolute;"
    isTurn = true;
}


// Submit the play selected by the client by emitting the "playSelected" event.
// NOTE: This only works when it is the clients turn.
function submitPlay(){
    if(isTurn){
        let playObject={}
        let divHand = document.getElementById("divHand");
        let play = []
        playObject["playerId"] = playerId

        // Create the array of cards to play for the playObject.
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

// I don't think this is necessary anymore
//function helloButton(){
//    console.log("hello");
//}

// When a new play is received from the server, update the client with the information.
function newPlayReceived(playObject){
    // playObject info:
    //   -"playFromId": The playerId of the player who played the new cards
    //   -"playerName": The playername of the player who played the cards
    //   -"cardsPlayed": The cards played by the player
    //   -"cardsOnTable": The cards on table after the play
    //   -"validPlay": Is the play valid
    //   -"nextId": The id of the next person to play
    //   -"isBurn": is the play a burn
    //   -"isFinished": is the game finished
    //   -"passed": Did the player pass

    // If it is the clients turn, remove the cards from hand and draw the new hand.
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
        let oponentId = playObject["playFromId"]
        oponentHands[oponentId]["numCards"] = oponentHands[oponentId]["numCards"] - playObject["cardsPlayed"].length  

        drawOponentCards(oponentId);    

        // Clear all oponent statuses and update the status of the player who just played
        clearAllOponentStatus();
        opSeatId = "opStatus" + oponentHands[oponentId]["seat"];
        opStatus = document.getElementById(opSeatId);
        if(playObject["isBurn"]){
            opStatus.innerHTML = "BURN!";
        }else if(playObject["passed"]){
            opStatus.innerHTML = "Pass...";
        }else{
            opStatus.innerHTML = "Played: " + playObject["play"];
        }
    }

    // isTurn is set to false because if it was the clients turn,
    // and the new turn is the play it sent, then the play was valid
    // and it is no longer the clients turn
    if(isTurn){
        isTurn = false;
    }

    // If the cards on the table did not change, do not update the cards on the table.
    if(cardsOnTable == playObject["cardsOntable"]){
        return
    }

    // Update the cards on the table.
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



// I don't think I need this anymore.
//function displayClientHello(){
//    let outputDiv = document.getElementById("gameDiv");
//    outputDiv.removeChild(outputDiv.firstChild);
//    li = document.createElement("li");
//    li.appendChild(document.createTextNode("ServerSaysHello"));
//    outputDiv.appendChild(li);
//}       

// When a game is finished, show the finish screen
function gameFinished(standings){
    let gameDiv = document.getElementById("gameDiv");
    let titleHeader = document.getElementById("titleHeader");
    titleHeader.innerHTML = "Game Over!"
    
    // Clear the game div. (Should move this to function.)
    while(gameDiv.children.length > 0){
        gameDiv.removeChild(gameDiv.firstChild);
    }

    // Create the standings ordered list.
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



