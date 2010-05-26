function recognize() {
  
  var writing = webcanvas.getWriting();
  var xml = writingToXML(writing);

  var hwreq = new Request.JSON({method: "post", url: "http://localhost:4567/recognize",onSuccess: update_results}).post({"char" : xml});
    
}

function update_results(results) {
  var html = "";
  results.map(function (item){html = html + item[0];}); 
  $("results").set("text",html);
}
