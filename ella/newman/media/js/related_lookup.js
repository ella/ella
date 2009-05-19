// Suggester input's lupicka
(function($) {
    function set_lupicka_handlers() {
        $('.suggest-related-lookup').unbind('click').click( function(evt) {
            if (evt.button != 0) return;
            $lo = $('#lupicka-overlay');
            if ($lo.length == 0) {
                $lo = $('<div id="lupicka-overlay" class="pop">').appendTo('body');
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
            // FIXME: Filters still bogus!
            $('#filters').one('content_added', function() {
                $(this).find('.filter li a').each( function() {
                    $(this).attr('href', $(this).attr('href').replace(/^\?/, 'filters::&')).addClass('simpleload');
                });
            });
            return false;
        });
        $lo.show();
    });
})(jQuery);

// Raw ID input's lupicka
(function($) {
    $('.rawid-related-lookup').click( function(evt) {
        if (evt.button != 0) return;
        
        // From '../../core/author/?pop' take 'core/author'
        var re_res = /([^\/]+)\/([^\/]+)\/(?:$|[?#])/.exec( $(this).attr('href') );
        if (!re_res) {
            carp('Unexpected href of related lookup:', $(this).attr('href'));
            return false;
        }
        var content_type = re_res[1] + '.' + re_res[2];
        
        var $target_input = $( '#' + this.id.replace(/^lookup_/, '') );
        if ($target_input.length == 0 || $target_input.attr('id') == this.id) {
            carp('Could not get raw id input from lupicka icon #'+this.id);
            return false;
        }
        
        open_overlay(content_type, function(id) {
            $target_input.val(id);
        });
        
        return false;
    });
})(jQuery)
