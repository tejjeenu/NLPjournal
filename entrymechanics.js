$(document).ready(function(){
    
    //API call here
    $.get("http://192.168.1.83:5000/entrynames", function(data, status){
      jsondata = JSON.parse(JSON.stringify(data));

      entrynamesraw = jsondata['names'].toString();

      //make lists out of each raw string

      entrynameslist = entrynamesraw.split(",").reverse();

      for(entry in entrynameslist){
        $("#subcontent").append('<button class="solvebtn" style="font-size:24px;width:400px;">' + 'Entry ' + entrynameslist[entry] + '</button><br>');
      }
      
    });

    $(document).on("click", ".solvebtn", function(){//use this function when you create elements by code dynamically
      rawinfo = $(this).text();
      length = rawinfo.length;
      id = rawinfo.charAt(length-1).toString();

      $.get("http://192.168.1.83:5000/entryset?id=" + id, function(data, status){
        jsondata = JSON.parse(JSON.stringify(data));
        status = jsondata['status'].toString();
        alert(status);
      });

    });
});