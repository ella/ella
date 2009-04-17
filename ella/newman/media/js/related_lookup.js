(function($) {
    function set_lupicka_handlers() {
        $('.suggest-related-lookup').unbind('click').click( function(evt) {
            if (evt.button != 0) return;
            $lo = $('#lupicka-overlay');
            if ($lo.length == 0) {
                $lo = $('<div id="lupicka-overlay">').appendTo('body');
            }
            var input_id = this.id.replace(/lookup_/,'') + '_suggest';
            var inp = document.getElementById(input_id);
            if (!inp) {
                carp('Could not get suggester input for '+this.id);
                return;
            }
            $lo.data('related_input', inp);
            var href = $(this).attr('href');
            ContentByHashLib.simple_load('lupicka-overlay::::'+href);
            return false;
        });
    }
    $(document).bind('content_added', set_lupicka_handlers);
    $(document).bind('content_added', function() {
        var $lo = ContentByHashLib._injection_target('#lupicka-overlay');
        if ( ! $lo ) return;
        var inp = $lo.data('related_input');
        if (!inp) {
            carp('No input is set up for lupicka-overlay.');
            $lo.hide();
            return;
        }
        $lo.find('th a').unbind('click').click( function() {
            var id = $(this).attr('href').replace(/\/$/,'');
            var str = $(this).text();
            GenericSuggestLib.insert_value(id, str, inp);
            $lo.hide();
            return false;
        });
        $lo.show();
    })
    set_lupicka_handlers();
})(jQuery);
