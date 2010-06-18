/**
 * Common utilities/functions and objects.
 * requires: jQuery 1.4.2+, 
 *          gettext() function,
 *          to_class() function (inheritance.js).
 *
 * provides:
 *          try_decorator(funct)  decorated function is called inside try statement,
 *          timer(), timerEnd() Firebug timer wrappers,
 *          timer_decorator(name, func) tracks elapsed time of called func,
 *          str_concat() effective string concatenation,
 *          carp() function for logging purposes,
 *          StringBuffer object,
 *          LoggingLib object,
 *          ContentElementViewportDetector object.
 */
var __LoggingLib = function () {
    this.init = function (name, enabled) {
        this.name = name;
        this.enabled = enabled;
        this.capabilities = [];
        this.enable_debug_div = false;
        this.str_buf = new StringBuffer();
    };

    this.log_debug_div = function () {
        $('#debug').append($('<p>').text($.makeArray(arguments).join(' ')));
    };

    this.log_console_apply = function () {
        console.log.apply(this, arguments);
    };

    this.log_console = function () {
        //console.log(arguments);
        // workaround for google chromium to see logged message immediately
        this.str_buf.clear();
        this.str_buf.append(this.name);
        for (var i = 0; i < arguments.length; i++) {
            this.str_buf.append(arguments[i]);
        }
        console.log(this.str_buf.to_string());
    };

    this.workaround_opera_browser = function () {
            try {
                var log_func = window.opera.postError;
                window.console = {};
                window.console.log = log_func;
            } catch (e) {
            }
    };

    this.first_log_attempt = function () {
        if (this.enable_debug_div) {
            try {
                this.log_debug_div.apply(this, arguments);
                this.capabilities.push(log_debug_div);
            } catch(e) { }
        }
        var args = Array.prototype.slice.call(arguments);
        args.unshift(this.name); // prepend logger name

        // Opera?
        if (typeof(console) == 'undefined') {
            this.workaround_opera_browser();
            this.capabilities.push(this.log_console);
            this.log_console.apply(this, args);
            return;
        }

        try {
            this.log_console_apply.apply(this, args);
            this.capabilities.push(this.log_console_apply);
        } catch(e) {
            try {
                this.log_console.apply(this, args);
                this.capabilities.push(this.log_console);
            } catch(e) { 
            }
        }
    };

    this.log_it = function () {
        var callback;
        var len = this.capabilities.length;
        var args = Array.prototype.slice.call(arguments);
        args.unshift(this.name); // prepend logger name
        for (var i = 0; i < len; i++) {
            callback = this.capabilities[i];
            //callback(arguments);
            callback.apply(this, args);
        }
        args = null;
    };

    this.log = function () {
        if (!this.enabled) return;
        if (this.capabilities.length == 0) {
            this.first_log_attempt.apply(this, arguments);
        } else {
            this.log_it.apply(this, arguments);
        }
    };

    return this;
};
var LoggingLib = to_class(__LoggingLib);

function carp() {
    log_generic.log.apply(log_generic, arguments);
}

function str_concat() {
    if (typeof(str_concat.string_buffer) == 'undefined') {
        str_concat.string_buffer = new StringBuffer();
    } else {
        str_concat.string_buffer.clear();
    }
    str_concat.string_buffer.append_array(arguments);
    return str_concat.string_buffer.to_string();
}

var __StringBuffer = function() {
    this.init = function () {
        this.buffer = [];
        this.clear_i = 0; //counter variable
    };

    this.clear = function () {
        var len = this.buffer.length;
        for (this.clear_i = 0; this.clear_i < len; this.clear_i++) {
            this.buffer.pop();
        }
    };
    
    this.append = function (text) {
        this.buffer.push(text);
    }

    function append_array(arr) {
        for (var i = 0; i < arr.length; i++) {
            this.buffer.push(arr[i]);
        }
    }
    this.appendArray = append_array;
    this.append_array = append_array;

    function to_string() {
        return this.buffer.join('');
    }
    this.toString = to_string;
    this.to_string = to_string;

    return this;
};
var StringBuffer = to_class(__StringBuffer);

function try_decorator(func) {
    function wrapped() {
        var out = null;
        try {
            out = func.apply(null, arguments);
        } catch (e) {
            carp('Error in try_decorator:' , e.toString(), ' when calling ', func);
        }
        return out;
    }
    return wrapped;
}

// Timer (useful for time consumption profilling)

function timer(name) {
    if (!DEBUG) return;
    try {
        console.time(name);
    } catch (e) {}
}

function timerEnd(name) {
    if (!DEBUG) return;
    try {
        console.timeEnd(name);
    } catch (e) {}
}

var accumulated_timers = {};
var AccumulatedTimeMeasurement = function(timer_name) {
    var me = new Object();
    me.name = timer_name;
    var times = [];
    var m_begin = null;
    var m_end = null;

    function begin_measurement() {
        m_begin = (new Date()).getTime();
    }

    function end_measurement() {
        m_end = (new Date()).getTime();
        times.push( (m_end - m_begin) );
    }

    function avg() {
        var res = 0;
        for (var i = 0; i < times.length; i++) {
            res += times[i]; //msec
        }
        return res / times.length;
    }
    me.avg = avg;

    function decorate(func) {
        function wrapped() {
            var out = null;
            begin_measurement();
            try {
                out = func.apply(null, arguments);
            } catch (e) {
                carp('Error in timer_decorator:' , e.toString());
            }
            end_measurement();
            return out;
        }
        return wrapped;
    }
    me.decorate = decorate;

    return me;
};

// static method (like a)
function AccumulatedTimeMeasurement__avg_all() {
    carp('Timers:');
    for (var timer_name in accumulated_timers) {
        var timer = accumulated_timers[timer_name];
        carp(timer.name, ': ', timer.avg());
    }
    carp('End Timers');
}
AccumulatedTimeMeasurement.avg_all = AccumulatedTimeMeasurement__avg_all;

function timer_decorator(name, func) {
    // create new timer object if timer does not exist
    if (!(name in accumulated_timers)) {
        accumulated_timers[name] = AccumulatedTimeMeasurement(name);
    }
    return accumulated_timers[name].decorate(func);
}

// /end of Timer


var __ContentElementViewportDetector = function() {
    /**
     * detects viewport for elements inside <div id="content">.
     * Resolution of viewport: top, middle and bottom of watched element.
     */
    this.init = function ($watched_element) {
        this._middle_in_viewport = false;
        this._top_in_viewport = false;
        this._bottom_in_viewport = false;
        this.$elem = $watched_element;
    };

    this.is_element_in_viewport = function () {
        /*var $li = $('a.saveall');
        var content_position = $('div.#content').scrollParent().scrollTop();
        var area_position = $elem.position().top;
        var area_bottom = area_position + element_height;*/

        var element_height = this.$elem.height();
        var element_top = this.$elem.offset().top;
        var from_top_visible = $('#footer').offset().top - element_top; // if var < 0, element is under #footer element.
        var from_top_element_bottom_hidden = from_top_visible - element_height;
        var from_top_hidden = this.$elem.position().top; // if var < 0, element is partialy or totally hidden under topmenu (#header).
        this._top_in_viewport = (from_top_visible >= 0) && (from_top_hidden >= 0);
        this._bottom_in_viewport = (from_top_element_bottom_hidden >= 0) && (from_top_visible >= 0)
            && (from_top_hidden + element_height >= 0);
        var whole_under_header = (element_height + element_top) > ($('#header').offset().top + $('#header').height());
        this._middle_in_viewport = (from_top_visible >= 0) && whole_under_header;
    };

    this.in_viewport = function in_viewport() {
        this.is_element_in_viewport();
        return this._middle_in_viewport;
    };
    this.middle_in_viewport = this.in_viewport;

    this.top_in_viewport = function top_in_viewport() {
        this.is_element_in_viewport();
        return this._top_in_viewport;
    };

    this.bottom_in_viewport = function () {
        this.is_element_in_viewport();
        return this._bottom_in_viewport;
    };

    return this;
};
var ContentElementViewportDetector = to_class(__ContentElementViewportDetector);


// init logging
var log_generic = null;
if (DEBUG) {
    log_generic = new LoggingLib('GENERIC:', true);
} else {
    log_generic = new LoggingLib('GENERIC:', false);
}
