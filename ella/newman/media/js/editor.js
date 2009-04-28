$(function(){
	$('.rich_text_area').markItUp(CTTASettings);
});
$(document).bind('content_added', function() {
	$('.rich_text_area').markItUpRemove().markItUp(CTTASettings);
});
