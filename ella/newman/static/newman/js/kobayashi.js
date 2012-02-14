/** 
 * Kobayashi AJAX powered content injection framework.
 * requires: jQuery 1.4.2+, 
 *          gettext() function,
 *          try_decorator() (utils.js),
 *          timer(), timerEnd() functions (utils.js),
 *          to_class() function (inheritance.js),
 *          LoggingLib object.
 *
 * provides:
 *          arr2map() conversion from array to "hashmap",
 *          adr(),
 *          get_adr(),
 *          get_hash(),
 *          get_hashadr(),
 *          Kobayashi object.
 *
 */
KOBAYASHI_VERSION = '2010-07-27';

// Kobayashi logging
log_kobayashi = new LoggingLib('KOBAYASHI:', false);

var CURRENT_HASH = '';
var KOBAYASHI_ADDRESSBAR_CHECK_INTERVAL = 250; // msec
var KOBAYASHI_CSS_LOAD_TRIES = 3;
var KOBAYASHI_CSS_LOAD_TIMEOUT = 250; // msec

// Debugging tools
;;; function alert_dump(obj, name) {
;;;     var s = name ? name + ":\n" : obj.toString ? obj.toString() + ":\n" : '';
;;;     for (var i in obj) s += i + ': ' + obj[i] + "\n";
;;;     alert(s);
;;; }

function arr2map(arr) {
    var rv = {};
    for (var i = 0; i < arr.length; i++) rv[ arr[i] ] = 1;
    return rv;
}

var BASE_PATH = window.BASE_URL ? BASE_URL.replace(/\/$/,'') : '';

function prepend_base_path_to(url) {
    if (url.charAt(0) == '/') url = BASE_PATH + url;
    return url;
}

//// URL management
var URLS = {
/*
    test: function($target) {
        alert($target.attr('id'));
        location.href = 'http://google.com';
    }
*/
};

// mapping for containers to the URLs that give out their base content (what's there when the page loads)
var BASES = {};
//// End of URL management

var Kobayashi = {};

// ID of the element where AJAX'ed stuff is placed if no target specified
Kobayashi.DEFAULT_TARGET = 'kobayashi-default-target';
Kobayashi.LOADED_MEDIA = {};

( function($) { $(document).ready( function() {
    
    // We need to remember what URL is loaded in which element,
    // so we can load or not load content appropriately on hash change.
    var LOADED_URLS = Kobayashi.LOADED_URLS = {};
    
    // We also need to keep track of what's been loaded from a hashchange
    // to be able to distinguish what's affected by
    // no longer being mentioned in the hash.
    var URL_LOADED_BY_HASH = Kobayashi.URL_LOADED_BY_HASH = {};
    
    // If the hash changes before all ajax requests complete,
    // we want to cancel the pending requests. MAX_REQUEST is actually the number
    // of the last hashchange event. Each ajax request then remembers the state
    // of this variable when it was issued and if it's obsolete by the time it's
    // finished, the results are discarded. It's OK to discard it because it
    // never gets into LOADED_URLS.
    var MAX_REQUEST = 0;
    
    // When a sequence of URLs to load into various elements is given,
    // the requests are stored in this fifo and their results are
    // rendered into the document as they become ready, but always in order.
    var LOAD_BUF = [];
    // These are the indices into the LOAD_BUF array -- MIN_LOAD is the index
    // of the request to be processed next (there should never be any defined
    // fields in LOAD_BUF at position less than MIN_LOAD).
    // MAX_LOAD should pretty much always be LOAD_BUF.length - 1.
    var MIN_LOAD, MAX_LOAD = -1;
    
    // When something is loaded into an element that has no base view (in urls.js),
    // and the user hits back, we need to reload. But then we don't want to reload again,
    // so keep information about whether we manipulated the content, so we can
    // abstain from reloading if we have not.
    var PAGE_CHANGED = 0;
    
    function object_empty(o) {
        for (var k in o) return false;
        return true;
    }
    function keys(o) {
        var rv = [];
        for (var k in o) rv.push(k);
        return rv;
    }
    
    // Returns the closest parent that is a container for a dynamically loaded piece of content, along with some information about it.
    function closest_loaded(el) {
        while ( el && (!el.id || !LOADED_URLS[ el.id ]) ) {
            el = el.parentNode;
        }
        if (!el) return null;
        return { container: el, id: el.id, url: LOADED_URLS[ el.id ], toString: function(){return this.id} };
    }
    Kobayashi.closest_loaded = closest_loaded;
    
    function inject_content($target, data, address, extras) {
        // whatever was loaded inside, remove it from LOADED_URLS
        if (!object_empty(LOADED_URLS)) {
            var sel = '#'+keys(LOADED_URLS).join(',#');
            $target.find(sel).each(function() {
                delete LOADED_URLS[ this.id ];
            });
        }
        
        var redirect_to;
        if (redirect_to = extras.xhr.getResponseHeader('Redirect-To')) {
            var arg = {};
            for (k in extras) { arg[k] = extras[k]; }
            delete arg.xhr;
            var literal_address;
            if (redirect_to.substr(0, BASE_PATH.length) == BASE_PATH) {
                literal_address = redirect_to.substr(BASE_PATH.length);
            }
            else {
                literal_address = redirect_to;
            }
            arg.address = literal_address;
            arg.is_priority_request = true;
            load_content(arg);
            if ( extras.by_hash ) {
                var literal_target_id = extras.target_id + '::';
                if (extras.target_id == Kobayashi.DEFAULT_TARGET) {
                    if (location.hash.indexOf('#'+extras.target_id+'::') < 0) {
                        literal_target_id = '';
                    }
                }
                adr(literal_target_id + literal_address, {just_set: true, nohistory: true});
            }
        }
        else {
            $target.removeClass('loading').html(data);
            if ( ! $target.hasClass('js-noautoshow') ) $target.show();
            if (address != undefined) {
                LOADED_URLS[ $target.attr('id') ] = address;
                if (extras && extras.by_hash) URL_LOADED_BY_HASH[ $target.attr('id') ] = true;
            }
            if ($.isFunction( extras.success_callback )) try {
                extras.success_callback.call(extras);
            } catch(e) { log_kobayashi.log('Failed success callback (load_content)', e, extras) };
            $target.trigger('content_added', extras);
            log_kobayashi.log('content_added triggered on element ', $target[0]);
        }
        $(document).trigger('dec_loading');
        PAGE_CHANGED++;
    }
    Kobayashi.inject_content = inject_content;
    
    // argument is a LOAD_BUF item
    function inject_error_message(info) {
        if (!info) {
            log_kobayashi.log('inject_error_message expect an object with target_id, xhr and address. Received:', info);
            return;
        }
        var $target = $('#'+info.target_id);
        $target.text(gettext('Rendering error...'));
        var response_text = info.xhr.responseText;
        var $err_div = $('<div class="error-code"></div>')/*.append(
            $('<a>reload</a>').css({display:'block'}).click(function(){
                load_content(info);
                return false;
            })
        )*/;
        LOADED_URLS[ info.target_id ] = 'ERROR:'+info.address;
        try {
            $err_div.append( JSON.parse(response_text).message );
        } catch(e) {
            // Render the income HTML
            if (response_text.indexOf('<html') >= 0) {
                // Render the HTML document in an <object>
                $obj = $(
                    '<object type="text/html" width="'
                    + ($target.width() - 6)
                    + '" height="'
                    + Math.max($target.height(), 300)
                    + '"></object>'
                );
                
                function append_error_data() {
                    $obj.attr({ data:
                        'data:text/html;base64,'
                        + Base64.encode(response_text)
                    }).appendTo( $err_div );
                }
                
                if (window.Base64) {
                    append_error_data();
                }
                else {
                    request_media(MEDIA_URL + 'js/base64.js');
                    $(document).one('media_loaded', append_error_data);
                }
            }
            else {
                $err_div.append( response_text );
            }
        }
        $target.empty().append($err_div);
    }
    Kobayashi.inject_error_message = inject_error_message;
    
    // get new index to LOAD_BUF (the request queue), either on its end (normal) or at the beginning (is_priority == true)
    function alloc_loadbuf(is_priority) {
        if (MIN_LOAD == undefined || MAX_LOAD+1 < MIN_LOAD) {
            return (MIN_LOAD = ++MAX_LOAD);
        }
        if (is_priority) {
            if (LOAD_BUF[MIN_LOAD] == undefined) return MIN_LOAD;
            if (MIN_LOAD <= 0) {
                log_kobayashi.log(new Error('Cannot make a priority request when request queue is not empty before first request has been finished.'));
                return ++MAX_LOAD;
            }
            return --MIN_LOAD;
        }
        else {
            return ++MAX_LOAD;
        }
    }
    
    // Check if the least present request has finished and if so, shift it
    // from the queue and render the results, and then call itself recursively.
    // This effectively renders all finished requests from the first up to the
    // first pending one, where it stops. If all requests are finished,
    // the queue gets cleaned and the indices reset.
    function draw_ready() {
        
        // Slide up to the first defined request or to the end of the queue
        while (!LOAD_BUF[ MIN_LOAD ] && LOAD_BUF.length > MIN_LOAD+1) MIN_LOAD++;
        
        // If the queue is empty, clean it
        if (!LOAD_BUF[ MIN_LOAD ]) {
//            ;;; log_kobayashi.log("Emptying buffer");
            LOAD_BUF = [];
            MIN_LOAD = undefined;
            MAX_LOAD = -1;
            return;
        }
        var info = LOAD_BUF[ MIN_LOAD ];
        
        if (!info.data) return; // Not yet ready
        
        delete LOAD_BUF[ MIN_LOAD ];
        while (LOAD_BUF.length > MIN_LOAD+1 && !LOAD_BUF[ ++MIN_LOAD ]) {}
        var $target = $('#'+info.target_id);
        if ($target && $target.jquery && $target.length) {} else {
            log_kobayashi.log('Could not find target element: #',info.target_id);
            if ($.isFunction(info.error_callback)) try {
                info.error_callback.call(info);
            } catch(e) { log_kobayashi.log('Failed error callback (load_content)', e, info); }
            $(document).trigger('dec_loading');
            draw_ready();
            return;
        }
        
        inject_content($target, info.data, info.address, info);
        
        // Check next request
        draw_ready();
    }
    
    // This removes a request from the queue
    function cancel_request( load_id ) {
        var info = LOAD_BUF[ load_id ];
        delete LOAD_BUF[ load_id ];
        $('#'+info.target_id).removeClass('loading');
        $(document).trigger('dec_loading');
        
        log_kobayashi.log('Failed to load ',info.address,' into ',info.target_id);
    }
    
    // Take a container and a URL. Give the container the "loading" class,
    // fetch the URL, push the request into the queue, and when it finishes,
    // check for requests ready to be loaded into the document.
    function load_content(arg) {
        var target_id = arg.target_id;
        var address = arg.address;
        if (target_id == undefined) {
            log_kobayashi.log('ERROR: Kobayashi.load_content must get target_id field in its argument.');
            return;
        }
        ;;; log_kobayashi.log('loading ',address,' into #',target_id);
        
        delete arg.xhr; // just in case there was one
            
        // An empty address means we should revert to the base state.
        // If one is not set up for the given container, reload the whole page.
        if (address.length == 0) {
            if (BASES[ target_id ]) {
                address = BASES[ target_id ];
            } else {
                if (PAGE_CHANGED) location.reload();
                return;
            }
        }
        
        $('#'+target_id).addClass('loading');
        $(document).trigger('show_loading');
        
        var url = prepend_base_path_to(address);
        url = $('<a>').attr('href', url).get(0).href;
        var load_id = alloc_loadbuf(arg.is_priority_request);
        LOAD_BUF[ load_id ] = {
            target_id: target_id,
            address: address
        };
        if (arg.by_hash) LOAD_BUF[ load_id ].by_hash = arg.by_hash;
        $.ajax({
            url: url,
            type: 'GET',
            complete: function(xhr) {
                LOAD_BUF[ this.load_id ].xhr = xhr;
                if (this.succeeded) {
                    this._success(xhr);
                }
                else {
                    this._error(xhr);
                }
            },
            success: function() { this.succeeded = true;  },
            error:   function() { this.succeeded = false; },
            _success: function(xhr) {
                if (this.request_no < MAX_REQUEST) {
                    cancel_request( this.load_id );
                }
                else {
                    LOAD_BUF[ this.load_id ].data = xhr.responseText;
                }
                if (this.success_callback) {
                    LOAD_BUF[ this.load_id ].success_callback = this.success_callback;
                }
                if (this.error_callback) {
                    LOAD_BUF[ this.load_id ].error_callback = this.error_callback;
                }
                draw_ready();
            },
            _error: function(xhr) {
                inject_error_message( LOAD_BUF[ this.load_id ] );
                cancel_request( this.load_id );
                $(document).trigger('load_content_failed', [xhr]);
                draw_ready();
                if ($.isFunction(this.error_callback)) try {
                    this.error_callback();
                } catch(e) { log_kobayashi.log('Failed error callback (load_content)', e, this); }
            },
            load_id: load_id,
            request_no: MAX_REQUEST,
            success_callback: arg.success_callback,
            error_callback: arg.error_callback,
            original_options: arg
        });
    }
    Kobayashi.load_content = load_content;
    
    function reload_content(container_id) {
        var addr = LOADED_URLS[ container_id ] || '';
        load_content({
            target_id: container_id,
            address: addr
        });
    }
    Kobayashi.reload_content = reload_content;
    
    function unload_content(container_id, options) {
        if (!options) options = {};
        delete LOADED_URLS[ container_id ];
        delete URL_LOADED_BY_HASH[ container_id ];
        var $container = $('#'+container_id);
        if (!options.keep_content) {
            $container.empty();
        }
    }
    Kobayashi.unload_content = unload_content;
    
    // We want location.hash to exactly describe what's on the page.
    // #url means that the result of $.get(url) be loaded into the default target div.
    // #id::url means that the result of $.get(url) be loaded into the #id element.
    // Any number of such specifiers can be concatenated, e.g. #/some/page/#header::/my/header/
    // If URLS[ foo ] is set (in urls.js), and #foo is present,
    // then the function is called given the $target as argument
    // and nothing else is done for this specifier.
    function load_by_hash() {
        var hash = location.hash.substr(1);
//        ;;; log_kobayashi.log('load #'+MAX_REQUEST+'; hash: '+hash)
        
        // Figure out what should be reloaded and what not by comparing the requested things with the loaded ones.
        var requested = {};
        var specifiers = hash.split('#');
        var ids_map = {};
        var ids_arr = [];
        for (var i = 0; i < specifiers.length; i++) {
            var spec = specifiers[ i ];
            var address = spec;
            var target_id = Kobayashi.DEFAULT_TARGET;
            if (spec.match(/^([-\w]+)::(.*)/)) {
                target_id = RegExp.$1;
                address = RegExp.$2;
            }
            
            requested[ target_id ] = address;
            ids_map[ target_id ] = 1;
            ids_arr.push(target_id);
        }
        for (var k in LOADED_URLS)  if (!ids_map[ k ]) {
            ids_map[ k ] = 1;
            ids_arr.push(k);
        }
        var is_ancestor = {};
        for (var ai = 0; ai < ids_arr.length; ai++) {
            for (var di = 0; di < ids_arr.length; di++) {
                if (ai == di) continue;
                var aid = ids_arr[ai];
                var did = ids_arr[di];
                var $d = $('#'+did);
                if ($d && $d.length) {} else continue;
                var $anc = $d.parent().closest('#'+aid);
                if ($anc && $anc.length) {
                    is_ancestor[ aid+','+did ] = 1;
                }
            }
        }
        var processed = {};
        var reload_target = {};
        while (!object_empty(ids_map)) {
            
            // draw an element that's independent on any other in the list
            var ids = [];
            for (var id in ids_map) ids.push(id);
            var indep;
            for (var i = 0; i < ids.length; i++) {
                var top_el_id = ids[i];
                var is_independent = true;
                for (var j = 0; j < ids.length; j++) {
                    var low_el_id = ids[j];
                    if (low_el_id == top_el_id) continue;
                    if (is_ancestor[ low_el_id + ',' + top_el_id ]) {
                        is_independent = false;
                        break;
                    }
                }
                if (is_independent) {
                    indep = top_el_id;
                    delete ids_map[ top_el_id ];
                    break;
                }
            }
            if (!indep) {
                log_kobayashi.log(ids_map);
                throw('Cyclic graph of elements???');
            }
            
            var result = {};
            for (var par in processed) {
                // if we went over an ancestor of this element
                if (is_ancestor[ par+','+indep ]) {
                    // and we marked it for reload
                    if (processed[ par ].to_reload) {
                        // and we're not just recovering
                        if (requested[ indep ]) {
                            // then reload no matter if url changed or not
                            result.to_reload = true;
                            break;
                        }
                        else {
                            // no need to recover when parent gets reloaded
                            result.to_reload = false;
                            break;
                        }
                    }
                }
            }
            
            // If parent didn't force reload or delete,
            if (result.to_reload == undefined) {
                // and the thing is no longer requested and we don't have the base loaded,
                if (!requested[ indep ] && LOADED_URLS[ indep ] != '') {
                    // and it's been loaded via URL hash change
                    if (URL_LOADED_BY_HASH[ indep ]) {
                        // then reload the base
                        result.to_reload = 1;
                    }
                    else {
                        // else prevent it from being reloaded
                        result.to_reload = false;
                    }
                }
            }
            
            if (result.to_reload == undefined) {
                // If the requested url changed,
                if (requested[ indep ] != LOADED_URLS[ indep ]) {
                    // mark for reload
                    result.to_reload = 1;
                }
            }
            
            // If we want to reload but no URL is set, default to the base
            if (result.to_reload && !requested[ indep ]) {
                requested[ indep ] = '';
            }
            
            processed[ indep ] = result;
        }
        // Now we figured out what to reload:
        // The things that are in requested AND that have processed[ $_ ].to_reload set to a true value
        
        for (var target_id in requested) {
            if (!processed[ target_id ].to_reload) {
                continue;
            }
            var address = requested[ target_id ];
            
            // A specially treated specifier. The callback should set up LOADED_URLS properly.
            // FIXME: Rewrite
            if (URLS[address]) {
                URLS[address](target_id);
                continue;
            }
           
            load_content({
                target_id: target_id,
                address: address,
                by_hash: true
            });
        }
    }
    
    // Fire hashchange event when location.hash changes
    window.CURRENT_HASH = '';
    $(document).bind('hashchange', function() {
//        log_kobayashi.log('hash: ' + location.hash);
        MAX_REQUEST++;
        $('.loading').removeClass('loading');
        $(document).trigger('hide_loading');
        load_by_hash();
    });

    function watch_location() {
        if (location.hash != CURRENT_HASH) {
            CURRENT_HASH = location.hash;
            try {
                $(document).trigger('hashchange');
            } catch(e) { log_kobayashi.log(e); }
        }
        setTimeout(arguments.callee, KOBAYASHI_ADDRESSBAR_CHECK_INTERVAL);
    }
    setTimeout(watch_location, KOBAYASHI_ADDRESSBAR_CHECK_INTERVAL);
    // End of hash-driven content management
    
    // Loads stuff from an URL to an element like load_by_hash but:
    // - Only one specifier (id-url pair) can be given.
    // - URL hash doesn't change.
    // - The specifier is interpreted by adr to get the URL from which to ajax.
    //   This results in support of relative addresses and the target_id::rel_base::address syntax.
    function simple_load(specifier) {
        var args = Kobayashi.get_simple_load_arguments(specifier);
        if (args == null) return;
        load_content(args);
    }
    Kobayashi.simple_load = simple_load;

    function get_simple_load_arguments(specifier) {
        var target_id;
        var COLON_LEN = 2;
        var colon_index = specifier.indexOf('::');
        if (colon_index < 0) {
            target_id = Kobayashi.DEFAULT_TARGET;
        }
        else {
            target_id = specifier.substr(0, colon_index);
        }
        
        var address = get_hashadr(specifier, {not_correct_get_parameters: false});
        
        if (LOADED_URLS[target_id] == address) {
            $('#'+target_id).slideUp('fast');
            unload_content(target_id);
            return null;
        }
        
        return {target_id:target_id, address:address};
    }
    Kobayashi.get_simple_load_arguments = get_simple_load_arguments;

    // Returns object containing HTTP GET parameters 
    function split_get_arguments(url) {
        var out = new Object();
        var qmark_position = url.indexOf('?');
        if (url.length == 0 || qmark_position < 0 || (qmark_position + 1) >= url.length) {
            return out;
        }
        var get_parameters = url.substr(qmark_position + 1);
        if (get_parameters.length == 0) {
            get_parameters = url;
        }
        var assignments = get_parameters.split(/&/);
        
        for (var i = 0; i < assignments.length; i++) {
            var ass = assignments[i];
            var param = (ass.indexOf('=') < 0) ? ass : ass.substr(0, ass.indexOf('='));
            if (param.length == 0) {
                continue;
            }
            var value = ass.substr(ass.indexOf('=') + 1);
            out[param] = value;
        }
        return out;
    }
    Kobayashi.split_get_arguments = split_get_arguments;
    
    // Set up event handlers
    $('.js-simpleload,.js-simpleload-container a').live('click', function(evt) {
        if (evt.button != 0) return true;    // just interested in left button
        var $this = $(this);
        if ( $this.data('hashadred') ) return true;
        simple_load($this.attr('href'));
        $this.data('simpleloaded', true);
        evt.preventDefault();
    });
    $('.js-hashadr,.js-hashadr-container a').live('click', function(evt) {
        if (evt.button != 0) return true;    // just interested in left button
        if ( $(this).data('simpleloaded') ) return true;
        if ( $(this).data('hashadred') ) return false;
        if ($(this).is('.js-nohashadr')) return true;   // override hashadr-container
        adr($(this).attr('href'), {evt: evt});
        $(this).data('hashadred', true);
        evt.preventDefault();
    });
})})(jQuery);


// Manipulate the hash address.
// 
// We use http://admin/#/foo/ instead of http://admin/foo/.
// Therefore, <a href="bar/"> won't lead to http://admin/#/foo/bar/ as we need but to http://admin/bar/.
// To compensate for this, use <a href="javascript:adr('bar/')> instead.
// adr('id::bar/') can be used too.
// 
// adr('bar/#id::baz/') is the same as adr('bar/'); adr('id::baz/').
// Absolute paths and ?var=val strings work too.
// 
// Alternatively, you can use <a href="bar/" class="js-hashadr">.
// The js-hashadr class says clicks should be captured and delegated to function adr.
// A third way is to encapsulate a link (<a>) into a .js-hashadr-container element.
// 
// The target_id::rel_base::address syntax in a specifier means that address is taken as relative
// to the one loaded to rel_base and the result is loaded into target_id.
// For example, suppose that location.hash == '#id1::/foo/'. Then calling
// adr('id2::id1::bar/') would be like doing location.hash = '#id1::/foo/#id2::/foo/bar/'.
// 
// The second argument is an object where these fields are recognized:
// - hash: a custom hash string to be used instead of location.hash,
// - just_get: 'address' Instructs the function to merely return the modified address (without the target_id).
// - just_get: 'hash'    Instructs the function to return the modified hash instead of applying it to location.
//   Using this option disables the support of multiple '#'-separated specifiers.
//   Other than the first one are ignored.
// - just_set: Instructs the function to change the URL without triggering the hashchange event.
// - nohistory: When true, the change of the location will not create a record in the browser history
//   (location.replace will be used).
// - _hash_preproc: Internal. Set when adr is used to preprocess the hash
//   to compensate for hash and LOADED_URLS inconsistencies.
// - evt: a related event (like a link click) that initiated the function call.
//   If there is such an event, it is a good idea to pass it to adr() because then it can set
//   the 'referer' field for the event to the original address, which enables other handlers
//   of the event to see where we're coming from.
//   The field can also be an array of related events.
function adr(address, options) {
    if (address == undefined) {
        log_kobayashi.log('No address given to adr()');
        return;
    }
    
    function set_location_hash(newhash, options) {
        if (newhash.charAt(0) != '#') newhash = '#' + newhash;
        if (options.nohistory) {
            location.replace( newhash );
        }
        else {
            location.hash = newhash;
        }
        if (options.just_set) {
            CURRENT_HASH = location.hash;
        }
    }
    
    // '#' chars in the address separate invividual requests for hash modification.
    // First deal with the first one and then recurse on the subsequent ones.
    if (address.charAt(0) == '#') address = address.substr(1);
    var hashpos = (address+'#').indexOf('#');
    var tail = address.substr(hashpos+1);
    address = address.substr(0, hashpos);
    
    if (!options) options = {};
    var hash = (options.hash == undefined) ? location.hash : options.hash;
    
    // Save the original address into the related event(s)
    var related_events = $.makeArray(options.evt);
    var original_address;
    for (var i = 0; i < related_events.length; i++) {
        if (original_address === undefined) original_address = get_hashadr('');
        related_events[i].referer = original_address;
    }
    
    // Figure out which specifier is concerned.
    var target_id = '';
    // But wait, if target_id::rel_base::address was specified,
    // then get the modifier address and insert it then as appropriate.
    var new_address, reg_res;
    if (reg_res = address.match(/([-\w]*)::([-\w]*)::(.*)/)) {
        var rel_base;
        target_id = reg_res[1];
        rel_base  = reg_res[2];
        address   = reg_res[3];
        if (rel_base.length) rel_base  += '::';
        new_address = adr(rel_base+address, {hash:hash, just_get:'address'})
        if (options.just_get == 'address') return new_address;
    }
    // OK, go on figuring out which specifier is concerned.
    else if (reg_res = address.match(/([-\w]*)::(.*)/)) {
        target_id = reg_res[1];
        address   = reg_res[2];
    }
    
    // If no hash is present, simply use the address.
    if (hash.length <= 1) {
        var newhash;
        if (target_id.length == 0) {
            newhash = address;
        }
        else {
            newhash = target_id + '::' + address
        }
        if (options.just_get == 'address') return address;
        if (options.just_get == 'hash')    return newhash;
        else {
            set_location_hash(newhash, options);
            return;
        }
    }
    
    // In case we're modifying a target that has something loaded
    // in it which is not in the hash, correct it first
    if (!options._hash_preproc) {
        var acc2hash   = get_hashadr(target_id+'::', {_hash_preproc:true});
        var acc2record = Kobayashi.LOADED_URLS[ target_id ];
        if (acc2record && acc2hash != acc2record) {
            hash = get_hash(target_id+'::'+acc2record, {_hash_preproc:true});
        }
    }
    
    // Figure out the span in the current hash where the change applies.
    var start = 0;
    var end;
    var specifier_prefix = '';
    if (target_id.length == 0) {
        for (; start >= 0; start = hash.indexOf('#', start+1)) {
            end = (hash+'#').indexOf('#', start+1);
            if (hash.substring(start, end).indexOf('::') < 0) {
                start++;
                break;
            }
        }
        if (start < 0) {
            hash += '#';
            start = end = hash.length;
        }
    }
    else {
        var idpos = hash.indexOf(target_id+'::');
        if (idpos == -1) {
            hash += '#';
            start = end = hash.length;
            specifier_prefix = target_id + '::';
        }
        else {
            start = idpos + target_id.length + '::'.length;
            end = (hash+'#').indexOf('#', start);
        }
    }
    // Now, hash.substring(start,end) is the address we need to modify.
    
    // Figure out whether we replace the address, append to it, or what.
    // Move start appropriately to denote where the part to replace starts.
    
    var newhash;
    var addr_start = start;
    var old_address = hash.substring(start,end);
    
    // We've not gotten the address from a previous recursive call, thus modify the address as needed.
    if (new_address == undefined) {
        log_kobayashi.log('address:', address);
        new_address = address;
        
        // empty address -- remove the specifier
        if (address.length == 0) {
            // but in case of just_get:address, return the original address for the container (relative "")
            if (options.just_get == 'address') new_address = hash.substring(start,end);
            start = hash.lastIndexOf('#',start);
            start = Math.max(start,0);
            addr_start = start;
        }
        // absolute address -- replace what's in there.
        else if (address.charAt(0) == '/') {
        }
        // set a get parameter
        else if (address.charAt(0) == '&') {
            var qstart = old_address.indexOf('?');
            if (qstart < 0) qstart = old_address.length;
            var oldq = old_address.substr(qstart);
            var newq = oldq;
            if (oldq.length == 0) {
                newq = '?' + address.substr(1);
            }
            else  {
                var assignments = address.substr(1).split(/&/);
                newq = '';
                for (var i = 0; i < assignments.length; i++) {
                    var ass = assignments[i];
                    var vname = (ass.indexOf('=') < 0) ? ass : ass.substr(0, ass.indexOf('='));
                    if (vname.length == 0) {
                        log_kobayashi.log('invalid assignment: ' , ass);
                        continue;
                    }
                    if (newq == '') {
                        newq = '?';
                    }
                    newq = newq + ass;
                    if (i <= (assignments.length - 1)) {
                        newq = newq + '&';
                    }
                }
            }
            new_address = old_address.substr(0, qstart) + newq;
        }
        // relative address -- append to the end, but no farther than to a '?'
        else {
            var left_anchor = hash.lastIndexOf('#', start)+1;
            start = (hash.substr(0, end)+'?').indexOf('?', start);
            
            // cut off the directories as appropriate when the address starts with ../
            while (new_address.substr(0,3) == '../' && hash.substring(left_anchor,start-1).indexOf('/') >= 0) {
                new_address = new_address.substr(3);
                start = hash.lastIndexOf('/', start-2)+1;
            }
        }
    }
    
    newhash = hash.substr(0, start) + specifier_prefix + new_address + hash.substr(end);
    
    if (options.just_get == 'address') {
        return hash.substring(addr_start, start) + new_address;
    }
    else if (tail) {
        return adr(tail, {hash:newhash});
    }
    else if (options.just_get == 'hash') {
        return newhash;
    }
    else {
        set_location_hash(newhash, options);
    }
}
// returns address for use in hash, i.e. without BASE_PATH
function get_hashadr(address, options) {
    if (!options) options = {};
    options.just_get = 'address';
    return adr(address, options);
}
// returns address for use in requests, i.e. with BASE_PATH prepended
function get_adr(address, options) {
    var hashadr = get_hashadr(address, options);
//    if (hashadr.charAt(0) != '/') hashadr = get_hashadr(hashadr);
    return prepend_base_path_to(hashadr);
        
}
// returns the hash instead of assigning it to location
function get_hash(address, options) {
    if (!options) options = {};
    options.just_get = 'hash';
    return adr(address, options);
}


// Dynamic media (CSS, JS) loading
(function() {
    
    // Get an URL to a CSS or JS file, attempt to load it into the document and call callback on success.
    function load_media(url, callbacks) {
        if (!url) {
            log_kobayashi.log('Error: No URL given to Kobayashi.load_media');
            return;
        }
        
        var succ_fn = callbacks.succ_fn;
        var err_fn  = callbacks.err_fn;
        var next_fn = callbacks.next_fn;
        
        if (Kobayashi.LOADED_MEDIA[ url ]) {
            if ($.isFunction(succ_fn)) succ_fn(url);
            if ($.isFunction(next_fn)) next_fn(url);
            ;;; log_kobayashi.log('Skipping loaded medium: ', url);
            return true;
        }
        
        ;;; log_kobayashi.log('loading medium ',url);
        
        /(?:.*\/\/[^\/]*)?([^?]+)(?:\?.*)?/.exec(url);
        $(document).data('loaded_media')[ RegExp.$1 ] = url;
        
        if (/\.(\w+)(?:$|\?)/.exec(url))
            var ext = RegExp.$1;
        else throw('Unexpected URL format: '+url);
        
        var abs_url = $('<a>').attr({href:url}).get(0).href;
        
        function stylesheet_present(url) {
            for (var i = 0; i < document.styleSheets.length; i++) {
                if (document.styleSheets[i].href == url) return document.styleSheets[i];
            }
            return false;
        }
        function get_css_rules(stylesheet) {
            try {
                if (stylesheet.cssRules) return stylesheet.cssRules;
                if (stylesheet.rules   ) return stylesheet.rules;
            } catch(e) { log_kobayashi.log(e); }
            log_kobayashi.log('Could not get rules from: ', stylesheet);
            return;
        }
        
        if (ext == 'css') {
            if (stylesheet_present(abs_url)) {
                if ($.isFunction(succ_fn)) succ_fn(url);
                if ($.isFunction(next_fn)) next_fn(url);
                ;;; log_kobayashi.log('Stylesheet already present: ',url);
                return true;
            }
            var tries = KOBAYASHI_CSS_LOAD_TRIES;
            
            setTimeout(function() {
                if (--tries < 0) {
                    Kobayashi.LOADED_MEDIA[ url ] = false;
                    log_kobayashi.log('Timed out loading CSS: ',url);
                    if ($.isFunction(err_fn)) err_fn(url);
                    return;
                }
                var ss;
                if (ss = stylesheet_present(abs_url)) {
                    var rules = get_css_rules(ss);
                    if (rules && rules.length) {
                        Kobayashi.LOADED_MEDIA[ url ] = true;
                        if ($.isFunction(succ_fn)) succ_fn(url);
                        ;;; log_kobayashi.log('CSS Successfully loaded: ',url);
                        
                    }
                    else {
                        Kobayashi.LOADED_MEDIA[ url ] = false;
                        if (rules) log_kobayashi.log('CSS stylesheet empty.');
                        if ($.isFunction(err_fn)) err_fn(url);
                        return;
                    }
                }
                else setTimeout(arguments.callee, KOBAYASHI_CSS_LOAD_TIMEOUT);
            }, KOBAYASHI_CSS_LOAD_TIMEOUT);
            
            var $csslink = $('<link rel="stylesheet" type="text/css" href="'+url+'" />').appendTo($('head'));
            if ($.isFunction(next_fn)) next_fn(url);
            return $csslink;
        }
        else if (ext == 'js') {
            var $scripts = $('script');
            for (var i = 0; i < $scripts.length; i++) {
                if ($scripts.get(i).src == abs_url) {
                    if ($.isFunction(succ_fn)) succ_fn(url);
                    if ($.isFunction(next_fn)) next_fn(url);
                    ;;; log_kobayashi.log('Script already present: ',url);
                    return true;
                }
            }
            return $.ajax({
                url: url,
                type: 'GET',
                dataType: 'script',
                success: function() {
                    Kobayashi.LOADED_MEDIA[ this.url ] = true;
                    if ($.isFunction(succ_fn)) succ_fn(url);
                    if ($.isFunction(next_fn)) next_fn(url);
                    ;;; log_kobayashi.log('JS Successfully loaded: ',this.url);
                },
                error: function() {
                    Kobayashi.LOADED_MEDIA[ this.url ] = false;
                    if ($.isFunction( err_fn))  err_fn(url);
                    if ($.isFunction(next_fn)) next_fn(url);
                    log_kobayashi.log('Failed to load JS: ',url, this);
                },
                cache: true
            });
        }
        else throw('Unrecognized media type "'+ext+'" in URL: '+url);
    }
    Kobayashi.load_media = load_media;
    
    
    var media_queue = [];
    $(document).data('loaded_media', {});
    function init_media() {
        //timer('trigger_ media_loaded');
        try {
            $(document).trigger('media_loaded').data('loaded_media', {});
        } catch (e) {
            log_kobayashi.log('Error when triggering media_loaded.', e);
        }
        //timerEnd('trigger_ media_loaded');
    }
    function draw_media() {
        if (media_queue.length == 0) {
            init_media();
            return true;
        }
        var url = media_queue.shift();
        Kobayashi.load_media(url, {next_fn: draw_media});
    }
    
    // Load a CSS / JavaScript file (given an URL) after previously requested ones have been loaded / failed loading.
    function request_media(url) {
        if (!url) {
            log_kobayashi.log('No URL given to request_media');
            return;
        }
        log_kobayashi.log('Request media ' , url);
        var do_start = media_queue.length == 0;
        media_queue.push(url);
        if (do_start) {
            setTimeout(draw_media,100);
            $(document).trigger('media_loading_start');
        }
    }
    window.request_media = request_media;
    
})();
