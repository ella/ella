/** 
 * Text Area powered by callbacks.
 * requires: jQuery 1.4.2+, 
 *          gettext() function, 
 *          log_ntarea object (initialized in fuckitup.js),
 *          ContentElementViewportDetector object (utils.js).
 *
 */
var NEWMAN_TEXTAREA_PREVIEW_SIZE_ADDITION = 10; //px
var newman_textarea_focused;
var newman_textarea_edit_content;

function install_box_editor() {
    // FIXME refactorize!
    function getTypeFromPath(id) {
        var path = AVAILABLE_CONTENT_TYPES[id].path;
        return path.substring(1,path.length - 1).replace('/','.');
    }

    if( $('#rich-box').length ) {
        return;
    }

    $('<div id="rich-box" title="Box"></div>').hide().appendTo('body');
    $('#rich-box').load(BASE_URL+'nm/editor-box/', function(){
        $('#id_box_obj_ct').bind('change', function(){
            if(getTypeFromPath($('#id_box_obj_ct').val()) == 'photos.photo'){
                $('#rich-box-attrs').hide();
                $('#rich-photo-format').show();
            } else {
                $('#rich-photo-format').hide();
                $('#rich-box-attrs').show();
            }
        });
        $('#lookup_id_box_obj_id').bind('click', function(e){
            e.preventDefault();
            open_overlay(getTypeFromPath($('#id_box_obj_ct').val()), function(id){
                $('#id_box_obj_id').val(id);
            });
        });
        $('#rich-object').bind('submit', function(e) {
            e.preventDefault();
            if($('#id_box_obj_ct').val()) {
                var type = getTypeFromPath($('#id_box_obj_ct').val());
                if(!!type){
                    var id = $('#id_box_obj_id').val() || '0';
                    var params = $('#id_box_obj_params').val().replace(/\n+/g, ' ');
                    // Add format and size info for photo
                    var addon = '';
                    var box_type = '';
                    if(getTypeFromPath($('#id_box_obj_ct').val()) == 'photos.photo'){
                        addon = '_'+$('#id_box_photo_size').val()+'_'+$('#id_box_photo_format').val();
                        box_type = 'inline';
                        // Add extra parameters
                        $('.photo-meta input[type=checkbox]:checked','#rich-photo-format').each(function(){
                            params += ((params) ? '\n' : '') + $(this).attr('name').replace('box_photo_meta_','') + ':1';
                        });
                    } else {
                        box_type = $('#id_box_type').val();
                    }
                    // Insert code
                    var selection_handler = TextAreaSelectionHandler();
                    newman_textarea_focused.focus();
                    selection_handler.init(newman_textarea_focused[0]); //newman_textarea_focused is jQuery object.
                    var box_text = '\n{% box '+box_type+addon+' for '+type+' with pk '+$('#id_box_obj_id').val()+' %}'+((params) ? '\n'+params+'\n' : '')+'{% endbox %}\n';
                    selection_handler.insert_after_selection(box_text);
                    // Reset and close dialog
                    $('#rich-object').trigger('reset');
                    $('#rich-box').dialog('close');
                    $('#id_box_obj_ct').trigger('change');
                    newman_textarea_focused.focus(); // after all set focus to text area
                    var toolbar = newman_textarea_focused.data('newman_text_area_toolbar_object');
                    NewmanLib.debug_area = newman_textarea_focused;
                    NewmanLib.debug_type = typeof(toolbar);
                    NewmanLib.debug_bar = toolbar;
                    if (typeof(toolbar) == 'object' && typeof(toolbar.trigger_preview) != 'undefined') {
                        toolbar.trigger_preview();
                    }
                }
            }
        });
        $('#rich-object').bind('cancel_close', function(e) {
            $('#rich-box').dialog('close');
            newman_textarea_focused.focus(); // after all set focus to text area
        });
    });
    $('#rich-box').dialog({
        modal: false,
        autoOpen: false,
        width: 420,
        height: 360
    });
}

function preview_iframe_height($iFrame, $txArea) {
    if ($iFrame) {
        $iFrame.css("height", Math.max(50, $txArea.height() + NEWMAN_TEXTAREA_PREVIEW_SIZE_ADDITION)+"px");
    }
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
    //log_ntarea.log('Discarding auto preview for: ' , $editor.selector);
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
        function call_markitdown_auto_preview() {
            markitdown_auto_preview(evt, true);
        }
        var tm = setTimeout(call_markitdown_auto_preview, AGE);
        $editor.data('auto_preview_timer', tm);
        existing_tm = tm;
    }

    if (optional_force_preview) {
        var last_key = Number($editor.data('last_time_key_pressed'));
        var trigger_ok = false;

        if (existing_tm) {
            clearTimeout(existing_tm);
            //log_ntarea.log('Clearing timeout ' , existing_tm);
            existing_tm = null;
            $editor.data('auto_preview_timer', existing_tm);
            trigger_ok = true;
        }
        var difference = now - last_key;
        if ( difference < MIN_KEY_PRESS_DELAY ) {
            // if key was pressed in shorter time MIN_KEY_PRESS_DELAY, re-schedule preview refresh
            set_preview_timer();
            //log_ntarea.log('Update timer Re-scheduled. diff=' , difference);
            return;
        }
        if (trigger_ok) {
            //log_ntarea.log('Auto preview triggering preview. diff=' , difference);
            //markitdown_trigger_preview(evt);
            $text_area.trigger('item_clicked.newman_text_area_toolbar', 'preview');
        }
        return;
    }

    $editor.data('last_time_key_pressed', now);

    if (!existing_tm) {
        // schedule preview refresh
        set_preview_timer();
        //log_ntarea.log('Update timer scheduled.');
    }
}

var toolbarButtonRegister = (function() {
    var buttons = {};

    return { // public interface
        addButton: function (title, name, callback, alt) {
            buttons[name] = ({'title': title, 'callback': callback, 'alt': alt});
        },
        getButton: function (name) {
            return buttons[name];
        },
        getButtonList: function () {
            return buttons;
        }
    };
})();

function handle_preview(evt, toolbar) {
    toolbar.trigger_preview();
}

function handle_box(evt, toolbar) {
    var me = toolbar;
    
    if (!me.$text_area) {
        log_ntarea.log('NO TEXT AREA');
        return;
    }
    $('#rich-box').dialog('open');
    var focused = me.$text_area;
    var range = focused.getSelection();
    var content = focused.val();
    if (content.match(/\{% box(.|\n)+\{% endbox %\}/g) && range.start != -1) {
        var start = content.substring(0,range.start).lastIndexOf('{% box');
        var end = content.indexOf('{% endbox %}',range.end);
        if (start != -1 && end != -1 && content.substring(start,range.start).indexOf('{% endbox %}') == -1) {
            var box = content.substring(start,end+12);
            newman_textarea_edit_content = box;
            var id = box.replace(/^.+pk (\d+) (.|\n)+$/,'$1');
            var mode = box.replace(/^.+box (\w+) for(.|\n)+$/,'$1');
            var type = box.replace(/^.+for (\w+\.\w+) (.|\n)+$/,'$1');
            var params = box.replace(/^.+%\}\n?((.|\n)*)\{% endbox %\}$/,'$1');
            $('#id_box_obj_ct').val(getIdFromPath(type)).trigger('change');
            $('#id_box_obj_id').val(id);
            if (type == 'photos.photo') {
                if(box.indexOf('show_title:1') != -1){
                    $('#id_box_photo_meta_show_title').attr('checked','checked');
                } else $('#id_box_photo_meta_show_title').removeAttr('checked');
                if(box.indexOf('show_authors:1') != -1){
                    $('#id_box_photo_meta_show_author').attr('checked','checked');
                } else $('#id_box_photo_meta_show_author').removeAttr('checked');
                if(box.indexOf('show_description:1') != -1){
                    $('#id_box_photo_meta_show_description').attr('checked','checked');
                } else $('#id_box_photo_meta_show_description').removeAttr('checked');
                if(box.indexOf('show_detail:1') != -1){
                    $('#id_box_photo_meta_show_detail').attr('checked','checked');
                } else $('#id_box_photo_meta_show_detail').removeAttr('checked');
                params = params.replace(/show_title:\d/,'').replace(/show_authors:\d/,'').replace(/show_description:\d/,'').replace(/show_detail:\d/,'').replace(/\n{2,}/g,'\n').replace(/\s{2,}/g,' ');
                if(mode.indexOf('inline_velka') != -1){
                    $('#id_box_photo_size').val('velka')
                } else if(mode.indexOf('inline_standard') != -1){
                    $('#id_box_photo_size').val('standard')
                } else if(mode.indexOf('inline_mala') != -1){
                    $('#id_box_photo_size').val('mala')
                }
                if(mode.indexOf('ctverec') != -1){
                    $('#id_box_photo_format').val('ctverec')
                } else if(mode.indexOf('obdelnik_sirka') != -1){
                    $('#id_box_photo_format').val('obdelnik_sirka')
                } else if(mode.indexOf('obdelnik_vyska') != -1){
                    $('#id_box_photo_format').val('obdelnik_vyska')
                } else if(mode.indexOf('nudle_sirka') != -1){
                    $('#id_box_photo_format').val('nudle_sirka')
                } else if(mode.indexOf('nudle_vyska') != -1){
                    $('#id_box_photo_format').val('nudle_vyska')
                }
            }
            $('#id_box_obj_params').val(params);
        }
    } else {
        log_ntarea.log('NO CONTENT MATCHED');
    }
}

function getIdFromPath(path){
    // function used by box
    var id;
    $.each(AVAILABLE_CONTENT_TYPES, function(i){
        if(this.path == '/'+path.replace('.','/')+'/'){
            id = i;
            return;
        }
    });
    return id;
}

function handle_gallery(evt, toolbar) {
    $('#rich-box').dialog('open');
    $('#id_box_obj_ct').val(getIdFromPath('galleries.gallery')).trigger('change');// 37 is value for galleries.gallery
}

function handle_photo(evt, toolbar) {
    $('#rich-box').dialog('open');
    $('#id_box_obj_ct').val(getIdFromPath('photos.photo')).trigger('change');// 20 is value for photos.photo in the select box
    $('#lookup_id_box_obj_id').trigger('click');
}

function handle_unordered_list(evt, toolbar) {
    var TEXT = '* text\n';
    var sel = toolbar.selection_handler.get_selection();
    if (!sel) {
        var str = [
            '\n',
            TEXT, 
            TEXT, 
            TEXT, 
        ].join('');
        toolbar.selection_handler.replace_selection(str);
        toolbar.trigger_delayed_preview();
        return;
    }
    var lines = sel.split(/\r\n|\n|\r/);
    var bullet_lines = [];
    for (var i = 0; i < lines.length; i++) {
        if ( /^\*\s+/.test( lines[i] ) ) {
            bullet_lines[i] = lines[i];
            continue;
        }
        bullet_lines[i] = [ '* ', lines[i] ].join('');
    }
    var str = bullet_lines.join('\n');
    toolbar.selection_handler.replace_selection(str);
    toolbar.trigger_delayed_preview();
}

function handle_ordered_list(evt, toolbar) {
    var TEXT = ' text';
    var sel = toolbar.selection_handler.get_selection();
    if (!sel) {
        var str = [
            '\n' // end line befor list begins
        ];
        for (var i = 1; i < 4; i++) {
            str.push( [ i.toString(), '.', TEXT ].join('') );
        }
        toolbar.selection_handler.replace_selection(str.join('\n'));
        toolbar.trigger_delayed_preview();
        return;
    }
    var lines = sel.split(/\r\n|\n|\r/);
    var numbered_lines = [];
    var line_regex = /^(\d+)(\.\s+.*)/;
    for (var i = 0; i < lines.length; i++) {
        var match = lines[i].match(line_regex);
        var counter = i + 1;
        if ( match ) {
            numbered_lines[i] = lines[i].replace(line_regex, counter + '$2');
            continue;
        }
        numbered_lines[i] = [ counter.toString(), '. ', lines[i] ].join('');
    }
    var str = numbered_lines.join('\n');
    toolbar.selection_handler.replace_selection(str);
    toolbar.trigger_delayed_preview();
}

function heading_markup(heading_char, default_text, toolbar) {
    var selection = toolbar.selection_handler.get_selection();
    if (selection == '') {
        selection = default_text;
    }
    var str = [
        '\n\n',
        selection,
        '\n',
        new Array( selection.length ).join(heading_char),
        '\n'
    ].join('');
    toolbar.selection_handler.replace_selection(str);
    toolbar.trigger_delayed_preview();
}

function handle_h1(evt, toolbar) {
    heading_markup('=', gettext('Heading H1'), toolbar);
}

function handle_h2(evt, toolbar) {
    heading_markup('-', gettext('Heading H2'), toolbar);
}

function handle_h3(evt, toolbar) {
    var sel = toolbar.selection_handler.get_selection();
    if (!sel) {
        sel = gettext('Heading H3');
    }
    var str = [
        '\n\n### ',
        sel,
        '\n'
    ].join('');
    toolbar.selection_handler.replace_selection(str);
    toolbar.trigger_delayed_preview();
}

function handle_bold(evt, toolbar) {
    toolbar.selection_handler.wrap_selection('**', '**');
    toolbar.trigger_delayed_preview();
}

function handle_italic(evt, toolbar) {
    toolbar.selection_handler.wrap_selection('*', '*');
    toolbar.trigger_delayed_preview();
}

function handle_url(evt, toolbar) {
    //'[', closeWith:']([![Url:!:http://]!] "[![Title]!]")', placeHolder: 'Text odkazu'
    var result = null;
    var replacement = '';
    var text = toolbar.selection_handler.get_selection();
    if (!text) {
        text = prompt('Text:', '');
        if (text == null) return;
    }
    result = prompt('URL:', 'http://');
    if (result == null) return;
    // if protocol is not inserted, force HTTP
    if ( ! /:\/\//.test(result) ) {
        result = 'http://' + result;
    }
    replacement = [
        '[',
        text,
        ']',
        '(',
        result,
        ' "',
        text,
        '")'
    ].join(''); // produces [Anchor text](http://dummy.centrum.cz "Anchor text")
    toolbar.selection_handler.replace_selection(replacement);
    toolbar.trigger_delayed_preview();
}

toolbarButtonRegister.addButton(gettext('Italic'), 'italic', handle_italic, 'I');
toolbarButtonRegister.addButton(gettext('Bold'), 'bold', handle_bold, 'B');
toolbarButtonRegister.addButton(gettext('Link'), 'url', handle_url, 'L');

toolbarButtonRegister.addButton(gettext('Head 1'), 'h1', handle_h1, '1');
toolbarButtonRegister.addButton(gettext('Head 2'), 'h2', handle_h2, '2');
toolbarButtonRegister.addButton(gettext('Head 3'), 'h3', handle_h3, '3');

toolbarButtonRegister.addButton(gettext('List unordered'), 'list-bullet', handle_unordered_list);
toolbarButtonRegister.addButton(gettext('List ordered'), 'list-numeric', handle_ordered_list);

toolbarButtonRegister.addButton(gettext('Box'), 'box', handle_box);
toolbarButtonRegister.addButton(gettext('Photo'), 'photo', handle_photo);
toolbarButtonRegister.addButton(gettext('Gallery'), 'gallery', handle_gallery);

toolbarButtonRegister.addButton(gettext('Quick preview'), 'preview', handle_preview);

/**
 * Standard toolbar with Bold, Italic, ..., Preview buttons.
 */
var NewmanTextAreaStandardToolbar = function () {
    var PREVIEW_URL = BASE_URL + 'nm/editor-preview/';
    var PREVIEW_VARIABLE = 'text';
    var PREVIEW_LOADING_GIF = MEDIA_URL + 'ico/15/loading.gif';
    var AUTO_PREVIEW_TOOLBAR_BUTTON_CLICKED_DELAY = 250; //msec
    var me = NewmanTextAreaToolbar();
    // selection_handler holds text selection of textarea element.
    var selection_handler = TextAreaSelectionHandler();
    me.selection_handler = selection_handler;
    // Note: me.$text_area holds associated textarea element
    var button_handlers = {
        bold: handle_bold,
        italic: handle_italic,
        url: handle_url,
        h1: handle_h1,
        h2: handle_h2,
        h3: handle_h3,
        photo: handle_photo,
        gallery: handle_gallery,
        box: handle_box,
        preview: handle_preview
    };
    button_handlers['list-bullet'] = handle_unordered_list;
    button_handlers['list-numeric'] = handle_ordered_list;
    var preview_window = null;
    me.preview_window = preview_window;

    function render_preview(success_callback) {
        var res = '';
        function success_handler(data) {
            res = data;
            try {
                success_callback(data);
            } catch (e) {
                log_ntarea.log('Problem calling preview success callback.' , e);
            }
        }

        function error_handler(xhr, error_status, error_thrown) {
            res = [
                gettext('Preview error.'),
                '\nException: ',
                error_thrown
            ].join('');
        }
        
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        //alert(csrf_token);
        var csrf_data = [ 'csrfmiddlewaretoken', '=', encodeURIComponent(csrf_token) ].join('');
        var preview_data = [ PREVIEW_VARIABLE, '=', encodeURIComponent(me.$text_area.val()) ].join('');
        var final_data = [ preview_data, '&', csrf_data ].join('')

        $.ajax( 
            {
                type: 'POST',
                async: true,
                cache: false,
                url: PREVIEW_URL,
                //data: [ PREVIEW_VARIABLE, '=', encodeURIComponent(me.$text_area.val()) ].join(''),
                data: final_data,
                success: success_handler,
                error: error_handler
            } 
        );
        return res;
    }

    function render_preview_wait() {
        var wait_data = [
            '<html><body>',
            '<div style="position: fixed; left: 20%; top: 20%;">',
            '<img src="',
            PREVIEW_LOADING_GIF,
            '" alt="" />&nbsp;&nbsp;&nbsp;',
            gettext('Sending'),
            '</div>',
            '</body></html>'
        ];
        /*
        wait_data = [
            '<html><body>',
            'Wait...',
            '</body></html>'
        ];
        */
        me.preview_window.document.open();
        me.preview_window.document.write(wait_data.join(''));
        me.preview_window.document.close();
    }

    function preview_show_callback(data) {
        if (me.preview_window.document) {
            me.$preview_iframe.hide();
            var sp;
            try {
                sp = me.preview_window.document.documentElement.scrollTop
            } catch(e) {
                sp = 0;
            }
            me.preview_window.document.open();
            me.preview_window.document.write(data);
            me.preview_window.document.close();
            me.preview_window.document.documentElement.scrollTop = sp;
            me.$text_area.trigger('preview_done', [me.$text_area, me.$preview_iframe, me.preview_window]); // trigger event on textarea when preview is finished
            me.$preview_iframe.show();
        }
        //preview_window.focus();
    }
    
    function handle_preview(evt) {
        var $iframe = me.$text_area.closest('.markItUpContainer').find('iframe.markItUpPreviewFrame');
        if ($iframe.length == 0) {
            $iframe = $('<iframe class="markItUpPreviewFrame"></iframe>');
        }
        $iframe.insertAfter(me.$text_area);
        me.preview_window = $iframe[$iframe.length-1].contentWindow || frame[$iframe.length-1];
        me.$preview_iframe = $iframe;
        render_preview_wait(me.preview_window);
        render_preview(preview_show_callback);
        me.$text_area.focus();
    }
    
    function trigger_preview() {
        handle_preview();
    }
    me.trigger_preview = trigger_preview;
    
    function trigger_delayed_preview() {
        setTimeout(handle_preview, AUTO_PREVIEW_TOOLBAR_BUTTON_CLICKED_DELAY);
    }
    me.trigger_delayed_preview = trigger_delayed_preview;
    
    function toolbar_buttons() {
        // creates NewmanTextAreaToolbar items.
        
        for (name in toolbarButtonRegister.getButtonList()) {
            b = toolbarButtonRegister.getButton(name);
            me.add_item(b.title, name, b.alt);
        }
        // TODO: add separators!
    }
    me.toolbar_buttons = toolbar_buttons;

    function item_clicked(evt, button_name) {
        var b = toolbarButtonRegister.getButton(button_name);
        var cback = b.callback;
        //log_ntarea.log('item_clicked ' , button_name , ', element name:' , me.$text_area.attr('name'));
        if (typeof(cback) == 'undefined') return;
        try {
            selection_handler.init(me.$text_area[0]); // init selection_handler (assigns textarea selection)
            cback(evt, me);
        } catch (e) {
            log_ntarea.log('item_clicked error: ' , e);
        }
    }
    me.toolbar_item_clicked = item_clicked;

    return me;
};

var TextAreaFocusListener = function() {
    /**
     * TextAreaFocusListener manages showing and hiding of toolbar.
     * Listens to all focus and focusout events triggered in textareas.
     */
    var me = new Object();
    var TOOLBAR_HIDE_TIMEOUT = 500; //msec
    var hide_toolbar_timeout = null;
    var $last_shown_header = null;
    var detector = null;
    var main_toolbar_offset = $('#header').position().top + $('#header').height();
    var main_toolbar_offset_px = main_toolbar_offset + 'px';

    function clean_toolbar_div() {
        var $bar = $('.js-textarea-toolbar');
        $bar.children().detach();
        $bar.hide();
        $last_shown_header = null;
        $('div#container').unbind('scroll.text_area_focus_listener', scroll_handler);
        detector = null;
        //log_ntarea.log('Toolbar cleaned');
    }

    function toolbar_stick_to_top($bar, $text_area) {
        //log_ntarea.log('sticked to top');
        //$bar.css('position', 'relative');
        var pos = [
            main_toolbar_offset + $text_area.position().top - $bar.height() - 5,
            'px'
        ].join('');
        $bar.css('top', pos);
        $bar.show();
    }

    function toolbar_stick_to_bottom($bar, $text_area) {
        //log_ntarea.log('sticked to bottom');
        //$bar.css('position', 'relative');
        var pos = [
            main_toolbar_offset + $text_area.height() + $text_area.position().top,
            'px'
        ].join('');
        $bar.css('top', pos);
        $bar.show();
    }

    function toolbar_float($bar) {
        //log_ntarea.log('floats on top');
        $bar.css('top', main_toolbar_offset_px);
        $bar.show();
    }

    function scroll_handler(evt) {
        var $bar = evt.data.$bar;
        if ( !detector.in_viewport() ) {
            // hide toolbar
            //log_ntarea.log('hidden');
            $bar.hide();
        } else if (detector.top_in_viewport() && !detector.bottom_in_viewport()) {
            // show toolbar sticked to textarea's top
            toolbar_stick_to_top($bar, evt.data.$text_area);
        } else if (detector.top_in_viewport() && detector.bottom_in_viewport()) {
            toolbar_stick_to_top($bar, evt.data.$text_area);
        } else {
            // only middle-part of textarea is in viewport, toolbar floats on top
            toolbar_float($bar);
        }
    }

    function show_toolbar($bar, $header) {
        clean_toolbar_div();
        /*var p_element = [
            '<p class="description">',
            gettext('Edit toolbar'),
            '</p>'
        ].join('');
        NewmanLib.debug_textarea = $text_area;
        $(p_element).appendTo($bar);*/
        $header.appendTo($bar);
        $bar.show();
        $last_shown_header = $header;
        //log_ntarea.log('toolbar shown');
    }

    function focus_in($text_area, $header) {
        if (hide_toolbar_timeout) {
            //log_ntarea.log('Clearing timeout');
            clearTimeout(hide_toolbar_timeout);
        }
        newman_textarea_focused = $text_area;

        var $bar = $('.js-textarea-toolbar');
        if ($bar.find('.markItUpHeader').length && ($header == $last_shown_header)) {
            //log_ntarea.log('toolbar instances are equiv. Aborting.');
            return;
        }
        show_toolbar($bar, $header);    

        // register handler for scroll event
        detector = new ContentElementViewportDetector($text_area);
        var $container = $('div#container');
        $container.bind('scroll.text_area_focus_listener', {$bar: $bar, $text_area: $text_area}, scroll_handler);
        $container.trigger('scroll.text_area_focus_listener');
    }
    me.focus_in = focus_in;

    function focus_out($text_area, $header) {
        hide_toolbar_timeout = setTimeout(clean_toolbar_div, TOOLBAR_HIDE_TIMEOUT);
    }
    me.focus_out = focus_out;

    return me;
};
textarea_focus_listener = TextAreaFocusListener(); // shared object among CustomToolbar instances.

var FloatingOneToolbar = function () {
    /**
     * Toolbar floats in fix-positioned <div>. textarea_focus_listener 
     * object handles showing and hiding of appropriate toolbar.
     * If textarea has focus (blinking caret) it's toolbar is shown, while
     * other textarea related toolbars are hidden.
     */
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
    // keycode table http://www.scottklarr.com/topic/126/how-to-create-ctrl-key-shortcuts-in-javascript/
    var RESIZE_DELAY_MSEC = 1250;
    var ENTER = 13;
    var KEY_A = 65;
    var KEY_Z = 90;
    var KEY_0 = 48;
    var KEY_9 = 57;
    var KEY_NUM_0 = 96;
    var KEY_NUM_DIVIDE = 111;
    var KEY_BACKSPACE = 8;
    var KEY_DELETE = 46;

    var newman_text_area_settings = {
        toolbar: FloatingOneToolbar
    };

    function register_textarea_events() {
        var key_code;
        var $tx_area = $(this);
        function textarea_keyup_handler(evt) {
            key_code = evt.keyCode || evt.which;
            key_code = parseInt(key_code);
            // auto refresh preview
            if ( 
                (key_code >= KEY_0 && key_code <= KEY_9) ||
                (key_code >= KEY_NUM_0 && key_code <= KEY_NUM_DIVIDE) ||
                (key_code >= KEY_A && key_code <= KEY_Z) ||
                key_code == KEY_BACKSPACE ||
                key_code == KEY_DELETE ||
                key_code == 0 // national coded keys
            ) {
                markitdown_auto_preview(evt);
            }
            // if not return pressed, textarea resize won't be done.
            if (key_code != ENTER) return;
            setTimeout(function() {enter_pressed_callback(evt); }, RESIZE_DELAY_MSEC);
        }

        $tx_area.bind('keyup', textarea_keyup_handler);

        $tx_area.bind(
            'preview_done',
            function (evt, $text_area, $iframe, preview_window) {
                preview_iframe_height($iframe, $text_area);
            }
        );
    } // end of register_textarea_events

    function media_loaded_handler() {
        // install only if there is change-form displayed
        if ($('.change-form').length == 0) {
            return;
        }
        if ( $('.change-form').data('textarea_handlers_installed') === true ) {
            log_ntarea.log('ALREADY INSTALLED TEXTAREA HANDLERS');
            return;
        }
        log_ntarea.log('INSTALLING TEXTAREA HANDLERS...');
        // enable NewmanTextArea (replacement for markItUp!)
        install_box_editor();
        $('.rich_text_area').newmanTextArea(newman_text_area_settings);

        $('.markItUpEditor').each(register_textarea_events);
        $('.rich_text_area.markItUpEditor').bind('focusout', discard_auto_preview);
        $('textarea.rich_text_area').autogrow();
        $('.change-form').data('textarea_handlers_installed', true);
    }
    
    $(document).bind('media_loaded', media_loaded_handler);
});
