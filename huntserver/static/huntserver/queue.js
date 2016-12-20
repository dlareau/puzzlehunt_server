$(document).ready(function() {
  var flashing = false,
  focused = true;
  var title = document.title;

  $('.sub_form').on('submit', formListener);

  window.addEventListener('focus', function() {
    focused = true;
    flashing = false;
  });
  window.addEventListener('blur', function() {
    focused = false;
  });

  /* flash the title if necessary */
  setInterval(function() {
    if (flashing && !focused) {
      if (document.title[0] == '[') {
        document.title = title;
      } else {
        document.title = '[' + title + '] - New Submissions';
      }
    } else {
      document.title = title;
    }
  }, 1000);

  last_date = new Date().toISOString().slice(0, 19) + 'Z';
  var get_posts = function() {
    $.ajax({
      type: 'get',
      url: "/ajax/submission",
      data: {last_date: last_date, all: true},
      success: function (response) {
        console.log(response);
        var messages = JSON.parse(response);
        if(messages.length > 0){
          for (var i = 0; i < messages.length-1; i++) {
            receiveMessage(messages[i]);
          };
          last_date = new Date().toISOString().slice(0, 19) + 'Z';
        }
      },
      error: function (html) {
        console.log(html);
      }
    });
  }
  setInterval(get_posts, 3000);


  function rowFromSubmission(submission){
    var row_class, response;
    if(submission['response_text'] == '') {
      form_text = "Wrong Answer";
    } else {
      form_text = submission['response_text'];
    }
    form = "<form class='sub_form' action='/staff/queue/' method='post' style='display:none'>\n" +
              "<input type='hidden' name='csrfmiddlewaretoken' value='" + Cookies.get('csrftoken') + "'>\n" +
              "<p>\n" +
                "<input id='id_response' maxlength='400' name='response' type='text' value='" + form_text + "'>\n" +
                "<input type='hidden' name='sub_id' value='" + submission['pk'] + "'>\n" +
                "<input type='Submit' value='Send Response'/>\n" +
              "</p>\n" +
            "</form>";
    if(submission['response_text'] == '') {
      row_class = "incorrect-unreplied";
      response = "<a href='#' class='needs-response'>[manual response]</a>\n" +
            "<a href='#' class='canned-response'>[canned response]</a>\n" + form;
    } else {
      if(submission['response_text'] == 'Correct!') {
        row_class = "correct";
      } else {
        row_class = "incorrect-replied";
      }
      response = "Response: " + submission['response_text'];
    }

    var row = $("<tr data-id='" + submission['pk'] + "' class='" +
          row_class +  "'> </tr>");
    var col1 = $("<td> " + submission['team'] + " </td>");
    var col2 = $("<td> " + submission['puzzle_name'] + " </td>");
    var col3 = $("<td> " + submission['submission_text'] + " </td>");
    var col4 = $("<td> " + submission['time_str'] + " </td>");
    var col5 = $("<td> " + response + " <a href='#' class='needs-response'>Fix</a>" + form + " </td>");
    row.append(col1,col2,col3,col4,col5);
    return row;
  }

  function formListener(e) {
    e.preventDefault();
    $.ajax({
      url : $(this).attr('action') || window.location.pathname,
      type: "POST",
      data: $(this).serialize(),
      error: function (jXHR, textStatus, errorThrown) {
        alert(errorThrown);
      }
    });
  }

  function receiveMessage(submission) {
    var row = rowFromSubmission(submission);
    if ($('tr[data-id=' + submission['pk'] + ']').length == 0) {
      if(submission['response_text'] != 'Correct!') {
        flashing = !focused;
        $('audio')[0].play();
      }
      row.prependTo("#sub_table");
    } else {
      $('tr[data-id=' + submission['pk'] + ']').replaceWith(row);
    }
    $('.sub_form').on('submit', formListener);
  }

  /* open a text box for submitting an email */
  $(document).delegate('.needs-response', 'click', function() {
    $(this).siblings('form').show();
    return false;
  });
  $(document).delegate('.canned-response', 'click', function() {
    $(this).siblings('form').submit();
    return false;
  });
});