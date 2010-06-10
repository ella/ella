/** 
 * Text Area powered by callbacks.
 * requires: jQuery 1.4.2+, 
 *          gettext() function, 
 *          str_concat() function (effective string concatenation),
 *          LoggingLib() object (utils.js).
 *
 * Note: Generate documentation via JSDoc http://jsdoc.sourceforge.net/ .
 */

// NewmanTextArea logging
log_ntarea = new LoggingLib('NTEXTAREA:', false);

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
                log_ntarea.log('WARNING: area == null');
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
			area.value = str_concat(
                area.value.substring(0, selection_start) , text , area.value.substring(area.selectionEnd)
            );
			area.setSelectionRange( 
                selection_start + text.length, selection_start + text.length
            );
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
		str_concat( me.replace_selection((before || '') , txt , (after || '')) );
	}
    me.inject_each_selected_line = check_area(inject_each_selected_line);

	function insert_before_each_selected_line(text, before, after){
		me.inject_each_selected_line(function(lines, line){
			lines.push( str_concat(text , line) );
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
            log_ntarea.log('item_clicked');
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
        toolbar: NewmanTextAreaToolbar           // default toolbar generator. Consider assigning 'toolbar' via extending_configuration
                                                 // if toolbar can be generated only once during run-time.
    };
    var toolbar_obj = null;

    function init($text_area, extending_configuration) {
        log_ntarea.log('Initializing NewmanTextArea.' , $text_area);
        $.extend(config, extending_configuration);
        // wrap <textarea> element with several <div> elements
        var div_id = str_concat('id="markItUp' , ($text_area.attr("id").substr(0, 1).toUpperCase()) , ($text_area.attr("id").substr(1)) , '"');
        $text_area.wrap('<div></div>');
        $text_area.wrap( str_concat('<div ' , div_id , ' class="' , HTML_CLASS , '"></div>') );
        $text_area.wrap( str_concat('<div class="' , CONTAINER_HTML_CLASS , '"></div>') );
        $text_area.addClass(EDITOR_HTML_CLASS);
        toolbar_obj = config.toolbar();
        var $toolbar = toolbar_obj.get_toolbar($text_area);
        var $header = $toolbar.insertBefore($text_area);
        //$toolbar.appendTo($header);
        $text_area.data('newman_text_area', $text_area);
        $text_area.data('newman_text_area_toolbar', $toolbar);
        $text_area.data('newman_text_area_toolbar_object', toolbar_obj);
        log_ntarea.log('Initialized');
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
                    var $area = $(this);
                    // install NewmanTextArea only if it's not already present for given textarea
                    if ( typeof($area.data('newman_text_area')) == 'undefined' ) {
                        NewmanTextArea($area, config_object);
                    }
                }
            );
            return $(this);
        }

        function remove_newman_textarea() {
            var $text_area = $(this);
            $text_area.each(
                function() {
                    var $area = $(this);
                    // install NewmanTextArea only if it's not already present for given textarea
                    if ( typeof($area.data('newman_text_area')) != 'undefined' ) {
                        $area.data('newman_text_area', null);
                        $area.data('newman_text_area_toolbar', null);
                        $area.removeData();
                    }
                }
            );
            return $(this);
        }
        
        $.fn.markItUp = newman_textarea;
        $.fn.newmanTextArea = newman_textarea;
        $.fn.newmanTextAreaRemove = remove_newman_textarea;
    })(jQuery);
}
