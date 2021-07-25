positions = [ "Top", "Jungle", "Mid", "Support" , "Bottom" ]
acceptedParser = [ "top", "jungle", "mid", "sup" , "bot", "adc", "support", "bottom", "*" ]
sides = [ "left", "right"]

var checkPlayerFunc = function checkPlayer() {
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

var checkPlayerApiFunc = function checkPlayer() {
    if(this.value == ""){
        return
    }
    url = "/player-api?id=" + this.value
    fetch(url).then(r => {
        if(r.status == 200){
            this.style.background = "#74bb74"
        }else{
            //this.style.background = "#d25252"
        }
    })
}

var fastPosChangedFunc = function fastPosChanged() {

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
        
        roleSubmission = document.getElementById("fastpos-submission")
        if(roleSubmission){
            string = "prio_" + accepted[i]
        }else {
            string = "prio-" + side + "-" + accepted[i] + "-" + pNr
        }

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
        retVal = true
    }

    if(retVal){
        this.style.background = "#74bb74"
    }else{
        this.style.background = "#d25252"
    }
}

function balance(){
    
    cont = document.getElementById("response-container")
    cont.innerHTML = ""
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

        }
    }
    
    prioBalanceCheckbox = document.getElementById("prio-balance")
    if(prioBalanceCheckbox.checked){
    	dictAll["acceptable-solution-threshold"] = 0.7
    }
    jsonData = JSON.stringify(dictAll, null, 4);

    /* transmitt */
    spinner = document.getElementById("loading")
    spinner.style.display = "block";
    fetch(window.location.href, {
          method: 'post',
          headers: {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json' },
          body: jsonData
    }).then(r => r.json()).then(j => {
        spinner.style.display = "none";
        cont.innerHTML = j["content"]
    })

}

function parseMultiline(){

    var names = []
    var prioStrings = []

    field = document.getElementById("multi-line-copy")
    lines = field.value.split("\n")
    lines.forEach(l => {
        
        lowestIndex = 100

        acceptedParser.forEach( p => {
            i = l.indexOf(" " + p)
            if(i >= 3 && i < lowestIndex){
                lowestIndex = i
            }
        })

        if(lowestIndex != 100){
            name = l.substring(0, lowestIndex)
            prioStr = l.substring(lowestIndex)
            names.push(name)
            prioStrings.push(prioStr)
        }
    })

    count = 0
    sides.forEach(s => {
        for(i = 0; i<5; i++){

            pObjField = document.getElementById("playername-" + s + "-" + i)
            prObjField = document.getElementById("check-" + s + "-fastpos-" + i)

            if(count >= names.length){
                pObjField.value = ""
                prObjField.value = ""
            }else{
                pObjField.value = names[count]
                prObjField.value = prioStrings[count]
            }

            count++;
        }
    })

    const inputEvent = new Event("input")
    fastPosFields.forEach(el => el.dispatchEvent(inputEvent))
    balance()
}

function queryForPlayerData(){
    ident = document.getElementById("ident-field").innerHTML
    fetch("/balance-tool-data?id=" + ident).then(r => r.json()).then(j => {
        if("no-data" in j){
            return
        }
        j["submissions"].forEach(el => {
            console.log(el)
            breakToSubmissions = false
            for(sid = 0; sid < 2; sid++){
            if(breakToSubmissions){
                break;
            }
            for(id = 0; id < 5; id++){
                stringPid = `playername-${sides[sid]}-${id}`
                pnameObj = document.getElementById(stringPid)
                if(pnameObj.value == "" || pnameObj.value == el["name"]){
                pnameObj.value = el["name"]
                for(acc = 0; acc < 5; acc++){
                    stringSelectorId = `prio-${sides[sid]}-${positions[acc]}-${id}`
                    selObj = document.getElementById(stringSelectorId)
                    selObj.value = el[positions[acc]]
                }
                breakToSubmissions = true
                break;
                }
            }
            }
        })
    })
}

function copy() {

    ident = document.getElementById("ident-field").innerHTML
    path = "/role-submission?id="
    copyText = window.location.protocol + "//" + window.location.hostname + path + ident
    
    navigator.clipboard.writeText(copyText)
        document.getElementById("copyLink").innerHTML = "Copied!"
    setTimeout(() => {
            document.getElementById("copyLink").innerHTML = "Copy Submission Link" }, 500);

}

fastPosFields = document.getElementsByClassName("fastpos")
playerNameFields = document.getElementsByClassName("pname")

playerNameFields.forEach(el => el.addEventListener('input', checkPlayerFunc));
playerNameFields.forEach(el => el.addEventListener('focus', checkPlayerFunc));

fastPosFields.forEach(el => el.addEventListener('input', fastPosChangedFunc));
//fastPosFields.forEach(el => el.addEventListener('focus', fastPosChangedFunc));

fastposSubmission = document.getElementById("fastpos-submission")
if(fastposSubmission){
    fastposSubmission.addEventListener("input", fastPosChangedFunc)
    fastposSubmission.addEventListener("focus", fastPosChangedFunc)
}
setInterval(queryForPlayerData(), 3000)

formContainer = document.getElementById("form-container")
if(formContainer){
    //formContainer.reset()
}

function resetAll(){
	formContainer = document.getElementById("form-container")
    	formContainer.reset()
}
