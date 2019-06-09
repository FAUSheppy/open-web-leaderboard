/* disable buttons if nessesary */
var url   = new URL(window.location.href)
var page  = url.searchParams.get("page")
var buttonBackward = document.getElementById("button-backward")
var buttonForward  = document.getElementById("button-forward")
var buttonFirst    = document.getElementById("button-first")
var isLastPage     = document.getElementById("eof")

if(!page || page == "0"){
    buttonBackward.disabled = true
    buttonFirst.disabled   = true

    buttonBackward.classList.add("disabled")
    buttonFirst.classList.add("disabled")
}

if(isLastPage){
    buttonForward.disabled = true;
    buttonForward.classList.add("disabled")
}

function forward(){


    /* clean URL from unessesary parameters */
    url.searchParams.delete("goto")

    if(page){
        page = parseInt(page) + 1
    }else{
        page = 1
    }
    
    url.searchParams.set("page", page)
    window.location.href = url.href

}
function backward(){

    /* clean URL from unessesary parameters */
    url.searchParams.delete("goto")
    
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
var gotoRankInputField = document.getElementById("gotoRank");
gotoRankInputField.addEventListener("keyup", function(event) {
    if (event.key == "Enter") {
        event.preventDefault();
        var rank = gotoRankInputField.value
        var page = Math.trunc((rank - 1)/100)
        url.searchParams.set("page", page)
        url.searchParams.set("goto", rank)
        window.location.href = url.href
    }
});
