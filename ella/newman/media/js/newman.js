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

    // When something is loaded into an element that has no base view (in urls.js),
    // and the user hits back, we need to reload. But then we don't want to reload again,
    // so keep information about whether we manipulated the content, so we can
    // abstain from reloading if we have not.
    var PAGE_CHANGED = 0;

    // Take a container and a URL. Give the container the "loading" class,
    // fetch the URL, remove the class and stuff the content into the container.
    function load_content($container, address) {
        ;;; carp('loading '+address+' into '+$container.attr('id'));

        // An empty address means we should revert to the base state.
        // If one is not set up for the given container, reload the whole page.
        if (address.length == 0) {
            if (BASES[ $container.attr('id') ]) {
                address = BASES[ $container.attr('id') ];
            } else {
                if (PAGE_CHANGED) location.reload();
                return;
            }
        }

        var url = $('<a>').attr('href', address).get(0).href;
        if ($container && $container.length && $container.jquery) { } else {
            carp('Could not insert into container:');
            carp($container);
            return;
        }
        $container.addClass('loading');
        $.get(url, function(data) {
            $container.removeClass('loading').html(data);
            LOADED_URLS[ $container.attr('id') ] = address;
            PAGE_CHANGED++;
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

        // Figure out what should be reloaded and what not by comparing the requested things with the loaded ones.
        var requested = {};
        var specifiers = hash.split('#');
        for (var i = 0; i < specifiers.length; i++) {
            var spec = specifiers[ i ];
            var address = spec;
            var $target = $CONTENT;
            if (spec.match(/^([-\w]+)::(.*)/)) {
                var id  = RegExp.$1;
                address = RegExp.$2;
                $target = $('#' + id);
                if (!$target || $target.length == 0) {
                    carp('Could not find #'+id);
                    continue;
                }
            }
            requested[ $target.attr('id') ] = address;
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

        for (var target_id in requested) {
            var $target = $('#'+target_id);
            var address = requested[ target_id ];

            // A specially treated specifier. The callback should set up LOADED_URLS properly.
            if (URLS[address]) {
                URLS[address]($target);
                continue;
            }

            load_content($target, address);
        }
    }

    // Simulate a hashchange event fired when location.hash changes
    var CURRENT_HASH = '';
    function hashchange() {
//        carp('hash: ' + location.hash);
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
