/*
 * overriding default django method because we dont want to delete
 * already filled authors from the field
 */
function dismissAddAnotherPopup(win, newId, newRepr) {
    // newId and newRepr are expected to have previously been escaped by
    // django.utils.html.escape.
    newId = html_unescape(newId);
    newRepr = html_unescape(newRepr);
    var name = win.name.replace(/___/g, '.');
    var elem = document.getElementById(name);
    if (elem) {
        if (elem.nodeName == 'SELECT') {
            var o = new Option(newRepr, newId);
            elem.options[elem.options.length] = o;
            o.selected = true;
        } else if (elem.nodeName == 'INPUT') {
            if ($(elem).hasClass('vSuggestMultipleFieldAuthor')) {
                elem.value += newId + ',';
                var input = $(elem);
                $.getJSON('/ella/12/' + newId + '/info/', function(data) {
                    input.val(input.val().replace(newId + ',', newId + ':' + data.name + ','));
                })
            } else
                elem.value = newId;
        }
    } else {
        var toId = name + "_to";
        elem = document.getElementById(toId);
        var o = new Option(newRepr, newId);
        SelectBox.add_to_cache(toId, o);
        SelectBox.redisplay(toId);
    }
    win.close();
}
