$(document).ready(function(){
  stage2Selection = 1;

  // Highlight on hover
  $(".reg_choice").hover(function(){
    $(this).css("background-color", "LightGrey");
  }, function(){
    $(this).css("background-color", "white");
  });

  // Make stage 2 divs clickable
  $(".reg_choice").click(function(){
    $("#stage2-" + stage2Selection).hide();
    stage2Selection = $(this).data("id")
    $("#stage2-" + $(this).data("id")).show();
    $("#stage1").fadeOut(500, function(){$("#stage2").fadeIn(500);});
  });

  // back buttons
  $(".back2to1").bind('click', function() {
    $("#stage2").fadeOut(500, function(){$("#stage1").fadeIn(500);});
  });

  // Stage2-1 Proccessing
  $('#newTeamForm').on('submit', function (e) {
    e.preventDefault();
    if($("#id_password").val() != $("#id_confirm_password").val()){
      alert("Passwords don't match");
      return false;
    }
    clean = true;
    $("#newTeamForm :input").each(function() {
      if($(this).val() === "")
        clean = false;
    });
    if(clean){
      $.ajax({
        url : $(this).attr('action') || window.location.pathname,
        type: "POST",
        data: $("#newTeamForm").serialize() + "&check=True",
        success: function(html){
          if(html == "fail"){ 
            alert("That team already exists");
          } else {
            $("#stage2").fadeOut(500, function(){$("#stage3").fadeIn(500);});
          }
        },
        error: function (jXHR, textStatus, errorThrown) {
          alert(errorThrown); 
        }
      });
    } else{
      alert("Please fill out form.");
    }
    return false;
  });

  // Stage2-2 Proccessing
  $('#existingTeamForm').on('submit', function (e) {
    if($("#existingTeamForm select").val() == ""){
      alert("Please pick a team.");
      return false;
    }
    e.preventDefault();
    $.ajax({
      url : $(this).attr('action') || window.location.pathname,
      type: "POST",
      data: $("#existingTeamForm").serialize() + "&validate=True",
      success: function(html){
        if(html == "fail-password"){
          alert("Incorrect password");
        }else if(html == "fail-full"){
          alert("Team is already full, contact team leader or staff.")
        }else{
          $("#stage2").fadeOut(500, function(){$("#stage3").fadeIn(500);});
        }
      },
      error: function (jXHR, textStatus, errorThrown) {
        alert(errorThrown);
      }
    });
    return false;
  });

  // Stage3 proccessing
  $('#individualForm').on('submit', function (e) {
    if(stage2Selection == 1){
      var data = $("#newTeamForm, #individualForm").serialize() + "&new=True";
    } else if(stage2Selection == 2){
      var data = $("#existingTeamForm, #individualForm").serialize() + "&existing=True";
    } else if(stage2Selection == 3){
      alert("This function is not yet ready");
    } else{
      alert("invalid stage 2 choice");
    }
    clean = true;
    $("#individualForm :input").each(function() {
      if($(this).val() === "" && $(this).attr("id") != "id_dietary_issues")
        clean = false;
    });
    if(clean){
      $.ajax({
        url : $(this).attr('action') || window.location.pathname,
        type: "POST",
        data: data,
        success: function (){
          $("#stage3").fadeOut(500, function(){$("#stage4").fadeIn(500);});
          window.setTimeout(function(){window.location.href = "/";}, 4000);
        },
        error: function (jXHR, textStatus, errorThrown) {
          alert(errorThrown);
        }
      });
    } else {
      alert("Please fill out form.");
    }
    return false;
  });
});