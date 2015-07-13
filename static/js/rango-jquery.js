$(document).ready( function(){

	$("#about-btn").click( function(event) {
		alert("You clicked the button using JQuery!")
	});

	$("p").hover(function(){
		$(p).css('color', 'red');
	},
	function(){
		$(p).css('color', 'blue');
	});

	$("#about-btn").click( function(event){
	msgstr = $("#msg").html()
		msgstr = msgstr + "o"
		$("#msg").html(msgstr)
	});

});
