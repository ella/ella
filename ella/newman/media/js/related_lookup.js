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
            var str = arg.str;
            if (!str) {
                ;;; carp('No string representation of selected object received.');
                return false;
            }
            
            // The form could have been removed and re-loaded
            if ($(inp).closest('body').length == 0) inp = document.getElementById(inp.id);
            
            GenericSuggestLib.insert_value(id, str, inp);
            delete input;
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

// Lupicka for generic relations (content type & object id)
( function($) {
    function id2ct(id) {
        var ct = AVAILABLE_CONTENT_TYPES[ id ];
        if ( ! ct ) {
            carp('Unrecognized Content-Type id: '+id);
            return;
        }
        return ct.path;
    }
    function get_corresponding_input($i) {
        var $ct, $id, $givens, $soughts;
        var $ct_inputs = $('.target_ct');
        var $id_inputs = $('.target_id');
        if ($i.is('.target_id')) {
            $id = $i;
            $givens = $id_inputs;
            $soughts = $ct_inputs;
        }
        else if ($i.is('.target_ct')) {
            $ct = $i;
            $givens = $ct_inputs;
            $soughts = $id_inputs;
        }
        else {
            throw('Invalid input fed to get_corresponding_input.');
        }
        if ($ct_inputs.length != $id_inputs.length) {
            throw('Different number of content type inputs and object id inputs in document.');
        }
        for (var i = 0; i < $ct_inputs.length; i++) {
            if ($i.get(0) == $givens.get(i)) {
                return $soughts.eq(i);
            }
        }
        throw("Couldn't find the corresponding input to " + $i.attr('id'));
    }
    $('.generic-related-lookup').live('click', function() {
        // Look for the corresponding content type input and target id input
        var $id_input = $( '#' + this.id.replace(/^lookup_/, '') );
        var $ct_input = get_corresponding_input($id_input);
        if ($ct_input.length == 0) {
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
        var $id_input = get_corresponding_input($(this));
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

// Adding objects with lupička
(function($) {
    $('.js-adrstack-push').live('click', function(evt) {
        if (evt.button != 0) return;
        evt.preventDefault();
        NewmanLib.ADR_STACK.push( {
            from: get_hashadr(''),
            to: get_hashadr($(this).attr('href')),
            selection_callback: $(ContentByHashLib.closest_loaded(this).container).data('selection_callback'),
            form_data: JSON.stringify({ data: $('.change-form').serializeArray() }),
            onsave: function(popped, action_table_obj) {
                if (!action_table_obj.vars.object_id) {
                    ADR_STACK = [];
                    carp('Did not get ID of newly added object -- breaking ADR_STACK');
                    return;
                }
                popped.oid = action_table_obj.vars.object_id;
                popped.str = action_table_obj.vars.object_title;
            },
            onreturn: function(popped, action_table_obj) {
                NewmanLib.restore_form(popped.form_data, $('.change-form'), {});
                $(document).one('media_loaded', function(){popped.selection_callback(popped.oid,{str: popped.str});});
            }
        } );
        if (adr( $(this).attr('href'), {just_get: 'hash'} ) == location.hash) {
            ContentByHashLib.reload_content(ContentByHashLib.DEFAULT_TARGET);
        }
        else {
            adr( $(this).attr('href') );
        }
    });
})(jQuery);
