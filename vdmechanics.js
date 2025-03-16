$(document).ready(function(){

    $.get("http://192.168.1.83:5000/entryget", function(data, status){
        jsondata = JSON.parse(JSON.stringify(data));
        status = jsondata['entry'].toString();
        alert(status);
        $("textarea").val(status);
    });
    
    $("button").click(function(){

      if($("textarea").val() !== ""){
        $.get("http://192.168.1.83:5000/entrydelete", function(data, status){
          jsondata = JSON.parse(JSON.stringify(data));
          status = jsondata['status'].toString();
          alert(status);
          $("textarea").val("");
        });
      }

    });
});