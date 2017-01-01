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

  last_pk = {{last_pk}};
  var get_posts = function() {
    if(is_visible()){
      $.ajax({
        type: 'get',
        url: "/ajax/message",
        data: {last_pk: last_pk},
        success: function (response) {
          var messages = JSON.parse(response);
          if(messages.length > 0){
            for (var i = 0; i < messages.length-1; i++) {
              receiveMessage(messages[i]);
            };
            last_pk = messages[messages.length-1];
          }
        },
        error: function (html) {
          console.log(html);
        }
      });
    }
  }
  setInterval(get_posts, 3000);

  $('#sendbutton').click(function() {
    data = {team_pk: {{ team.pk }}, message: $('#messagebox').val(), 
            is_response: false, csrfmiddlewaretoken: '{{ csrf_token }}'};
    jQuery.post("/chat/", data);
    $('#messagebox').val('');
  });
  $(document).on("keypress", "#messagebox", function(e) {
    if (e.which == 13) {
      data = {team_pk: {{ team.pk }}, message: $('#messagebox').val(),
              is_response: false, csrfmiddlewaretoken: '{{ csrf_token }}'};
      jQuery.post("/chat/", data);
      $('#messagebox').val('');
    }
  });

  function receiveMessage(message) {
    if(message.is_response){
      message.team_name = "Admin";
    }
    if(message.team_name.length > 10){
      message.team_name = message.team_name.slice(0,10);
    }
    if(message.team_name.length < 10){
      message.team_name += Array(11-message.team_name.length).join(" ");
    }
    var message_window = $("#chatcontainer");
    var div = "<div style='white-space:pre-wrap;";
    if(message.is_response){
      div += " color:red;";
    }
    div += "'>" + message.team_name + ": " + message.text + "</div>";
    message_window.append(div);
  }
});