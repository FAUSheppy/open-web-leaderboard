positions = [ "Top", "Jungle", "Mid", "Support" , "Bottom" ]

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

	if(retVal){
		this.style.background = "green"
	}else{
		this.style.background = "red"
	}
}

function balance(){
	sides  = ["left", "right"]
	var prioList = [5, 5, 5, 5, 5]
	var pname = "undef"
	for(sid = 0; sid < 2; sid++){
		for(id = 0; id < 5; id++){
			stringPid = `playername-${sides[sid]}-${id}`
			pnameObj = document.getElementById(stringPid)
			pname = pnameObj.value
			for(acc = 0; acc < 5; acc++){
				stringSelectorId = `prio-${sides[sid]}-${positions[acc]}-${id}`
				selObj = document.getElementById(stringSelectorId)
				prioList[acc] = selObj.value
			}
		}
	}
	console.log(pname, prioList)
}

fastPosFields = document.getElementsByClassName("fastpos")
fastPosFields.forEach(el => el.addEventListener('input', fastPosChanged));
fastPosFields.forEach(el => el.addEventListener('focus', fastPosChanged));
