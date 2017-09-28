$(document).ready(function() {
  function recolor () {
    $(".available").each(function(){
      var time_diff = Math.floor(Date.now()/1000) - $(this).data("date");
      var ratio = Math.floor(Math.min((1-time_diff/14400), 1)*255);
      var color = "rgb(255, " + ratio + ", 0)"
      $(this).css("background", color);
    });
  }
  recolor();
  setInterval(recolor, 5000);

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
        url: "/staff/progress/",
        data: {last_solve_pk: last_solve_pk, last_unlock_pk: last_unlock_pk,
               last_submission_pk: last_submission_pk},
        success: function (response) {
          var response = JSON.parse(response);
          messages = response.messages
          if(messages.length > 0){
            for (var i = 0; i < messages.length; i++) {
              receiveMessage(messages[i]);
              console.log(messages[i]);
            };
            last_solve_pk = response.update_info[0];
            last_unlock_pk = response.update_info[1];
            last_submission_pk = response.update_info[2];
          }
        },
        error: function (html) {
          console.log(html);
        }
      });
    }
  }
  setInterval(get_posts, 3000);


  $('.unlock_form').on('submit', function(e) {
    e.preventDefault();
    $.ajax({
      url : $(this).attr('action') || window.location.pathname,
      type: "POST",
      data: $(this).serialize(),
      error: function (jXHR, textStatus, errorThrown) {
        alert(errorThrown);
        console.log(jXHR);
      }
    });
  });

  function receiveMessage(update) {
    $td = $("#p" + update.puzzle.id + "t" + update.team_pk);
    if(update.status_type == "solve"){
      $td.removeClass();
      $td.addClass('solved');
      $td.html(update.time_str);
      $td.css("background", "");
    }
    else if(update.status_type == "unlock"){
      $td.removeClass();
      $td.addClass('available');
      $td.data("date", (Date.now()/1000));
      $td.html(" ");
    }
    else if(update.status_type == "submission"){
      $td.html("<b>" + update.time_str + "</b>");
    }
  }
});