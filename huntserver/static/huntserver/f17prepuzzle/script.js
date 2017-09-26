var consoleSpan;
var commandQueue = [];
var printing = false;
var prelink = "";
var fastMode = false;
var eventName = "EVENT NAME HERE";
function printText(){
	var lcharDelay = 30;
	var charDelay = 10;
	var dotDelay = 300;
	var br = " <br />";
	
	consoleSpan.innerHTML = "";
	var line1 = ("CONNECTING TO ENRICHMENT CENTER");
	var line2 = ("LOADING EVENT DETAILS");
	var line3 = ("----- " + eventName + " -----");
	var line3lnk = '----- <a href="prepuzzle.html">' + eventName + '</a> -----'
	var line4 = ("DATE: Oct 14");
	var line5 = ("TIME: 11:30 AM - 8:00 PM");
	var line6 = ("LOCATION: Porter 100");
	var line7 = ("DESCRIPTION: Solve Puzzles, Help Science!");
	var line8 = ("Dinner will be provided. Successful test " + 
		"subjects will be served cake.");
	var regLink = '<a href="https://puzzlehunt.club.cc.cmu.edu/registration/">REGISTER<a/>';
	printString(line1, lcharDelay);
	printString("...", dotDelay);
	addLambda(function(){consoleSpan.innerHTML = line1 + br;}, 0);
	printString(line2, lcharDelay);
	printString("...", dotDelay);
	addLambda(function(){consoleSpan.innerHTML += br + br;}, 0);
	addLambda(function(){prelink = consoleSpan.innerHTML}, 0);
	printString(line3 + "\n", charDelay);
	addLambda(function(){consoleSpan.innerHTML = prelink + line3lnk + br + br;}, 0);
	printString(line4 + "\n\n", charDelay);
	printString(line5 + "\n\n", charDelay);
	printString(line6 + "\n\n", charDelay);
	printString(line7 + "\n\n", charDelay);
	printString(line8 + "\n\n", charDelay);
	addLambda(function(){prelink = consoleSpan.innerHTML}, 0);
	printString("REGISTER", charDelay);
	addLambda(function(){consoleSpan.innerHTML = prelink + regLink;}, 0);
	addLambda(function(){setCookie("fastMode","true",10);}, 0);
}

function esc(str){
	str = str.split("<").join("&lt;");
	str = str.split(">").join("&gt;");
	return str;
}


function onLoad(){
	fastMode = getCookie("fastMode") == "true";
	ans = getCookie("answer");
	if (ans.length >= 16) {
		eventName = ans.substring(0, 7) + " " + ans.substring(7, 14) + " " + ans.substring(14);
	}
	consoleSpan = document.getElementById("consoleSpan");
	printText();
}

function sleep(delay) {
	if (fastMode) {
		return;
	}
	var cmd = {};
	cmd.delay = delay;
	addCommand(cmd);
}

function printString(str, delay) {
	if (fastMode) {
		str = str.split("<").join("&lt;");
		str = str.split(">").join("&gt;");
		str = str.split("\n").join(" <br />");
		consoleSpan.innerHTML += str;
		return;
	}
	parts = str.split("");
	parts.forEach(function (part) {
		var cmd = {};
		cmd.delay = delay;
		part = part.split("<").join("&lt;");
		part = part.split(">").join("&gt;");
		part = part.split("\n").join(" <br />");
		cmd.text = part;
		addCommand(cmd);
	});
}

function addLambda(fn, delay) {
	if (fastMode) {
		fn();
		return;
	}
	var cmd = {};
	cmd.fn = fn;
	cmd.delay = delay;
	addCommand(cmd);
}

function addCommand(cmd) {
	commandQueue.push(cmd);
	if (!printing) {
		printLoop();
	}
}

function printLoop(){
	if (commandQueue.length == 0) {
		printing = false;
		return;
	}
	else {
		cmd = commandQueue.shift();
		if (cmd.text != undefined) {
			consoleSpan.innerHTML += cmd.text;
		}
		if (cmd.fn != undefined) {
			cmd.fn();
		}
		window.setTimeout(printLoop, cmd.delay);
		printing = true;
	}
}

function setCookie(cname, cvalue, exmin) {
	var d = new Date();
	d.setTime(d.getTime() + (exmin*60*1000));
	var expires = "expires="+ d.toUTCString();
	document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
	var name = cname + "=";
	var decodedCookie = decodeURIComponent(document.cookie);
	var ca = decodedCookie.split(';');
	for(var i = 0; i <ca.length; i++) {
		var c = ca[i];
		while (c.charAt(0) == ' ') {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		}
	}
	return "";
}
