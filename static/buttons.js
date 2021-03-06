/* predefine some variables */
var url    = new URL(window.location.href)
var page   = url.searchParams.get("page")
var player = url.searchParams.get("string")
var buttonBackward = document.getElementById("button-backward")
var buttonForward  = document.getElementById("button-forward")
var isLastPage     = document.getElementById("eof")

/* clean URL from unessesary parameters */
url.searchParams.delete("goto")
url.searchParams.delete("string")

/* disable buttons if nessesary */
if(!page || page == "0"){
    buttonBackward.disabled = true
    buttonBackward.classList.add("disabled")
}

if(isLastPage){
    buttonForward.disabled = true;
    buttonForward.classList.add("disabled")
}

/* if request was a playersearch, move to player */
targetPlayer = document.getElementById("targetPlayer")
if(targetPlayer){
    /* scrollIntoView broken on android?? wtf */
    scrollOptions = {beahviour: "smooth", block:"center"} 
    targetPlayer.scrollIntoView(scrollOptions);
    targetPlayer.style.background = "#56a456a3";
    targetPlayer.children.forEach(c => c.style.borderColor="#56a456a3")
}

/* alert on mobile devices if player was not found */
//if(player && targetPlayerElements.length != 1){
//    alert("Player " + player + " not found :/")
//}


function forward(){

    if(page){
        page = parseInt(page) + 1
    }else{
        page = 1
    }
    
    url.searchParams.set("page", page)
    window.location.href = url.href

}
function backward(){

    if(page){
        page = parseInt(page) - 1
        if(page < 0){
            page = 0
        }
    }else{
        page = 0
    }
    
    url.searchParams.set("page", page)
    window.location.href = url.href
}

function firstPage(){
    var href = window.location.href
    var parameterSeperator = "?"

    if(href.includes(parameterSeperator)){
        window.location.href = href.split(parameterSeperator)[0]
    }
}

/* input fields */
//var gotoRankInputField = document.getElementById("gotoRank");
//gotoRankInputField.addEventListener("keyup", function(event) {
//    if (event.key == "Enter") {
//        event.preventDefault();
//        var rank = gotoRankInputField.value
//        var page = Math.trunc((rank - 1)/100)
//        url.searchParams.set("page", page)
//        url.searchParams.set("goto", rank)
//        window.location.href = url.href
//    }
//});

var getPlayerInputField = document.getElementById("getPlayer");
getPlayerInputField.addEventListener("keyup", function(event) {
    if (event.key == "Enter") {
        event.preventDefault();
        var string = getPlayerInputField.value
        url.searchParams.set("string", string)
        url.searchParams.delete("page")
        window.location.href = url.href
    }
});
