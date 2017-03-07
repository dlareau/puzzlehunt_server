jQuery(document).ready(function($) {
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
    $.ajax({
      type: 'get',
      url: puzzle_url,
      data: {last_date: last_date},
      success: function (response) {
        var response = JSON.parse(response);
        messages = response.submission_list;
        if(messages.length > 0){
          for (var i = 0; i < messages.length; i++) {
            receiveMessage(messages[i]);
          };
          last_date = response.last_date;
        }
      },
      error: function (html) {
        console.log(html);
      }
    });
  }
  setInterval(get_posts, 3000);


  $('#sub_form').on('submit', function(e) {
    e.preventDefault();
    $.ajax({
      url : $(this).attr('action') || window.location.pathname,
      type: "POST",
      data: $(this).serialize(),
      error: function (jXHR, textStatus, errorThrown) {
        console.log(jXHR.responseText);
        alert(errorThrown);
      },
      success: function (response) {
        response = JSON.parse(response);
        receiveMessage(response.submission_list[0]);
      }
    });
    $('#id_answer').val('');
  }); 

  // receive a message though the websocket from the server
  function receiveMessage(submission) {
    submission = $(submission);
    pk = submission.data('id');
    if ($('tr[data-id=' + pk + ']').length == 0) {
      submission.prependTo("#sub_table");
      $('#sub_table tr:last').remove();
    } else {
      $('tr[data-id=' + pk + ']').replaceWith(submission);
    }
  }
});