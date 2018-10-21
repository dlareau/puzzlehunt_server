$(document).ready(function() {

  $("#chatcontainer").scrollTop($("#chatcontainer")[0].scrollHeight);

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

  function send_message(){
    if($("#announce_checkbox:checked").length > 0){
      is_announcement = $("#announce_checkbox:checked")[0].checked
    } else {
      is_announcement = false
    }
    data = {team_pk: curr_team, message: $('#messagebox').val(),
            is_response: is_response, csrfmiddlewaretoken: csrf_token,
            is_announcement: is_announcement};
    $.post(chat_url, data, 'json')
      .fail( function(xhr, textStatus, errorThrown) {
        console.log(xhr);
      })
      .done(function(response) {
        response = JSON.parse(response);
        receiveMessages(response['message_dict']);
        last_pk = response['last_pk'];
      });
    $('#messagebox').val('');
  }

  var get_posts = function() {
    if(is_visible()){
      $.getJSON(chat_url, {last_pk: last_pk})
        .done(function(result){
          receiveMessages(result['message_dict']);
          last_pk = result['last_pk'];
        })
        .fail( function(xhr, textStatus, errorThrown) {
          console.log(xhr);
        });
    }
  }

  $('#sendbutton').click(function() {
    send_message();
  });
  $(document).on("keypress", "#messagebox", function(e) {
    if (e.which == 13) {
      send_message();
    }
  });

  setInterval(get_posts, 3000);

  function receiveMessages(message_dict) {
    $.each(message_dict, function(team_name, team_data) {
      if($("#chat_"+ team_data['pk']).length == 0){
        $("#chatcontainer").append("<div id='chat_" + team_data['pk'] + "'  class='chatwindow'>");
        var b = "<button data-id='" + team_data['pk'] + "'class='chatselect'>";
        $("#button_container").append(b + team_name + "</button>");
        map_buttons();
      }
      var message_window = $("#chat_" + team_data['pk']);
      message_window.append(team_data['messages']);
      if(team_data['pk'] != curr_team && $(team_data['messages']).hasClass('user-message')){
        $("button[data-id=" + team_data['pk'] + "]").css("background-color", "red");
      }
      $("#chatcontainer").scrollTop($("#chatcontainer")[0].scrollHeight);
    });
  }
});