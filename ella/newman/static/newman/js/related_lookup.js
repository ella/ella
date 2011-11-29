/**
 * Common utilities/functions and objects.
 * requires: jQuery 1.4.2+, 
 *          LoggingLib object (utils.js).
 */
// related lookup logging
log_lookup = new LoggingLib('RELATED LOOKUP:', true);

// Suggester input's lupicka
(function($) {
    $('.suggest-related-lookup').live('click', function(evt) {
        if (evt.button != 0) return;
        
        var content_type = /\/(\w+\/\w+)\/(?:\?|$)/.exec( $(this).attr('href') )[1];
        if ( ! content_type ) {
            log_lookup.log('Lupicka has unexpected href format: '+this);
            return false;
        }
        
        var input_id = this.id.replace(/lookup_/,'') + '_suggest';
        var inp = document.getElementById(input_id);
        if (!inp) {
            log_lookup.log('Could not get suggester input for '+this.id);
            return;
        }
        
        open_overlay(content_type, function(id, arg) {
            var str = arg.str;
            if (!str) {
                ;;; log_lookup.log('No string representation of selected object received.');
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
    function rawid_related_lookup_update_photo($input, id, extras) {
        function process_update(response_text, text_status, xhr) {
            var $img = $thumb.find('img');
            if ($img.length == 0) return;
            var json_result = JSON.parse(response_text);
            if ( typeof(json_result.data) == 'undefined' ) {
                log_lookup.log('WARNING: No data in JSON received');
                return;
            }
            var image_path = str_concat(DJANGO_MEDIA_URL, json_result.data.image);
            // Because of hardcoded thumbnail filename in ella.photos.models 
            // (neither thumbnail filename nor URL is saved in database), 
            // we should add prefix thumb- to the received photo filename.
            var re_photo = /(.*\/)([\w_\-\.]+.jpg)$/i;
            NewmanLib.debug_image_path = image_path;
            var new_path = image_path.replace( re_photo, str_concat('$1', 'thumb-', '$2') );
            $img.attr('src', new_path);
            var $img_anchor = $thumb.find('a.js-nohashadr');
            $img_anchor.attr('href', image_path);
            $img_anchor.attr('title', json_result.data.title);
            
            // change text and href of anchor element:
            $anchor.attr( 'href', str_concat(BASE_URL, 'photos/photo/', id) );
            $anchor.text( json_result.data.title );
        }

        var $anchor = $input.siblings('a.js-hashadr:first');
        var $thumb = $input.siblings('span.widget-thumb');
        if ($thumb.length > 0) {
            var ajax_parms = {
                async: true,
                url: str_concat(BASE_URL, 'photos/photo/', id, '/json/detail/'),
                success: try_decorator(process_update),
            };
            $.ajax(ajax_parms);
        }
    }

    function rawid_related_lookup_click_handler(evt) {
        function overlay_callback(id, extras) {
            $target_input.val(id);
            $target_input.trigger('change', [extras]);
            // try to change photo (if rawid-related-lookup is for photo)
            rawid_related_lookup_update_photo($target_input, id, extras);
            log_lookup.log('photo updated');
        } 

        if (evt.button != 0) return;
        
        // From '../../core/author/?pop' take 'core/author'
        var re_res = /([^\/]+)\/([^\/]+)\/(?:$|[?#])/.exec( $(this).attr('href') );
        if (!re_res) {
            log_lookup.log('Unexpected href of related lookup:', $(this).attr('href'));
            return false;
        }
        var content_type = re_res[1] + '.' + re_res[2];
        
        var $target_input = $( '#' + this.id.replace(/^lookup_/, '') );
        if ($target_input.length == 0 || $target_input.attr('id') == this.id) {
            log_lookup.log('Could not get raw id input from lupicka icon #'+this.id);
            return false;
        }
        log_lookup.log('Opening overlay...');
        open_overlay(content_type, overlay_callback);
        log_lookup.log('overlay opened.');
        
        return false;
    }

    $('.rawid-related-lookup').live('click', rawid_related_lookup_click_handler);
})(jQuery);

// Lupicka for generic relations (content type & object id)
( function($) {
    function id2ct(id) {
        var ct = AVAILABLE_CONTENT_TYPES[ id ];
        if ( ! ct ) {
            log_lookup.log('Unrecognized Content-Type id: '+id);
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
    function click_live_handler() {
        // Look for the corresponding content type input and target id input
        log_lookup.log('CALL.generic-related-lookup');
        var $id_input = $( '#' + this.id.replace(/^lookup_/, '') );
        var $ct_input = get_corresponding_input($id_input);
        if ($ct_input.length == 0) {
            return false;
        }
        var ct_id = $ct_input.val();
        NewmanLib.debug_ct_input = $ct_input;
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
    }
    $('.generic-related-lookup').live('click', click_live_handler);
    
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
            selection_callback: $(Kobayashi.closest_loaded(this).container).data('selection_callback'),
            form_data: JSON.stringify({ data: $('.change-form').serializeArray() }),
            onsave: function(popped, action_table_obj) {
                if (!action_table_obj.vars.object_id) {
                    ADR_STACK = [];
                    log_lookup.log('Did not get ID of newly added object -- breaking ADR_STACK');
                    return;
                }
                popped.oid = action_table_obj.vars.object_id;
                popped.str = action_table_obj.vars.object_title;
            },
            onreturn: function(popped, action_table_obj) {
                $(document).one('content_added', function(evt) {
                    NewmanLib.restore_form(popped.form_data, $('.change-form'), {});
                });
                $(document).one('media_loaded', function(){popped.selection_callback(popped.oid,{str: popped.str});});
            }
        } );
        if (adr( $(this).attr('href'), {just_get: 'hash'} ) == location.hash) {
            Kobayashi.reload_content(Kobayashi.DEFAULT_TARGET);
        }
        else {
            adr( $(this).attr('href') );
        }
    });
})(jQuery);
