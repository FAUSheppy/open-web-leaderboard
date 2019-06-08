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
