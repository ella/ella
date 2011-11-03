function handle_table(evt, toolbar) {
    var headers = prompt(gettext('Enter column headings (split by ";"):'));
    var rowCount = prompt(gettext('Row count (excluding header):', 2));

    if (! headers || ! rowCount) return;

    function makeRow(length, content) {
        var contentArr = [];
        while (length--) { contentArr.push(content); }
        return contentArr.join(' | ') + "\n";   
    }

    headers = headers.split(';');
    source = [
        headers.join(' | '),
        '\n',
        makeRow(headers.length, new Array(gettext('REPLACE').length + 1).join('-')),
        new Array(parseInt(rowCount) + 1).join(makeRow(headers.length, gettext('REPLACE'))),
    ].join('');
 
    toolbar.selection_handler.replace_selection(source);
    toolbar.trigger_delayed_preview();
}

toolbarButtonRegister.addButton(gettext('Table'), 'table', handle_table);