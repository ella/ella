( function($) { $(document).ready( function() {

    // Debugging tools
    ;;; function alert_dump(obj, name) {
    ;;;     var s = name ? name + ":\n" : '';
    ;;;     for (var i in obj) s += i + ': ' + obj[i] + "\n";
    ;;;     alert(s);
    ;;; }
    ;;; function carp(message) {
    ;;;    if (window.console) {
    ;;;        console.log(message);
    ;;;    }
    ;;; }

    // Store the #content div, so we need not always mine it from the DOM.
    var $CONTENT = $('#content');

    // We need to remember what URL is loaded in which element,
    // so we can load or not load content appropriately on hash change.
    var LOADED_URLS = {};

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
            ;;; carp("Emptying buffer");
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
            carp('Could not find target element: #'+info.target_id);
            return;
        }
        $target.removeClass('loading').html(info.data);
        LOADED_URLS[ info.target_id ] = info.address;
        PAGE_CHANGED++;

        // Check next request
        draw_ready();
    }

    // This removes a request from the queue and
    function cancel_request( load_id ) {
        var info = LOAD_BUF[ load_id ];
        delete LOAD_BUF[ load_id ];
        $('#'+info.target_id).removeClass('loading');
        carp('Failed to load '+info.address+' into '+info.target_id);
    }

    // Take a container and a URL. Give the container the "loading" class,
    // fetch the URL, push the request into the queue, and have it checked
    // when it finishes.
    function load_content(arg) {
        var target_id = arg.target_id;
        var address = arg.address;
        ;;; carp('loading '+address+' into '+target_id);

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

        var url = $('<a>').attr('href', address).get(0).href;
        var load_id = ++MAX_LOAD;
        if (MIN_LOAD == undefined || load_id < MIN_LOAD) MIN_LOAD = load_id;
        LOAD_BUF[ load_id ] = {
            target_id: target_id,
            order: arg.order,
            address: address
        };
        $.ajax({
            url: url,
            type: 'GET',
            success: function(data) {
                if (this.request_no < MAX_REQUEST) {
                    cancel_request( this.load_id );
                }
                else {
                    LOAD_BUF[ this.load_id ].data = data;
                }
                draw_ready();
            },
            error: function() {
                cancel_request( this.load_id );
                draw_ready();
            },
            load_id: load_id,
            request_no: MAX_REQUEST
        });
    }

    // We want location.hash to exactly describe what's on the page.
    // #url means that the result of $.get(url) be loaded into the #content div.
    // #id::url means that the result of $.get(url) be loaded into the #id element.
    // Any number of such specifiers can be concatenated, e.g. #/some/page/#header::/my/header/
    // If URLS[ foo ] is set (in urls.js), and #foo is present,
    // then the function is called given the $target as argument
    // and nothing else is done for this specifier.
    function load_by_hash() {
        var hash = location.hash.substr(1);
        ;;; carp('load #'+MAX_REQUEST+'; hash: '+hash)

        // Figure out what should be reloaded and what not by comparing the requested things with the loaded ones.
        var requested = {};
        var specifiers = hash.split('#');
        for (var i = 0; i < specifiers.length; i++) {
            var spec = specifiers[ i ];
            var address = spec;
            var target_id = 'content';
            if (spec.match(/^([-\w]+)::(.*)/)) {
                target_id  = RegExp.$1;
                address = RegExp.$2;
            }
            requested[ target_id ] = address;
        }
        for (var k in LOADED_URLS) {
            // if this specifier didn't change, don't load it again
            if (LOADED_URLS[k] == requested[k]) {
                delete requested[k];
                continue;
            }
            // if this specifier is no longer present, reload the base
            if (!requested[k]) requested[k] = '';
        }

        var ord = 0;
        for (var target_id in requested) {
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
                order: ord++
            });
        }
    }

    // Simulate a hashchange event fired when location.hash changes
    var CURRENT_HASH = '';
    function hashchange() {
//        carp('hash: ' + location.hash);
        MAX_REQUEST++;
        $('.loading').removeClass('loading');
        load_by_hash();
    }
    setTimeout( function() {
        try {
            if (location.hash != CURRENT_HASH) {
                CURRENT_HASH = location.hash;
                hashchange();
            }
        } catch(e) { carp(e); }
        setTimeout(arguments.callee, 50);
    }, 50);
})})(jQuery);
