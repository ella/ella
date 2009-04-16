(function($) {
    function set_lupicka_handlers() {
        $('.suggest-related-lookup').unbind('click').click( function(evt) {
            if (evt.button != 0) return;
            $lo = $('#lupicka-overlay');
            if ($lo.length == 0) {
                $lo = $('<div id="lupicka-overlay">').appendTo('body');
            }
            var href = $(this).attr('href');
            $lo.show();
            adr('#lupicka-overlay::::'+href);
            return false;
        });
    }
    $(document).bind('content_added', set_lupicka_handlers);
    set_lupicka_handlers();
})(jQuery);
