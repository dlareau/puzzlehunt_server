$(document).ready(function() {
  function is_visible(){
    var stateKey, keys = {
      hidden: "visibilitychange",
      webkitHidden: "webkitvisibilitychange",
      mozHidden: "mozvisibilitychange",
      msHidden: "msvisibilitychange"
    };
    for (stateKey in keys) {
      if (stateKey in document) {
        return !document[stateKey];
      }
    }
    return true;
  }

  var get_posts = function() {
    if(is_visible()){
      $.getJSON("/chat/status/")
        .done(function(result){
          num_messages = result['num_messages']
          if(num_messages > 0) {
            $("#num_messages").css("background-color", "indianred");
          } else {
            $("#num_messages").css("background-color", "");
          }
          $("#num_messages").text(num_messages);
        })
        .fail( function(xhr, textStatus, errorThrown) {
          console.log(xhr);
        });
    }
  }

  setInterval(get_posts, 120000); //Two minutes
});