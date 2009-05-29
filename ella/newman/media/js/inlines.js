function add_inline($template, no) {
    $template.before(
        $template.html()
        .replace(/<!--|-->/g, '')
        .replace(/-#-/g, '--')
        .replace(/__NO__/g, no)
    ).parent().trigger('content_added');
}
$('.remove-inline-button').live('click', function(evt) {
    if (evt.button != 0) return;
    $(this).closest('.inline-item').remove();
});

//// listings
$('.add-listing-button').live('click', function(evt) {
    if (evt.button != 0) return;
    var no = $('.listing-row').length + 1;
    var $template = $('.listing-row-template:first');
    add_inline($template, no);
});

//// gallery items
$('.add-gallery-item-button').live('click', function(evt) {
    if (evt.button != 0) return;
    var $last_item = $('.inline-related.last-related fieldset.gallery-item:last');
    var $new_item = $last_item.clone();
    $last_item.removeClass('last-related');
    $new_item.find('*').each( function() {
        var no_re = /galleryitem_set-(\d+)-/g;
        var oldno, newno;
        if (oldno = no_re.exec( this.name )) {
            newno = new Number(oldno[1]) + 1;
            var newname = this.name.replace(no_re, 'galleryitem_set-'+newno+'-');
            $(this).attr({name: newname});
        }
        if (oldno = no_re.exec( this.id )) {
            newno = new Number(oldno[1]) + 1;
            var newid = this.id.replace(no_re, 'galleryitem_set-'+newno+'-');
            $(this).attr({id: newid});
        }
    });
    $new_item.insertAfter( $last_item );
    var $no_items = $('#id_galleryitem_set-TOTAL_FORMS');
    $no_items.val(
        new Number($no_items.val()) + 1
    );
});

// check for unique photo ID
function check_unique_photo( $form ) {
    var used_ids = {};
    var rv = true;
    $form.find('.gallery-item .target_id').each( function() {
        if (rv == false) return;
        var val = $(this).val();
        if (val == undefined) return;
        if (used_ids[ val ]) {
            alert(gettext('Duplicate photo')+' #'+val);
            $(this).focus();
            rv = false;
            return;
        }
        used_ids[ val ] = 1;
    });
    return rv;
}
$('#gallery_form').data('validation', check_unique_photo);
$(document).bind('content_added', function(evt) {
    $('#gallery_form').removeData('validation').data('validation', check_unique_photo);
});
