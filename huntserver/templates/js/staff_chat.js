$(document).ready(function() {
  curr_team = "";

  last_pk = {{last_pk}};
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
    data = {team_pk: curr_team, message: $('#messagebox').val(),
            is_response: true, csrfmiddlewaretoken: '{{ csrf_token }}'};
    jQuery.post("/chat/", data);
    $('#messagebox').val('');
  });
  $(document).on("keypress", "#messagebox", function(e) {
    if (e.which == 13) {
      data = {team_pk: curr_team, message: $('#messagebox').val(),
              is_response: true, csrfmiddlewaretoken: '{{ csrf_token }}'};
      jQuery.post("/chat/", data);
      $('#messagebox').val('');
    }
  });

  function receiveMessage(message) {
    if(message.is_response){
      message.team_name = "Admin";
    }
    if(message.team_name.length > 10){
      message.team_name.length = message.team_name.slice(0,10);
    }
    if(message.team_name.length < 10){
      message.team_name += Array(11-message.team_name.length).join(" ");
    }
    if($("#chat_"+ message.team_pk).length == 0){
      $("#chatcontainer").append("<div id='chat_" + message.team_pk + "'  class='chatwindow'>");
      var b = "<button data-id='" + message.team_pk + "'class='chatselect'>";
      $("#button_container").append(b + message.team_name + "</button>");
      map_buttons();
    }
    var message_window = $("#chat_" + message.team_pk);
    var div = "<div style='white-space:pre-wrap;";
    if(message.is_response){
      div += " color:red;";
    }
    div += "'>" + message.team_name + ": " + message.text + "</div>";
    message_window.append(div);
    if(message.team_pk != curr_team){
$("button[data-id=" + message.team_pk + "]").css("background-color", "red");
    }
  }

  function map_buttons() {
    $('.chatselect').click(function() {
      $('.chatselect').each(function() {
        $("#chat_" + $(this).data('id')).hide();
      });
      $("#chat_" + $(this).data('id')).show();
      curr_team = $(this).data('id');
      $("button[data-id=" + curr_team + "]").css("background-color", "white");
    });
  }
  map_buttons();
});