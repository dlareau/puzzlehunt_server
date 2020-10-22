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
          messages = response.submission_list;
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
    $("#answer_help").remove();
    $(this).removeClass("has-error");
    $(this).removeClass("has-warning");

    // Check for invalid answers:
    var non_alphabetical = /[^a-zA-Z \-_]/;
    if(non_alphabetical.test($(this).find(":text").val())) {
      $(this).append("<span class=\"help-block\" id=\"answer_help\">" +
                     "Answers will only contain the letters A-Z.</span>");
      $(this).addClass("has-error");
      return;
    }
    var spacing = /[ \-_]/;
    if(spacing.test($(this).find(":text").val())) {
      $(this).append("<span class=\"help-block\" id=\"answer_help\">" +
                     "Spacing characters are automatically removed from responses.</span>");
      $(this).addClass("has-warning");
    }
    $.ajax({
      url : $(this).attr('action') || window.location.pathname,
      type: "POST",
      data: $(this).serialize(),
      error: function (jXHR, textStatus, errorThrown) {
        if(jXHR.status == 403){
          error = "Submission rejected due to exessive guessing."
          $("<tr><td colspan = 3><i>" + error +"</i></td></tr>").prependTo("#sub_table");
        } else {
          var response = JSON.parse(jXHR.responseText);
          if("answer" in response && "message" in response["answer"][0]) {
            console.log(response["answer"][0]["message"]);
          }
        }
      },
      success: function (response) {
        clearTimeout(ajax_timeout);
        ajax_delay = 3;
        ajax_timeout = setTimeout(get_posts, ajax_delay*1000);
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
    } else {
      $('tr[data-id=' + pk + ']').replaceWith(submission);
    }
    if(submission.data('correct') == "True") {
      $("#id_answer").prop("disabled", true);
      $('button[type="submit"]').addClass("disabled");
      $('button[type="submit"]').attr('disabled', 'disabled');
    }
  }
});
