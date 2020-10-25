function reload_table(refresh_url, selected_dice) {
	$.ajax({
		method: 'GET',
		url: refresh_url,
		data: selected_dice,
		dataType: 'html',
		success: function (data) {
			$( "#dicetable" ).html( data );
			bind_select_dice();
			bind_table_dice();
			turn_on_roll();
			bind_next_player();
		}
	});
}

function bind_table_dice() {
	$('input#tabledice').click(function(event){
		var selected_dice = {};
		var target_url = $(this).attr('data-check-url');
		var refresh_url = $(this).attr('data-select-url');
		$('.dice-selected').each(function(){
			selected_dice[$(this).attr('id')] = $(this).attr('data-dice-value');
		});
		$.ajax({
			method: 'GET',
			url: target_url,
			data: selected_dice,
			dataType: 'json',
			success: function (data) {
				if(data['valid_selection']) {
					reload_table(refresh_url, selected_dice);
		  			reload_history();
				} else {
					alert('That is not a scoring hand. Try again');
				}
			}
		});
	});
}

function bind_select_dice() {
	$('img.dice').each(function(){
		$(this).click(function(){
			if ($(this).hasClass('dice-selected')) {
				$(this).removeClass('dice-selected');
			} else {
				$(this).addClass('dice-selected');
			}
		});
	});
}

function turn_off_roll() {
	$('input#rolldice').css('display', 'none');
}

function turn_on_roll() {
	$('input#rolldice').css('display', 'block');
}

function reload_history() {
	var target_url = $('input#history-url').val();
	$.ajax({
		method: 'GET',
		url: target_url,
		dataType: 'html',
		success: function (data) {
			$('div#historyboard').html(data);
		}
	});
}

function bind_roll_dice() {
	$('input#rolldice').click(function(event){
		var target_url = $(this).attr('data-target-url');
		$.get( target_url, function( data ) {
		  $( "#dicetable" ).html( data );
		  turn_off_roll();
		  bind_select_dice();
		  bind_table_dice();
		  bind_next_player();
		  reload_history();
		});
	});
}

function bind_next_player() {
	$('input#nextplayer').click(function(){
		window.location.replace($(this).attr('data-target-url'));
	});
}

$(document).ready(function(){
	bind_roll_dice();
});