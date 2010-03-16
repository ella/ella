/** Text Area with toolbar powered by callbacks
 *
 * Generate documentation via JSDoc http://jsdoc.sourceforge.net/ .
 */

var Debug = new Object();
if (typeof(carp) == 'undefined') {
    function carp() {
        try {
            console.log.apply(null, arguments);
        } catch (e) { }
    }
}

var NewmanTextAreaToolbar = function () {
    var me = new Object();
    var item_counter = 1;
    var $header = $('<div class="markItUpHeader"></div>');
    var $ul = $('<ul></ul>');
    var toolbar_generated = false;

   
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
            '"><a title="',
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
        if (!toolbar_generated) {
            me.$text_area = $text_area;
            me.toolbar_buttons();
            me.register_toolbar_event_handlers();
            $ul.appendTo($header);
            toolbar_generated = true;
        }
        return $header;
    }
    me.get_toolbar = get_toolbar;


    return me;
};

/**
 * Standard toolbar with Bold, Italic, ..., Preview buttons.
 */
var NewmanTextAreaStandardToolbar = function () {
    var me = NewmanTextAreaToolbar();
    var button_handlers = {
        bold: handle_bold
    };

    function handle_bold() {
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
        me.add_item(gettext('Quote'), 'quote');
        me.add_separator();
        me.add_item(gettext('Photo'), 'photo');
        me.add_item(gettext('Gallery'), 'gallery');
        me.add_item(gettext('Box'), 'box');
        me.add_separator();
        me.add_item(gettext('Quick preview'), 'preview');
        me.add_item(gettext('Preview on site'), 'preview_on_site');
    }
    me.toolbar_buttons = toolbar_buttons;

    function item_clicked(evt, button_name) {
        var cback = button_handlers[button_name];
        if (typeof(cback) == 'undefined') return;
        cback(evt);
        //carp('item_clicked ' + button_name + ', element name:' + me.$text_area.attr('name'));
    }
    me.toolbar_item_clicked = item_clicked;

    return me;
};

var TextAreaSelectionHandler = function () {
    // this object is based on code snippets from Maxim Izmaylov's editor.js made for project Zenaadmin.
    var me = new Object();
    var area = null;

	function getSelection(){
		if(!!document.selection){
			return document.selection.createRange().text;
		} else if(!!area.setSelectionRange){
			return area.value.substring(area.selectionStart, area.selectionEnd);
		} else {
			return false;
		}
	}
    me.get_selection = getSelection;

	function replaceSelection(text){
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
		refresh();
		area.focus();
	}

	function wrapSelection(before, after){
		this.replaceSelection(before + this.getSelection() + after);
	}

	function insertBeforeSelection(text){
		this.replaceSelection(text + this.getSelection());
	}

	function insertAfterSelection(text){
		this.replaceSelection(this.getSelection() + text);
	}

	function injectEachSelectedLine(callback, before, after){
		var lines = Array();
		var txt = '';
		$.each(this.getSelection().split("\n"), function(i, line){
			callback(lines, line);
		});
		for(var m = 0; m < lines.length; m++){
			txt += lines[m] + '\n';
		}
		this.replaceSelection((before || '') + txt + (after || ''));
	}

	function insertBeforeEachSelectedLine(text, before, after){
		this.injectEachSelectedLine(function(lines, line){
			lines.push(text + line);
			return lines;
		}, before, after);
	}
};

var NewmanTextArea = function ($text_area) {
    /*
     Params:

     $text_area   text area selected
     */
    var me = new Object();;
    var HTML_CLASS = 'markItUp';
    var CONTAINER_HTML_CLASS = 'markItUpContainer';
    var EDITOR_HTML_CLASS = 'markItUpEditor';
    var config = {
        toolbar: NewmanTextAreaStandardToolbar() // default toolbar generator. Consider assigning 'toolbar' via extending_configuration
                                                 // if toolbar can be generated only once during run-time.
    };

    function init($text_area, extending_configuration) {
        carp('Initializing NewmanTextArea.' + $text_area);
        $.extend(config, extending_configuration);
        // wrap <textarea> element with several <div> elements
        var div_id = 'id="markItUp' + ($text_area.attr("id").substr(0, 1).toUpperCase()) + ($text_area.attr("id").substr(1)) + '"';
        $text_area.wrap('<div></div>');
        $text_area.wrap('<div ' + div_id + ' class="' + HTML_CLASS + '"></div>');
        $text_area.wrap('<div class="' + CONTAINER_HTML_CLASS + '"></div>');
        $text_area.addClass(EDITOR_HTML_CLASS);
        var $toolbar = config.toolbar.get_toolbar($text_area);
        var $header = $toolbar.insertBefore($text_area);
        //$toolbar.appendTo($header);
        carp('Initialized');
    }

    // get the selection TODO rewrite
    function get() {
        textarea.focus();

        scrollPosition = textarea.scrollTop;
        if (document.selection) {
            selection = document.selection.createRange().text;
            if ($.browser.msie) { // ie
                var range = document.selection.createRange(), rangeCopy = range.duplicate();
                rangeCopy.moveToElementText(textarea);
                caretPosition = -1;
                while(rangeCopy.inRange(range)) { // fix most of the ie bugs with linefeeds...
                    rangeCopy.moveStart('character');
                    caretPosition ++;
                }
            } else { // opera
                caretPosition = textarea.selectionStart;
            }
        } else { // gecko
            caretPosition = textarea.selectionStart;
            selection = $$.val().substring(caretPosition, textarea.selectionEnd);
        } 
        return selection;
    }

    // TODO rewrite
    function insert(block) {	
        if (document.selection) {
            var newSelection = document.selection.createRange();
            newSelection.text = block;
        } else {
            //$$.val($$.val().substring(0, caretPosition)	+ block + $$.val().substring(caretPosition + selection.length, $$.val().length));
        }
    }

    // initialize NewmanTextArea component.
    init($text_area);

    return me;
};

if ( typeof(jQuery) != 'undefined' ) {
    (function () {
        carp('fuckitup init 013');

        function newman_textarea(config_object) {
            var $text_area = $(this);
            var newman_text_areas = [];
            $text_area.each(
                function() {
                    newman_text_areas.push( NewmanTextArea($(this), config_object) );
                }
            );
            carp('===\nPika pika chu, pika pikapii.');
            return newman_text_areas;
        }
        
        $.fn.markItUp = newman_textarea;
        $.fn.newmanTextArea = newman_textarea;
    })(jQuery);
}
