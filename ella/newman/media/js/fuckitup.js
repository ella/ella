/** 
 * Text Area powered by callbacks.
 * reuires: jQuery 1.4.2+, 
 *          gettext() function, 
 *          carp() function for logging purposes located in kobayashi.js .
 *
 * Note: Generate documentation via JSDoc http://jsdoc.sourceforge.net/ .
 */

/**
 * TextAreaSelectionHandler object is based on code snippets from Maxim Izmaylov's editor.js made for project Zenaadmin.
 */
var TextAreaSelectionHandler = function () {
    var me = new Object();
    var area = null;

    function init(textarea_element) {
        if (area == null) {
            area = textarea_element;
        }
    }
    me.init = init;

    // decorator used as check
    function check_area(func) {
        function check_it() {
            if (area == null) {
                carp('WARNING: area == null');
                return function () {};
            }
            return func.apply(null, arguments);
        }
        return check_it;
    }

	function get_selection(){
		if(!!document.selection){
			return document.selection.createRange().text;
		} else if(!!area.setSelectionRange){
			return area.value.substring(area.selectionStart, area.selectionEnd);
		} else {
			return false;
		}
	}
    me.get_selection = check_area(get_selection);

	function replace_selection(text){
		if(!!document.selection){
			area.focus();
			var old = document.selection.createRange().text;
			var range = document.selection.createRange();
			if(old == ''){
				area.value += text;
			} else {
				range.text = text;
				range -= old.length - text.length;
			}
		} else if(!!area.setSelectionRange){
			var selection_start = area.selectionStart;
			area.value = area.value.substring(0, selection_start) + text + area.value.substring(area.selectionEnd);
			area.setSelectionRange(selection_start + text.length,selection_start + text.length);
		}
        // TODO trigger event text was changed? Probably no..
		area.focus();
	}
    me.replace_selection = check_area(replace_selection);

	function wrap_selection(before, after) {
        var data = [
            before,
            me.get_selection(),
            after
        ];
		me.replace_selection(data.join(''));
	}
    me.wrap_selection = check_area(wrap_selection);

	function insert_before_selection(text){
		me.replace_selection(text + me.get_selection());
	}
    me.insert_before_selection = check_area(insert_before_selection);

	function insert_after_selection(text){
		me.replace_selection(me.get_selection() + text);
	}
    me.insert_after_selection = check_area(insert_after_selection);

	function inject_each_selected_line(callback, before, after){
		var lines = Array();
		var txt = '';
		$.each(me.get_selection().split("\n"), function(i, line){
			callback(lines, line);
		});
		for(var m = 0; m < lines.length; m++){
			txt += lines[m] + '\n';
		}
		me.replace_selection((before || '') + txt + (after || ''));
	}
    me.inject_each_selected_line = check_area(inject_each_selected_line);

	function insert_before_each_selected_line(text, before, after){
		me.inject_each_selected_line(function(lines, line){
			lines.push(text + line);
			return lines;
		}, before, after);
	}
    me.insert_before_each_selected_line = check_area(insert_before_each_selected_line);

    return me;
};


var NewmanTextAreaToolbar = function () {
    /**
     * Toolbar prototype. Should be overloaded by its copy (aka inheritance).
     */ 
    var me = new Object();
    me.toolbar_generated = false;
    me.$header = $('<div class="markItUpHeader"></div>');
    var item_counter = 1;
    var $ul = $('<ul></ul>');

   
    /**
     * toolbar_buttons function should be overloaded (and implemented).
     * This function is purposed to add toolbars' buttons and separators.
     */
    me.toolbar_buttons = function () {};

    /**
     * Adds item to toolbar. Item consists of title, class name and 
     * optionaly access key may be used.
     */
    function add_item( title, class_name, access_key ) {
        var accessible_title = '';
        if (access_key) {
            accessible_title = [
                title,
                ' [Ctrl+',
                access_key,
                ']'
            ].join('');
        } else {
            accessible_title = title;
        }
        var item = [
            '<li class="markItUpButton markItUpButton', 
            item_counter, 
            ' ',
            class_name,
            '"><a onclick="javascript:return false;" title="',
            accessible_title,
            '" accesskey="',
            access_key,
            '" href=""></a></li>'
        ].join('');
        var $item = $(item);
        $item.bind('click', me.$text_area, item_click_handler);
        $item.data('button_name', class_name); //button is named via its class
        $item.appendTo($ul);
        item_counter++;
    }
    me.add_item = add_item;

    /**
     * Callback assigned to toolbar items' click events.
     */
    function item_click_handler(evt) {
        var button_name = $(evt.target).closest('li').data('button_name');
        // When toolbar button is clicked, trigger event.
        me.$text_area.trigger('item_clicked.newman_text_area_toolbar', button_name);
        evt.preventDefault();
    }

    function add_separator() {
        var $item = $('<li class="markItUpSeparator>---</li>');
        $item.appendTo($ul);
    }
    me.add_separator = add_separator;

    /**
     * Callback invoked when action is fired.
     *
     * Example:
        function custom_toolbar_item_clicked(evt, button_name) {
            carp('item_clicked');
        }
        me.toolbar_item_clicked = custom_toolbar_item_clicked;
     */
    me.toolbar_item_clicked = null;

    /**
     * Registers handler for item_clicked event.
     */
    function register_toolbar_event_handlers() {
        var EVENT_NAME = 'item_clicked.newman_text_area_toolbar';
        if (me.toolbar_item_clicked) {
            me.$text_area.unbind(EVENT_NAME, me.toolbar_item_clicked);
            me.$text_area.bind(EVENT_NAME, me.toolbar_item_clicked);
        }
    }
    me.register_toolbar_event_handlers = register_toolbar_event_handlers;

    /**
     * Returns rendered toolbar as jQuery object.
     * @param $text_area Contains textarea for whom should be toolbar generated.
     */
    function get_toolbar($text_area) {
        if (!me.toolbar_generated) {
            me.$text_area = $text_area;
            me.toolbar_buttons();
            me.register_toolbar_event_handlers();
            $ul.appendTo(me.$header);
            me.toolbar_generated = true;
        }
        return me.$header;
    }
    me.get_toolbar = get_toolbar;


    return me;
};

/**
 * Standard toolbar with Bold, Italic, ..., Preview buttons.
 */
var NewmanTextAreaStandardToolbar = function () {
    var PREVIEW_URL = BASE_URL + 'nm/editor-preview/';
    var PREVIEW_VARIABLE = 'text';
    var PREVIEW_LOADING_GIF = MEDIA_URL + 'ico/15/loading.gif';
    var me = NewmanTextAreaToolbar();
    // selection_handler holds text selection of textarea element.
    var selection_handler = TextAreaSelectionHandler();
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
        $.ajax( 
            {
                type: 'POST',
                async: true,
                cache: false,
                url: PREVIEW_URL,
                data: [ PREVIEW_VARIABLE, '=', encodeURIComponent(me.$text_area.val()) ].join(''),
                success: function(data) {
                    res = data;
                    try {
                        success_callback(data);
                    } catch (e) {
                        carp('Problem calling preview success callback.' + e);
                    }
                },
                error: function(xhr, error_status, error_thrown) {
                    res = [
                        gettext('Preview error.'),
                        '\nException: ',
                        error_thrown
                    ].join('');
                }
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
            carp('PREVIEW DONE');
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
        render_preview_wait(me.preview_window);
        render_preview(preview_show_callback);
    }

    function handle_box(evt) {
        $('#rich-box').dialog('open');
        if (!me.$text_area) {
            return;
        }
        var focused = me.$text_area;
        var range = focused.getSelection();
        var content = focused.val();
        if (content.match(/\{% box(.|\n)+\{% endbox %\}/g) && range.start != -1) {
            var start = content.substring(0,range.start).lastIndexOf('{% box');
            var end = content.indexOf('{% endbox %}',range.end);
            if (start != -1 && end != -1 && content.substring(start,range.start).indexOf('{% endbox %}') == -1) {
                var box = content.substring(start,end+12);
                edit_content = box;
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
                    if(box.indexOf('show_author:1') != -1){
                        $('#id_box_photo_meta_show_author').attr('checked','checked');
                    } else $('#id_box_photo_meta_show_author').removeAttr('checked');
                    if(box.indexOf('show_description:1') != -1){
                        $('#id_box_photo_meta_show_description').attr('checked','checked');
                    } else $('#id_box_photo_meta_show_description').removeAttr('checked');
                    if(box.indexOf('show_detail:1') != -1){
                        $('#id_box_photo_meta_show_detail').attr('checked','checked');
                    } else $('#id_box_photo_meta_show_detail').removeAttr('checked');
                    params = params.replace(/show_title:\d/,'').replace(/show_author:\d/,'').replace(/show_description:\d/,'').replace(/show_detail:\d/,'').replace(/\n{2,}/g,'\n').replace(/\s{2,}/g,' ');
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
        }
    }

    function handle_gallery(evt) {
        $('#rich-box').dialog('open');
        $('#id_box_obj_ct').val(getIdFromPath('galleries.gallery')).trigger('change');// 37 is value for galleries.gallery
    }

    function handle_photo(evt) {
        $('#rich-box').dialog('open');
        $('#id_box_obj_ct').val(getIdFromPath('photos.photo')).trigger('change');// 20 is value for photos.photo in the select box
        $('#lookup_id_box_obj_id').trigger('click');
    }

    function handle_unordered_list(evt) {
        var TEXT = '* text\n';
        var sel = selection_handler.get_selection();
        if (!sel) {
            var str = [
                '\n',
                TEXT, 
                TEXT, 
                TEXT, 
            ].join('');
            selection_handler.replace_selection(str);
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
        selection_handler.replace_selection(str);
    }

    function handle_ordered_list(evt) {
        var TEXT = ' text';
        var sel = selection_handler.get_selection();
        if (!sel) {
            var str = [
                '\n' // end line befor list begins
            ];
            for (var i = 1; i < 4; i++) {
                str.push( [ i.toString(), '.', TEXT ].join('') );
            }
            selection_handler.replace_selection(str.join('\n'));
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
        selection_handler.replace_selection(str);
    }

    function heading_markup(heading_char, default_text) {
        var selection = selection_handler.get_selection();
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
        selection_handler.replace_selection(str);
    }

    function handle_h1(evt) {
        heading_markup('=', gettext('Heading H1'));
    }

    function handle_h2(evt) {
        heading_markup('-', gettext('Heading H2'));
    }

    function handle_h3(evt) {
        var sel = selection_handler.get_selection();
        if (!sel) {
            sel = gettext('Heading H3');
        }
        var str = [
            '\n\n### ',
            sel,
            '\n'
        ].join('');
        selection_handler.replace_selection(str);
    }

    function handle_bold(evt) {
        selection_handler.wrap_selection('**', '**');
    }

    function handle_italic(evt) {
        selection_handler.wrap_selection('*', '*');
    }

    function handle_url(evt) {
        //'[', closeWith:']([![Url:!:http://]!] "[![Title]!]")', placeHolder: 'Text odkazu'
        var result = null;
        var replacement = '';
        var text = selection_handler.get_selection();
        if (!text) {
            text = prompt('Text:', '');
            if (text == null) return;
        }
        result = prompt('URL:', 'http://');
        if (result == null) return;
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
        selection_handler.replace_selection(replacement);
    }
    
    function toolbar_buttons() {
        // creates NewmanTextAreaToolbar items.
        me.add_item(gettext('Italic'), 'italic', 'I');
        me.add_item(gettext('Bold'), 'bold', 'B');
        me.add_separator();
        me.add_item(gettext('Link'), 'url', 'L');
        me.add_separator();
        me.add_item(gettext('Head 1'), 'h1', '1');
        me.add_item(gettext('Head 2'), 'h2', '2');
        me.add_item(gettext('Head 3'), 'h3', '3');
        me.add_separator();
        me.add_item(gettext('List unordered'), 'list-bullet');
        me.add_item(gettext('List ordered'), 'list-numeric');
        me.add_separator();
        //me.add_item(gettext('Quote'), 'quote');
        //me.add_separator();
        me.add_item(gettext('Photo'), 'photo');
        me.add_item(gettext('Gallery'), 'gallery');
        me.add_item(gettext('Box'), 'box');
        me.add_separator();
        me.add_item(gettext('Quick preview'), 'preview');
        //me.add_item(gettext('Preview on site'), 'preview_on_site');
    }
    me.toolbar_buttons = toolbar_buttons;

    function item_clicked(evt, button_name) {
        var cback = button_handlers[button_name];
        carp('item_clicked ' + button_name + ', element name:' + me.$text_area.attr('name'));
        if (typeof(cback) == 'undefined') return;
        try {
            selection_handler.init(me.$text_area[0]); // init selection_handler (assigns textarea selection)
            cback(evt);
        } catch (e) {
            carp('item_clicked error: ' + e);
        }
    }
    me.toolbar_item_clicked = item_clicked;

    return me;
};

var NewmanTextArea = function ($text_area, extending_configuration_object) {
    /*
     Params:

     $text_area   text area selected
     */
    var me = new Object();;
    var HTML_CLASS = 'markItUp';
    var CONTAINER_HTML_CLASS = 'markItUpContainer';
    var EDITOR_HTML_CLASS = 'markItUpEditor';
    var config = {
        toolbar: NewmanTextAreaStandardToolbar   // default toolbar generator. Consider assigning 'toolbar' via extending_configuration
                                                 // if toolbar can be generated only once during run-time.
    };
    var toolbar_obj = null;

    function init($text_area, extending_configuration) {
        carp('Initializing NewmanTextArea.' + $text_area);
        $.extend(config, extending_configuration);
        // wrap <textarea> element with several <div> elements
        var div_id = 'id="markItUp' + ($text_area.attr("id").substr(0, 1).toUpperCase()) + ($text_area.attr("id").substr(1)) + '"';
        $text_area.wrap('<div></div>');
        $text_area.wrap('<div ' + div_id + ' class="' + HTML_CLASS + '"></div>');
        $text_area.wrap('<div class="' + CONTAINER_HTML_CLASS + '"></div>');
        $text_area.addClass(EDITOR_HTML_CLASS);
        toolbar_obj = config.toolbar();
        var $toolbar = toolbar_obj.get_toolbar($text_area);
        var $header = $toolbar.insertBefore($text_area);
        //$toolbar.appendTo($header);
        $text_area.data('newman_text_area', $text_area);
        $text_area.data('newman_text_area_toolbar', $toolbar);
        carp('Initialized');
    }

    // initialize NewmanTextArea component.
    init($text_area, extending_configuration_object);

    return me;
};

if ( typeof(jQuery) != 'undefined' ) {
    (function () {
        function newman_textarea(config_object) {
            var $text_area = $(this);
            $text_area.each(
                function() {
                    NewmanTextArea($(this), config_object);
                }
            );
            return $(this);
        }
        
        $.fn.markItUp = newman_textarea;
        $.fn.newmanTextArea = newman_textarea;
    })(jQuery);
}
