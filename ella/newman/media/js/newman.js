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

    // When something is loaded into an element that has no base view (in urls.js),
    // and the user hits back, we need to reload. But then we don't want to reload again,
    // so keep information about whether we manipulated the content, so we can
    // abstain from reloading if we have not.
    var PAGE_CHANGED = 0;

    // We need to keep track of what URL is loaded into what element
    // and what should be loaded yet. Each element of this array
    // represents one '>'-bounded part of the URL and its state of loadedness.
    var CHAIN = [];

    function Step() {
        this.changed = true;
        this.loaded = {};
    }

    // Take a container and a URL. Give the container the "loading" class,
    // fetch the URL, remove the class and stuff the content into the container.
    function load_content($container, address, step, options) {
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
            step.loaded[ $container.attr('id') ] = address;
            PAGE_CHANGED++;
            if (options && options.next_level) load_by_stepstr(options.next_level);
        });
    }

    // We want location.hash to exactly describe what's on the page.
    // #url means that the result of $.get(url) be loaded into the #content div.
    // #id::url means that the result of $.get(url) be loaded into the #id element.
    // Any number of such specifiers can be concatenated, e.g. #/some/page/#header::/my/header/
    // If URLS[ foo ] is set (in urls.js), and #foo is present,
    // then the function is called given the $target as argument
    // and nothing else is done for this specifier.
    function load_by_stepstr(level) {
        if (CHAIN.hash == undefined) throw "CHAIN.hash undefined.";
        else if (CHAIN.hash.length == 0 && !CHAIN[level]) {
            // We're done
            for (var i = 0; i < CHAIN.length; i++) CHAIN[i].changed = false;
            return;
        }
        var hash = CHAIN.hash;
        var stepstr_len = (hash + '>').indexOf('>');
        var stepstr = hash.substr(0, stepstr_len);
        var step;
        if (CHAIN[level]) step = CHAIN[level];
        else {
            if (level > 0 && !CHAIN[level-1]) throw "Cannot load_by_stepstr("+level+") until done load_by_stepstr("+(level-1)+").";
            step = new Step();
            CHAIN.push(step);
        }
        CHAIN.hash = hash.substr(stepstr_len+1);
        ;;; carp('loading stepstr '+stepstr);

        var loaded = step.loaded;

        // Figure out what should be reloaded and what not by comparing the requested things with the loaded ones.
        var requested = {};
        var specifiers = stepstr.split('#');
        var last_id;
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
            requested[ last_id = $target.attr('id') ] = address;
        }
        var keep_present = (level == 0 || !CHAIN[level-1].changed);
        for (var k in loaded) {
            // if this specifier didn't change, don't load it again
            // but only if the previous level has not changed
            if (loaded[k] == requested[k] && keep_present) {
                delete requested[k];
                continue;
            }
            // if this specifier is no longer present, reload the base
            if (!requested[k]) requested[k] = '';
        }

        var no_request = true;
        for (var _ in requested) no_request = false;
        if (level == 0 || !CHAIN[level-1].changed) if (no_request) step.changed = false;

        if (no_request) {
            load_by_stepstr(level+1);
            return;
        }

        for (var target_id in requested) {
            no_request = false;
            var $target = $('#'+target_id);
            var address = requested[ target_id ];

            // A specially treated specifier. The callback should set up CHAIN[level].loaded properly.
            if (URLS[address]) {
                URLS[address]($target, level);
                continue;
            }

            var load_content_options = {};
            if (target_id == last_id) load_content_options.next_level = level+1;
            load_content($target, address, step, load_content_options);
        }
    }

    function update_content() {
        CHAIN.hash = location.hash.substr(1);
        load_by_stepstr(0);
    }

    // Simulate a hashchange event fired when location.hash changes
    var CURRENT_HASH = '';
    function hashchange() {
//        carp('hash: ' + location.hash);
        update_content();
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
