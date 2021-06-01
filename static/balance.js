positions = [ "Top", "Jungle", "Mid", "Support" , "Bottom" ]

function checkPlayer() {
	if(this.value == ""){
		return
	}
	url = "/player?id=" + this.value
	fetch(url).then(r => {
		if(r.status == 200){
			this.style.background = "#74bb74"
		}else{
			//this.style.background = "#d25252"
		}
	})
}

function fastPosChanged() {

	accepted = [ "top", "jungle", "mid", "sup" , "bot" ]
	uniqArr  = []
	prioArray = [5, 5, 5, 5, 5]

	/* commence cleanup */
	clean = this.value.replaceAll(" ", "").toLocaleLowerCase()
	clean = clean.replace("support", "sup")
	clean = clean.replace("adc", "bot")
	clean = clean.replace("bottom", "bot")

	retVal = true
	if(clean.includes("<")){
		console.log("Not accepted (includes <)")
		retVal = false
	}

  	list = clean.split(">")
	cur = 1
	list.forEach(el => {
		if(el.includes("=")){
			listEq = el.split("=")
			listEq.forEach(sub => {
				if(accepted.includes(sub) && !uniqArr.includes(sub)){
					prioArray[accepted.indexOf(sub)] = cur
					uniqArr += [sub]
				}else{
					console.log("Not accepted (=): " + sub)
					retVal = false
				}
			})
			cur++
		}else{
			if(accepted.includes(el) && !uniqArr.includes(el)){
				prioArray[accepted.indexOf(el)] = cur
				uniqArr += [el]
				cur++
			}else{
				console.log("Not accepted (>): " + el)
				retVal = false
			}
		}
	})
	for(i = 0; i<5; i++){
		arr = this.id.split("-")
		pNr = arr[arr.length-1]
		side = this.id.includes("left") ? "left" : "right"
		string = "prio-" + side + "-" + accepted[i] + "-" + pNr

		string = string.replace("top","Top")
		string = string.replace("jungle","Jungle")
		string = string.replace("mid","Mid")
		string = string.replace("sup","Support")
		string = string.replace("bot","Bottom")

		selector = document.getElementById(string)
		selector.value = prioArray[i]
		selector.style.background = "lightblue"
	}

	/* allow some basic shit */
	if(clean == "*" || clean == ""){
		console.log("lol")
		retVal = true
	}

	if(retVal){
		this.style.background = "#74bb74"
	}else{
		this.style.background = "#d25252"
	}
}

function balance(){
	
	sides  = ["left", "right"]

	blue = [ "", "", "", "", ""]
	red  = [ "", "", "", "", ""]

	dictToBeSorted = {
				0 : [],
				1 : [],
				2 : [],
				3 : [],
				4 : []
			 }
	filler = []
	impossible = []

	dictAll = {}
	for(sid = 0; sid < 2; sid++){
		for(id = 0; id < 5; id++){
			
			var pname = "undef"
			var prioList = [5, 5, 5, 5, 5]

			stringPid = `playername-${sides[sid]}-${id}`
			pnameObj = document.getElementById(stringPid)
			pname = pnameObj.value
			for(acc = 0; acc < 5; acc++){
				stringSelectorId = `prio-${sides[sid]}-${positions[acc]}-${id}`
				selObj = document.getElementById(stringSelectorId)
				prioList[acc] = selObj.value
			}

			dictAll[pname] = prioList

			/* deal with one pos andys */
			countPos = prioList.filter(a => a < 5).length
			if(countPos == 1){
				pos = null
				count = 0
				prioList.forEach(a => {
					if(a < 5){
						pos = positions[count]
					}
					count++;
				})
				indexPos = positions.indexOf(pos)
				if(blue[indexPos] == ""){
					blue[indexPos] = pname
				}else if(red[indexPos] == ""){
					red[indexPos] = pname
				}else{
					impossible += [pname]
				}
			}else if(prioList.reduce((a, b) => a + b, 0) == 25){
				/* those are fillers */
				fillers += [pname]
			}else{
				for(i = 0; i<5; i++){
					dictToBeSorted[i] += [{ "name" : pname, "val" : prioList[i]}]
				}
			}

		}
	}

	/* fill rest */
	for(i = 0; i < 5; i++){
		if(red[i] == ""){
			candidates = dictToBeSorted[i]
		}
		if(blue[i] == ""){

		}
	}

	jsonData = JSON.stringify(dictAll, null, 4);

	/* transmitt */
	fetch(window.location.href, {
  		method: 'post',
  		headers: {
    			'Accept': 'application/json, text/plain, */*',
    			'Content-Type': 'application/json' },
  		body: jsonData
	}).then(r => r.json()).then(j => {
		cont = document.getElementById("response-container")
		cont.innerHTML = j["content"]
	})

}

fastPosFields = document.getElementsByClassName("fastpos")
playerNameFields = document.getElementsByClassName("pname")

playerNameFields.forEach(el => el.addEventListener('input', checkPlayer));
playerNameFields.forEach(el => el.addEventListener('focus', checkPlayer));

fastPosFields.forEach(el => el.addEventListener('input', fastPosChanged));
fastPosFields.forEach(el => el.addEventListener('focus', fastPosChanged));
