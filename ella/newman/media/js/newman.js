( function($) { $(document).ready( function() {

    // Debugging tools
    ;;; function alert_dump(obj, name) {
    ;;;     var s = name ? name + ":\n" : '';
    ;;;     for (var i in obj) s += i + ': ' + obj[i] + "\n";
    ;;;     alert(s);
    ;;; }

    // Store the #content div, so we need not always mine it from the DOM.
    var $CONTENT = $('#content');

    // We want location.hash to exactly describe what's on the page.
    // #url means that the result of $.get(url) be loaded into the #content div.
    // #id::url means that the result of $.get(url) be loaded into the #id element.
    // Any number of such specifiers can be concatenated, e.g. #/some/page/#header::/my/header/
    function load_by_hash() {
        var hash = location.hash.substr(1);
        if (hash.length == 0) {
            // TODO: A smarter reset
            location.reload();
        }
        var specifiers = hash.split('#');
        for (var i = 0; i < specifiers.length; i++) {
            var spec = specifiers[ i ];
            if (spec.length == 0) continue;
            var address = spec;
            var $target = $CONTENT;
            if (spec.match(/^([-\w]+)::(.+)/)) {
                var id  = RegExp.$1;
                address = RegExp.$2;
                $target = $('#' + id);
                if (!$target || $target.length == 0) {
                    console.log('Could not find #'+id);
                    continue;
                }
            }
            if (URLS[address]) {
                URLS[address]($target);
                continue;
            }
            var url = $('<a>').attr('href', address).get(0).href;
            $.get(url, function(data) {
                $target.html(data);
            });
        }
    }

    // Simulate a hashchange event fired when location.hash changes
    var CURRENT_HASH = '';
    function hashchange() {
        console.log('hash: ' + location.hash);
        load_by_hash();
    }
    setTimeout( function() {
        try {
            if (location.hash != CURRENT_HASH) {
                CURRENT_HASH = location.hash;
                hashchange();
            }
        } catch(e) { console.log(e); }
        setTimeout(arguments.callee, 50);
    }, 50);
})})(jQuery);
