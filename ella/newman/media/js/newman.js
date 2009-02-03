( function($) { $(document).ready( function() {

    // Debugging tools
    ;;; function alert_dump(obj, name) {
    ;;;     var s = name ? name + ":\n" : '';
    ;;;     for (var i in obj) s += i + ': ' + obj[i] + "\n";
    ;;;     alert(s);
    ;;; }

    // Store the #content div, so we need not always mine it from the DOM.
    var $CONTENT = $('#content');

    // Load some content to the #content div.
    // The argument is an object with these fields:
    // html (exclusive with url): the HTML to put there;
    // url (exclusive with html): the URL from which to load the contents;
    // data (optional; requires url): data to send along with the XMLHttpRequest to the server;
    // method (optional; requires url): type of the request: GET or POST;
    function cnt_switch(arg) {
        function inject(data) {
            $CONTENT.html(data);
        }
        if (!arg) return;
        if (arg.url) {
            var options = {
                success: inject,
                url: arg.url
            };
            options.type = (arg.method || 'GET').toUpperCase();
            if (arg.data) options.data = arg.data;
            $.ajax(options);
            return;
        }
        if (arg.html) {
            inject(html);
            return;
        }
    }

    // Loads a link's href or a form's action to the #content
    function autoajax() {
        if (this.href) {
            cnt_switch({ url: this.href });
            return false;
        }
        var $form = $(this).closest('form');
        if (!$form) throw("Cannot autoajax this element: no encapsulating form and no href attribute found.");
        cnt_switch({ url: $form.attr('action'), method: $form.attr('method') });
        return false;
    }
    $('a.autoajax,:input.autoajax').live('click', autoajax);
/*    $('#change_password_link').click( function() {
        cnt_switch({ url: this.href });
        return false;
    });*/
})})(jQuery);
