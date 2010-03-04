function DateTimeInput(input) {
    this.input = input;
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
}

function DateInput(input) {
    this.input = input;
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
}

(function($) {
    $('span.js-dtpicker-trigger').live('click', function() {
        var $dtp = $('.datetimepicker');
        var x = $(this).offset().left + $(this).width();
        var y = simple_offset(this).top - $('#container').offset().top; // not $(this).offset().top because of scrolling fixed #container, in which the dtpicker also is
        var $input = $(this).data('input');

        // check if Y doesn't reach below the current screen height
        var d = y + $dtp.outerHeight()  -  $(window).outerHeight();
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

                $(  '<span class="js-dtpicker-trigger"><img src="'
                    +MEDIA_URL
                    +'ico/16/vcalendar.png" alt="cal" /></span>'
                )
                .data('input', $input)
                .insertAfter(this);

                $input.keydown(function(evt) {
                    var delta = 0;
                    if (evt.keyCode == 38) delta =  1;
                    if (evt.keyCode == 40) delta = -1;
                    if (!delta) return true;
                    var pos = this.selectionEnd;
                    $input.data('dti').scroll(pos, delta);
                    evt.preventDefault();
                });
            }
        });
    }
    datetime_init();

    var timepicker_html;
    function media_dependent_datetime_init(evt) {

        if ( ! timepicker_html ) {
            var args = arguments; args._this = this;
            get_html_chunk('timepicker', function(data) {
                timepicker_html = data;
                args.callee.apply( args._this, args );
            });
            return;
        }

        // create the datetimepicker div
        if ($('.datetimepicker').length) { }    // but only if there is none yet
        else if (
               evt.type == 'content_added'  // and we added something that uses a datepicker
            && $(evt.target).find('.js-dtpicker-trigger').length == 0    // if anything
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
                    $(this).closest('.datetimepicker').hide();
                },
                onClose: function() {
                    $(this).closest('.datetimepicker').hide();
                }
            }));
            $datepicker.appendTo($dtpicker);

            // Time picker
            var $timepicker = $('<div class="timepicker">')
            .html(timepicker_html).appendTo($dtpicker);


            // Container placement
            $dtpicker.appendTo(
                   $('.change-form').get(0)
                || $('#content').get(0)
                || $('body').get(0)
            );
        }
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
        $(this).closest('.datetimepicker').hide();
    });

    $( document ).bind('content_added', datetime_init);
    $( document ).bind('content_added', media_dependent_datetime_init);
    $( document ).one ('media_loaded' , media_dependent_datetime_init);

})(jQuery);
