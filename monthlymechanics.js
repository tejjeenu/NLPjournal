$(document).ready(function(){

    
    //API call here
    $.get("http://192.168.1.83:5000/monthly", function(data, status){
      jsondata = JSON.parse(JSON.stringify(data));

      goalquotesraw = jsondata['goal quotes'].toString();
      learningquotesraw = jsondata['learning quotes'].toString();
      gratefulquotesraw = jsondata['grateful quotes'].toString();
      goalkeywordsraw = jsondata['goal keywords'].toString();
      learningkeywordsraw = jsondata['learning keywords'].toString();
      gratefulkeywordsraw = jsondata['grateful keywords'].toString();

      //make lists out of each raw string

      goalquoteslist = goalquotesraw.split(",-").reverse();
      learningquoteslist = learningquotesraw.split(",-").reverse();
      gratefulquoteslist = gratefulquotesraw.split(",-").reverse();
      goalkeywordslist = goalkeywordsraw.split(" ").reverse();
      learningkeywordslist = learningkeywordsraw.split(" ").reverse();
      gratefulkeywordslist = gratefulkeywordsraw.split(" ").reverse();

      for(goal in goalquoteslist){
        quote = goalquoteslist[goal].trim(); //this will remove any trailing spaces as it is possible
        length = quote.length;
        keywords = goalkeywordslist[goal].split(",");
        for(word in keywords){
          quote = quote.replace(keywords[word], "<b>" + keywords[word] + "</b>");
        }

        newlines = Math.trunc(length/140);
        for (let i = 0; i < newlines; i++) {
          indexposition = (140 * (i + 1)) - 1;
          indexposition = quote.substring(indexposition).indexOf(" ") + indexposition;
          quote = quote.substring(0, indexposition) + "<br>" + quote.substring(indexposition);
        }

        $("#goals").append('<div class="cell">' + '"' + quote.substring(2) + '"' + '<br><span style="color: rgb(150, 150, 150);"> -entry '+ quote.charAt(0) +'</span></div><br>');
      }

      for(learning in learningquoteslist){
        quote = learningquoteslist[learning].trim(); //this will remove any trailing spaces as it is possible
        length = quote.length;
        keywords = learningkeywordslist[learning].split(",");
        for(word in keywords){
          quote = quote.replace(keywords[word], "<b>" + keywords[word] + "</b>");
        }

        newlines = Math.trunc(length/140);
        for (let i = 0; i < newlines; i++) {
          indexposition = (140 * (i + 1)) - 1;
          indexposition = quote.substring(indexposition).indexOf(" ") + indexposition;
          quote = quote.substring(0, indexposition) + "<br>" + quote.substring(indexposition);
        }

        $("#learning").append('<div class="cell">' + '"' + quote.substring(2) + '"' + '<br><span style="color: rgb(150, 150, 150);"> -entry '+ quote.charAt(0) +'</span></div><br>');
      }

      for(gratitude in gratefulquoteslist){
        quote = gratefulquoteslist[gratitude].trim();
        length = quote.length; //this will remove any trailing spaces as it is possible
        keywords = gratefulkeywordslist[gratitude].split(",");
        for(word in keywords){
          quote = quote.replace(keywords[word], "<b>" + keywords[word] + "</b>");
        }
        //to calculate number of newlines to add
        newlines = Math.trunc(length/140);
        for (let i = 0; i < newlines; i++) {
          indexposition = (140 * (i + 1)) - 1;
          indexposition = quote.substring(indexposition).indexOf(" ") + indexposition;
          quote = quote.substring(0, indexposition) + "<br>" + quote.substring(indexposition);
        }

        $("#gratitude").append('<div class="cell">' + '"' + quote.substring(2) + '"' + '<br><span style="color: rgb(150, 150, 150);"> -entry '+ quote.charAt(0) +'</span></div><br>');
      }
      
    });
});