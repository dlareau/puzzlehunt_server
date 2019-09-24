  function map_buttons() {
    $('.chatselect').click(function() {
      $('.chatselect').each(function() {
        $("#chat_" + $(this).data('id')).hide();
        $(this).removeClass('active')
      });
      $("#chat_" + $(this).data('id')).show();
      curr_team = $(this).data('id');
      full_name = $(this).data('full_name');
      $("button[data-id=" + curr_team + "]").addClass('active')
      $("button[data-id=" + curr_team + "]").css("background-color", "");
      $("#team_label").html("Chatting with: " + full_name);
      $("#chatcontainer").scrollTop($("#chatcontainer")[0].scrollHeight);
    });
  }
$(document).ready(function() {
  map_buttons();
});
