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

  var string_start = "You currently have ";
  var string_mid = " available hint";
  var string_end =" for this hunt";

  // get_posts is set to be called every 3 seconds.
  // Each time get_posts does not receive any data, the time till the next call
  // gets multiplied by 2.5 until a maximum of 120 seconds, reseting to 3 when
  // get_posts receives data.
  // TODO: reset to 3 seconds when the user sends an answer
  var ajax_delay = 3;
  var ajax_timeout;

  var get_posts = function() {
    if(is_visible()){
      $.ajax({
        type: 'get',
        url: puzzle_url,
        data: {last_date: last_date},
        success: function (response) {
          var response = JSON.parse(response);
          messages = response.hint_list;
          if(messages.length > 0){
            ajax_delay = 3;
            for (var i = 0; i < messages.length; i++) {
              receiveMessage(messages[i]);
            };
            last_date = response.last_date;
          }
          else {
            ajax_delay = ajax_delay * 2.5;
            if(ajax_delay > 120){
              ajax_delay = 120;
            }
          }
          $("#num_available_hints").html(string_start + response.num_available_hints + 
            string_mid + ((response.num_available_hints == 1) ? '' : 's') + string_end)
        },
        error: function (html) {
          console.log(html);
          ajax_delay = ajax_delay * 2.5;
          if(ajax_delay > 120){
            ajax_delay = 120;
          }
        }
      });
    }
    ajax_timeout = setTimeout(get_posts, ajax_delay*1000);
  }

  ajax_timeout = setTimeout(get_posts, ajax_delay*1000);


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
        clearTimeout(ajax_timeout);
        ajax_delay = 3;
        ajax_timeout = setTimeout(get_posts, ajax_delay*1000);
        response = JSON.parse(response);
        receiveMessage(response.hint_list[0]);
        last_date = response.last_date;
        $("#num_available_hints").html(string_start + response.num_available_hints + 
          string_mid + ((response.num_available_hints == 1) ? '' : 's') + string_end)
      }
    });
    $('#id_request').val('');
  });

  // receive a message though the websocket from the server
  function receiveMessage(submission) {
    submission = $(submission);
    pk = submission.data('id');
    if ($('tr[data-id=' + pk + ']').length == 0) {
      submission.prependTo("#hint_table");
    } else {
      $('tr[data-id=' + pk + ']').replaceWith(submission);
    }
  }
});
