(function($) {
    
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
        var $last_item = $('.gallery-items-sortable .inline-related.last-related');
        var $new_item = $last_item.clone(true);
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
            
            // Unset values
            if ($(this).is('.target_id')) $(this).val('');
            if (/galleryitem_set-\d+-order/.test( this.name )) $(this).val('');
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
            if (val == '') return;
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
    
    function make_gallery_sortable(root) {
        if ( ! root ) root = document;
        var $sortables = $(root).find('.gallery-items-sortable').not('ui-sortable');
        $sortables.children().filter( function() {
            return $(this).find('input.target_id').val();
        }).addClass('sortable-item');
        $sortables.sortable({
            distance: 20,
            items: '.sortable-item',
            update: function(evt, ui) {
                var $target = $( evt.target );
                $target.find('input').filter( function() {
                    return /galleryitem_set-\d+-order/.test( this.name );
                }).each( function(i) {
                    $(this).val( i+1 );
                });
                $target
                .children(':last')     
                .filter(':last').addClass('last-related');
            }
        });
        
        // make sure only the inputs with a selected photo are sortable
        $(root).find('input.target_id').change( function() {
            if ($(this).val()) $(this).closest('.inline-related').addClass('sortable-item');
        });
    }
    make_gallery_sortable();
    
    $(document).bind('content_added', function(evt) {
        $('#gallery_form').removeData('validation').data('validation', check_unique_photo);
        make_gallery_sortable( evt.target );
    });
    
})(jQuery);
