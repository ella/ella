(function($) { $( function() {
    ;;; DEBUG = true;
    ;;; DBG = 1;
    var DEL_IMG = '/admin_media/img/admin/icon_deletelink.gif';
    var MIN_LENGTH = 2;
    var SUGGEST_FIELD_SEPARATOR = '|';
    var SUGGEST_RECORD_SEPARATOR = "\n";
    var URL_VAR_SEPARATOR = '&';
    var URL_FIELD_DENOTER = 'f';
    var SUGGEST_SELECTOR = '.GenericSuggestField,.GenericSuggestFieldMultiple';

    var CR = 13;
    var LF = 10;
    var ESC = 27;
    var BACKSPACE = 8;
    var UPARROW = 38;
    var DOWNARROW = 40;

    var MOUSE_ON_BUBBLE = false;

    var $SUGGEST_BUBBLE = $('<ul class="suggest-bubble">');
    $('body').append($SUGGEST_BUBBLE);
    var $ins = $('input[rel]').filter(function(){return $(this).parents('ul:first').attr('class').indexOf('Suggest') >= 0});

    function arr2map(arr) {
        var map = {};
        for (var i = 0; i < arr.length; i++) {
            map[ arr[i] ] = 1;
        }
        return map;
    }

    // Keep track of where the suggest bubble currently belongs
    function set_current_input() {
        var $this = $(this);
        var $input;
        if (this.id.indexOf('_suggest') > 0)
            $input = $this;
        else
            var $ul = $this.filter(SUGGEST_SELECTOR);
            if (!$ul || $ul.length == 0)
                $ul = $this.parents(SUGGEST_SELECTOR);
            $input = $ul.eq(0).find('input').filter(function(){return this.id.indexOf('_suggest') > 0});
        $SUGGEST_BUBBLE.data('cur_input', $input);
    }
    // Export
    window.set_current_input = set_current_input;
    $(SUGGEST_SELECTOR).click( set_current_input ).focus( set_current_input );

    // Various initializations
    $ins.each(function() {
        // Parse the field names (?f=bla&f=ble)
        var rel = $(this).attr('rel');
        rel = rel.substr(rel.indexOf('?') + 1);
        var fields = $.map(rel.split(URL_VAR_SEPARATOR), function(n) {
            if (n.substr(0,2) == URL_FIELD_DENOTER+'=') {
                return n.substr(2);
            }
            else return;
        });

        $(this).data('fields', fields).attr('autocomplete', 'off');

        // Shave off the string representations from the hidden inputs upon form submit
        $(this).parents('form:first').submit(function(){
            $(this).find('input:hidden').each(function(){
                $(this).val( $(this).val().replace(/#.*/, '') );
            });
            return true;
        });

        // Make the popup-throwing magnifying glass not raise the default dnajgo event but rather ours which cooperates with the <ul> inputs
        var $lens = $('#lookup_'+this.id.replace('_suggest', ''));
        $lens.removeAttr('onclick').click(show_lookup_popup);
    });

    // Make the <ul>s behave like text input fields
    $(SUGGEST_SELECTOR).find('input:text').focus(function() {
        $(this).parents('ul:first').css('backgroundColor', '#F4F7FB');
    }).blur(function() {
        var $ul = $(this).parents('ul:first');
        $ul.css('backgroundColor', $ul.data('bgcolor'));
    }).each(function() {
        var $ul = $(this).parents('ul:first');
        $ul.data('bgcolor', $ul.css('backgroundColor'));
    });
    $('ul').filter(SUGGEST_SELECTOR).click(function() {
        $(this).find('input:text:visible:first').focus();
    });
    $('li.suggest-selected-item > a').click(set_current_input).click(delete_item);

    // Manipulation with the inputs
    function get_hidden($text) {
        return $('#'+$text.attr('id').replace('_suggest', ''));
    }
    function get_current_inputs(el) {
        var $text;
        if (el) {
            $text = $(el).parents(SUGGEST_SELECTOR).find('input').filter(function(){return this.id.indexOf('_suggest')>0});
        }
        else {
            $text = $SUGGEST_BUBBLE.data('cur_input');
        }
        var $hidden = get_hidden($text);
        var $ul = $text.parents('ul:first');
        return {text: $text, hidden: $hidden, ul: $ul};
    }
    // Updates values of the hidden input based on the <li>s present
    function update_values(el) {
        var $inputs = get_current_inputs(el);
        var ids = [];
        var repres = [];
        $inputs.ul.find('li').not(':last').each(function() {
            ids.push( $(this).data('item_id') );
            repres.push( $.trim(this.firstChild.data) );
        });
        if (!is_multiple($inputs.ul) && ids.length > 1) {
            //TODO: warning
        }
        $inputs.hidden.val(ids.join(',') + '#' + repres.join(','));
        $inputs.text.data('values', arr2map(ids));
    }
    function parse_suggest_result(result, fields) {
        if (result == null || result.length == 0) return [];
        var results = result.split(SUGGEST_RECORD_SEPARATOR);
        var parsed_results = $.map(results, function(n) {
            var values = n.split(SUGGEST_FIELD_SEPARATOR);
            var parsed_result = { id: values.shift() };

            //TODO: warning if (fields.length != values.length);

            var repre = '';
            for (var i = 0; i < values.length; i++) {
                parsed_result[ fields[i] ] = values[i];
                if (repre.length == 0) repre = values[i];
            }
            parsed_result.REPRE = repre || parsed_result.id;
            return parsed_result;
        });
        return parsed_results;
    }
    function new_item(item_id, item_str) {
        var $newli = $('<li class="suggest-selected-item">');
        $newli.click(set_current_input);
        var $newdel = $('<a><img src="'+DEL_IMG+'" alt="x" /></a>');
        $newdel.click(set_current_input).click(delete_item);
        $newli.html( item_str ).append( $newdel ).data( 'item_id', item_id );
        return $newli;
    }
    // Adds a value (in case of multiples) or sets the value (in case of singles)
    function insert_value (id, repre, el) {
        var $inputs = get_current_inputs(el);
        var multiple = is_multiple($inputs.ul);
        var $newli = new_item(id, repre);
        $inputs.text.val('');
        var $prev = $inputs.text.parent().prev('li');
        $inputs.text.parent().before($newli);
        if (!multiple && $prev && $prev.length > 0) {
            $prev.remove();
        }
        update_values(el);
        $inputs.text.focus();
        $SUGGEST_BUBBLE.empty().hide();
        MOUSE_ON_BUBBLE = false;
    }
    // export this function
    window.insert_value = insert_value;

    // Enhance textual X's of delete links with graphical crosses used at the "delete this item from database" link
    $('li.suggest-selected-item a').html('<img src="'+DEL_IMG+'" alt="x" />')

    // Ensure that the initial values fit
    $ins.each(function() {
        var $inputs = get_current_inputs( this );
        if ( /^(.+)#(.+)$/.test($inputs.hidden.val()) ) {
            var ids    = RegExp.$1;
            var repres = RegExp.$2;
            ids    = ids.match(/\d+/g);
            repres = repres.match(/[^,]+/g);
            if (!ids || !repres || ids.length != repres.length) ids = repres = [];
            $inputs.ul.find('li').not(':last').remove();
            while (ids.length > 0) {
                var id    = ids.pop();
                var repre = repres.pop();
                item = new_item(id, repre);
                $inputs.ul.prepend(item);
            }
        }
        else if ( /^([\d,]+)$/.test($inputs.hidden.val()) ) {
            var raw_ids = RegExp.$1;
            var ids = raw_ids.match(/\d+/g);
            var $lis = $inputs.ul.find('li').not(':last');
            var repres = $.map( $.makeArray($lis), function(n) {
                return $.trim( n.firstChild.data );
            });
            if (repres && ids && repres.length == ids.length) {
                $lis.each(function(i) {
                    $(this).data('item_id', ids[i]);
                });
            }
        }
    });/* */
    /* Version, where titles were AJAX'ed from id's in the hidden's.* /
    // TODO: View na get_item_by_id
    $ins.each(function() {
        var $inputs = get_current_inputs( this );
        var ids = /^\d+(?:,\d+)*$/.test($inputs.hidden.val()) ? $inputs.hidden.val().match(/\d+/g) : [];
        ;;; ids = [];   // FIXME: treba view na items podle IDcek -- ted nefungujou 1ciferna
        var get_item_url = $inputs.text.attr('rel');
        if (!get_item_url.match(/[?&]f=id\b/)) {
            get_item_url = get_item_url.replace('&q=', '&f=id&q=');
        }
        var items = [];
        for (var i = 0; i < ids.length; i++) {
            var id = ids[i];
            $.ajax({
                type: 'GET',
                url: get_item_url+id,
                async: false,   // Need to have the values ready before continuing
                success: function(result) {
                    var parsed_results = parse_suggest_result(result, $inputs.text.data('fields'));
                    var item_of_id = $.grep(parsed_results, function(parsed_result) {
                        if (parsed_result.id == ids[i]) return true;
                        else return false;
                    })[0];
                    items.push(item_of_id);
                }
            });
        }
        $inputs.ul.find('li').not(':last').remove();
        while (items.length > 0) {
            var item = items.pop();
            item = new_item(item.id, item.REPRE);
            $inputs.ul.prepend(item);
        }
    }); /* */
    $ins.each(function() {
        update_values($(this));
    });

    function is_multiple( $el ) {
        if ($el.hasClass('GenericSuggestFieldMultiple')) return true;
        if ($el.parents('.GenericSuggestFieldMultiple').length > 0) return true;
        return false;
    }
    function delete_item() {
        var $li = $(this).parent();
        $li.remove();
        update_values();
        get_current_inputs().text.focus();
    }
    function suggest_select($sug_item) {
        var item_id = $sug_item.data('sug_result').id;
        var item_str = $sug_item.data('sug_result').REPRE;
        insert_value(item_id, item_str);
    }
    function suggest_update($input) {
        var $val = $input.val();
        if ($val.length < MIN_LENGTH) {
            $SUGGEST_BUBBLE.hide();
            return;
        }
        var sug_url = $input.attr('rel');
        $.get(sug_url+$val, {}, function(sug_result) {
            $SUGGEST_BUBBLE.empty();
            $input.each(set_current_input); // sets $input as the current input
            var fields = $input.data('fields');
            var parsed_results = parse_suggest_result(sug_result, fields)
            parsed_results = $.grep(parsed_results, function(parsed_result) {
                if ($input.data('values')[ parsed_result.id ])
                    return false;
                else
                    return true;
            });
            if (parsed_results.length == 0) {
                $SUGGEST_BUBBLE.hide();
            }
            else {
                $.map(parsed_results, function(parsed_result) {
                    var $elem = $('<li>');
                    $elem.data('sug_result', parsed_result);
                    $elem.text(parsed_result.REPRE);
                    $SUGGEST_BUBBLE.append($elem);
                    $elem.click(function(){suggest_select($elem);});
                });
                var pos = $input.offset();
                pos.top += $input.outerHeight();
                $SUGGEST_BUBBLE.css({
                    left: pos.left,
                    top:  pos.top,
                }).show();
            }
        });
    }
    function suggest_scroll($input, key) {
        var $lis = $SUGGEST_BUBBLE.find('li');
        var $active_elem = $lis.filter('.A:first');
        $lis.removeClass('A');
        if (key == DOWNARROW) {
            if ($active_elem.length == 0)
                $active_elem = $lis.eq(0);
            else {
                $active_elem = $active_elem.next();
                if ($active_elem.length == 0)
                    $active_elem = $lis.eq(0);
            }
        }
        if (key == UPARROW) {
            if ($active_elem.length == 0)
                $active_elem = $lis.filter(':last');
            else {
                $active_elem = $active_elem.prev();
                if ($active_elem.length == 0)
                    $active_elem = $lis.filter(':last');
            }
        }
        $active_elem.addClass('A');
        return;
    }
    $ins.keyup( function($event) {
        var $this = $(this);
        var key = $event.keyCode;
        if (key == ESC) {
            $SUGGEST_BUBBLE.hide();
            $this.val('');
            return;
        }
        else if (key == UPARROW || key == DOWNARROW) {
            return;
        }
        else if (key == CR || key == LF) {
            return;
        }
        else {
            suggest_update($this);
            return;
        }
    });
    $ins.keypress( function($event) {
        var key = $event.keyCode;
        var $this = $(this);
        if (key == CR || key == LF) {
            if ($SUGGEST_BUBBLE.filter(':visible').length == 1) {
                var $active_li = $SUGGEST_BUBBLE.find('li.A:first');
                if ($active_li.length == 0)
                    $active_li = $SUGGEST_BUBBLE.find('li:first');
                suggest_select($active_li);
                return false;
            }
        }
        else if (key == BACKSPACE && $this.val().length == 0) {
            var $prev = $this.parent().prev();
            if ($prev.length == 0) return;
            $this.val('');
            $prev.remove();
            update_values();
        }
        else if (key == UPARROW || key == DOWNARROW) {
            suggest_scroll($this, key);
            return;// false;
        }
        return true;
    });
    $ins.blur( function() {
        if (!MOUSE_ON_BUBBLE)
            $SUGGEST_BUBBLE.hide();
    });
    $ins.focus( function() {
        suggest_update( $(this) );
    });
    $SUGGEST_BUBBLE.bind('mouseenter', function(){ MOUSE_ON_BUBBLE = true;  });
    $SUGGEST_BUBBLE.bind('mouseleave', function(){ MOUSE_ON_BUBBLE = false; });
}); })(jQuery);

// Functions for handling popups (lupička) taken from django admin
function show_lookup_popup() {
    var name = this.id.replace(/^lookup_/, '');
    // IE doesn't like periods in the window name, so convert temporarily.
    name = name.replace(/\./g, '___');
    var href;
    if (this.href.search(/\?/) >= 0) {
        href = this.href + '&pop=1';
    } else {
        href = this.href + '?pop=1';
    }
    var win = window.open(href, name, 'height=1,width=800,resizable=yes,scrollbars=yes');
    $(win).load(function() {
        var $linx = win.jQuery('a[onclick]');
        $linx.removeAttr('onclick').unbind('click').click(function() {
            this.href.match(/(\d+)\/?$/);
            dismiss_lookup_popup(win, RegExp.$1);
            return false;
        });
        win.resizeTo(500,800);
    })
    win.focus();
    return false;
}
function dismiss_lookup_popup(win, chosenId) {
    var name = win.name.replace(/___/g, '.');
    var elem = document.getElementById(name+'_suggest');
    // This cute expression takes the first non-blank field of the item whose ID we got
    var item_str = $.grep($.map($.makeArray($('a[href='+chosenId+'/]',win.document.body).parents('tr').children()),function(n){return $(n).text()}),function(n){return/\S/.test(n)})[0]||chosenId;
    insert_value(chosenId, item_str, elem);
    win.close();
    $(elem).each(set_current_input);
}
