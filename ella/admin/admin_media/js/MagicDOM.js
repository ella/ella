var MagicDOM = {
    isDict: function(o) {
        var str_repr = String(o);
        return str_repr.indexOf(" Object") != -1;
    },

    createDOM: function(name, attrs) {
        var i=0, attr;
        var elm = document.createElement(name);

        var first_attr = attrs[0];
        if(MagicDOM.isDict(attrs[i])) {
            for(k in first_attr) {
                attr = first_attr[k];
                if(k == "style")
                    elm.style.cssText = attr;
                else if(k == "class" || k == 'className')
                    elm.className = attr;
                else {
                    elm.setAttribute(k, attr);
                }
            }
            i++;
        }

        if(first_attr == null)
            i = 1;

        for(var j=i; j < attrs.length; j++) {
            var attr = attrs[j];
            if(attr) {
                var type = typeof(attr);
                if(type == 'string' || type == 'number')
                    attr = TN(attr);
                elm.appendChild(attr);
            }
        }

        return elm;
    },

    _createDomShortcuts: function() {
        var elms = [
                "ul", "li", "td", "tr", "th",
                "tbody", "table", "input", "span", "b",
                "a", "div", "img", "button", "h1",
                "h2", "h3", "br", "textarea", "form",
                "p", "select", "option", "optgroup", "iframe", "script",
                "center", "dl", "dt", "dd", "small",
                "pre"
        ];
        var extends_win = function(elm) {
            window[elm.toUpperCase()] = function() {
                return MagicDOM.createDOM.apply(null, [elm, arguments]);
            };
        }

        for(var i=0; i < elms.length; i++)
            extends_win(elms[i]);

        TN = function(text) { return document.createTextNode(text) };
    }
}

MagicDOM._createDomShortcuts();
