// Suggester input's lupicka
(function($) {
    $('.suggest-related-lookup').live('click', function(evt) {
        if (evt.button != 0) return;
        
        var content_type = /\/(\w+\/\w+)\/(?:\?|$)/.exec( $(this).attr('href') )[1];
        if ( ! content_type ) {
            carp('Lupicka has unexpected href format: '+this);
            return false;
        }
        
        var input_id = this.id.replace(/lookup_/,'') + '_suggest';
        var inp = document.getElementById(input_id);
        if (!inp) {
            carp('Could not get suggester input for '+this.id);
            return;
        }
        
        open_overlay(content_type, function(id, arg) {
            var $link = $(arg.evt.target);
            if ( $link.length == 0 ) {
                carp('Cannot determine which link was clicked');
                return false;
            }
            var str = $link.text();
            
            GenericSuggestLib.insert_value(id, str, inp);
        });
        return false;
    });
})(jQuery);

// Raw ID input's lupicka
(function($) {
    $('.rawid-related-lookup').live('click', function(evt) {
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
})(jQuery);

// Lupicka for listings
( function($) {
    $('.generic-related-lookup').live('click', function() {
        var id_stem = this.id.replace(/^lookup_/, '').replace(/_id$/, '');
        var $id_input = $('#'+id_stem+'_id');
        var $ct_input = $('#'+id_stem+'_ct');
        if ($id_input.length == 0 || $ct_input.length == 0) {
            carp('Could not find id input and/or content-type input for lupicka #'+this.id, this);
            return false;
        }
        var ct_id = $ct_input.val();
        if ( ! ct_id ) {
            $ct_input
            .addClass('highlighted')
            .focus()
            .change(function(){$(this).removeClass('highlighted')});
            return false;
        }
        var ct = AVAILABLE_CONTENT_TYPES[ ct_id ];
        if ( ! ct ) {
            carp('Unrecognized Content-Type id: '+ct_id);
            return false;
        }
        var content_type = ct.path.substr(1).replace(/\/$/, '').replace(/\//, '.');
        open_overlay(content_type, function(id) {
            $id_input.val( id );
        });
        return false;
    });
})(jQuery);
