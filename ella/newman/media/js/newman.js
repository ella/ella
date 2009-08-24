var LF = 10, CR = 13;

// Set the default target for Kobayashi to #content
Kobayashi.DEFAULT_TARGET = 'content';

// Set the base URL for #content
BASES.content = '/nm/';

// Containers for things we need to export
NewmanLib = {};
AjaxFormLib = {};

NewmanLib.ADR_STACK = [];

// A less smart alternative to jQuery's offset method.
function simple_offset(el) {
    var l, t;
    l = t = 0;
    if (el.offsetParent) {
        do {
            l += el.offsetLeft;
            t += el.offsetTop;
        } while (el = el.offsetParent);
    }
    return { left: l, top: t };
}

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

function lock_window(msg) {
    if ( ! msg ) msg = gettext('Wait')+'...';
    
    var $modal = $('#window-lock');
    if ($modal.length == 0) $modal = $(
            '<div id="window-lock"></div>'
    ).html(
          '<p><img src="'
        + MEDIA_URL + 'ico/15/loading.gif'
        + '" alt="" /> <span id="lock-message"></span></p>'
    ).appendTo('body').dialog({
        autoOpen: false,
        modal: true,
        resizable: false,
        draggable: false,
        closeOnEscape:false,
        beforeclose: function() {
            return !!$(this).data('close_ok');
        }
    });
    $('#lock-message').html(msg);
    $modal.data('close_ok', false)
    $modal.dialog('open');
}
function unlock_window() {
    $('#window-lock').data('close_ok', true).dialog('close');
}

function get_html_chunk(tmpl, success) {
    $.get(get_adr('/nm/render-chunk/'), {chunk: tmpl}, success);
}

//// Layout adjustment

$( function() {
    CONTAINER_TOP_OFFSET = 105;
    CONTAINER_BOT_OFFSET = 135;
    $('#container').css({
        position: 'fixed',
        top: CONTAINER_TOP_OFFSET+'px',
        width: '100%',
        height: ($(window).height()-CONTAINER_BOT_OFFSET)+'px',
        overflow: 'auto'
    });
    $(window).bind('resize', function() {
        $('#container').css({
            height: ($(window).height()-CONTAINER_BOT_OFFSET)+'px',
        })
    });
});

//// Homepage initialization

$(function(){Kobayashi.reload_content('content');});

//// Lock window when media are being loaded

$(document).bind('media_loading_start', function() { lock_window(gettext('Loading media')+'...'); });
$(document).bind('media_loaded', unlock_window);

//// Drafts and templates
(function() {
    var draft_id;
    function save_preset($form, options) {
        var form_data = JSON.stringify( $form.serializeArray() );
        var things_to_send = {data: form_data};
        if (!options) options = {};
        if (options.title) things_to_send.title = options.title;
        if (options.id   ) things_to_send.id    = options.id;
        var message = options.msg || gettext('Saved');
        var url = get_adr('draft/save/');
        var $saving_msg = show_message(gettext('Saving')+'...', {duration: 0});
        $.ajax({
            url: url,
            data: things_to_send,
            type: 'POST',
            success: function(response_text) {
                $saving_msg.remove();
                show_ok(message, {duration: 2000});
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
                    show_err(gettext('Preset saved but erroneous result received.')+' '+gettext('Reload to see the preset.'));
                }
            },
            error: function(xhr) {
                $saving_msg.remove();
                show_ajax_error(xhr);
            }
        });
    }
    AjaxFormLib.save_preset = save_preset;
    $('a#save-form').live('click', function() {
        var title = prompt(gettext('Enter template name'));
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
    
    function restore_form(response_text, $form, args) {
        var response_data;
        try {
            response_data  = JSON.parse(response_text);
        } catch(e) {
            show_err(gettext('Failed loading preset'));
            return;
        }
        
        $form.trigger('preset_load_initiated', [response_data]);
        
        $form.get(0).reset();
        $form.find(':checkbox,:radio').removeAttr('checked');
        $form.find(':text,textarea,:password').val('');
        var form_data = response_data.data;
        if (response_data.message) show_message( response_data.message );
        var used_times = {};    // how many times which key was used
        
        for (var i = 0; i < form_data.length; i++) {
            var form_datum = form_data[i];
            var key = form_datum['name'];
            var val = form_datum['value'];
            
            var occ_no = used_times[ key ] || 0;
            
            var $inputs = $form.find(':input[name='+key+']');
            if (!$inputs || $inputs.length == 0) {
                carp('restore_form: input #'+key+' not found');
                continue;
            }
            var val_esc = val.replace(/(\W)/g, '\\$1');
            $inputs.filter(':checkbox,:radio').filter('[value='+val_esc+']').attr({checked: 'checked'});
            $inputs.find('option[value='+val_esc+']').attr({selected: 'selected'});
            $inputs.filter(':text,[type=hidden],textarea').eq(occ_no).val(val);
            
            used_times[ key ] = occ_no + 1;
        }
        $form.find('.GenericSuggestField,.GenericSuggestFieldMultiple').find('input[rel]').each(function() {
            restore_suggest_widget_from_value(this);
        });
        
        $form.trigger('preset_load_completed', [response_data, args]);
    }
    NewmanLib.restore_form = restore_form;
    function load_preset(id, $form) {
        $.ajax({
            url: get_adr('draft/load/'),
            data: {id:id},
            success: function(response_text) {
                restore_form(response_text, $form, {preset_id:id});
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
    
    function delete_preset(id) {
        $.ajax({
            url: get_adr('draft/delete/'),
            data: {id:id},
            success: function(response_text) {
                show_ajax_success(response_text);
                $('#id_drafts option[value='+id+']').remove();
            },
            error: show_ajax_error
        });
    }
    
    // Delete crash save on restoration
    $(document).bind('preset_load_completed', function(evt, response_data, args) {
        var id = args.preset_id;
        var name = $('#id_drafts option[value='+id+']').text();
        if (/^\* /.test( name )) {
            delete_preset(id);
        }
    });
    
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
                save_preset($change_form, {id: draft_id});
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


$( function() {
    //// Ajax forms
    
    function get_inputs($form) {    // all except metadata
        return $form.find(':input').filter(function() {
            return ! $(this).parent().is('.js-form-metadata');
        });
    }
    
    // Validate
    var validations = {
/*        required: function(input) {
            if ($(input).val()) return false;
            else return gettext('Field cannot be blank.');
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
        var $antecedant = $(input).closest('.markItUp').add(input).eq(0);
        $antecedant.before($msg);
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
        $('.form-error-msg,.non-field-errors').remove();
        get_inputs($form).each( function() {
            var $label = $('label[for='+this.id+']');
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
        
        if (ok && $form.data('validation')) {
            ok = $form.data('validation')( $form );
        }

        return ok;
    }
    
    // Submit event
    function ajax_submit($form, button_name) {
        if (!$form.jquery) $form = $($form);
        if ( ! validate($form) ) return false;
        
        // Hack for file inputs
        var has_files = false;
        $form.find(':file').each( function() {
            if ( $(this).val() ) has_files = true;
        });
        if (has_files) {
            // Shave off the names from suggest-enhanced hidden inputs
            $form.find('input:hidden').each( function() {
                if ($form.find( '#'+$(this).attr('id')+'_suggest' ).length == 0) return;
                $(this).val( $(this).val().replace(/#.*/, '') );
            });
            // Shave off the days of week from date-time inputs
            $form.find('.vDateTimeInput,.vDateInput').each( function() {
                $(this).val( $(this).val().replace(/ \D{2}$/, '') );
            } );
            $form.data('standard_submit', true);
            if (button_name) {
                $form.append('<input type="hidden" value="1" name="'+button_name+'" />');
            }
            $form.submit();
            return true;
        }
        // End of hack for file inputs
        
        lock_window(gettext('Sending')+'...');
        
        var action =  $form.attr('action');
        var method = ($form.attr('method') || 'POST').toUpperCase();
        var $meta = $form.find('.js-form-metadata');
        var $success = $meta.find('input[name=success]');
        var $error   = $meta.find('input[name=error]');
        var success, error;
        if ($success && $success.length) {
            success = $success.data('callback');
        }
        else {
            success = show_ajax_success;
        }
        if ($error && $error.length) {
            error = $error.data('callback');
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
        if ($form.hasClass('js-reset-on-submit')) $form.get(0).reset();
        var address = $form.hasClass('js-dyn-adr')
            ? get_adr(action)
            :         action;
        var url = $('<a>').attr('href', address).get(0).href;
        
        var request_options = {
            url: url,
            type: method,
            data: data,
            success:  function() { this.succeeded = true;  },
            error:    function() { this.succeeded = false; },
            complete: function(xhr) {
                var redirect_to;
                if (redirect_to = xhr.getResponseHeader('Redirect-To')) {
                    var new_req = {};
                    for (k in this) new_req[k] = this[k];
                    new_req.url = redirect_to;
                    new_req.redirect_to = redirect_to;
                    $.ajax( new_req );
                    return;
                }
                if (this.succeeded) { try {
                    success.call(this, xhr.responseText, xhr);
                } catch (e) {
                    carp('Error processing form-send success:', e);
                }}
                else { try {
                    error.apply(this, arguments);
                } catch(e) {
                    carp('Error processing form-send error:', e);
                }}
                unlock_window();
            },
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
        var $form = this._form;
        try { res = JSON.parse( xhr.responseText ); }
        catch (e) { }
        if (res && res.errors) {
            // Show the bubble with scrollto buttons
            var $err_overlay = $('#err-overlay');
            if ($err_overlay.length == 0) $err_overlay = $(
                '<div id="err-overlay" class="overlay">'
            ).html(
                '<h6></h6>'
            ).appendTo(
                   $form
                || $('.change-form').get(0)
                || $('#content').get(0)
                || $('body').get(0)
            );
            
            $err_overlay.find('h6').text(res.message);
            
            // Show the individual errors
            for (var i = 0; i < res.errors.length; i++) {
                var err = res.errors[i];
                var id = err.id;
                var msgs = err.messages;
                var label = err.label;
                var input;
                
                // non-field errors
                if (id == 'id___all__') {
                    var $nfe = $('#non-field-errors');
                    if ($nfe.length == 0) {
                        $nfe = $('<p class="non-field-errors">').insertBefore($form);
                        $nfe.prepend(
                              '<input type="text" id="id_non_form_errors" style="position: absolute; left: -500px;" />'+ "\n"
                            + '<label for="id_non_form_errors" style="display: none;">'
                            +     gettext('Form errors')
                            + '</label>'
                        );
                    }
                    input = document.getElementById('id_non_form_errors');
                    
                    show_form_error(input, msgs);
                }
                else {
                    input = document.getElementById(id);
                    show_form_error(input, msgs);
                    if (!input) carp('Error reported for nonexistant input #'+id);
                }
                
                $('<p>')
                .data('rel_input',
                      !input                             ? null
                    : $('#'+input.id+'_suggest').length  ? $('#'+input.id+'_suggest').get(0) // take suggest input if available
                    :                                      input                             // otherwise the input itself
                )
                .text(
                       label
                    || ($('label[for='+input.id+']').text() || id).replace(/:$/,'') // identify the input with its label text or id; no trailing ':' pls
                )
                .click( function(evt) { // focus and scroll to the input
                    if (evt.button != 0) return;
                    var input = $(this).closest('p').data('rel_input');
                    try { input.focus(); } catch(e) {}
                    $(input).addClass('blink')
                    .closest('.collapsed').removeClass('collapsed').addClass('collapse');
                    setTimeout( function() { $(input).removeClass('blink'); }, 1500 );
                    return false;
                })
                .appendTo($err_overlay);
            }
            $err_overlay.show();
        }
        else {
            if (!$form) {
                alert(
                    gettext('Error sending form.')+' '+
                    gettext('Moreover, failed to handle the error gracefully.')+"\n"+
                    gettext('Reloading page')+'...'
                );
                location.reload();
            }
            if ($form.is('.change-form')) {
                AjaxFormLib.save_preset($form, {title: '* '+gettext('crash save'), msg: gettext('Form content backed up')});
            }
            var id = Kobayashi.closest_loaded( $form.get(0) ).id;
            var address = $form.hasClass('js-dyn-adr')
                ? get_adr($form.attr('action'))
                :         $form.attr('action');
            Kobayashi.inject_error_message({
                target_id: id,
                xhr: xhr,
                address: address
            });
        }
        show_ajax_error(xhr);
    }
    AjaxFormLib.ajax_submit_error = ajax_submit_error;
    
    // Collapsible fieldsets
    $('.collapse legend').live('click', function(evt) {
        if (evt.button != 0) return;
        $(this).closest('fieldset').removeClass('collapse').addClass('collapsed');
    });
    $('.collapsed legend').live('click', function(evt) {
        if (evt.button != 0) return;
        $(this).closest('fieldset').removeClass('collapsed').addClass('collapse');
    });
    
    // Submit button
    $('.js-form a.js-submit').live('click', function(evt) {
        if (evt.button != 0) return true;    // just interested in left button
        if ($(this).hasClass('js-noautosubmit')) return true;
        var $form = $(this).closest('.js-form');
        return ajax_submit($form, this.name);
    });
    
    // Reset button
    $('.js-form a.js-reset').live('click', function(evt) {
        try {
            $(this).closest('form').get(0).reset();
        } catch(e) { }
        return false;
    });
    
    // Overload default submit event
    function overload_default_submit() {
        $('.js-form')
        .unbind('submit.ajax_overload')
        .bind('submit.ajax_overload', function(evt) {
            if ($(this).data('standard_submit')) return true;
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
            return AjaxFormLib.ajax_submit( $(this), name );
        });
    }
    $(document).bind('content_added', overload_default_submit);
    overload_default_submit();
    //// End of ajax forms
    
    // Set up returning to publishable changelist when coming to change form from it
    $('#changelist tbody th a,.actionlist a').live('click', function(evt) {
        if (evt.button != 0) return;
        NewmanLib.ADR_STACK = [];
        var appname = /js-app-(\w+)\.(\w+)/.exec( $('#changelist').attr('className') );
        if ( ! appname ) {
            return;
        }
        var appname_path = '/' + appname[1] + '/' + appname[2] + '/';
        if (appname_path == '/core/publishable/') {
            NewmanLib.ADR_STACK = [ { from: '/core/publishable/', to: get_hashadr($(this).attr('href')) } ];
        }
    });
    
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
    
    // Close filters button
    $('#filters a.cancel').live('click', function(evt) {
        if (evt.button != 0) return;
        Kobayashi.unload_content('filters');
    });
    
    // Re-initialization of third party libraries
    /*
    $(document).bind('content_added', function() {
    });
    */
    
    // Update document title
    var ORIGINAL_TITLE = document.title;
    $(document).bind('content_added', function(evt) {
        var newtitle = $(evt.target).find('#doc-title').text();
        document.title = (newtitle ? newtitle+' | ' : '') + ORIGINAL_TITLE;
    });
    
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
    function changelist_search($input) {
        if ($('#changelist').length == 0) return;   // We're not in changelist
        var search_terms = $input.val();
        if (!search_terms) return;  // Nothing to search for
        var adr_term = '&q=' + search_terms;
        var loaded = Kobayashi.closest_loaded( $input.get(0) );
        if (loaded.id == 'content') {
            adr(adr_term);
        }
        else {
            Kobayashi.simple_load( loaded.id + '::' + adr_term );
        }
        return false;
    }
    $('#filters-handler .btn.search').live('click', function(evt) {
        if (evt.button != 0) return;
        var $input = $(this).prev('input#searchbar');
        return changelist_search( $input );
    });
    $('#filters-handler #searchbar').live('keyup', function(evt) {
        if (evt.keyCode == CR || evt.keyCode == LF) { } else return;
        return changelist_search( $(this) );
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
$('#opmsg').live('click', function(evt) {
    if (evt.button != 0) return;
    hide_loading();
    $('#opmsg *').remove();
});


// The 'loading...' message
//                How many things need the loading message shown concurrently
var $LOADING_MSG, LOADING_CNT = 0;
function show_loading() {
    LOADING_CNT++;
    if ($LOADING_MSG) return;
    $LOADING_MSG = show_message(gettext('Loading')+'...', {duration:0});
}
$(document).bind('show_loading', show_loading);
function hide_loading() {
    if ($LOADING_MSG) $LOADING_MSG.remove();
    LOADING_CNT = 0;
    $LOADING_MSG = undefined;
}
$(document).bind('hide_loading', hide_loading);
function dec_loading() {
    if (--LOADING_CNT <= 0) {
        LOADING_CNT = 0;
        hide_loading();
    }
}
$(document).bind('dec_loading', dec_loading);

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
        message = gettext('Request failed')+' ('+xhr.status+': '+gettext(xhr.statusText)+')';
        paste_code_into_debug( xhr.responseText.replace(/\n(\s*\n)+/g, "\n"), 'Ajax error response' );
    }
    show_err(message);
}
$(document).bind('load_content_failed', function(evt, xhr) {
    show_ajax_error(xhr);
});
function show_ajax_success(response_text) {
    var message, data;
    try {
        data = JSON.parse(response_text);
        message = data.message;
    } catch (e) {
        message = gettext('Successfully sent');
        paste_code_into_debug( (response_text||'').replace(/\n(\s*\n)+/g, "\n"), 'Ajax success response' );
    }
    if (this.redirect_to) {
        var literal_address;
        if (this.redirect_to.substr(0, BASE_PATH.length) == BASE_PATH) {
            literal_address = this.redirect_to.substr(BASE_PATH.length);
        }
        else {
            literal_address = this.redirect_to;
        }
        adr(literal_address);
    }
    show_ok(message);
}

function PostsaveActionTable(vars) {
    this.vars = vars;
}
PostsaveActionTable.prototype = {
    _save_: function() {
        var return_to;
        if (NewmanLib.ADR_STACK.length) {
            var popped = NewmanLib.ADR_STACK.pop();
            if (get_hashadr('') == popped.to) {
                return_to = popped.from;
                if ($.isFunction(popped.onsave))
                    popped.onsave(popped,this);
                if ($.isFunction(popped.onreturn)) {
                    var action_table_obj = this;
                    $('#'+Kobayashi.DEFAULT_TARGET).one('content_added', function(evt) {
                        popped.onreturn(popped,action_table_obj);
                    });
                }
            }
            else {
                return_to = '../';
                NewmanLib.ADR_STACK = [];
            }
        }
        else {
            return_to = '../';
        }
        if (adr(return_to, {just_get: 'hash'}) == location.hash) {
            Kobayashi.reload_content(Kobayashi.DEFAULT_TARGET);
        }
        else {
            adr(return_to);
        }
    },
    _addanother_: function() {
        if ( /add\/$/.test(get_hashadr('')) ) {
            Kobayashi.reload_content('content');
            scrollTo(0,0);
        }
        else {
            adr('../add/');
        }
    },
    _continue_: function() {
        if ( /add\/$/.test(get_hashadr('')) ) {
            var oid = this.vars.object_id;
            if (!oid) {
                var message = gettext('Cannot continue editing') + ' (' + gettext('object ID not received') + ')';
                show_err(message);
                carp(message, 'xhr options:', this.vars.options);
                adr('../');
                return;
            }
            adr('../'+oid+'/');
        }
        else {
            Kobayashi.reload_content('content');
        }
    },
    _saveasnew_: function() {
        var oid = this.vars.object_id;
        if (!oid) {
            show_err(gettext('Failed to redirect to newly added object.'));
            carp('Cannot redirect to newly added object: ID not received.');
        }
        else {
            adr('../'+oid+'/');
        }
    },
    run: function(action) {
        var a = action+'_';
        if (this[ a ]) {
            this[ a ]();
        }
        else {
            var message = action
                ? gettext('Unrecognized post-save action: ')+action
                : gettext('No post-save action, redirecting to homepage');
            show_message(message);
            carp(message);
            location.hash = '#';
        }
    }
};


// submit line (save, save as new, etc)
function save_change_form_success(text_data) {
    var options = this;
    if (!options || !options._button_name || !options._form) {
        var message;
        if (!options) message = 'No XHR options passed to save_change_form_success';
        else if (!options._form) message = '_form not set in the XML HTTP Request for change_form submit';
        else if (!options._button_name) message = '_button_name not set in the XML HTTP Request for change_form submit';
        carp(message);
        show_ajax_success(text_data);
        show_err(gettext('Failed to follow form save with a requested action'));
        return;
    }
    var $form = options._form;
    var action = options._button_name;
    var data, object_id, response_msg;
    try {
        data = JSON.parse(text_data);
        object_id = data.data.id;
        object_title = data.data.title;
        response_msg = data.message;
    } catch(e) { carp('invalid data received from form save:', text_data, e); }
    response_msg = response_msg || gettext('Form saved');
    
    var action_table = new PostsaveActionTable({
        object_id: object_id,
        object_title: object_title,
        options: options
    });
    
    // load form-specific post-save actions
    var $meta = $form.find('.js-form-metadata');
    var post_save_callback = $meta.find('input[name=post_save]').data('callback');
    var post_save = {};
    if (post_save_callback) post_save = post_save_callback($form);
    for (var act in post_save) {
        action_table[ act ] = post_save[ act ];
    }
    
    show_ok(response_msg);
    action_table.run(action);
    Kobayashi.unload_content('history');
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
    Kobayashi.reload_content('content');
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

// RichText editor -- re-initialize markitup on newly added rich text areas.
$(document).bind('content_added', function(evt) {
    if ( ! window.MARKITUP_SETTINGS ) return;  // let them initialize themselves on document load -- avoid action here
    var $target = $( evt.target );
    // let those rich text areas alone that are in .markItUpContainer -- they are already initialized
    $target.find('.rich_text_area').not('.markItUpContainer .rich_text_area').each( function() {
        $(this).markItUp(MARKITUP_SETTINGS);
    });
});

// Related lookup
$(document).bind('content_added', function(evt) {
    if ($(evt.target).find('.suggest-related-lookup').length) {
        request_media(MEDIA_URL +  'js/related_lookup.js?' +MEDIA_VERSION);
        request_media(MEDIA_URL + 'css/related_lookup.css?'+MEDIA_VERSION);
    }
});

// Thickbox
$(document).ready( function() {
    request_media(MEDIA_URL + 'jquery/thickbox/thickbox.css');
    request_media(MEDIA_URL + 'jquery/thickbox/thickbox.js');
    $(document).one('media_loaded', function() {
        tb_pathToImage = MEDIA_URL + 'jquery/thickbox/loadingAnimation.gif';
    });
    $(document).bind('content_added', function() {
        try {
            tb_init('a.thickbox, area.thickbox, input.thickbox');
        } catch(e) {
            carp('Failed to re-initialize thickbox:', e);
        }
    });
});

// Opens an overlay with a changelist and calls supplied function on click on item.
$( function() {
    var overlay_html;
    
    open_overlay = function(content_type, selection_callback) {
        var ooargs = arguments;
        if ( ! overlay_html ) {
            get_html_chunk('overlay', function(data) {
                overlay_html = data;
                ooargs.callee.apply(this, ooargs);
            });
            return;
        }
        
        var top_zindex = ( function() {
            var rv = 1;
            $('.ui-widget-overlay').each( function() {
                rv = Math.max(rv, $(this).css('zIndex'));
            });
            return rv + 1;
        })();
        var $overlay = $('#changelist-overlay');
        if ($overlay.length == 0) {
            $overlay = $( overlay_html )
            .css({top:0,left:0})
            .appendTo(
                   $('.change-form').get(0)
                || $('#content').get(0)
                || $('body').get(0)
            );
            $('#overlay-content').bind('content_added', init_overlay_content);
        }
        $overlay.css({zIndex:top_zindex});
        
        $('#overlay-content').data('selection_callback', selection_callback);
        
        var ct_arr = /(\w+)\W(\w+)/.exec( content_type );
        if ( ! ct_arr ) {
            carp('open_overlay: Unexpected content type: '+content_type);
            return false;
        }
        var address = '/' + ct_arr[1] + '/' + ct_arr[2] + '/?pop';
        
        Kobayashi.load_content({
            address: address,
            target_id: 'overlay-content',
            selection_callback: selection_callback/*,
            success_callback: function() {
                var xhr = this;
                var $target = $('#'+xhr.original_options.target_id);
                
            }*/
        });
    };
    $('.overlay-closebutton').live('click', function() {
        $(this).closest('.overlay').css({zIndex:5}).hide()
        .find('.overlay-content').removeData('selection_callback');
        Kobayashi.unload_content('overlay-content');
    });
    function init_overlay_content(evt, extras) {
        var $target = $(evt.target);
        
        var target_selector = $target.attr('id') ? '#'+$target.attr('id')+' ' : '';
        
        // selection
        var $target_links = $target.find('#changelist tbody a');
        $target_links.each( function() {
            this.onclick = null;
        });
        $target_links
        .unbind('click')
        .click( function(evt) {
            var clicked_id = /\d+(?=\/$)/.exec( $(this).attr('href') )[0];
            try {
                ($target.data('selection_callback'))(clicked_id, {str: $(evt.target).text()});
            } catch(e) { carp('Failed running overlay callback', e); }
            Kobayashi.unload_content('overlay-content');
            $('#changelist-overlay').css({zIndex:5}).hide();
            $target.removeData('selection_callback');
            return false;
        });
        
        function modify_getpar_href(el) {
            $(el).attr('href', $(el).attr('href').replace(/^\?/, 'overlay-content::&')).addClass('js-simpleload');
        }
        
        // pagination
        $target.find('.paginator a').each( function() {
            modify_getpar_href(this);
        });
        
        // sorting
        $target.find('#changelist thead a').each( function() {
            modify_getpar_href(this);
        });
        
        // filters
        var $filt = $('#filters-handler .popup-filter');
        if ($filt.length) {
            $filt.addClass('js-simpleload').attr( 'href', $filt.attr('href').replace(/::::/, '::'+$target.attr('id')+'::') );
            function init_filters() {
                $(this).find('.filter li a').each( function() {
                    $(this).attr('href', $(this).attr('href').replace(/^\?/, 'overlay-content::&')).addClass('js-simpleload');
                });
            }
            $('#filters').unbind('content_added', init_filters).one('content_added', init_filters);
        }
        
        var $cancel = $('#filters-handler a.js-clear').not('.overlay-adapted');
        if ($cancel.length) $cancel
        .attr( 'href', $target.attr('id')+'::'+$cancel.attr('href') )
        .removeClass('js-clear')
        .addClass('js-simpleload overlay-adapted');
        
        $('#changelist-overlay').show();
    };
});

function DATEPICKER_OPTIONS(opts) {
    this.firstDay = 1;
    this.dateFormat = 'dd';
    this.dayNames = [
        gettext('Sunday'),
        gettext('Monday'),
        gettext('Tuesday'),
        gettext('Wednesday'),
        gettext('Thursday'),
        gettext('Friday'),
        gettext('Saturday')
    ];
    this.dayNamesMin = [
        gettext('Su'),
        gettext('Mo'),
        gettext('Tu'),
        gettext('We'),
        gettext('Th'),
        gettext('Fr'),
        gettext('Sa')
    ];
    this.dayNamesShort = [
        gettext('Sun'),
        gettext('Mon'),
        gettext('Tue'),
        gettext('Wed'),
        gettext('Thu'),
        gettext('Fri'),
        gettext('Sat')
    ];
    this.monthNames = [
        gettext('January'),
        gettext('February'),
        gettext('March'),
        gettext('April'),
        gettext('May'),
        gettext('June'),
        gettext('July'),
        gettext('August'),
        gettext('September'),
        gettext('October'),
        gettext('November'),
        gettext('December')
    ];
    this.monthNamesShort = [
        gettext('Jan'),
        gettext('Feb'),
        gettext('Mar'),
        gettext('Apr'),
        gettext('May'),
        gettext('Jun'),
        gettext('Jul'),
        gettext('Aug'),
        gettext('Sep'),
        gettext('Oct'),
        gettext('Nov'),
        gettext('Dec')
    ];
    for (var o in opts) {
        this[o] = opts[o];
    }
}
