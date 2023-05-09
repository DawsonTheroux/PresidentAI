var canvas;
var barsArray = [];							// Array of Bar properties
var headerHeight = 125;						// Height of header
var numBars;								// The number of bars in the header
var sorted;									// Is the barArr sorted
var barColor = '#B2D2A4';					// The colour of the bars
var selectedBarColor = '#0b1f19'//'rgb(11, 31, 25)';	// The selected color of the bars
var bColor = "#122620"; 					// Background Color

// Sleep function that stops the execution of the program for miliseconds.
function sleep(ms){
	return new Promise(resolve => setTimeout(resolve,ms));
}

async function setup(){
	// Window setup
	canvas = createCanvas(windowWidth, headerHeight);
	canvas.position(0,0);
	frameRate(10);
	
	// Animation setup
	numBars = Math.ceil(windowWidth/27);
	barsArray = await createBars();
	bubbleSort(await slowShuffleBars(barsArray));
}

function draw(){
	background(bColor);
	drawBars(barsArray);
	textSize(50);
}

function windowResized(){
	setup();
}

// bar class.
function Bar(v, i){
	
	this.x = i * windowWidth / numBars;			// bar x pos.
	this.y = 0;									// bar y pos.
	this.value = v;								// bar value (what is being sorted).
	this.selected = false;						// selected?
	this.width = windowWidth/numBars - 5;		// bar width.
	this.height = v * (headerHeight / numBars);	// bar height.
	
	// Function that draws the bar.
	this.show = function(){
		if(this.selected){
			// fill(190,47,41);
			fill(selectedBarColor);
		}else{
			fill(barColor);
		}
		rect(this.x, this.y, this.width, this.height);
	}
	
	// Function to change the location of the bar.
	this.changeIndex = function(index){
		this.x = index * windowWidth / numBars;
	}
}

function createBars(){
	var retArr = [];
	for(var i=0; i<numBars; ++i){
		retArr[i] = new Bar(i+1, i);
	}
	return retArr;
}

async function swapBars(barArr,i1,i2){

	var temp = barArr[i1];
	barArr[i1] = barArr[i2];
	barArr[i2] = temp;
	barArr[i1].changeIndex(i1);
	barArr[i2].changeIndex(i2);
	await sleep(100);
	return barArr;
}

// Swaps bars without speeping.
function fastSwapBars(barArr,i1,i2){

	var temp = barArr[i1];
	barArr[i1] = barArr[i2];
	barArr[i2] = temp;
	barArr[i1].changeIndex(i1);
	barArr[i2].changeIndex(i2);;
	return barArr;
}


async function slowShuffleBars(barArr){
	var index = barArr.length;
	var randomNum;
	var tempBar;
	
	while(index !== 0){
		randomNum = Math.floor(Math.random() * index);
		index--;
		selectedBar = barArr[index];
		selectedBar.selected = true;
		barArr = await swapBars(barArr,index,randomNum);
		selectedBar.selected = false;
	}
	return barArr;
}

function drawBars(barArr){
	for(var i=0; i< barArr.length; ++i){
		barArr[i].show();
	}
}

async function bubbleSort(barArr){
	var sorted = false;
	var temp;
	
	while(!sorted){
		sorted = true;
		for(var i=0; i<barArr.length - 1; ++i){
			barArr[i].selected = true;
			barArr[i+1].selected = true;
			if(barArr[i].value > barArr[i+1].value){
				sorted = false;
				await swapBars(barArr, i, i+1);
			}else{
				await swapBars(barArr,i,i);
			}
			barArr[i].selected = false;
			barArr[i+1].selected = false;
			
		}
	}
	return barArr;
}

function checkSorted(barArr){
	for(var i=0;i<barArr.length - 1; ++i){
		if(barArr[i] > barArr[i+1]){
			return false;
		}
	}
	return true;
}
