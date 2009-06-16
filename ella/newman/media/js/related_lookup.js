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
        
        open_overlay(content_type, function(id, extras) {
            $target_input.val(id);
            $target_input.trigger('change', [extras]);
        });
        
        return false;
    });
})(jQuery);

// Lupicka for listings
( function($) {
    function id2ct(id) {
        var ct = AVAILABLE_CONTENT_TYPES[ id ];
        if ( ! ct ) {
            carp('Unrecognized Content-Type id: '+id);
            return;
        }
        return ct.path;
    }
    $('.generic-related-lookup').live('click', function() {
        var id_stem = this.id.replace(/^lookup_/, '').replace(/_id$/, '');
        var $id_input = $('#'+id_stem+'_id');
        var $ct_input = $('#'+id_stem+'_ct');
        if ($id_input.length == 0) {
            carp('Could not find id input for lupicka (#'+id_stem+'_id); this:', this);
            return false;
        }
        if ($ct_input.length == 0) {
            carp('Could not find content-type input for lupicka (#'+id_stem+'_ct); this:', this);
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
        var content_type = id2ct(ct_id);
        open_overlay(content_type, function(id, extras) {
            $id_input.val(id);
            $id_input.trigger('change', [extras]);
        });
        return false;
    });
    
    // When content-type is selected, no need to wait for lupicka to be clicked. Fire the overlay right away.
    function open_overlay_on_ct_selection() {
        var ct_id = $(this).val();
        if ( ! ct_id ) return;
        var content_type = id2ct(ct_id);
        var id_input_id = this.id.replace(/ct$/, 'id');
        if (id_input_id == this.id) {
            carp('Error attempting to attach open_overlay to select.target_ct onchange: Unexpected ID: '+this.id, this);
            return;
        }
        var $id_input = $('#'+id_input_id);
        if ($id_input.length == 0) {
            carp('Error attempting to attach open_overlay to select.target_ct onchange: Failed to get ID input #'+id_input_id);
            return;
        }
        open_overlay(content_type, function(id, extras) {
            $id_input.val(id);
            $in_input.trigger('change', [extras]);
        });
    }
    $('select.target_ct').unbind('change', open_overlay_on_ct_selection).bind('change', open_overlay_on_ct_selection);
    $(document).bind('content_added', function(evt) {
        var $target = $(evt.target);
        var $ct_sel = $target.find('select.target_ct');
        if ($ct_sel.length == 0) return;
        $ct_sel.unbind('change', open_overlay_on_ct_selection).bind('change', open_overlay_on_ct_selection);
    });
})(jQuery);
