function forward(){

    var url   = new URL(window.location.href)
    var start = url.searchParams.get("start")
    var page  = url.searchParams.get("page")
    
    if(page){
        page = parseInt(page) + 1
    }else if(start){
        page = Math.trunc(parseInt(start)/100) + 1
    }else{
        page = 1
    }
    
    url.searchParams.set("page", page)
    window.location.href = url.href

}
function backward(){

    var url   = new URL(window.location.href)
    var start = url.searchParams.get("start")
    var page  = url.searchParams.get("page")
    
    if(page){
        page = parseInt(page) - 1
        if(page < 0){
            page = 0
        }
    }else if(start){
        page = Math.trunc(parseInt(start)/100) - 1
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
        var url  = new URL(window.location.href)
        var rank = gotoRankInputField.value
        var page = Math.trunc((rank - 1)/100)
        url.searchParams.set("page", page)
        url.searchParams.set("goto", rank)
        window.location.href = url.href
    }
});
