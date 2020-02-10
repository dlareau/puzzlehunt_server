window.addEventListener("load", function() {
    (function($) {
    	function update_hidden(argument) {
    		var radio_val = $('input[name="unlock_type"]:checked').val();
	    	console.log(radio_val);
	    	$('.points_unlocking').show();
	   		$('.solve_unlocking').show();
	    	if(radio_val == 'SOL'){
	    		$('.points_unlocking').hide();
	    	}
	    	if(radio_val == 'POT'){
	    		$('.solve_unlocking').hide();
	    	}
    	}
    	$('input[type=radio][name=unlock_type]').change(function() {
    		update_hidden();
		});
		update_hidden();
    })(django.jQuery);
});