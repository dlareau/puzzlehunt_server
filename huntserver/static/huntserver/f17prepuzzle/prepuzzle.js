var formurl = "";

function checkans() {
	var ans = answer.value;
	if (verify(ans)) {
		feedback.innerHTML = "Correct!";
		window.setTimeout(function() {
			window.open(formurl,'_blank');
			feedback.innerHTML = "Correct!";
			feedback.innerHTML += '<br /> <a class="whitelink" href="' + formurl + '" target="_blank">' + formurl + '</a>';
		}, 1000);
	}
	else {
		feedback.innerHTML = "Incorrect";
	}
}

/* This puzzle requires no CS/hacking knowledge to solve. */
function verify(ans) {
	var ans = ans.trim().split(" ").join("").toUpperCase();
	var lsalt = "DKFSIZZEWXGRHUECTRDM";
	var rsalt = "GWZYNFAEZMHJUEXNOFNJ";
	var hash = CryptoJS.MD5(lsalt + ans + rsalt);
	var res = hash == "e2c4050a0496c9ab3b165766da831263";
	if (res) {
		setCookie("answer", ans, 60*24*30);
		var hash2 = "THJXDZCBJLDQQMPWSMUM" + ans + "GZFBVHFIMDJGLWMPCKIS";
		var aeskey = CryptoJS.MD5(hash2).toString();
		ciphertext = "U2FsdGVkX19Pu0P24xmTrhYYo7aVs99Yh3cW7J/y/QHCYueBQtmgAYqVAgHtw5r1";
		formurl = CryptoJS.AES.decrypt(ciphertext, aeskey).toString(CryptoJS.enc.Utf8);
	}
	return res;
}

function checkkey(e) {
	if (e.keyCode == 13) {
		checkans();
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