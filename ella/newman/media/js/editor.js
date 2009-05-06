$(function(){
    $('.rich_text_area').markItUp(mySettings);
});
$(document).bind('content_added', function(evt) {
    $(evt.target).find('.rich_text_area').markItUpRemove().markItUp(mySettings);
});
