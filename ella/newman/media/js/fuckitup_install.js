var MARKITUP_PREVIEW_SIZE_ADDITION = 10; //px

function preview_iframe_height($iFrame, $txArea) {
    if ($iFrame) {
        $iFrame.css("height", Math.max(50, $txArea.height() + MARKITUP_PREVIEW_SIZE_ADDITION)+"px");
    }
}

function preview_height_correct(evt) {
    var $container = $(evt.currentTarget).parents('.markItUpContainer');
    var $editor = $container.find('.markItUpEditor');
    var $iFrame = $container.find('iframe');
    preview_iframe_height($iFrame, $editor);
}

// resize appropriately after enter key is pressed inside markItUp <textarea> element.
function enter_pressed_callback(evt) {
    var $txArea = $(evt.currentTarget);
    var $container = $txArea.parents('.markItUpContainer');
    var $iFrame = $container.find('iframe');
    preview_iframe_height($iFrame, $txArea);
}

function discard_auto_preview(evt) {
    var $editor = markitdown_get_editor(evt);
    var existing_tm = $editor.data('auto_preview_timer');
    if (existing_tm) {
        clearTimeout(existing_tm);
        $editor.data('auto_preview_timer', null);
    }
    //carp('Discarding auto preview for: ' + $editor.selector);
}

function markitdown_get_editor(evt) {
    var $container = $(evt.currentTarget).parents('.markItUpContainer');
    var $editor = $container.find('.markItUpEditor');
    return $editor;
}

function markitdown_auto_preview(evt, optional_force_preview) {
    var AGE = 90;
    var MIN_KEY_PRESS_DELAY = 1000;
    var $editor = markitdown_get_editor(evt);
    var $text_area = $editor.data('newman_text_area');
    var existing_tm = $editor.data('auto_preview_timer');
    var now = new Date().getTime();

    function set_preview_timer() {
        var tm = setTimeout(function() {markitdown_auto_preview(evt, true); }, AGE);
        $editor.data('auto_preview_timer', tm);
        existing_tm = tm;
    }

    if (optional_force_preview) {
        var last_key = Number($editor.data('last_time_key_pressed'));
        var trigger_ok = false;

        if (existing_tm) {
            clearTimeout(existing_tm);
            //carp('Clearing timeout ' + existing_tm);
            existing_tm = null;
            $editor.data('auto_preview_timer', existing_tm);
            trigger_ok = true;
        }
        var difference = now - last_key;
        if ( difference < MIN_KEY_PRESS_DELAY ) {
            // if key was pressed in shorter time MIN_KEY_PRESS_DELAY, re-schedule preview refresh
            set_preview_timer();
            //carp('Update timer Re-scheduled. diff=' + difference);
            return;
        }
        if (trigger_ok) {
            //carp('Auto preview triggering preview. diff=' + difference);
            //markitdown_trigger_preview(evt);
            $text_area.trigger('item_clicked.newman_text_area_toolbar', 'preview');
        }
        return;
    }

    $editor.data('last_time_key_pressed', now);

    if (!existing_tm) {
        // schedule preview refresh
        set_preview_timer();
        //carp('Update timer scheduled.');
    }
}

var TextAreaFocusListener = function() {
    var me = new Object();
    var hide_toolbar_timeout = null;
    var $last_shown_header = null;

    function clean_toolbar_div() {
        var $bar = $('.js-textarea-toolbar');
        $bar.children().detach();
        $bar.hide();
        $last_shown_header = null;
        carp('Toolbar cleaned');
    }

    function focus_in($text_area, $header) {
        if (hide_toolbar_timeout) {
            carp('Clearing timeout');
            clearTimeout(hide_toolbar_timeout);
        }

        var $bar = $('.js-textarea-toolbar');
        if ($bar.find('.markItUpHeader').length && ($header == $last_shown_header)) {
            carp('toolbar instances are equiv. Aborting.');
            return;
        }
        
        clean_toolbar_div();
        $('<p class="description">Editacni lista</p>').appendTo($bar);
        $header.appendTo($bar);
        $bar.show();
        $last_shown_header = $header;
        carp('toolbar shown');
    }
    me.focus_in = focus_in;

    function focus_out($text_area, $header) {
        hide_toolbar_timeout = setTimeout(clean_toolbar_div, 500);
    }
    me.focus_out = focus_out;

    return me;
};
textarea_focus_listener = TextAreaFocusListener();

var CustomToolbar = function () {
    var me = NewmanTextAreaStandardToolbar();
    var super_get_toolbar = me.get_toolbar;

    function textarea_focus_in(evt) {
        textarea_focus_listener.focus_in(me.$text_area, me.$header);
    }

    function textarea_focus_out(evt) {
        textarea_focus_listener.focus_out(me.$text_area, me.$header);
    }

    function get_toolbar($text_area) {
        var $fake_out = $('<div></div>');
        if (!me.toolbar_generated) {
            $text_area.bind('focus', textarea_focus_in);
            $text_area.bind('focusout', textarea_focus_out);
            // super!
            super_get_toolbar($text_area);
        }
        return $fake_out;
    }
    me.get_toolbar = get_toolbar;

    return me;
};

$(function() {
    var RESIZE_DELAY_MSEC = 1250;
    var ENTER = 13;
    var KEY_A = 65;
    var KEY_Z = 90;
    var KEY_0 = 48;
    var KEY_9 = 57;
    var KEY_BACKSPACE = 8;

    var newman_text_area_settings = {
        toolbar: CustomToolbar
    };

    function register_markitup_editor_enter_callback() {
        var key_code;
        $(this).bind(
            'keyup',
            function(evt) {
                key_code = evt.keyCode || evt.which;
                key_code = parseInt(key_code);
                // auto refresh preview
                //markitdown_auto_preview(evt);
                // if not return pressed, textarea resize won't be done.
                if (key_code != ENTER) return;
                setTimeout(function() {enter_pressed_callback(evt); }, RESIZE_DELAY_MSEC);
            }
        );
    }

    $(document).bind(
        'media_loaded',
        function () {
            // enable NewmanTextArea (replacement for markItUp!)
            $('.rich_text_area').newmanTextArea(newman_text_area_settings);

            $('.markItUpEditor').each(register_markitup_editor_enter_callback);
            $('li.preview').bind('mouseup', preview_height_correct);
            $('.rich_text_area.markItUpEditor').bind('focusout', discard_auto_preview);
            //markitdown_toolbar();
            $('textarea.rich_text_area').autogrow();
        }
    );
});
