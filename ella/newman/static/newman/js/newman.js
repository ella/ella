/** 
 * Newman specific things used in conjunction with Kobayashi.
 * requires: jQuery 1.4.2+, 
 *          gettext() function.
 *          carp(),
 *          adr(),
 *          get_adr(),
 *          get_hashadr(),
 *          str_concat(),
 *          timer(), timerEnd(),
 *          Kobayashi object.
 *
 * provides:
 *          lock_window()  locks window to prevent user clicking anywhere,
 *          unlock_window(),
 *          show_err() shows error bubble,
 *          show_ok() show bubble (should be used for messages like 'Object saved', 'Data loaded', etc.),
 *          show_loading(),
 *          hide_loading(),
 *          show_ajax_error(xhr),
 *          show_ajax_success(response_text),
 *          Drafts object,
 *          NewmanLib object,
 *          AjaxFormLib object.
 *
 */
var LF = 10;
var CR = 13;
var ASCII_PRINTABLE_BEGIN = 32;
var ASCII_PRINTABLE_END = 126;
var ASCII_BACKSPACE = 8;
var ASCII_DELETE = 46;
var UNICODE = 160;
var DEFAULT_MESSAGE_BUBBLE_DURATION = 5000;

// Set the default target for Kobayashi to #content
Kobayashi.DEFAULT_TARGET = 'content';

// Set the base URL for #content
BASES.content = '/nm/';

// Prevent JS fail when calling console.log() in nonFireBugged browser.
if (typeof console != 'object') {
    console = {};
    console.log = function(){ return; };
}

/** Useful when method of an object should be used as jQuery event handler.
 *  Example:
 *  $(document).bind('hashchange', this_decorator(this, this.method) );
 * 
 *  Is much better than:
 *  var me = this;
 *  $(document).bind('hashchange', function () { me.method(); } );
 */
function this_decorator(context, fce) {
    var me = this;
    function wrap() {
        return fce.apply(context, arguments);
    }
    return wrap;
}

// Containers for things we need to export
AjaxFormLib = {};
NewmanLib = {};
(function() {
    NewmanLib.post_save_callbacks = [];
    NewmanLib.pre_submit_callbacks = [];
    NewmanLib.pre_submit_once_callbacks = [];
    NewmanLib.post_save_once_callbacks = [];

    function register_post_submit_callback(callback) {
        if (!(callback in NewmanLib.post_save_callbacks)) {
            NewmanLib.post_save_callbacks.push(callback);
        }
    }
    NewmanLib.register_post_submit_callback = register_post_submit_callback;

    function register_post_submit_callback_once(callback) {
        if (!(callback in NewmanLib.post_save_once_callbacks)) {
            NewmanLib.post_save_once_callbacks.push(callback);
        }
    }
    NewmanLib.register_post_submit_callback_once = register_post_submit_callback_once;

    function register_pre_submit_callback(callback) {
        if (!(callback in NewmanLib.pre_submit_callbacks)) {
            NewmanLib.pre_submit_callbacks.push(callback)
        }
    }
    NewmanLib.register_pre_submit_callback = register_pre_submit_callback;

    function register_pre_submit_callback_once(callback) {
        if (!(callback in NewmanLib.pre_submit_once_callbacks)) {
            NewmanLib.pre_submit_once_callbacks.push(callback)
        }
    }
    NewmanLib.register_pre_submit_callback_once = register_pre_submit_callback_once;

    function call_callbacks_in_array(carray, destructive_call_once, arg1) {
        var i, item;
        for(i = 0; i < carray.length; i++) {
            if (destructive_call_once) {
                item = carray.pop();
            } else {
                item = carray[i];
            }
            item(arg1);
        }
    }

    function call_post_submit_callbacks(submit_succeeded) {
        var once = true;
        try {
            call_callbacks_in_array(NewmanLib.post_save_once_callbacks, true, submit_succeeded);
            once = false;
            call_callbacks_in_array(NewmanLib.post_save_callbacks, false, submit_succeeded);
        } catch(e) {
            if (once) {
                carp('Error occured when calling post submit callback (once).' , e.toString());
            } else {
                carp('Error occured when calling post submit callback.' , e.toString());
            }
        }
    }
    NewmanLib.call_post_submit_callbacks = call_post_submit_callbacks;

    function call_pre_submit_callbacks() {
        var once = true;
        try {
            call_callbacks_in_array(NewmanLib.pre_submit_once_callbacks, true);
            once = false;
            call_callbacks_in_array(NewmanLib.pre_submit_callbacks);
        } catch(e) {
            if (once) {
                carp('Error occured when calling post submit callback (once).' , e.toString());
            } else {
                carp('Error occured when calling post submit callback.' , e.toString());
            }
        }
    }
    NewmanLib.call_pre_submit_callbacks = call_pre_submit_callbacks;
})();


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

// workaround for jQuery's incomplete cloning of forms
// (it doesn't copy textareas' contents and selected options)
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

// Shows a modal window and disables its close button.
function lock_window(msg) {
    if (lock_window.dependencies_loaded == false) {
        lock_window.dependencies_loaded = true;
        Kobayashi.load_media(MEDIA_URL + 'jquery/jquery-ui-smoothness.css', {callbacks: null});
        Kobayashi.load_media(MEDIA_URL + 'jquery/jquery-ui.js', {callbacks: null});
    }

    if ( ! msg ) msg = str_concat( gettext('Wait'),'...' );

    var $modal = $('#window-lock');
    if ($modal.length == 0) $modal = $(
            '<div id="window-lock"></div>'
    ).html(
        str_concat(
          '<p><img src="'
        , MEDIA_URL , 'ico/15/loading.gif'
        , '" alt="" /> <span id="lock-message"></span></p>'
        )
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

    //carp('Window Locked');
}
lock_window.dependencies_loaded = false;

function raw_unlock_window() {
    $('#window-lock').data('close_ok', true).dialog('close');
    //carp('Window Unlocked');
}

function unlock_window() {
    setTimeout(raw_unlock_window, 50);
}

function is_window_locked() {
    //return $('#window-lock').is(':visible'); // FIXME Buggy buggy buggy st. tropez, tada da da...
    var $res = $('#window-lock').data('close_ok');
    if (typeof($res) == 'undefined') {
        return false;
    }
    return $res == true;
}

function get_html_chunk(tmpl, success) {
    $.get(get_adr('/nm/render-chunk/'), {chunk: tmpl}, success);
}

//// Layout adjustment
// this is here to make the content scroll but not beneath the favicons

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

function media_loading_start_handler() { 
    //timer('media_loading'); 
    lock_window( str_concat(gettext('Loading media'), '...') );
}

//// Lock window when media are being loaded
$(document).bind('media_loading_start', media_loading_start_handler);
$(document).bind('media_loaded', function() {
    unlock_window();
    //timerEnd('media_loading');
});

//// Drafts and templates
Drafts = new Object;
(function() {
    var draft_id;
    function save_preset($form, options) {
        var form_data = JSON.stringify( $form.serializeArray() );
        var things_to_send = {data: form_data};
        if (!options) options = {};
        if (options.title) things_to_send.title = options.title;
        if (options.id   ) things_to_send.id    = options.id;
	things_to_send.csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();
        var message = options.msg || gettext('Saved');
        var url = get_adr('draft/save/');
        var $saving_msg = show_message( str_concat(gettext('Saving'), '...'), {duration: 0});
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
                    show_err(str_concat(
                        gettext('Preset saved but erroneous result received.'),
                        ' ',
                        gettext('Reload to see the preset.')
                    ));
                }
            },
            error: function(xhr) {
                $saving_msg.remove();
                show_ajax_error(xhr);
            }
        });
    }
    AjaxFormLib.save_preset = save_preset;

    function save_preset_dialog(title) {
        if (!title) {
            return;
        }
        title = $.trim(title);
        // retrieve the id of template with this name
        // TODO: to be rewritten (saving interface needs a lift)
        var id =
            title
            ? $('#id_drafts option').filter(function(){return $(this).text().indexOf(title+' (') == 0}).val()
            : draft_id;
        save_preset($('.change-form'), {title:title, id:id});
        return false;
    }
    $('a#save-form').live('click', function() {
        jPrompt(gettext('Enter template name'), '', gettext('Enter template name'), save_preset_dialog);
    });

    function restore_initial_forms() {
        this.value = 0;
    }

    function restore_add_form_values($form) {
        var str_location = new String(window.location);
        var form_is_addform = str_location.search('/add/') > -1;

        // in case of add-form change back INITIAL_FORMS value to 0,
        if (!form_is_addform) {
            return;
        }
        $form.find('input[name$=INITIAL_FORMS]').each(restore_initial_forms);
        // and remove IDs of inlined items
        $id_elements = $form.find('.original input').filter(function () {
            return this.name.match(/^(\w|_)+set-\d+-\w+$/);
        });
        $id_elements.each(function () {
            this.value = '';
        });
    }

    function restore_form(response_text, $form, args) {
        var response_data;
        try {
            response_data  = JSON.parse(response_text);
        } catch(e) {
            show_err(gettext('Failed loading preset'));
            return;
        }

        try {
            //carp('Triggering preset_load_initiated event on ' , $form.selector);
            $form.trigger('preset_load_initiated', [response_data]);
        } catch (e) {
            carp('ERROR occured while triggering preset_load_initiated. Exception: ' , e.toString());
        }
        //carp('Trigger preset_load_inititated done.');

        try {
            //carp('Triggering preset_load_process event on ' , $form.selector);
            $form.trigger('preset_load_process', [response_data]);
        } catch (e) {
            carp('ERROR occured while triggering preset_load_process. Exception: ' , e.toString());
        }
        //carp('Trigger preset_load_process done.');

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
            var is_text_area = false;

            var occ_no = 0;
            if (key in used_times) {
                occ_no = used_times[key];
            }

            var $inputs = $form.find( str_concat(':input[name=',key,']') );
            if (!$inputs || $inputs.length == 0) {
                //carp('restore_form: input #' , key , ' not found');
                continue;
            }
            // test whether large data (textarea) is processed
            $inputs.each(
                function () {
                    if (is_text_area) return;
                    if (this.tagName.toLowerCase() == 'textarea') is_text_area = true;
                }
            );
            var val_esc = val.replace(/(\W)/g, '\\$1');
            if (!is_text_area) {
                $inputs.filter(':checkbox,:radio').filter( str_concat('[value=',val_esc,']') ).attr({checked: 'checked'});
                $inputs.find( str_concat('option[value=',val_esc,']') ).attr({selected: 'selected'});
            }
            $inputs.filter(':text,[type=hidden],textarea').eq(occ_no).val(val);

            used_times[ key ] = occ_no + 1;
        }
        $form.find('.GenericSuggestField,.GenericSuggestFieldMultiple').find('input[rel]').each(function() {
            restore_suggest_widget_from_value(this);
        });

        restore_add_form_values($form);

        try {
            $form.trigger('preset_load_completed', [response_data, args]);
        } catch (e) {
            carp('ERROR occured while triggering preset_load_completed. '  , ' Exception: ' , e.toString());
        }
    }
    NewmanLib.restore_form = restore_form;

    function load_preset(id, $form) {
        $.ajax({
            async: false,
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
        timer('load_draft');
        lock_window();
        load_preset(id, $('.change-form'));
        unlock_window();
        timerEnd('load_draft');
    }

    function set_load_draft_handler() {
        $('#id_drafts').unbind('change', load_draft_handler).change(load_draft_handler);
    }
    Drafts.set_load_draft_handler = set_load_draft_handler;
    Drafts.set_load_draft_handler();
    $(document).bind('content_added', Drafts.set_load_draft_handler);

    function delete_preset(id) {
        $.ajax({
            url: get_adr('draft/delete/'),
            data: {id:id},
            success: function(response_text) {
                show_ajax_success(response_text);
                $( str_concat('#id_drafts option[value=',id,']') ).remove();
            },
            error: show_ajax_error
        });
    }

    // Delete crash save on restoration
    $(document).bind('preset_load_completed', function(evt, response_data, args) {
        var id = args.preset_id;
        var name = $( str_concat('#id_drafts option[value=',id,']') ).text();
        if (/^\* /.test( name )) {
            delete_preset(id);
        }
    });

    var autosave_interval;
    function set_autosave_interval(evt) {
        var proceed, target_ids;

        if ($('.change-form').length == 0) { // nothing to autosave
             //carp('.change-form not present -- not setting up interval');
             clearInterval(autosave_interval);
             proceed = false;
        }
        else if ( evt && evt.type == 'content_added' ) {
            if ( $(evt.target).find('.change-form').length ) {
                //carp('waiting for form to change to set up autosave interval');
                proceed = true; // .change-form was just loaded
            }
            else {  // .change-form was there before -- don't touch it
                //carp('.change-form not in loaded stuff -- letting it alone');
                proceed = false;
            }
        }
        else {
            //carp('no injection storage found -- interval reset forced');
            proceed = true;
        }

        if (!proceed) return;

        if (autosave_interval != undefined) {
            //carp('clearing interval prior to setting new one');
            clearInterval(autosave_interval);
        }
        var $inputs = $('.change-form :input');
        // start auto-saving when an input's value changes
        function onchange_autosave_handler() {
            $('.change-form :input').unbind('change', onchange_autosave_handler).unbind('keypress', onkeypress_autosave_handler);
            //carp('.change-form changed -- setting up autosave interval');
            autosave_interval = setInterval( function() {
                var $change_form = $('.change-form');
                if ($change_form.length == 0) {
                    ;;; carp('.change-form disappeared -- clearing interval');
                    clearInterval(autosave_interval);
                    autosave_interval = undefined;
                    return;
                }
                //carp('Saving draft ', new Date());
                save_preset($change_form, {id: draft_id});
            }, 60 * 1000 );
        }
        // start auto-saving when typing occurs on the changeform
        function onkeypress_autosave_handler(evt) {
            var w = evt.which;
            var c = evt.keyCode;
            if (   w >= ASCII_PRINTABLE_BEGIN && w <= ASCII_PRINTABLE_END  // ASCII printable chars
                || w >= UNICODE
                || w == ASCII_BACKSPACE
                || c == ASCII_DELETE
            ) {
                onchange_autosave_handler();
            }
            else if (
                   $(this).is('textarea')
                && (w == CR || w == LF) // enter
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
    
    /**
     * Adds serializeObject method to elements. When called on forms, it results
     * in form being serialized into JSON object {name:value, name2: value2}.
     */
    $.fn.serializeObject = function() {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };

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
        if (msg.shift) {
            var msgs = msg;
            msg = msgs.shift();
        }
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
            var $label = $( str_concat('label[for=',this.id,']') );
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
    
    function clean_inputs($form) {
        var $inputs = $('#absolutely#_nothing');
        get_inputs($form).each( function() {
            // Don't send suggest inputs
            if ( /(.*)_suggest$/.test($(this).attr('id')) ) {
                return;
            }
            // Shave off the names from suggest-enhanced hidden inputs
            if ( $(this).is('input:hidden') && $form.find( str_concat('#',$(this).attr('id'),'_suggest') ).length ) {
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
        return $inputs;
    }
    AjaxFormLib.clean_inputs = clean_inputs;
    
    function clean_inputs_with_files($form) {
        // Shave off the names from suggest-enhanced hidden inputs
        $form.find('input:hidden').each( function() {
            if ($form.find( str_concat('#',$(this).attr('id'),'_suggest') ).length == 0) return;
            $(this).val( $(this).val().replace(/#.*/, '') );
        });
        // Shave off the days of week from date-time inputs
        $form.find('.vDateTimeInput,.vDateInput').each( function() {
            $(this).val( $(this).val().replace(/ \D{2}$/, '') );
        } );
    }
    AjaxFormLib.clean_inputs_with_files = clean_inputs_with_files;

    // Submit event
    function ajax_submit($form, button_name, process_redirect) {
        if (!$form.jquery) $form = $($form);
        if ( ! validate($form) ) {
            unlock_window();
            return false;
        }
        NewmanLib.call_pre_submit_callbacks();
        //carp(['ajax_submit: submitting... selector="', $form.selector, '"'].join(''));

        // Hack for file inputs
        var has_files = false;
        $form.find(':file').each( function() {
            if ( $(this).val() ) has_files = true;
        });
        if (has_files) {
            clean_inputs_with_files($form);
            $form.data('standard_submit', true);
            if (button_name) {
                $form.append( str_concat('<input type="hidden" value="1" name="',button_name,'" />') );
            }
            $form.submit();
            unlock_window();
            return true;
        }
        // End of hack for file inputs

        lock_window( str_concat(gettext('Sending'), '...') );

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
        var $inputs = clean_inputs($form);

        if (button_name) $inputs = $inputs.add( str_concat('<input type="hidden" value="1" name="',button_name,'" />') );
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
                // JSON redirects temporarily commented out.
                if (process_redirect) {
                    if (redirect_to = xhr.getResponseHeader('Redirect-To')) {
                        var new_req = {};
                        for (k in this) new_req[k] = this[k];
                        new_req.url = redirect_to;
                        new_req.redirect_to = redirect_to;
                        $.ajax( new_req );
                        unlock_window();
                        return;
                    }
                }
                NewmanLib.call_post_submit_callbacks(this.succeeded);
                if (this.succeeded) {
                    try {
                        success.call(this, xhr.responseText, xhr);
                    } catch (e) {
                        carp('Error processing form-send success:', e);
                    }
                }
                else {
                    try {
                        error.apply(this, arguments);
                    } catch(e) {
                        carp('Error processing form-send error:', e);
                    }
                }
                unlock_window();
            },
            _form: $form,
            _button_name: button_name
        };
        if (button_name) request_options._button_name = button_name;
        //NewmanLib.call_pre_submit_callbacks();

        $.ajax( request_options );
        //carp('ajax_submit: request sent (async)');
        return false;
    }
    AjaxFormLib.ajax_submit = ajax_submit;

    function is_error_overlay_empty() {
        var $err_overlay = $('#err-overlay');
        if ($err_overlay.length == 0 || $err_overlay.find('h6') != "") {
            return true;
        }
        return false;
    }

    // Handle error response from the server from a form submit event.
    // In case of changeform and expected JSON response, renders the error messages.
    function ajax_submit_error(xhr) {
        function error_blinking_input() {
            $(input).removeClass('blink');
        }

        function focus_errored_element(input_element) {
            var MOVE_UP_PIXELS = 60;
            var $inp = $(input_element);
            var element_id = $inp.attr('id');
            input_element.focus();
            if (element_id != '') {
                // try to find label and scroll div#content to viewport if neccessary
                $label = $( str_concat('label[for=', element_id, ']') );
                //log_generic.log('label:', $label, ' label for=', element_id);
                var detector = new ContentElementViewportDetector($inp);
                if (!detector.top_in_viewport()) {
                    var $content = $('div#content');
                    var existing_offset = $content.offset();
                    $content.offset({top: existing_offset.top + MOVE_UP_PIXELS});
                }
            }
        }

        var res;
        var $form = this._form;
        try {
            res = JSON.parse( xhr.responseText );
        }
        catch (e) {
            carp('Error parsing JSON error response text.' , e);
        }
        if (res && res.errors) {
            // Show the bubble with scrollto buttons
            var $err_overlay = $('#err-overlay');
            if (is_error_overlay_empty()) {
                $err_overlay = $(
                    '<div id="err-overlay" class="overlay">'
                ).html(
                    '<h6></h6>'
                ).appendTo(
                       $form
                    || $('.change-form').get(0)
                    || $('#content').get(0)
                    || $('body').get(0)
                );
            }

            $err_overlay.find('h6').text(res.message);

            // Show the individual errors
            for (var i = 0; i < res.errors.length; i++) {
                var err = res.errors[i];
                var id = err.id;
                var msgs = err.messages;
                var first_message = '';
                var label = err.label;
                var input;

                // assign first message
                if (msgs.length > 0) {
                    first_message = msgs[0];
                }
                // non-field errors
                if (id == 'id___all__') {
                    var $nfe = $('#non-field-errors');
                    if ($nfe.length == 0) {
                        $nfe = $('<p class="non-field-errors">').insertBefore($form);
                        $nfe.prepend( str_concat(
                              '<input type="text" id="id_non_form_errors" style="position: absolute; left: -500px;" />', "\n"
                            , '<label for="id_non_form_errors" style="display: none;">'
                            ,     gettext('Form errors')
                            , '</label>'
                        ) );
                    }
                    input = document.getElementById('id_non_form_errors');

                    show_form_error(input, msgs);
                }
                else {
                    input = document.getElementById(id);
                    show_form_error(input, msgs);
                    if (!input) carp('Error reported for nonexistant input #',id);
                }

                var $p_element = $('<p>');
                // FIXME (what following 3 lines do?):
                $p_element.data('rel_input',
                      !input                             ? null
                    : $( str_concat('#',input.id,'_suggest') ).length  ? $( str_concat('#',input.id,'_suggest') ).get(0) // take suggest input if available
                    :                                      input                             // otherwise the input itself
                );
                try {
                    var $error_label = $( str_concat('label[for=',input.id,']') );
                    var parts = [
                        '__FILL_THIS__',
                        ': ' ,
                        first_message
                    ];
                    if ($error_label) {
                            parts[0] = $error_label.text();
                    } else {
                            parts[0] = id;
                    }
                    $p_element.text(parts.join('').replace(/:$/,''));
                } catch (e) {
                    // problem occurred
                    $p_element.text(first_message);
                }
                $p_element.click( function(evt) { // focus and scroll to the input
                    if (evt.button != 0) return;
                    var input = $(this).closest('p').data('rel_input');
                    try { focus_errored_element(input); } catch(e) { carp(e); }
                    $(input).addClass('blink')
                    .closest('.collapsed').removeClass('collapsed').addClass('collapse');
                    setTimeout( error_blinking_input, 1500 );
                    return false;
                });
                $p_element.appendTo($err_overlay);
            }
            $err_overlay.show();
        }
        else {
            if (!$form) {
                alert( str_concat(
                    gettext('Error sending form.'),' ',
                    gettext('Moreover, failed to handle the error gracefully.'),"\n",
                    gettext('Reloading page'),'...'
                ) );
                location.reload();
            }
            if ($form.is('.change-form')) {
                AjaxFormLib.save_preset($form, {title: str_concat('* ',gettext('crash save')), msg: gettext('Form content backed up')});
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
        // lock the window
        lock_window();
        var parent_this = this;
        setTimeout(
            function() {
                var $form = $(parent_this).closest('.js-form');
                return ajax_submit($form, parent_this.name, true);
            },
            200
        );
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

    // set focus to first field of just-added form
    $(document).bind('content_added', function(evt, extras) {
        var $cont = $('#' + extras.target_id);
        if ($cont && $cont.length) {} else {
            log_generic.log('Error setting focus to form field: content_added provided no target_id');
            return;
        }
        $cont.find('.js-form :input').not(':hidden').first().focus();
    });
    //// End of ajax forms

    // Set up returning to publishable changelist when coming to change form from it
    $('#changelist tbody th a,.actionlist a').live('click', function(evt) {
        if (evt.button != 0) return;
        NewmanLib.ADR_STACK = [];
        var appname = /js-app-(\w+)\.(\w+)/.exec( $('#changelist').attr('className') );
        if ( ! appname ) {
            return;
        }
        var appname_path = str_concat('/' , appname[1] , '/' , appname[2] , '/');
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
        document.title = str_concat( (newtitle ? str_concat(newtitle,' | ') : '') , ORIGINAL_TITLE);
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
    function do_search(evt) {
        var $form = $('#search-form');
        var option = $form.find('select[name=action] option[selected]').val();
        if (!option) return false;
        var search_terms = $form.find('input[name=q]').val();
        var url = str_concat(option , '?q=' , search_terms);
        adr(url, {evt:evt});
        return false;
    }
    $('#search-form a.search.btn').live('click', do_search);
    function search_on_enter(evt) {
        if (evt.keyCode == CR || evt.keyCode == LF) {
            do_search(evt);
            return false;
        }
    }
    $('#search-form input[name=q]'      ).live('keypress', search_on_enter);
    $('#search-form select[name=action]').live('keypress', search_on_enter);

    // Search in change lists
    function changelist_search($input, $pop, evt) {
        if ($('#changelist').length == 0) return;   // We're not in changelist
        var is_pop = $pop.length > 0;
        var search_terms = $input.val();
        var loaded = Kobayashi.closest_loaded( $input.get(0) );
        var adr_term = str_concat('&q=' , search_terms);
        if (is_pop) {
            adr_term = str_concat('&pop=', adr_term);
        }

        // append existing filter arguments to adr_term variable
        var existing_get = Kobayashi.split_get_arguments(loaded.url);
        for (var param in existing_get) {
            if (param == 'q' || param == 'pop') {
                continue;
            }
            adr_term = str_concat(adr_term, '&', param, '=', existing_get[param]);
        }

        if (loaded.id == 'content') {
            adr(adr_term, {evt:evt});
        }
        else {
            Kobayashi.simple_load( str_concat(loaded.id , '::' , adr_term) );
        }
        return false;
    }
    $('#filters-handler .btn.search').live('click', function(evt) {
        if (evt.button != 0) return;
        var $input = $(this).prev('input#searchbar');
        var $pop = $(this).siblings('input#id_pop');
        return changelist_search( $input, $pop, evt );
    });
    $('#filters-handler #searchbar').live('keyup', function(evt) {
        if (evt.keyCode == CR || evt.keyCode == LF) {
            evt.preventDefault(); // prevent event propagation to changeform's Save button
        } else {
            return;
        }
        var $pop = $(this).siblings('input#id_pop');
        return changelist_search( $(this), $pop, evt );
    });
});

// Message bubble
function show_message(message, options) {
    if (!options) options = {};
    var duration = (options.duration == undefined) ? DEFAULT_MESSAGE_BUBBLE_DURATION : options.duration;
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
    $LOADING_MSG = show_message( str_concat(gettext('Loading'),'...'), {duration:0});
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
        message = str_concat( gettext('Request failed'),' (',xhr.status,': ',gettext(xhr.statusText),')' );
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
    unlock_window();
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
                    $( str_concat('#', Kobayashi.DEFAULT_TARGET) ).one('content_added', function(evt) {
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
                var message = str_concat( gettext('Cannot continue editing') , ' (' , gettext('object ID not received') , ')' );
                show_err(message);
                carp(message, 'xhr options:', this.vars.options);
                adr('../');
                return;
            }
            adr( str_concat('../',oid,'/') );
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
            adr( str_concat('../',oid,'/') );
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
    var redirect_to;
    try {
        data = JSON.parse(text_data);
        if (data.status == 'redirect') {
            redirect_to = data.redirect_to;
        } else {
            object_id = data.data.id;
            object_title = data.data.title;
            response_msg = data.message;
        }
    } catch(e) { carp('invalid data received from form save:', text_data, e); }
    response_msg = response_msg || gettext('Form saved');

    if (!redirect_to) {
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
        carp('Running Postsave Action Table');
        action_table.run(action);
    } else {
        show_ok(response_msg);
        adr(redirect_to, {just_set: true, nohistory: true});
    }

    Kobayashi.unload_content('history');
}

function changelist_shown_handler(evt) {
    /** called when changelist is shown (rendered) */
    function th_click(evt) {
        if ( !$(evt.target).is('th') ) {
            return;
        }
        var pass_event = jQuery.Event('click');
        pass_event.button = 0;
        evt.data.anchor.trigger(pass_event);
        evt.preventDefault();
        return false;
    }

    var $anchors = $('div#changelist table tr').filter('.row1,.row2').find('th a:last');
    $anchors.each(
        function(counter, anchor) {
            var $th = $(anchor).closest('th');
            $th.css('cursor', 'pointer');
            $th.one('click', {anchor: $(anchor)}, th_click);
        }
    );
}
//$(document).bind('changelist_shown', changelist_shown_handler); //FIXME buggy in Positions changelist.

function old_changelist_batch_success(response_text) {
    var $dialog = $('<div id="confirmation-wrapper">');
    $dialog.html(response_text).find('.cancel').click(function() {
        $dialog.remove();
        $('#content').show();
    });
    $('#content').hide().before($dialog);
}
function changelist_batch_success(response_text) {
    Kobayashi.reload_content('content');
}
function batch_delete_confirm_complete(data, xhr) {
    $('#confirmation-wrapper').remove();
    $('#content').show();
    adr('../');
}
function batch_delete_confirm_error(xhr) {
    carp('Error occured.');
    show_ajax_error(xhr);
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
    }).html( str_concat('<img alt="?" src="',MEDIA_URL,'ico/16/help.png" />') ).data('antecedant_input', $(this));
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

// Actions
$(document).bind('content_added', function(evt) {
    var actions_flag = false;
    $('#action-toggle').click(function() {
        actions_flag = !actions_flag;
        $('input.action-select').attr('checked', actions_flag);
    });
});

// Related lookup
$(document).bind('content_added', function(evt) {
    if ($(evt.target).find('.suggest-related-lookup').length) {
        request_media(MEDIA_URL +  'js/related_lookup.js');
        request_media(MEDIA_URL + 'css/related_lookup.css');
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
    function OverlayOpener(content_type, selection_callback, overlay_data) {
        var arg_content_type = content_type;
        var arg_selection_callback = selection_callback;

        // 1st step
        function init_overlay_html() {
            get_html_chunk('overlay', init_overlay_html_chunk_callback);
        }

        // 2nd step
        function init_overlay_html_chunk_callback(data) {
            overlay_html = data;
            continue_opening_overlay(arg_content_type, arg_selection_callback);
        }

        // 3rd (final) step
        function continue_opening_overlay(content_type, selection_callback) {
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

            if (typeof(overlay_data) !== 'object') {
                overlay_data = {};
            }
            overlay_data.selection_callback = selection_callback;
            $('#overlay-content').data(overlay_data);

            var ct_arr = /(\w+)\W(\w+)/.exec( content_type );
            if ( ! ct_arr ) {
                carp('open_overlay: Unexpected content type: '+content_type);
                return false;
            }
            var address = str_concat('/' , ct_arr[1] , '/' , ct_arr[2] , '/?pop');

            Kobayashi.load_content({
                address: address,
                target_id: 'overlay-content',
                selection_callback: selection_callback
            });
        }
        
        // init
        init_overlay_html();

        return this;
    }

    var overlay_html;
    
    open_overlay = OverlayOpener;
    $('.overlay-closebutton').live('click', function() {
        $(this).closest('.overlay').css({zIndex:5}).hide()
        .find('.overlay-content').removeData('selection_callback');
        Kobayashi.unload_content('overlay-content');
    });
    function init_overlay_content(evt, extras) {
        var $target = $(evt.target);

        var target_selector = $target.attr('id') ? str_concat('#',$target.attr('id'),' ') : '';

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

        // search button
        $target.find('#filters-handler .btn.icn.search').attr('href', 'filters::overlay-content::filters/');

        // filters
        var $filt = $('#filters-handler .popup-filter');
        if ($filt.length) {
            $filt.addClass('js-simpleload').attr( 'href', $filt.attr('href').replace(/::::/, str_concat('::',$target.attr('id'),'::') ) );
            function init_filters() {
                $(this).find('.filter li a').each( function() {
                    var $this = $(this);
                    $this.attr('href', $this.attr('href').replace(/^\?/, 'overlay-content::&')).addClass('js-simpleload');
                    var href = $this.attr('href');
                    var params = href.split(/&/);
                    // params[1] is part after token 'overlay-content::'
                    if (params.length == 2 && params[1].indexOf('pop') >= 0) {
                        // there is no other GET parameter, addition of string '&q=' is needed
                        $this.attr('href', href + '&q=');
                    }
                });
            }
            log_generic.log('HREF: ', $filt.attr('href'));
            $('#filters').unbind('content_added', init_filters).one('content_added', init_filters);
        }
        log_generic.log('init_overlay_content');

        var $cancel = $('#filters-handler a.js-clear').not('.overlay-adapted');
        if ($cancel.length) $cancel
        .attr( 'href', str_concat($target.attr('id'),'::',$cancel.attr('href')) )
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


// Timeline (ella.exports application)

function timeline_init() {
    $(document).one('media_loaded', Timeline.timeline_register);
}

Timeline = new Object();
( function() {
    function changed(event, ui) {
        carp("Timeline changed:", event);
    }

    function item_clicked(event, ui) {
        carp("Item hit:", event);
    }

    function item_mouse_over(event, ui) {
        $(this).find('.timeline-item-navigation').show()
    }

    function item_mouse_out(event, ui) {
        $(this).find('.timeline-item-navigation').hide()
    }

    function drag_update(event, ui) {
        /*var $target = $( evt.target );
        $target.find('input.item-order').each( function(i) {
            var ord = i+1;
            $(this).val( ord ).change();
            $(this).siblings('h4:first').find('span:first').text( ord );
        });
        $target.children().removeClass('last-related');
        $target.children(':last').addClass('last-related');*/
    }

    // dialog -- Publishable suggester

    function click_continue_dialog(export_params) {
        var url_parts = export_params.id.replace(/;/g, '/');
        var id_publishable_value = $('#id_publishable').val();
        var id_publishable = id_publishable_value.split('#')[0];
            //'service-container::::',
        var parts = [
            BASE_URL,
            export_params.url,
            url_parts,
            '/',
            id_publishable,
            '/'
        ];
        //carp('Final URL: ' + parts.join(''));
        // Final URL example: '/newman/#/exports/export/timeline/insert/position/id_item/id_export/'
        var ajax_params = {
            url: parts.join(''),
            type: 'GET',
            dataType: 'script',
            success: click_continue_dialog_ajax_success,
            error: click_continue_dialog_ajax_error
        };
        $.ajax(ajax_params);
        return false;
    }

    function modified_simple_load(specifier, success_callback) {
        var args = Kobayashi.get_simple_load_arguments(specifier);
        if (args == null) return;
        args.success_callback = success_callback;
        Kobayashi.load_content(args);
    }

    function omit_newman(url) {
        return url.replace(BASE_URL, '/');
    }

    function exportmeta_postsave_callback() {
        $('#id-exportmeta-modal-dialog').hide();
        window.location.reload();
    }
    Timeline.exportmeta_postsave_callback = exportmeta_postsave_callback;

    function click_continue_dialog_ajax_success(response_text) {
        var success_callback = function() {
            // keep Save button only
            $('#id-exportmeta div.submit-row').children().each(
                function() {
                     if ($(this).attr('name') != '_save') {
                        $(this).remove();
                     }
                }
            );
            // remove breadcrumbs (die Broesel)
            $('.breadcrumbs').each(
                function() {
                    $(this).remove();
                }
            );
            $('.breadcrumbs').remove();
            // remove content-toolbar table (presets, help, etc.)
            $('#content-toolbar').each(
                function() {
                    $(this).remove();
                }
            );
            $('#content-toolbar').remove();
            // bind custom _save callback (post save action)
            $('.change-form .js-form-metadata #save-change-form-success').data(
                'callback',
                Timeline.exportmeta_postsave_callback
            );
            // prefill form
            var form_selector = '#id-exportmeta .change-form';
            PrefilledChangeForm.fill_form(form_selector, Timeline._continue_dialog_redirect_to);
            // disable auto-save!
            $(document).unbind('content_added', Drafts.set_autosave_interval);
        };

        try {
            var json_redir = JSON.parse(response_text);
            // simple-load(tm) content
            Timeline._continue_dialog_redirect_to = json_redir.redirect_to; // temporary "static" variable
            var selector = [
                'id-exportmeta',
                '::::',
                omit_newman(json_redir.redirect_to)
            ];
            hide_dialog();
            $('#id-exportmeta-modal-dialog').show();
            modified_simple_load(selector.join(''), success_callback);
        } catch(e) {
            show_err(gettext('Wrong response received from timeline-insert view.'));
        }
    }

    function click_continue_dialog_ajax_error() {
        show_err(gettext('Error processing timeline-insert reponse (JSON redirect).'));
    }

    // shows publishable choice dialog
    function show_publishable_choice_dialog(export_params) {
        $('#id-modal-dialog').show();
        $('.suggest-bubble,.suggest-list,.suggest-fields-bubble').css('z-index', '90');
        $('#id_publishable_suggest').focus();

        $('#id-continue-dialog').bind(
            'click',
            function() {
                hide_dialog();
                return export_params.continue_click_callback(export_params);
            }
        );
    }

    // insert an export position
    function show_insert_dialog(evt) {
        // Position, id_item, id_export contained in tartget element id.
        var export_params = new Object();
        export_params.id = evt.target.id;
        export_params.event_data = evt;
        export_params.url = 'exports/export/timeline/insert/';
        export_params.continue_click_callback = click_continue_dialog;
        show_publishable_choice_dialog(export_params);
    }

    // append an export position
    function show_append_dialog(evt) {
        // Position, id_item, id_export contained in tartget element id.
        var export_params = new Object();
        export_params.id = evt.target.id;
        export_params.event_data = evt;
        export_params.url = 'exports/export/timeline/append/';
        export_params.continue_click_callback = click_continue_dialog;
        show_publishable_choice_dialog(export_params);
    }

    function hide_dialog() {
        // remove suggester -- hide
        // TODO cleaning of suggester should be implemented in generic.suggest.js library!
        $('#id-modal-dialog').hide();
        $('#id_publishable').value = '#';
        $('.suggest-selected-item').remove();
        $('.suggest-bubble,.suggest-list,.suggest-fields-bubble').css('z-index', '0');
    }

    function remove_beginning_char(address, character) {
        var ch = '/';
        if (character) ch = character;
        if (address.charAt(0) == ch) {
            return address.substring(1);
        }
        return address;
    }

    // register timeline events, etc. (entry point)

    function timeline_register() {
        var sortable_params = {
            axis: 'y',
            items: '.timeline-item',
            containment: 'parent',
            cursor: 'move',
            delay: 100,
            // callback when timeline is changed
            stop: changed,
            update: drag_update,
        }
        //$('.timeline-ul').sortable(sortable_params);
        //$('.timeline-ul').disableSelection();
        //$('.timeline-item').click(item_clicked);
        $('.timeline-item').hover(item_mouse_over, item_mouse_out);

        $('.timeline-item-navigation a.edit').live('mousedown', function(evt) {
            if (evt.button != 0) return;
            var from_url = str_concat(document.location.pathname , document.location.hash);
            var to_url = $(this).attr('href');
            // remove /#  from to_url
            to_url = remove_beginning_char(to_url);
            to_url = remove_beginning_char(to_url, '#'); 
            from_url = remove_beginning_char(from_url);

            NewmanLib.ADR_STACK = [
                { from: from_url, to: to_url }
            ];
        });

        /*
        $('.timeline-item-navigation .insert').live(
            'click',
            show_insert_dialog
        );
        $('.timeline-item-navigation .append').live(
            'click',
            show_append_dialog
        );

        // TODO change z-index to NULL when URL is changed before the dialog is closed.
        $('#id-modal-dialog #id-close-dialog').live(
            'click',
            hide_dialog
        );
        */
    }
    Timeline.timeline_register = timeline_register;

})(); // end of Timeline

// Main category filter widget
var __MainCategoryFilter = function() {
    // depends on Kobayashi object, jQuery
    //me.super_class = OtherClass;

    function init(target_id, display_element_selector) {
        this.target_id = target_id;
        this.display_element_selector  = display_element_selector;
        this.CATEGORY_FILTER_URL = '/nm/filter-by-main-categories/';
        this.ASYNC_REGISTER_DELAY = 500;
        this.displayed = false;
    }
    this.init = init;

    function register_post_save() {
        $frm = $(this.display_element_selector);
        if ($frm.length == 0) {
            // if newman homepage element is not found abort loading main category filter.
            return;
        }
        var me = this;
        function wrap() {
            me.display();
        }
        $frm.find('input[type=hidden][name=success]').data('callback', wrap);
    }
    this.register_post_save = register_post_save;

    function display() {
        if ($(this.display_element_selector).length == 0) {
            // if newman homepage element is not found abort loading main category filter.
            return;
        }
        var args = {
            address: this.CATEGORY_FILTER_URL,
            target_id: this.target_id
        };
        Kobayashi.load_content(args);
        var me = this;
        function reg_wrap() {
            me.register_post_save(); // should by called asynchronously due to dom is not ready yet.
        }
        $(document).one('content_added', reg_wrap);
        this.displayed = true;
    }
    this.display = display;

    return this;
};
var __MainCategoryFilter4ChangeList = function() {
    // depends on MainCategoryFilter object, Kobayashi object.
    this.super_class = MainCategoryFilter;

    function init(target_id, display_element_selector, reload_element_id) {
        MainCategoryFilter.call(this, target_id, display_element_selector);
        this.reload_element_id = reload_element_id;
    }
    this.init = init;

    function register_post_save() {
        $frm = $(this.display_element_selector);
        if ($frm.length == 0) {
            // if newman homepage element is not found abort loading main category filter.
            return;
        }
        var me = this;
        function wrap() {
            Kobayashi.reload_content(me.reload_element_id);
        }
        $frm.find('input[type=hidden][name=success]').data('callback', wrap);
    }
    this.register_post_save = register_post_save;

    function toggle_display() {
        var $elem = $(this.display_element_selector);
        if ( $elem.is(':visible') && this.displayed ) {
            $elem.hide();
        } else {
            if (!this.displayed) {
                this.display();
                return;
            }
            $elem.show();
        }
    }
    this.toggle = toggle_display;

    return this;
};
var MainCategoryFilter = to_class(__MainCategoryFilter);
var MainCategoryFilter4ChangeList = to_class(__MainCategoryFilter4ChangeList);

// filter placed on homepage
var hp_main_category_filter = new MainCategoryFilter(
    'id-hpbox-setup-main-category-filters',
    '#id-hpbox-setup-main-category-filters'
);
// filter placed in changelists (not popup changelists)
var changelist_main_category_filter = null;
(function() {
    function display_main_category_filter_in_homepage() {
        // jquery changes context for display method to selector's target, so
        // calling .display() must be wrapped in another function.
        hp_main_category_filter.display(); 
    }

    function display_main_category_filter_in_changelist() {
        changelist_main_category_filter.toggle();
        // apply css to shown div
        var $div = $('div#id-main-category-filter');
        $div.css('position', 'absolute');
    }

    function register_main_category_button() {
        var $button = $('div#id-main-category-filter').siblings().find('.btn.combo');
        if ($button.length != 1) {
            return;
        }
        changelist_main_category_filter = new MainCategoryFilter4ChangeList(
            'id-main-category-filter',
            '#id-main-category-filter',
            'content'
        );
        $button.unbind('click', display_main_category_filter_in_changelist);
        $button.bind('click', display_main_category_filter_in_changelist);
    }
    function filters_content_added() {
        register_main_category_button();
    }

    function register_filters_show_click() {
        $('.icn.btn.filter').live( 'click', 
            function() {
                var $filters = $('div#filters');
                $filters.unbind('content_added', filters_content_added);
                $filters.one('content_added', filters_content_added);
            }
        );
    }

    $(document).bind( 'media_loaded', display_main_category_filter_in_homepage );
    $(document).bind( 'changelist_shown', register_filters_show_click );
})(jQuery);
// end of Main category filter widget


// EOF
