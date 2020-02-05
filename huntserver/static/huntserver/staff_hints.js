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

  $('.btn-number').click(function(e){
    e.preventDefault();
    team  = $(this).attr('data-team');
    value = $(this).attr('data-value');
    $.post("/staff/hints/control/", 
      {action:'update', 'team_pk': team, value: value, csrfmiddlewaretoken: csrf_token}, 
      function( data ) {
        var response = JSON.parse(data);
        for (var i = 0; i < response.length; i++) {
          $('input[data-team=' + response[i][0] + ']').val(response[i][1]);
        }
      }
    );
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

  var get_posts = function() {
    // Hint texts:
    $.ajax({
      type: 'get',
      url: "/staff/hints/",
      data: {last_date: last_date},
      success: function (response) {
        var response = JSON.parse(response);
        messages = response.hint_list;
        if(messages.length > 0){
          for (var i = 0; i < messages.length; i++) {
            var submission = $(messages[i]);
            pk = submission.data('id');
            if ($('tr[data-id=' + pk + ']').length == 0) {
              submission.prependTo("#sub_table");
              if($('#sub_table tr').length >= 10){
                $('#sub_table tr:last').remove();
              }
            } else {
              $('tr[data-id=' + pk + ']').replaceWith(submission);
            }
            $('.sub_form').on('submit', formListener);
          };
          last_date = response.last_date;
        }
      },
      error: function (html) {
        console.log(html);
      }
    });

    // Available hints:
    $.ajax({
      type: 'get',
      url: "/staff/hints/control/",
      success: function (response) {
        var response = JSON.parse(response);
        for (var i = 0; i < response.length; i++) {
          $('input[data-team=' + response[i][0] + ']').val(response[i][1]);
        }
      },
      error: function (html) {
        console.log(html);
      }
    });
  }
  setInterval(get_posts, 30000);

  function formListener(e) {
    e.preventDefault();
    // This sucks, I should be more precise
    old_row = $(this).parent().parent().parent().parent().parent().parent().parent();
    $.ajax({
      url : $(this).attr('action') || window.location.pathname,
      type: "POST",
      data: $(this).serialize(),
      success: function (response) {
        response = JSON.parse(response);
        old_row.replaceWith($(response.hint_list[0]));
        $('.sub_form').on('submit', formListener);
        last_date = response.last_date;
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(jXHR);
      }
    });
  }

  /* open a text box for submitting an email */
  $(document).delegate('.fix_link', 'click', function() {
    $(this).siblings('form').show();
    $(this).siblings('p').hide();
    $(this).hide();
    return false;
  });
});