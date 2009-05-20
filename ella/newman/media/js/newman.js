var LF = 10, CR = 13;

function clone_form($orig_form) {
    var $new_form = $orig_form.clone();
    var $orig_textareas = $orig_form.find('textarea');
    var  $new_textareas =  $new_form.find('textarea');
    for (var i = 0; i < $orig_textareas.length; i++) {
        $new_textareas.eq(i).val(
            $orig_textareas.eq(i).val()
        );
    }
    var $orig_selects = $orig_form.find('select');
    var  $new_selects =  $new_form.find('select');
    for (var i = 0; i < $orig_selects.length; i++) {
        var $orig_options = $orig_selects.eq(i).find('option');
        var  $new_options =  $new_selects.eq(i).find('option');
        for (var j = 0; j < $orig_options.length; j++) {
            if ($orig_options.eq(j).is(':selected')) {
                $new_options.eq(j).attr({selected:'selected'})
            }
        }
    }
    return $new_form;
}

//// Homepage initialization

$(function(){ContentByHashLib.reload_content('content');});

//// Drafts and templates
(function() {
    var draft_id;
    function save_preset($form, options) {
        var form_data = JSON.stringify( $form.serializeArray() );
        var things_to_send = {data: form_data};
        if (!options) options = {};
        if (options.title) things_to_send.title = options.title;
        if (options.id   ) things_to_send.id    = options.id;
        var url = get_adr('draft/save/');
        var $saving_msg = show_message(_('Saving')+'...', {duration: 0});
        $.ajax({
            url: url,
            data: things_to_send,
            type: 'POST',
            success: function(response_text) {
                $saving_msg.remove();
                show_ok(_('Saved')+'.', {duration: 2000});
                try {
                    var response_data = JSON.parse(response_text);
                    var id           = response_data.data.id;
                    var actual_title = response_data.data.title;
                    if (options.id) {    // We were overwriting -- remove old version
                        $('#id_drafts option').filter(function() {
                            return $(this).val() == id;
                        }).remove();
                    }
                    else {
                        draft_id = id;
                    }
                    $('#id_drafts option:first').after(
                        $('<option>').attr({value: id}).html(actual_title)
                    );
                } catch(e) {
                    show_err(_('Preset saved but erroneous result received.')+' '+_('Reload to see the preset.'));
                }
            },
            error: function(xhr) {
                $saving_msg.remove();
                show_ajax_error(xhr);
            }
        });
    }
    $('a#save-form').live('click', function() {
        var title = prompt(_('Enter template name'));
        if (title == null) return;
        title = $.trim(title);
        // retrieve the id of template with this name
        // TODO: to be rewritten (saving interface needs a lift)
        var id = 
            title
            ? $('#id_drafts option').filter(function(){return $(this).text().indexOf(title+' (') == 0}).val()
            : draft_id;
        save_preset($('.change-form'), {title:title, id:id});
        return false;
    });
    
    function restore_form(response_text, $form) {
        var response_data;
        try {
            response_data  = JSON.parse(response_text);
        } catch(e) {
            show_err(_('Failed loading preset'));
            return;
        }
        $form.get(0).reset();
        $form.find(':checkbox,:radio').removeAttr('checked');
        $form.find(':text,textarea,:password').val('');
        var form_data = response_data.data;
        show_message( response_data.message );
        for (var i = 0; i < form_data.length; i++) {
            var form_datum = form_data[i];
            var key = form_datum['name'];
            var val = form_datum['value'];
            var $inputs = $form.find(':input[name='+key+']');
            if (!$inputs || $inputs.length == 0) {
                carp('restore_form: input #'+key+' not found');
                continue;
            }
            var val_esc = val.replace(/\W/g, '\\$1');
            $inputs.filter(':checkbox,:radio').find('[value='+val_esc+']').attr({checked: 'checked'});
            $inputs.filter('option[value='+val_esc+']').attr({selected: 'selected'});
            $inputs.filter(':text,[type=hidden],textarea').val(val);
            $form.find('.GenericSuggestField,.GenericSuggestFieldMultiple').find('input[rel]').each(function() {
                restore_suggest_widget_from_value(this);
            });
        }
    }
    function load_preset(id, $form) {
        $.ajax({
            url: get_adr('draft/load/'),
            data: {id:id},
            success: function(response_text) {
                restore_form(response_text, $form);
            },
            error: show_ajax_error
        });
    }
    function load_draft_handler() {
        var id = $(this).val();
        if (!id) return;
        load_preset(id, $('.change-form'));
    }
    function set_load_draft_handler() {
        $('#id_drafts').unbind('change', load_draft_handler).change(load_draft_handler);
    }
    set_load_draft_handler();
    $(document).bind('content_added', set_load_draft_handler);
    
    var autosave_interval;
    function set_autosave_interval(evt) {
        var proceed, target_ids;
        
        if ($('.change-form').length == 0) { // nothing to autosave
             ;;; carp('.change-form not present -- not setting up interval');
             clearInterval(autosave_interval);
             proceed = false;
        }
        else if ( evt && evt.type == 'content_added' ) {
            if ( $(evt.target).find('.change-form').length ) {
                ;;; carp('waiting for form to change to set up autosave interval');
                proceed = true; // .change-form was just loaded
            }
            else {  // .change-form was there before -- don't touch it
                ;;; carp('.change-form not in loaded stuff -- letting it alone');
                proceed = false;
            }
        }
        else {
            ;;; carp('no injection storage found -- interval reset forced');
            proceed = true;
        }
        
        if (!proceed) return;
        
        if (autosave_interval != undefined) {
            ;;; carp('clearing interval prior to setting new one');
            clearInterval(autosave_interval);
        }
        var $inputs = $('.change-form :input');
        function onchange_autosave_handler() {
            $('.change-form :input').unbind('change', onchange_autosave_handler).unbind('keypress', onkeypress_autosave_handler);
            ;;; carp('.change-form changed -- setting up autosave interval');
            autosave_interval = setInterval( function() {
                var $change_form = $('.change-form');
                if ($change_form.length == 0) {
                    ;;; carp('.change-form disappeared -- clearing interval');
                    clearInterval(autosave_interval);
                    autosave_interval = undefined;
                    return;
                }
                carp('Saving draft '+new Date());
                save_preset($('.change-form'), {id: draft_id});
            }, 60 * 1000 );
        }
        function onkeypress_autosave_handler(evt) {
            var w = evt.which;
            var c = evt.keyCode;
            if (   w >= 32 && w <= 126  // ASCII printable chars
                || w >= 160             // Unicode
                || w == 8               // backspace
                || c == 46              // delete
            ) {
                onchange_autosave_handler();
            }
            else if (
                   $(this).is('textarea')
                && (w == 10 || w == 13) // enter
            ) {
                onchange_autosave_handler();
            }
            return true;
        }
        $inputs.bind('change', onchange_autosave_handler).filter('textarea,[type=text]').bind('keypress', onkeypress_autosave_handler);
    }
    set_autosave_interval();
    $(document).bind('content_added', set_autosave_interval);
})();
// End of drafts and templates


AjaxFormLib = {};
$( function() {
    //// Ajax forms
    
    function get_inputs($form) {    // all except metadata
        return $form.find(':input').filter(function() {
            return ! $(this).parent().is('.form-metadata');
        });
    }
    
    // Validate
    var validations = {
/*        required: function(input) {
            if ($(input).val()) return false;
            else return _('Field cannot be blank.');
        }*/
    };
    AjaxFormLib.validations = validations;
    function show_form_error(input, msg) {
        if (!input) {
            carp("Attempt to render error for empty input:", msg);
            return;
        }
        if (msg.shift) { var msgs = msg; msg = msgs.shift(); }
        var $msg = $('<span>').addClass('form-error-msg').text(msg);
        $('label[for='+input.id+']').append($msg);
        if (msgs && msgs.length) show_form_error(input, msgs);
    }
    /**
     * Automatic class-driven validation.
     * For each :input in the form, find its label and check if some of the label's classes
     * isn't in the validations object. If so, then run the function passing it the input.
     * If it returns *FALSE*, then this input *VALIDATES*.
     * If it returns a true value, it is used as the error message and passed to show_form_error.
     */
    function validate($form) {
        var ok = true;
        get_inputs($form).each( function() {
            var $label = $('label[for='+this.id+']');
            $label.find('span.form-error-msg').remove();
            $('#err-overlay').empty().hide();
            var classes = ($label.attr('className')||'').split(/\s+/);
            for (var i = 0; i < classes.length; i++) {
                var cl = classes[i];
                if ($.isFunction(validations[ cl ])) {
                    var err = validations[ cl ](this);
                    if (err) {
                        show_form_error(this, err);
                        ok = false;
                    }
                }
            }
        });
        return ok;
    }
    
    // Submit event
    function ajax_submit($form, button_name) {
        if (!$form.jquery) $form = $($form);
        if ( ! validate($form) ) return false;
        var action =  $form.attr('action');
        var method = ($form.attr('method') || 'POST').toUpperCase();
        var $meta = $form.find('.form-metadata:first');
        var $success = $meta.find('input[name=success]');
        var $error   = $meta.find('input[name=error]');
        var success, error;
        if ($success && $success.length) {
            success = function(data) { $success.get(0).onchange(data, this); };
        }
        else {
            success = show_ajax_success;
        }
        if ($error && $error.length) {
            error = function(xhr, st) { $error.get(0).onchange(xhr, st); };
        }
        else {
            error = ajax_submit_error;
        }
        // Process the inputs prior to sending
        var $inputs = $('#absolutely#_nothing');
        get_inputs($form).each( function() {
            // Don't send suggest inputs
            if ( /(.*)_suggest$/.test($(this).attr('id')) ) {
                return;
            }
            // Shave off the names from suggest-enhanced hidden inputs
            if ( $(this).is('input:hidden') && $form.find( '#'+$(this).attr('id')+'_suggest' ).length ) {
                $inputs = $inputs.add(   $(this).clone().val( $(this).val().replace(/#.*/, '') )   );
                return;
            }
            // Shave off the days of week from date-time inputs
            if ( $(this).is('.vDateTimeInput,.vDateInput') ) {
                $inputs = $inputs.add(   $(this).clone().val( $(this).val().replace(/ \D{2}$/, '') )   );
                return;
            }
            $inputs = $inputs.add($(this));
        });
        
        if (button_name) $inputs = $inputs.add('<input type="hidden" value="1" name="'+button_name+'" />');
        var data = $inputs.serialize();
        if ($form.hasClass('reset-on-submit')) $form.get(0).reset();
        var url = $form.hasClass('dyn-addr')
            ? get_adr(action)
            : action;
        url = $('<a>').attr('href', url).get(0).href;
        
        var request_options = {
            url: url,
            type: method,
            data: data,
            success: success,
            error:   error,
            _form: $form,
            _button_name: button_name
        };
        if (button_name) request_options._button_name = button_name;
        
        $.ajax( request_options );
        return false;
    }
    AjaxFormLib.ajax_submit = ajax_submit;
    
    function ajax_submit_error(xhr) {
        var res;
        try { res = JSON.parse( xhr.responseText ); }
        catch (e) { }
        if (res && res.errors) {
            // Show the bubble with scrollto buttons
            var $err_overlay = $('#err-overlay');
            if ($err_overlay.length == 0) $err_overlay = $(
                '<div id="err-overlay" class="overlay">'
            ).appendTo(
                   $('.change-form').get(0)
                || $('#content').get(0)
                || $('body').get(0)
            );
            
            // Show the individual errors
            for (var id in res.errors) {
                var msgs = res.errors[ id ];
                var input = $('#'+id).get(0);
                show_form_error(input, msgs);
                if (!input) carp('Error reported for nonexistant input #'+id);
                
                $('<p>')
                .data('rel_input',
                      !input                             ? null
                    : $('#'+input.id+'_suggest').length  ? $('#'+input.id+'_suggest').get(0) // take suggest input if available
                    :                                      input                             // otherwise the input itself
                )
                .text(
                    ($('label[for='+id+']').text() || id).replace(/:$/,'')  // identify the input with its label text or id; no trailing ':' pls
                )
                .click( function(evt) { // focus and scroll to the input
                    if (evt.button != 0) return;
                    var input = $(this).closest('p').data('rel_input');
                    try { input.focus(); } catch(e) {}
                    return false;
                })
                .appendTo($err_overlay);
            }
            $err_overlay.show();
        }
        show_ajax_error(xhr);
    }
    AjaxFormLib.ajax_submit_error = ajax_submit_error;
    
    // Submit button
    $('.ajax-form a.ok').live('click', function(evt) {
        if (evt.button != 0) return true;    // just interested in left button
        if ($(this).hasClass('noautosubmit')) return true;
        var $form = $(this).closest('.ajax-form');
        ajax_submit($form, this.name);
        return false;
    });
    
    // Reset button
    $('.ajax-form a.eclear').live('click', function(evt) {
        try {
            $(this).closest('form').get(0).reset();
        } catch(e) { }
        return false;
    });
    
    // Overload default submit event
    function overload_default_submit() {
        $('.ajax-form')
        .unbind('submit.ajax_overload')
        .bind('submit.ajax_overload', function(evt) {
            var name;
            function get_def(form) { return $(form).find('.def:first').attr('name'); }
            if (!evt.originalEvent) name = get_def(this);
            else try {
                // Try to figure out the submit button used.
                var initiator = evt.originalEvent.explicitOriginalTarget;
                if (initiator.type == 'submit')
                    name = initiator.name;
                else
                    name = get_def(this);
            } catch(e) {
                // Event is defined but failed to figure out which button clicked
                // -- leave the name empty.
            }
            AjaxFormLib.ajax_submit( $(this), name );
            return false;
        });
    }
    $(document).bind('content_added', overload_default_submit);
    overload_default_submit();
    //// End of ajax forms
    
    //// Filters
    
    // Packing and unpacking filter list. To be removed when filters are reimplemented.
    $('#filters :header').live('click', function(evt) {
        if (evt.which != 1) return true;    // just interested in left button
        var $affected = $(this).next(':first').filter('ul');
        if ($affected.is(':hidden')) {
            $(this).siblings('ul').hide();
        }
        $affected.slideToggle('slow');
    });
    
    // Persistent filters -- add the query string if:
    // - there is none AND
    // - one is there for the specifier's URL in the changelistFilters object
    $(document).bind('ready', function() {
        if (!window.changelistFilters || typeof changelistFilters != 'object') return;
        for (a in changelistFilters) {
            var adr = a.replace(/^filter/, '').replace(/__/g, '/') + '/';
            var decoded = $('<span>').html(changelistFilters[a]).text()
            ContentByHashLib.ADDRESS_POSTPROCESS[ adr ] = adr + decoded;
        }
    });
    
    // Update persistent filters when filter clicked
    $('#filters a').live('click', function(evt) {
        if (evt.button != 0) return;    // only interested in left click
        var href = $(this).attr('href');
        if (   /^\?/.test( href )   ) {} else return;
        var base = get_hashadr('?').replace(/\?$/,'');
        ContentByHashLib.ADDRESS_POSTPROCESS[ base ] = base+href;
        var pop_id;
        if ( pop_id = $(this).closest('.pop').attr('id') ) {
            ContentByHashLib.simple_load(
                pop_id
                + '::' +
                ContentByHashLib.LOADED_URLS[ pop_id ]
                + '::' +
                href
            );
        }
        else {
            adr(href);
        }
        return false;
    });
    $('#filters-handler .eclear').live('click', function() {
        var base = get_hashadr('?').replace(/\?$/,'');
        delete ContentByHashLib.ADDRESS_POSTPROCESS[ base ];
        adr($(this).attr('href'));
        return false;
    });
    
    // Re-initialization of third party libraries
    /*
    $(document).bind('content_added', function() {
    });
    */
    
    // Initialization of JavaScripts
    /*
    $(document).bind('media_loaded', function() {
        var loaded_media = $(document).data('loaded_media');
        if (loaded_media[ MEDIA_URL + 'js/admin/DateTimeShortcuts.js' ]) {
            DateTimeShortcuts.admin_media_prefix = MEDIA_URL;
            DateTimeShortcuts.init();
        }
        delete loaded_media[ MEDIA_URL + 'js/admin/DateTimeShortcuts.js' ];
    });
    */
    // Setting up proper suggesters URLs to take the hash address into account
    $(document).bind('content_added', function(evt) {
        var $new_suggest_inputs = $(evt.target).find('.GenericSuggestField,.GenericSuggestFieldMultiple');
        if (!$new_suggest_inputs || $new_suggest_inputs.length == 0) return;
        $new_suggest_inputs.find('input[rel]').each(function() {
            if ($(this).data('original_rel')) return;
            var old_rel = $(this).attr('rel');
            $(this).attr(
                'rel', get_adr(old_rel)
            ).data(
                'original_rel', old_rel
            );
        });
    });
    
    // Search on HP
    // The search button should send us to an address according to the thing selected in the select
    function do_search() {
        var $form = $('#search-form');
        var option = $form.find('select[name=action] option[selected]').val();
        if (!option) return false;
        var search_terms = $form.find('input[name=q]').val();
        var url = option + '?q=' + search_terms;
        adr(url);
        return false;
    }
    $('#search-form a.search.btn').live('click', do_search);
    function search_on_enter(evt) {
        if (evt.keyCode == CR || evt.keyCode == LF) {
            do_search();
            return false;
        }
    }
    $('#search-form input[name=q]'      ).live('keypress', search_on_enter);
    $('#search-form select[name=action]').live('keypress', search_on_enter);
    
    // Search in change lists
    $('#filters-handler .btn.search').live('click', function(evt) {
        if (evt.button != 0) return;
        if ($('#changelist').length == 0) return;   // We're not in changelist
        var search_terms = $(this).prev('input#searchbar').val();
        if (!search_terms) return;  // Nothing to search for
        var adr_term = '&q=' + search_terms;
        adr(adr_term);
        return false;
    });
});

// Message bubble
function show_message(message, options) {
    if (!options) options = {};
    var duration = (options.duration == undefined) ? 5000 : options.duration;
    var $span = $('<span></span>').html(message);
    var $msg = $('<br />').add($span);
    if (options.msgclass) $span.addClass(options.msgclass);
    $('#opmsg').append($msg);
    if (duration) setTimeout(function() {
        $span.fadeOut('slow', function(){ $msg.remove(); });
    }, duration);
    return $msg;
}
function show_ok(message, options) {
    if (!options) options = {};
    if (!options.msgclass) options.msgclass = 'okmsg';
    show_message(message, options);
}
function show_err(message, options) {
    if (!options) options = {};
    if (!options.msgclass) options.msgclass = 'errmsg';
    show_message(message, options);
}


// The 'loading...' message
//                How many things need the loading message shown concurrently
var $LOADING_MSG, LOADING_CNT = 0;
function show_loading() {
    LOADING_CNT++;
    if ($LOADING_MSG) return;
    $LOADING_MSG = show_message(_('loading')+'...', {duration:0});
}
function hide_loading() {
    if ($LOADING_MSG) $LOADING_MSG.remove();
    LOADING_CNT = 0;
    $LOADING_MSG = undefined;
}
function dec_loading() {
    if (--LOADING_CNT <= 0) {
        LOADING_CNT = 0;
        hide_loading();
    }
}

function paste_code_into_debug(code, description) {
    $('#debug').append(
        $('<div>').addClass('debug-codeframe').append(
            $('<p>').click(function() {
                $(this).next().toggle();
            }).text( (description || 'CODE') + '+' )
            .add( $('<div>').css({ display: 'none', whiteSpace: 'pre' }).text(code) )
        )
    );
}

function show_ajax_error(xhr) {
    var message, data;
    try {
        data = JSON.parse(xhr.responseText);
        message = data.message;
    } catch(e) {
        message = _('Request failed')+' ('+xhr.status+': '+_(xhr.statusText)+')';
        paste_code_into_debug( xhr.responseText.replace(/\n(\s*\n)+/g, "\n"), 'Ajax error response' );
    }
    show_err(message);
}
function show_ajax_success(response_text) {
    var message, data;
    try {
        data = JSON.parse(response_text);
        message = data.message;
    } catch (e) {
        message = _('Successfully sent');
        paste_code_into_debug( response_text.replace(/\n(\s*\n)+/g, "\n"), 'Ajax success response' );
    }
    show_ok(message);
}


// submit line (save, save as new, etc)
function save_change_form_success(text_data, options) {
    if (!options || !options._button_name || !options._form) {
        var message;
        if (!options) message = 'No XHR options passed to save_change_form_success';
        else if (!options._form) message = '_form not set in the XML HTTP Request for change_form submit';
        else if (!options._button_name) message = '_button_name not set in the XML HTTP Request for change_form submit';
        carp(message);
        show_ajax_success(text_data);
        show_err(_('Failed to follow form save with a requested action'));
        return;
    }
    var $form = options._form;
    var action = options._button_name;
    var data, object_id, response_msg;
    try {
        data = JSON.parse(text_data);
        object_id = data.data.id;
        response_msg = data.message;
    } catch(e) { carp('invalid data received from form save:', text_data, e); }
    response_msg = response_msg || _('Form saved');
    var action_table = {
        _save_: function() {
            adr('../');
        },
        _addanother_: function() {
            if ( /add\/$/.test(get_hashadr('')) ) {
                $form.get(0).reset();
                scrollTo(0,0);
            }
            else {
                adr('../add/');
            }
        },
        _continue_: function() {
            if ( /add\/$/.test(get_hashadr('')) ) {
                if (!object_id) {
                    var message = 'Cannot continue editing (object ID not received)'
                    show_err(message);
                    carp(message, 'xhr options:', options);
                    adr('../');
                    return;
                }
                adr('../'+object_id+'/');
            }
            // else do nothing
        },
        _saveasnew_: function() {
            if (!object_id) {
                show_err(_('Failed to redirect to newly added object.'));
                carp('Cannot redirect to newly added object: ID not received.');
            }
            else {
                adr('../'+object_id+'/');
            }
        },
        run: function(action) {
            var a = action+'_';
            if (action_table[ a ]) {
                action_table[ a ]();
            }
            else {
                var message = action
                    ? 'Unrecognized post-save action: '+action
                    : 'No post-save action, redirecting to change list';
                show_message(message);
                carp(message);
            }
        }
    };
    show_ok(response_msg);
    action_table.run(action);
    ContentByHashLib.unload_content('history');
}

function changelist_batch_success(response_text) {
    var $dialog = $('<div id="confirmation-wrapper">');
    $dialog.html(response_text).find('.cancel').click(function() {
        $dialog.remove();
        $('#content').show();
    });
    $('#content').hide().before($dialog);
}
function batch_delete_confirm_complete() {
    ContentByHashLib.reload_content('content');
    $('#confirmation-wrapper').remove();
    $('#content').show();
}


// Help and hint rendering
var HelpButton = {};
$('.hint-enhanced input').live('mouseover', function() {
    if ($(this).attr('title')) return;
    var hint = $(this).nextAll('.hint').text();
    if (!hint) {
        carp('Hint requested but undefined for:', this);
        return;
    }
    $(this).attr({title: hint});
});
HelpButton.save_from_fading = function($help_button) {
    $help_button.stop().css({opacity:1});
    if ( $help_button.data('fadeout_timeout') ) {
        clearInterval( $help_button.data('fadeout_timeout') );
        $help_button.removeData('fadeout_timeout');
    }
}
HelpButton.set_to_fade = function($input, $help_button) {
    var help_button_fade_timeout = setTimeout( function() {
        $help_button.fadeOut(3000, function () {
            $input.removeData('help_button');
            $help_button.remove();
        })
    }, 1000);
    $help_button.data('fadeout_timeout', help_button_fade_timeout);
}
$('.help-enhanced input').live('mouseover', function() {
    if ($(this).data('help_button')) {
        HelpButton.save_from_fading($(this).data('help_button'))
        return;
    }
    var $help_button = $('<div>').addClass('help-button').css({
        position: 'absolute',
        top: $(this).offset().top,
        left: $(this).offset().left + $(this).outerWidth(),
        minHeight: $(this).outerHeight()
    }).html('<img alt="?" src="'+MEDIA_URL+'ico/16/help.png" />').data('antecedant_input', $(this));
    $help_button.appendTo($(this).closest('.help-enhanced'));
    $(this).data('help_button', $help_button);
}).live('mouseout', function() {
    var $help_button = $(this).data('help_button');
    if (!$help_button) return;
    HelpButton.set_to_fade($(this), $help_button);
});
$('.help-button').live('mouseover', function() {
    HelpButton.save_from_fading($(this));
}).live('mouseout', function() {
    var $input = $(this).data('antecedant_input');
    HelpButton.set_to_fade($input, $(this));
}).live('click', function() {
    $(this).closest('.help-enhanced').find('.help').slideToggle();
});

$(document).bind('content_added', function() {
    if ($('.suggest-related-lookup').length) {
        request_media(MEDIA_URL +  'js/related_lookup.js?' +MEDIA_VERSION);
        request_media(MEDIA_URL + 'css/related_lookup.css?'+MEDIA_VERSION);
    }
});

// Opens an overlay with a changelist and calls supplied function on click on item.
$(function(){ open_overlay = function(content_type, selection_callback) {
    var top_zindex = ( function() {
        var rv = 1;
        $('.ui-widget-overlay').each( function() {
            rv = Math.max(rv, $(this).css('zIndex'));
        });
        return rv + 1;
    })();
    var $overlay = $('#box-overlay');
    if ($overlay.length == 0) $overlay = $(
        '<div id="box-overlay" class="overlay">'
    )
    .css({top:0,left:0,zIndex:top_zindex})
    .appendTo(
           $('.change-form').get(0)
        || $('#content').get(0)
        || $('body').get(0)
    );
    var address = '/' + content_type.split('.').join('/') + '/?pop';
    ContentByHashLib.load_content({
        address: address,
        target_id: 'box-overlay',
        selection_callback: selection_callback,
        success_callback: function() {
            var xhr = this;
            $('#'+xhr.original_options.target_id+' tbody a')
            .unbind('click')
            .click( function(evt) {
                var clicked_id = $(this).attr('href').replace(/\/$/,'');
                try {
                    xhr.original_options.selection_callback(clicked_id, {evt: evt});
                } catch(e) { carp('Failed running overlay callback', e); }
                ContentByHashLib.unload_content('box-overlay');
                return false;
            })
            .each( function() {
                this.onclick = undefined;
            });
        }
    });
}});
