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
    set_lupicka_handlers();
    $(document).bind('content_added', set_lupicka_handlers);
    $(document).bind('content_added', function(evt) {   // FIXME: reagovat na element.added
        var $lo = $(evt.target);
        if ( ! $lo.is('#lupicka-overlay') ) return;
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
        }).each( function() {
            this.onclick = undefined;
        });
        $('.popup-filter').click( function() {
            var lupicka_addr = ContentByHashLib.LOADED_URLS[ 'lupicka-overlay' ];
            var fakehash = '#' + get_hashadr(lupicka_addr);
            var href = get_hashadr('filters/', {hash:fakehash});
            ;;; carp('filters:', href);
            ContentByHashLib.simple_load('filters::'+href);
            return false;
        });
        $lo.show();
    });
})(jQuery);
