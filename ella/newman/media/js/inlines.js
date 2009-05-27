$('.add-inline-button').live('click', function(evt) {
    if (evt.button != 0) return;
    var no = $('.listing-row').length + 1;
    var $template = $('.listing-row-template:first');
    $template.before(
        $template.html()
        .replace(/<!--|-->/g, '')
        .replace(/-#-/g, '--')
        .replace(/__NO__/g, no)
    ).parent().trigger('content_added');
});
$('.remove-inline-button').live('click', function(evt) {
    if (evt.button != 0) return;
    $(this).closest('.listing-row').remove();
});
