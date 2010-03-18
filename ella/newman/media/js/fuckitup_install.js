
$(function(){
    $(document).bind(
        'media_loaded',
        function () {
            // enable NewmanTextArea (replacement for markItUp!)
            $('.rich_text_area').newmanTextArea();
        }
    );
});
