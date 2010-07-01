/** 
 * Generic Suggester library.
 * requires: jQuery 1.4.2+, 
 *          str_concat() function (effective string concatenation).
 *
 * provides:
 *          GenericSuggestLib object.
 *
 */
/* TODO:
 * neukazovat vybrané hodnoty v lupičce,
 */
GenericSuggestLib = {};
(function($) { $( function() {
    GenericSuggestLib.VERSION = '2010.04.13-newman';
    var DEL_IMG = str_concat(MEDIA_URL , 'ico/10/icon_deletelink.gif');
    var MIN_LENGTH = 2;
    var SUGGEST_FIELD_SEPARATOR = '|';
    var SUGGEST_RECORD_SEPARATOR = "\n";
    var URL_VAR_SEPARATOR = '&';
    var URL_FIELD_DENOTER = 'f';
    var SUGGEST_SELECTOR = '.GenericSuggestField,.GenericSuggestFieldMultiple';
    var SUGGEST_DELAY = 300;    // ideally, just a touch more than the delay between keypresses

    var CR = 13;
    var LF = 10;
    var ESC = 27;
    var BACKSPACE = 8;
    var LEFTARROW = 37;
    var UPARROW = 38;
    var RIGHTARROW = 39
    var DOWNARROW = 40;
    var PAGEUP = 33;
    var PAGEDOWN = 34;

    var MOUSE_ON_BUBBLE = false;

    // HTML snippets
    var $SUGGEST_BUBBLE = $('<div class="suggest-bubble"></div>');
    var $SUGGEST_LIST = $('<ul class="suggest-list"></ul>');
    $SUGGEST_BUBBLE.append($SUGGEST_LIST).append('<div class="suggest-next-page"><a href="#">&nabla; další strana &nabla;</a></div>');
    var $SUGGEST_FIELDS_BUBBLE = $( str_concat(
        '<div class="suggest-fields-bubble">'           ,"\n",
        '    <div class="suggest-fields-list">'         ,"\n",
        '        <table></table>'                       ,"\n",
        '    </div>'                                    ,"\n",
        '</div>'                                        ,"\n"
    ) );
    $('body').append($SUGGEST_BUBBLE).append($SUGGEST_FIELDS_BUBBLE);

    // ['foo', 'bar'] => { foo: 1, bar: 1 }
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

    var $ins;
    function initialize() {
        
        GenericSuggestLib.NO_TRIGGER_CHANGE = true;
        
        if ( $(SUGGEST_SELECTOR).length == 0 ) return;
        $(SUGGEST_SELECTOR)
            .unbind('click', set_current_input).bind('click', set_current_input)
            .unbind('focus', set_current_input).bind('focus', set_current_input);
        $('.hidden').hide();
        $ins = $('input[rel]').filter(function(){return this.id.substr(this.id.length - '_suggest'.length) == '_suggest'});
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
            $(this).closest('form').submit(function() {
                $(this).find('input:hidden').each(function() {
                    $(this).val( $(this).val().replace(/#.*/, '') );
                });
                return true;
            });

            // Make the popup-throwing magnifying glass not raise the default django event but rather ours which cooperates with the <ul> inputs
            var $lens = $('#lookup_'+this.id.replace('_suggest', ''));
            $lens.removeAttr('onclick');//.click(show_lookup_popup);
        });

        // Make the <ul>s behave like text input fields
        $(SUGGEST_SELECTOR).find('input:text')
        .unbind('focus.ulbgcol').bind('focus.ulbgcol', function() {
            $(this).closest('ul').css('backgroundColor', '#F4F7FB');
        }).unbind('blur.ulbgcol').bind('blur.ulbgcol', function() {
            var $ul = $(this).closest('ul');
            $ul.css('backgroundColor', $ul.data('bgcolor'));
        }).each(function() {
            var $ul = $(this).closest('ul');
            $ul.data('bgcolor', $ul.css('backgroundColor'));
        });
        $('ul').filter(SUGGEST_SELECTOR)
        .unbind('click.ulpassfocus').bind('click.ulpassfocus', function() {
            $(this).find('input:text:visible:first').focus();
        });
        $('li.suggest-selected-item > a.suggest-delete-link')
        .unbind('click.delsetinput')
        .bind(  'click.delsetinput', set_current_input)
        .bind(  'click.delsetinput', delete_item);

        // Enhance textual X's of delete links with graphical crosses used at the "delete this item from database" link
        $('li.suggest-selected-item a').html( str_concat('<img src="',DEL_IMG,'" alt="x" />') )

        // Ensure that the initial values fit
        function restore_suggest_widget_from_value(el) {
            var $inputs = get_current_inputs(el);
            if ( /^(.*)#(.*)$/.test($inputs.hidden.val()) ) {
                var ids    = RegExp.$1;
                var repres = RegExp.$2;
                ids    = ids.match(/\d+/g);
                repres = repres.match(/[^,]+/g);
                if (!ids || !repres || ids.length != repres.length) ids = repres = [];
                $inputs.ul.find('li.suggest-selected-item').remove();
                while (ids.length > 0) {
                    var id    = ids.pop();
                    var repre = repres.pop();
                    var item = new_item(id, repre);
                    $inputs.ul.prepend(item);
                }
                return true;
            }
            return false;
        }
        window.restore_suggest_widget_from_value = restore_suggest_widget_from_value;
        $ins.each(function() {
            var $inputs = get_current_inputs( this );
            if ( restore_suggest_widget_from_value(this) ) { }
            else if ( /^([\d,]+)$/.test($inputs.hidden.val()) ) {
                var raw_ids = RegExp.$1;
                var ids = raw_ids.match(/\d+/g);
                var $lis = $inputs.ul.find('li.suggest-selected-item');
                var repres = $.map( $.makeArray($lis), function(n) {
                    return $.trim( n.firstChild.data ).replace(/,/g, '&#44;');
                });
                if (repres && ids && repres.length == ids.length) {
                    $lis.each(function(i) {
                        $(this).data('item_id', ids[i]);
                    });
                }
            }
        });
        $ins.each(function() {
            update_values($(this));
        });
        $ins.unbind('keyup').bind('keyup', function($event) {
            var $this = $(this);
            var key = $event.keyCode;
            if (  key == CR || key == LF ) return;
            else if (key == ESC || key ==    UPARROW || key == PAGEUP
                                || key ==  DOWNARROW || key == PAGEDOWN
                                || key ==  LEFTARROW
                                || key == RIGHTARROW
            ) {
                bubble_keyevent(key, $this);
                return;
            }
            else {
                schedule_suggest_update($this);
                return;
            }
        })
        .unbind('keypress').bind('keypress', function($event) {
            var key = $event.keyCode;
            var $this = $(this);
            if (  key == CR || key == LF ) {
                bubble_keyevent(key, $this);
                return false;
            }
            return true;
        })
        .unbind('keydown').bind('keydown', function($event) {
            var key = $event.keyCode;
            var $this = $(this);
            if (key == BACKSPACE && $this.val().length == 0) {
                var $prev = $this.parent().prev();
                if ($prev.length == 0) return;
                $this.val('');
                $prev.remove();
                update_values();
            }
        })
        .unbind('blur.hidebub').bind('blur.hidebub', function() {
            if (!MOUSE_ON_BUBBLE)
                hide_bubbles();
        })
        .unbind('focus.reshowbub').bind('focus.reshowbub', function() {
            if ($(this).data('internal_focus')) {
                $(this).removeData('internal_focus');
            }
            else {
                suggest_update( $(this) );
            }
        });
        
        delete GenericSuggestLib.NO_TRIGGER_CHANGE;
    }
    initialize();
    $(document).bind('content_added', initialize);

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
        var $ul = $text.closest('ul');
        return {text: $text, hidden: $hidden, ul: $ul};
    }
    // Updates values of the hidden input based on the <li>s present
    function update_values(el) {
        var $inputs = get_current_inputs(el);
        var ids = [];
        var repres = [];
        $inputs.ul.find('li.suggest-selected-item').each(function() {
            ids.push( $(this).data('item_id') );
            repres.push( $.trim(this.firstChild.data).replace(/,/g, '&#44;') );
        });
        if (!is_multiple($inputs.ul) && ids.length > 1) {
            //TODO: warning
        }
        $inputs.hidden.val( str_concat(ids.join(',') , '#' , repres.join(',')) );
        $inputs.text.data('values', arr2map(ids));
        if ( ! GenericSuggestLib.NO_TRIGGER_CHANGE ) $inputs.hidden.trigger('change');
    }
    function parse_suggest_result(result, fields) {
        if (result == null || result.length == 0) return [];
        var results = result.split(SUGGEST_RECORD_SEPARATOR);
        var meta_str = results.shift();
        var meta;
        eval('meta = '+meta_str);
        if (results.length == 0) return [];
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
        parsed_results.meta = meta;
        return parsed_results;
    }
    function new_item(item_id, item_str) {
        var $newli = $('<li class="suggest-selected-item">');
        $newli.click(set_current_input);
        var $newdel = $( str_concat('<a class="suggest-delete-link"><img src="',DEL_IMG,'" alt="x" /></a>') );
        $newdel.click(set_current_input).click(delete_item);
        $newli.html( item_str ).append( $newdel ).data( 'item_id', item_id );
        return $newli;
    }
    // Adds a value (in case of multiples) or sets the value (in case of singles)
    function insert_value(id, repre, el) {
        var $inputs = get_current_inputs(el);
        var multiple = is_multiple($inputs.ul);
        $inputs.ul.removeData('offset');
        var $newli = new_item(id, repre);
        $inputs.text.val('');
        var $prev = $inputs.text.parent().prev('li');
        $inputs.text.parent().before($newli);
        if (!multiple && $prev && $prev.length > 0) {
            $prev.remove();
        }
        update_values(el);
        $inputs.text.focus();
        $SUGGEST_LIST.empty();
        hide_bubbles();
        MOUSE_ON_BUBBLE = false;
    }
    GenericSuggestLib.insert_value = insert_value;

    function hide_bubbles() {
        $SUGGEST_BUBBLE.hide();
        $SUGGEST_FIELDS_BUBBLE.hide();
    }
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

    // This element will be cloned to generate the items in the suggest bubble
    var $suggest_item_template = $('<li>')
    .click( function() {
        suggest_select($(this));
    }).hover( function() {
        set_field_bubble($(this));
    }, function() {
        $SUGGEST_FIELDS_BUBBLE.hide();
    });

    var suggest_update_timer;
    function schedule_suggest_update($input) {
        clearTimeout(suggest_update_timer);
        suggest_update_timer = setTimeout(function() {
            suggest_update($input);
        }, SUGGEST_DELAY);
    }
    function suggest_update($input, offset) {
        var val = $input.val();
        if (val.length < MIN_LENGTH) {
            hide_bubbles();
            return;
        }
        $SUGGEST_FIELDS_BUBBLE.hide();
        // create a regexp that will match every occurrence of the text input value
        var val_re = new RegExp( '(' + val.replace(/([^\w\s])/g, '\\$1') + ')', 'ig' ); // the replace does /\Q$val/
        var sug_url = $input.attr('rel');
        // The rel attribute is a relative address.
        // If we're using the content-by-hash library, we want it to be relative to what's in the hash.
        if (window.adr && $.isFunction(adr)) sug_url = adr(sug_url, { just_get: 'address' });

        if (offset == null || offset < 0)
            offset = 0;
        if (offset > 0) {
            sug_url = sug_url.replace('&q', str_concat('&o=',offset,'&q') );
        }
        $input.data('offset', offset);

        $.get(sug_url+val, {}, function(sug_result) {
            if (sug_result == 'SPECIAL: OFFSET OUT OF RANGE') {
                if (offset > 0) suggest_update($input, 0);
                else hide_bubbles();
                return;
            }
            $SUGGEST_LIST.empty();
            $input.each(set_current_input); // sets $input as the current input
            var fields = $input.data('fields');
            var parsed_results = parse_suggest_result(sug_result, fields)
            var meta = parsed_results.meta;

            // don't suggest what's already selected
            parsed_results = $.grep(parsed_results, function(parsed_result) {
                if ($input.data('values')[ parsed_result.id ])
                    return false;
                else
                    return true;
            });

            if (parsed_results.length == 0) {
                hide_bubbles();
            }
            else {
                var no_items = parsed_results.length;
                if (offset + no_items >= meta.cnt) {
                    $SUGGEST_BUBBLE.find('.suggest-next-page').hide();
                }
                else {
                    $SUGGEST_BUBBLE.find('.suggest-next-page').show();
                }
                $.map(parsed_results, function(parsed_result) {
                    $suggest_item_template.clone(!!'CLONE HANDLERS')
                    .data('sug_result', parsed_result)
                    .html(parsed_result.REPRE.replace(val_re, '<span class="hilite">$1</span>'))
                    .appendTo($SUGGEST_LIST);
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
        $SUGGEST_FIELDS_BUBBLE.hide();
        var $lis = $SUGGEST_LIST.find('li');
        var $active_elem = $lis.filter('.A:first');
        $lis.removeClass('A');
        if (key == DOWNARROW) {
            if ($active_elem.length == 0)
                $active_elem = $lis.eq(0);
            else {
                $active_elem = $active_elem.next();
                if ($active_elem.length == 0) { // request next page
                    suggest_scroll_page(1, $input);
                    return;
                }
            }
        }
        if (key == UPARROW) {
            if ($active_elem.length == 0)
                $active_elem = $lis.filter(':last');
            else {
                $active_elem = $active_elem.prev();
                if ($active_elem.length == 0) { // request previous page
                    suggest_scroll_page(-1, $input);
                    return;
                }
            }
        }
        $active_elem.addClass('A');
        set_field_bubble( $active_elem );
        return;
    }
    function suggest_scroll_page(delta, $input) {
        if ($input == null) $input = get_current_inputs().text;
        var offset = $input.data('offset') + delta * $SUGGEST_LIST.find('li').length;
        suggest_update($input, offset);
    }
    function set_field_bubble($item) {
        var sug_result = $item.data('sug_result');
        var list = [];
        var i = 0;
        for (var k in sug_result) {
            if (i++ == 1) { first = false; continue; }
            if (k == 'REPRE') continue;
            list.push( str_concat('<tr><th>' , k , '</th><td>' , sug_result[ k ] , '</td></tr>') );
        }
        if (list.length == 0) {
            $SUGGEST_FIELDS_BUBBLE.hide();
            return;
        }
        var pos = $item.offset();
        $SUGGEST_FIELDS_BUBBLE.find('table').empty().append(
            list.join("\n")
        ).end().css({
            top:  pos.top + $item.height()/2 - $SUGGEST_FIELDS_BUBBLE.height()/2,
            left: pos.left + $item.outerWidth()
        }).show();
    }
    function bubble_keyevent(key, $input) {
        if ($input == null) input = get_current_inputs().text;
        switch (key) {
        case ESC:
            hide_bubbles();
            $input.val('');
            break;
        case UPARROW:
        case DOWNARROW:
            suggest_scroll($input, key);
            break;
        case CR:
        case LF:
            if ($SUGGEST_BUBBLE.is(':visible')) {
                var $active_li = $SUGGEST_LIST.find('li.A:first');
                if ($active_li.length == 0)
                    $active_li = $SUGGEST_LIST.find('li:first');
                suggest_select($active_li);
            }
            break;
        case PAGEUP:
        case PAGEDOWN:
            var delta = (key == PAGEUP) ? -1 : 1;
            suggest_scroll_page(delta, $input);
            break;
        }
    }

    // Setup the behavior of the next-page widget
    $('div.suggest-next-page a').click(function() {
        suggest_scroll_page(1);
        return false;
    }).focus(function() {
        var $input = get_current_inputs().text;
        $input.data('internal_focus', 1);
        $input.focus();
    });

    $SUGGEST_BUBBLE.bind('mouseenter', function(){ MOUSE_ON_BUBBLE = true;  return true; });
    $SUGGEST_BUBBLE.bind('mouseleave', function(){ MOUSE_ON_BUBBLE = false; return true; });


    // Functions for handling popups (lupička) taken from django admin
    function parse_lupicka_data(data) {
        data = data.substring( data.indexOf('<table'), data.indexOf('</table>')+8 );
        var $data = $('<div>').html(data);
        var col_names = $.map( $.makeArray($data.find('thead th')), function(n){return $.trim($(n).text())} );
        var $trs = $data.find('tbody tr');
        var rv = [col_names];
        $trs.each(function() {
            var rec = $.map( $.makeArray( $(this).find('th,td') ), function(n) { return $.trim( $(n).text() ); } );
            $(this).find('th a').attr('href').match(/(\d+)\/$/);
            var id = RegExp.$1;
            rec.push( id );
            rv.push(rec);
        });
        return rv;
    }
    function get_popup_content( href, $popup ) {
        $.ajax({
            url: href,
            success: function(data) {
                var rows = parse_lupicka_data(data);
                var col_names = rows.shift();
                var $table = $("<table></table>\n");
                var $header = $("<tr></tr>\n");
                for (var i = 0; i < col_names.length; i++) {
                    $header.append( str_concat('<th>' , col_names[i] , '</th>') );
                }
                $table.append($header);
                for (var i = 0; i < rows.length; i++) {
                    var row = rows[i];
                    var id = row.pop();
                    $( str_concat(
                        '<tr><td>',
                        rows[i].join('</td><td>')
                        ,"</td></tr>\n"
                    ) )
                    .data('id',id)
                    .appendTo($table);
                }
                $table.find('tr:gt(0)').click( function() {
                    var chosenId = $(this).data('id');
                    var item_str = $.trim( $(this).find('td,th').eq(0).text() );
                    var elem = document.getElementById( $('div.lupicka-popup').data('input_id') );
                    insert_value(chosenId, item_str, elem);
                    dismiss_lookup_popup();
                });
                var $pagin_cont = $('<div class="fakewin-paginator"></div>');
                $pagin_cont.append('<ul></ul>');
                $popup.empty().append($('<div class="table"></div>').append($table)).append($pagin_cont);
            }
        });
    }
    function show_lookup_popup() {
        var name = this.id.replace(/^lookup_/, '');
        var href;
        if (this.href.search(/\?/) >= 0) {
            href = this.href + '&pop=1';
        } else {
            href = this.href + '?pop=1';
        }

        var $related_item = $( str_concat('#',name,'_suggest') ).parents('.GenericSuggestField,.GenericSuggestFieldMultiple').eq(0);

        // Create the fake popup window
        dismiss_lookup_popup();
        var $popup_w = $( str_concat(                                    "\n",
            '<div class="lupicka-popup fakewin">'                       ,"\n",
            '    <div class="fakewin-title">'                           ,"\n",
            '        <div class="fakewin-titletext"></div>'             ,"\n",
            '        <div class="fakewin-closebutton">&times;</div>'    ,"\n",
            '        <div class="clearfix"></div>'                      ,"\n",
            '    </div>'                                                ,"\n",
            '    <div class="fakewin-content">'                         ,"\n",
            '    </div>'                                                ,"\n",
            '</div>'                                                    ,"\n"
        ) );
        $popup_w.data('input', $related_item);
        $related_item.addClass('pod-lupickou');
        $popup_w.draggable().draggable('disable').resizable().data('input_id', name+'_suggest')
        .find('.fakewin-title').bind('mouseenter', function() {
            $popup_w.draggable('enable');
        }).bind('mouseleave', function() {
            $popup_w.draggable('disable');
        }).find('.fakewin-titletext').html('&nbsp;')
        .end().find('.fakewin-closebutton').click(dismiss_lookup_popup);
        var $popup = $popup_w.find('div.fakewin-content');
        $popup.text('Loading...');
        $('body').append( $popup_w );
        get_popup_content(href, $popup);
        return false;
    }
    function dismiss_lookup_popup() {
        var $w = $('div.lupicka-popup:first');
        if ($w.length == 0) return;
        $w.data('input').removeClass('pod-lupickou');
        $w.remove();
    }
    
    GenericSuggestLib.copy = function(from, to) {
        var $from = get_current_inputs(from);
        var $to   = get_current_inputs(to);
        $to.hidden.val(
            $from.hidden.val()
        );
        restore_suggest_widget_from_value(to);
    };
    
    GenericSuggestLib.get_value = function(el) {
        var $inputs = get_current_inputs(el);
        var val = $inputs.hidden.val().replace(/#.*/, '');
        if ($inputs.ul.is('.GenericSuggestField')) return val;
        else return val.split(/,/);
    };
    
    function equidistant_array_coverage(count, characters) {
        if (characters == null)
            characters = 'abcčdefghijklmnoprřsštuvzž'.split('');
        if (count >= characters.length) return characters;
        if (count == 0) return [];
        var len = characters.length;
        var ofs = len / (2*count);
        var rv = new Array(count);
        for (var i = 0; i < count; i++) {
            rv[i] = characters[ Math.round( ofs + (i * len) / count ) ];
        }
        return rv;
    }
}); })(jQuery);

/*

To display the documentation, enter the command:

perldoc generic.suggest.js

To export it to various formats, see the pod2* family of commands.

=encoding utf8

=head1 NAME

Generic Suggest -- autocomplete tool for ellaadmin

This document describes generic.suggest.js version 2009.01.13

=head1 SYNOPSIS

 <html><head>

 <script type="text/javascript" src="jquery.js"></script>
 <!-- minimal jquery version tested: 1.2.6 -->

 <script type="text/javascript" src="jquery-ui.js"></script>
 <!-- jQuery UI draggable and resizable are needed for the popup fake windows to run -->

 <script type="text/javascript" src="generic.suggest.js"></script>

 </head><body>

 <!-- An autocomplete-enabled input for a single value (despite of the <ul><li> construct) -->
 <input class="vForeignKeyRawIdAdminField hidden" type="text" name="source" id="id_source" />
 <!-- This is the apparently hidden input that carries the values to be sent upon submit. The first class is filled by the server part. -->
 <ul class="GenericSuggestField">
 <!-- The GenericSuggestField class indicates a single-value pseudo-input. -->
     <li>
         <input type="text" id="id_source_suggest" rel="../../../core/source/suggest/?f=name&amp;f=url&amp;q=" />
         <!-- This is the actual text input where the autocompleting takes place.
              The rel attribute holds the URL to which the typed-in text is concatenated and from which the results are drawn via AJAX.
              The 'f' args denote the DB columns that are returned. ID is implicitly present and the first after it is used as the text representation.
              It is necessary for the id to be that of the related hidden input with '_suggest' appended. -->
     </li>
 </ul>
 <a href="../../../core/source/" class="suggest-related-lookup" id="lookup_id_source" onclick="return showRelatedObjectLookupPopup(this);">
 <!-- The popup (lupička) icon. Without generic.suggest.js, it opens a new window but doesn't operate with the <ul> pseudo-inputs.
      The onclick attribute is overriden by generic.suggest.js.
      It is necessary for the id to be that of the related hidden input with 'lookup_' prepended. -->
     <img src="/admin_media/img/admin/selector-search.gif" width="16" height="16" alt="Lookup" />
 </a>

 <!-- A similar input but for multiple values. -->
 <input class="vManyToManyRawIdAdminField hidden" type="text" name="authors" value="205,1425" id="id_authors" />
 <!-- The value attribute holds the initial values in a comma-separated list of id's. -->
 <ul class="GenericSuggestFieldMultiple">
 <!-- The GenericSuggestFieldMultiple class indicates a multi-value input -->
     <!-- initial values: text representations -->
     <li class="suggest-selected-item">
         redakce <a class="suggest-delete-link">x</a>
     </li>
     <li>
         opička <a class="suggest-delete-link">x</a>
     </li>
     <!-- end of initial values -->
     <li>
         <input type="text" id="id_authors_suggest" rel="../../../core/author/suggest/?f=name&amp;f=slug&amp;q=" />
     </li>
 </ul>
 <a href="../../../core/author/" class="suggest-related-lookup" id="lookup_id_authors" onclick="return showRelatedObjectLookupPopup(this);">
     <img src="/admin_media/img/admin/selector-search.gif" width="16" height="16" alt="Lookup" />
 </a>

=head1 DESCRIPTION

This script alters the behavior and appearance of pseudo-inputs (i.e. HTML
elements that simulate the functionality of an enhanced input) who bear the
C<GenericSuggestField> or C<GenericSuggestFieldMultiple> class.

=head2 Links of the Chain

For the suggester to work on an input, there must be some conditions satisfied:

=over 4

=item HTML Structure

1) A text / hidden input must be present that will hold the id's of the items
sent to the server when the form is submitted. It must have an id.

2) An <ul> element with class either C<GenericSuggestField> or
C<GenericSuggestFieldMultiple>

3) A text input field with the same id as the one in (1) but with C<_suggest>
appended. It must be inside a <li> tag inside the <ul> mentioned in (2). It must
have a C<rel> attribute whose value be the URL from where the suggested items
can be retrieved when the text typed into this input is appended to the URL.

4) If a link with the same id as (1) has but with C<lookup_> prepended is
present, then it is also affected by generic.suggest.js.

=item Server Side

When the text typed into the C<*_suggest> input is appended to the URL in the
C<rel> attribute, and a request is made, the response should be of mimetype
C<text/plain>, the first line should be a JSON object containing metadata about
the response. At least, the C<cnt> key should be present and contain the total
number of results drawn from the database for the query (in particular, not the
number of items returned). The subsequent lines of the response body are
'|'-separated lists of the appropriate database columns. The columns are those
present in the URL query string (C<f> fields) with C<id> always coming before
them.

A special response body in the form C<SPECIAL: OFFSET OUT OF RANGE> is also
accepted.

=item JavaScript libraries

jQuery and jQuery UI must be loaded before generic.suggest.js is. Tested jQuery
versions are 1.2.6 and 1.3b. jQuery UI must provide C<draggable> and
C<resizable> capabilities. The jQuery UI is only required for the popups.

=back

=head2 Not-really-global Variables

In general, variables whose name starts with dollar are instances of the jQuery
object.

A number of variables are useful throughout the whole encapsulating function.
Apart from those defied above with UPCASE self-descriptive names, there are:

=over 4

=item $ins

The C<$ins> variable holds the jQuery-wrapped collection of the text inputs that
are enhanced with the autocomplete functionality.

=item $SUGGEST_BUBBLE

A div that contains the list of suggested items and optionally the "next page"
widget. There's just this one and it gets hidden / showed & moved depending on
where the user types, i.e. a new one is B<not> created when the user starts
typing into another autocomplete-enabled input.

=item $SUGGEST_LIST

The list of suggested items (contained in C<$SUGGEST_BUBBLE>).

=item $SUGGEST_FIELDS_BUBBLE

A div containing the descriptive bubble that appears next to the active
suggested item, showing other fields (e.g. when C<title> is showed in the list,
this one might show C<id> and C<slug>).

=back

=head2 Quick Modification Instructions

If you want to change what the bubble contains or how it behaves, edit the
C<$SUGGEST_BUBBLE> variable, as it is initialized and changed by the
C<suggest_update> function.

If you want to change the secondary bubble that shows up to the right of the
highlighted suggested item, edit the C<set_field_bubble> function.

If you want to change what the selected items look like, edit

=over 4

=item the C<new_item> or C<insert_value> function,

=item the initializations,

=item and the HTML generated on the server side.

=back

=head2 How It Works

The real text inputs of the pseudo-inputs (i.e. that with C<id> ending with
C<_suggest>) have a handler for the keyup event (they also have other handlers).
When the keyup event is fired with other key than enter, escape or a scrolling
key, the L<suggest_update> function is run. The escape key is forwarded to the
L<bubble_keyevent> function.

The keypress handler on the same inputs forwards enter and scrolling keys to the
L<bubble_keyevent> function. The escape key is made to delete the last selected
item if the text input is empty.

To sum up what keys are captured by which event: carriage return, line feed,
uparrow, downarrow, page up and page down are captured by the keypress event.
Backspace is processed by both keyup (fires L<suggest_update>) and keypress
(deletes last selected item). All other keys are captured by the keyup event.

The number of suggested items returned is limited on the server side. When there
are more applicable results to a query than the limit, the "next page" widget is
shown. For this to be possible, the total number of results is sent along with
the suggested items themselves. When the widget receives focus, it is passed to
the currently active pseudo-input's text input. This is made not to fire the
usual actions bound to the focus event. This is for keyboard to keep controlling
the text input even after the "next page" widget is clicked. The click event is
processed by the widget itself though.

The $SUGGEST_BUBBLE holds information about which is the currently active input
in its data cache, i.e. C<$SUGGEST_BUBBLE.data('cur_input')>. This is updated on
a variety of events with the C<set_current_input> function.

=head2 functions

Rhe top-level blocks of the suggester functionality are the functions named
C<suggest_*>.

=over 4

=item bubble_keyevent

This function executes appropriate actions on the current input based on a key
pressed. When enter (CR or LF) is the key, the L<suggest_select> function is
run, inserting the desired item into the pseudo-input. Uparrow and downarrow
have expected behavior, shifting the active item up or down. When scrolled
beyond the last or before the first item, previous or next page of results is
requested (L<suggest_scroll_page>). Page up and page down request previous or
next page as well. Escape empties the input and hides the suggest bubble.

=item suggest_update

This function has the responsibility for showing the appropriate content in the
suggest bubble based on the text in the input and previous scrolling actions.

First parameter is the real text input whose value is the base for autocomplete
lookup. Second parameter is the optional offset -- the ord. number of the item
that will be displayed first in the suggest bubble.

If the offset is absent or negative, zero is used instead. If the offset is out
of range (which we'll only know by the special return string from the AJAX
request), it will call itself with zero offset, if it was positive before.

=item suggest_scroll_page

Calls L<suggest_update> with changed offset. The number of currently displayed
suggested items is added to / subtracted from the current offset. Whether adding
or subtracting will be done is set by the first parameter (-1 => subtraction =>
scroll up; +1 => addition => scroll down).

=item suggest_scroll

Takes the I<active> property (css class C<A>) from whichever suggested item had
it and gives it to the next or previous one, based on the key passed as second
argument (expects uparrow or downarrow). If scrolling beyond the last element or
before the first one is attempted, L<suggest_scroll_page> is executed.

=back

=head2 Unexpectednesses

=head3 Triggering change event

Modifying a suggest-enhanced input (inserting or deleting a value) triggers the
C<change> event on the hidden input. However, this is suppressed during the
C<initialize> function. The suppression can be achieved by setting
C<GenericSuggestLib.NO_TRIGGER_CHANGE> to a true value.

=head1 AUTHOR

Oldrich Kruza L<Oldrich.Kruza@sixtease.net>

=cut

*/
