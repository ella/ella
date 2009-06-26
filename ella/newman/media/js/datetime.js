function DateTimeInput(input) {
    this.input = input;
    this.x_pos = $(input).offset().left;
    this.cursor_pos = function(evt) {
        var input = this.input;
        var input_style;
        try {
            input_style = getComputedStyle(input, '');
        } catch(e) {
            input_style = input.currentStyle;
        }
        if (input_style == undefined) input_style = {};
        
        var padding = input_style.paddingLeft;
        if (/^(\d+)(?:px)?$/.test(padding)) padding = new Number(RegExp.$1);
        else padding = 0;
        var border = input_style.borderLeftWidth;
        if (/^(\d+)(?:px)?$/.test(border )) border  = new Number(RegExp.$1);
        else border = 0;
        
        var x = evt.clientX - this.x_pos - padding - border;
        
        var $tempspan = $('<span>').css({
            position: 'absolute',
            top: '-100px'
        });
        for (var property in input_style) {
            if (property.substr(0, 4) == 'font') {
                $tempspan.css(property, input_style[property]);
            }
        }
        $tempspan.insertAfter($(input));
        
        $tempspan.text('m');
        var dotwidth = -$tempspan.width();
        $tempspan.text('m.');
        dotwidth += $tempspan.width();
        $tempspan.text( $(input).val() + '.' );
        
        var text, last = '';
        while ($tempspan.width() - dotwidth >= x) {
            text = $tempspan.text();
            if (text == '.') break;
            text = text.substr(0,text.length-1);
            last = text.substr(text.length-1);
            $tempspan.text(
                text.substr(0, text.length-1) + '.'
            );
        }
        text = $tempspan.text();
        text = text.substr(0, text.length-1) + last;
        $tempspan.remove();
//        ;;; $('#pos').text( text );
        return text.length;
    };
    this.set_date = function(d, preserve) {
        var fields = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/.exec( $(this.input).val() );
        var year, month, day, hour, minute, dow;
        if (!fields) preserve = {};
        else {
            year   = fields[1];
            month  = fields[2];
            day    = fields[3];
            hour   = fields[4];
            minute = fields[5];
            month = new Number(month) - 1;
        }
        if (!preserve) preserve = { };
        
        if (preserve.year  ) d.setFullYear(year  );
        if (preserve.month ) d.setMonth   (month );
        if (preserve.day   ) d.setDate    (day   );
        if (preserve.hour  ) d.setHours   (hour  );
        if (preserve.minute) d.setMinutes (minute);
        
        year = d.getFullYear();
        month = new Number(d.getMonth()) + 1;
        day = d.getDate();
        hour = d.getHours();
        minute = d.getMinutes();
        dow = ([
            gettext('Su'), gettext('Mo'), gettext('Tu'), gettext('We'), gettext('Th'), gettext('Fr'), gettext('Sa')
        ])[ d.getDay() ];
        
        function pad(str,n) {
            var s = new String(str);
            while (s.length < n) s = '0'+s;
            return s;
        }
        
        var nval = ''
        + pad(  year,4) + '-'
        + pad( month,2) + '-'
        + pad(   day,2) + ' '
        + pad(  hour,2) + ':'
        + pad(minute,2) + ' '
        + dow;
        $(this.input).val( nval ).change();
    };
    this.scroll = function(pos, delta) {
        var input = this.input;
        var fields = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/.exec( $(input).val() );
        if (!fields) {
            carp('Invalid date:', $(input).val());
            return;
        }
        
        var i = ([
            undefined,
            1,1,1,1,
            undefined,
            2,2,
            undefined,
            3,3,
            undefined,
            4,4,
            undefined,
            5,5,
            undefined,
            3,3
        ])[pos];
        if (i == undefined) return;
        fields[i] = new Number(fields[i]) + delta;
        
        var year   = fields[1];
        var month  = fields[2];
        var day    = fields[3];
        var hour   = fields[4];
        var minute = fields[5];
        month = new Number(month) - 1;
        
        var d = new Date();
        d.setFullYear(year);
        d.setMonth(month);
        d.setDate(day);
        d.setHours(hour);
        d.setMinutes(minute);
        d.setSeconds(0);
        d.setMilliseconds(0);
        
        this.set_date(d);
        
        input.selectionStart = input.selectionEnd = pos;
    };
}

function DateInput(input) {
    this.input = input;
    this.x_pos = $(input).offset().left;
    this.cursor_pos = function(evt) {
        var input = this.input;
        var input_style;
        try {
            input_style = getComputedStyle(input, '');
        } catch(e) {
            input_style = input.currentStyle;
        }
        if (input_style == undefined) input_style = {};
        
        var padding = input_style.paddingLeft;
        if (/^(\d+)(?:px)?$/.test(padding)) padding = new Number(RegExp.$1);
        else padding = 0;
        var border = input_style.borderLeftWidth;
        if (/^(\d+)(?:px)?$/.test(border )) border  = new Number(RegExp.$1);
        else border = 0;
        
        var x = evt.clientX - this.x_pos - padding - border;
        
        var $tempspan = $('<span>').css({
            position: 'absolute',
            top: '-100px'
        });
        for (var property in input_style) {
            if (property.substr(0, 4) == 'font') {
                $tempspan.css(property, input_style[property]);
            }
        }
        $tempspan.insertAfter($(input));
        
        $tempspan.text('m');
        var dotwidth = -$tempspan.width();
        $tempspan.text('m.');
        dotwidth += $tempspan.width();
        $tempspan.text( $(input).val() + '.' );
        
        var text, last = '';
        while ($tempspan.width() - dotwidth >= x) {
            text = $tempspan.text();
            if (text == '.') break;
            text = text.substr(0,text.length-1);
            last = text.substr(text.length-1);
            $tempspan.text(
                text.substr(0, text.length-1) + '.'
            );
        }
        text = $tempspan.text();
        text = text.substr(0, text.length-1) + last;
        $tempspan.remove();
//        ;;; $('#pos').text( text );
        return text.length;
    };
    this.set_date = function(d, preserve) {
        var fields = /^(\d{4})-(\d{2})-(\d{2})/.exec( $(this.input).val() );
        var year, month, day,  dow;
        if (!fields) preserve = {};
        else {
            year   = fields[1];
            month  = fields[2];
            day    = fields[3];
            month = new Number(month) - 1;
        }
        if (!preserve) preserve = { };
        
        if (preserve.year ) d.setFullYear(year );
        if (preserve.month) d.setMonth   (month);
        if (preserve.day  ) d.setDate    (day  );
        
        year = d.getFullYear();
        month = new Number(d.getMonth()) + 1;
        day = d.getDate();
        dow = ([
            gettext('Su'), gettext('Mo'), gettext('Tu'), gettext('We'), gettext('Th'), gettext('Fr'), gettext('Sa')
        ])[ d.getDay() ];
        
        function pad(str,n) {
            var s = new String(str);
            while (s.length < n) s = '0'+s;
            return s;
        }
        
        var nval = ''
        + pad(  year,4) + '-'
        + pad( month,2) + '-'
        + pad(   day,2) + ' '
        + dow;
        $(this.input).val( nval ).change();
    };
    this.scroll = function(pos, delta) {
        var input = this.input;
        var fields = /^(\d{4})-(\d{2})-(\d{2})/.exec( $(input).val() );
        if (!fields) {
            carp('Invalid date:', $(input).val());
            return;
        }
        
        var i = ([
            undefined,
            1,1,1,1,
            undefined,
            2,2,
            undefined,
            3,3,
            undefined,
            3,3
        ])[pos];
        if (i == undefined) return;
        fields[i] = new Number(fields[i]) + delta;
        
        var year   = fields[1];
        var month  = fields[2];
        var day    = fields[3];
        month = new Number(month) - 1;
        
        var d = new Date();
        d.setFullYear(year);
        d.setMonth(month);
        d.setDate(day);
        d.setHours(0);
        d.setMinutes(0);
        d.setSeconds(0);
        d.setMilliseconds(0);
        
        this.set_date(d);
        
        input.selectionStart = input.selectionEnd = pos;
    };
}

(function($) {
    $('span.dtpicker-trigger').live('click', function() {
        var $dtp = $('.datetimepicker');
        var x = $(this).offset().left + $(this).width();
        var y = $(this).offset().top;
        var $input = $(this).data('input');
        
        // check if Y doesn't reach below the current screen height
        var d = y + $dtp.outerHeight()  -  $('body').outerHeight();
        if (d > 0) y -= d;
        if (y < 0) y = 0;   // But rather reach below bottom than above top
        
        $('.datetimepicker').css({
            top : y + 'px',
            left: x + 'px'
        }).toggle().data( 'input', $input );
    });
    
    function datetime_init() {
        $('.vDateTimeInput,.vDateInput').each( function() {
            var $input = $(this);
            var is_datetime = $input.hasClass('vDateTimeInput');
            if (! $input.data('dti')) {
                if (is_datetime) {
                    $input.data('dti', new DateTimeInput(this));
                }
                else {
                    $input.data('dti', new DateInput(this));
                }
                
                $(  '<span class="dtpicker-trigger"><img src="'
                    +MEDIA_URL
                    +'ico/16/vcalendar.png" alt="cal" /></span>'
                )
                .data('input', $input)
                .insertAfter(this);
                
                $input.keypress(function(evt) {
                    var delta = 0;
                    if (evt.keyCode == 38) delta =  1;
                    if (evt.keyCode == 40) delta = -1;
                    if (!delta) return true;
                    var pos = this.selectionEnd;
                    $input.data('dti').scroll(pos, delta);
                });
            }
        });
    }
    datetime_init();

    function media_dependent_datetime_init(evt) {
        // create the datetimepicker div
        if ($('.datetimepicker').length) { }    // but only if there is none yet
        else if (
               evt.type == 'content_added'  // and we added something that uses a datepicker
            && $(evt.target).find('.dtpicker-trigger').length == 0    // if anything
        ) { }
        else {
            // Container creation
            var $dtpicker = $('<div class="datetimepicker">');
            
            // Date picker
            var $datepicker = $('<div class="datepicker">');
            $datepicker.datepicker(new DATEPICKER_OPTIONS({
                onSelect: function(dtext, dpick) {
                    var $dtpicker = $(this).closest('.datetimepicker');
                    var dti = $( $dtpicker.data('input') ).data('dti');
                    var d = new Date();
                    d.setFullYear(dpick.selectedYear);
                    d.setMonth(dpick.selectedMonth);
                    d.setDate(dpick.selectedDay);
                    d.setHours(0);
                    d.setMinutes(0);
                    d.setSeconds(0);
                    d.setMilliseconds(0);
                    dti.set_date(d, {/*preserve*/hour:true,minute:true});
                },
                onClose: function() {
                    $(this).closest('.datetimepicker').hide();
                }
            }));
            $datepicker.appendTo($dtpicker);
            
            // Time picker
            var $timepicker = $('<div class="timepicker">')
            .html(
                '<button type="button" class="js-dtpicker-close"><img src="'+MEDIA_URL+'ico/16/cancel.png" alt="X" /></button>' +
                '<button type="button" class="js-timepick js-time-now">' +gettext('Now' )+'</button>' +
                '<button type="button" class="js-timepick js-time-0600">'+gettext('6am' )+'</button>' +
                '<button type="button" class="js-timepick js-time-1200">'+gettext('Noon')+'</button>'
            ).appendTo($dtpicker);
            
            // Container placement
            $dtpicker.appendTo(
                   $('.change-form').get(0)
                || $('#content').get(0)
                || $('body').get(0)
            );
        }
        
        // mousewheel datetime scrolling
        function mousewheel_handler(evt, delta) {
            var dti = $(this).data('dti');
            var pos = dti.cursor_pos(evt);
            dti.scroll(pos, delta / Math.abs(delta||1));
        };
        if (DEBUG)  // FIXME: mousewheel scrolling broken!
        $('.vDateTimeInput,.vDateInput').not('.mwheel-enhanced').focus( function() {
            $(this)  .bind('mousewheel', mousewheel_handler);
        }).blur( function() {
            $(this).unbind('mousewheel', mousewheel_handler);
        }).addClass('mwheel-enhanced');
    }
    
    $('.js-dtpicker-close').live('click', function(evt) {
        if (evt.button != 0) return;
        $(this).closest('.datetimepicker').hide();
    });
    $('.js-timepick').live('click', function(evt) {
        if (evt.button != 0) return;
        var dti = $( $(this).closest('.datetimepicker').data('input') ).data('dti');
        var selected_time = /js-time-(\d\d)(\d\d)/.exec(this.className);
        var d = new Date();
        d.setSeconds(0);
        d.setMilliseconds(0);
        if ( ! selected_time ) {
            if ( ! $(this).hasClass('js-time-now') ) return;
        }
        else {
            var selected_hours   = selected_time[1];
            var selected_minutes = selected_time[2];
            d.setHours  (selected_hours  );
            d.setMinutes(selected_minutes);
            // let default date be the following 24 hours
            if (d.getTime() < new Date().getTime()) {
                d.setDate( d.getDate() + 1 );
            }
        }
        dti.set_date(d, {/*preserve*/year:true,month:true,day:true});
    });
    
    $( document ).bind('content_added', datetime_init);
    $( document ).bind('content_added', media_dependent_datetime_init);
    $( document ).one ('media_loaded' , media_dependent_datetime_init);
    
    // Close the datetimepicker when something else is clicked
    $('body').live('click', function(evt) {
        // ignore clicking on the datepicker triggering icon
        if ($(evt.target).closest('.dtpicker-trigger').length) return true;
        // ignore clicking on the datepicker itself
        if ($(evt.target).closest('.datetimepicker').length)   return true;
        // if there's no datepicker shown, don't attempt to hide it
        if ($('.datetimepicker').not(':hidden').length == 0)   return true;
        // all else failed, hide all present datepickers
        $('.datetimepicker').hide();
        // and let the click be processed as usual
        return true;
    });

})(jQuery);
