$(function(){
	$('.rich_text_area').markItUp(mySettings);
});
$(document).bind('content_added', function() {
	$('.rich_text_area').markItUpRemove().markItUp(mySettings);
});
