$(document).ready(function(){

    
    $("button").click(function(){
      entry = $("textarea").val()
      alert(entry);
      sendable = encodeURIComponent(entry);
      
      if(entry.trim() !== ""){
        $.get("http://192.168.1.83:5000/add?entry=" + sendable, function(data, status){
          jsondata = JSON.parse(JSON.stringify(data));
          status = jsondata['status'].toString();
          alert(status);
          $("textarea").val("");
        });
      }

      //$.get("http://192.168.1.83:5000/entryget", function(data, status){
      //  jsondata = JSON.parse(JSON.stringify(data));
      //  status = jsondata['entry'].toString();
      //  alert(status);
      //  $("textarea").val(status);
      //});

    });
});