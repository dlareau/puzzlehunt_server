  function map_buttons() {
    $('.chatselect').click(function() {
      $('.chatselect').each(function() {
        $("#chat_" + $(this).data('id')).hide();
        $(this).removeClass('active')
      });
      $("#chat_" + $(this).data('id')).show();
      curr_team = $(this).data('id');
      $("button[data-id=" + curr_team + "]").addClass('active')
      $("#chatcontainer").scrollTop($("#chatcontainer")[0].scrollHeight);
    });
  }
$(document).ready(function() {
  map_buttons();
});
