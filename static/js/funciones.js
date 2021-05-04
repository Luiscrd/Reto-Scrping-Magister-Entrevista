function carg() {
    $('#cargando').fadeIn(500);
}

        
function rellenar(x) { 
    if ("geolocation" in navigator){ 
        $('#cargando').fadeIn(500);
        navigator.geolocation.getCurrentPosition(function(position){ 
            $("#pk").val(x);
            $("#lati").val(position.coords.latitude);
            $("#longi").val(position.coords.longitude);
            $('#cargando').fadeOut(0);
            $('#for_datos').submit();
            });
    }else{
        console.log("Browser doesn't support geolocation!");
    }
};