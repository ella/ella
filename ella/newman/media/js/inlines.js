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
    function add_listing(evt) {
        if (evt && evt.button != 0) return;
        var no = $('.listing-row').length + 1;
        var $template = $('.listing-row-template:first');
        add_inline($template, no);
    }
    $('.add-listing-button').live('click', add_listing);

    //// choices (Polls application)
    function add_choice(evt) {
        if (evt && evt.button != 0) return;
        var no = $('.choice-row').length + 1;
        var $template = $('.choice-row-template:first');
        add_inline($template, no);
    }
    $('.add-choice-button').live('click', add_choice);
    
    // create desired inputs for loaded preset
    function add_listings_for_preset(evt, preset) {
        var $form = $( evt.target );
        var no_items = $form.find('.listing-row.inline-item').length;
        var desired_no = 0;
        var $template = $form.find('.listing-row-template:first');
        if ($template.length == 0) {
            carp('add_listings_for_preset: template not found');
            return;
        }
        for (var i = 0; i < preset.data.length; i++) {
            var o = preset.data[i];
            if (o.name == 'placement_set-0-listings') desired_no++;
        }
        // add listings if necessary
        for (var i = no_items; i < desired_no; i++) {
            add_inline($template, i+1);
        }
        // remove listings if necessary
        for (var i = no_items; i > desired_no; i--) {
            $('.listing-row.inline-item:last').remove();
        }
    }
    $('.change-form:has(.add-listing-button)').bind('preset_load_initiated.listing', add_listings_for_preset);
    $(document).bind('content_added', function(evt) {
        $( evt.target ).find('.change-form:has(.add-listing-button)')
        .unbind('preset_load_initiated.listing')
        .bind('preset_load_initiated.listing', add_listings_for_preset);
    });
    
    // main category button
    $('.js-placement-main-category').live('click', function(evt) {
        if ($('#id_category').val().length <= 1) return;
        
        var      main_category_input = $('#id_category_suggest'                ).get(0);
        var placement_category_input = $('#id_placement_set-0-category_suggest').get(0);
        
        GenericSuggestLib.copy(main_category_input, placement_category_input);
        
        if ($('.listing-row').length == 0) {
            add_listing();
            var listing_category_input = $('#id_category_1_suggest').get(0);
            GenericSuggestLib.copy(main_category_input, listing_category_input);
        }
    });
    function init_main_category_button() {
        function _() {
            var cat = $('#id_category').val() + '';
            if (cat.length <= 1) {
                $('.js-placement-main-category').closest('p').hide();
            }
            else {
                $('.js-placement-main-category').closest('p').show();
            }
        }
        _();
        $('#id_category').unbind('change', _).bind('change', _);
    }
    init_main_category_button();
    $(document).bind('content_added', init_main_category_button);

    //// gallery items
    function max_order() {
        return Math.max.apply(this, $.map( $.makeArray( $('.gallery-items-sortable input.item-order') ), function(e) {
            var n = new Number( $(e).val() );
            if (n > 0) return n;
            else return 0;
        }));
    }
    
    function add_gallery_item(evt) {
        if (evt && evt.button != 0) return;
        var $last_item = $('.gallery-items-sortable .inline-related:last');
        var $new_item = $last_item.clone(true);
        var no_items = $('.gallery-items-sortable input.target_id').length;
        $last_item.removeClass('last-related');
        
        var no_re = /galleryitem_set-\d+-/;
        $new_item.find('*').each( function() {
            if (no_re.test( this.name )) {
                var newname = this.name.replace(no_re, 'galleryitem_set-'+no_items+'-');
                $(this).attr({name: newname});
            }
            if (no_re.test( this.id )) {
                var newid = this.id.replace(no_re, 'galleryitem_set-'+no_items+'-');
                $(this).attr({id: newid});
            }
            
            // init values
            if ($(this).is('.target_id' )) $(this).val('');
            if ($(this).is('.item-order')) $(this).val( max_order() + 1 );
            if ($(this).is('img.thumb'  )) $(this).attr({src:'', alt:''});
        });
        $new_item.find('h4').remove();
        $new_item.insertAfter( $last_item );
        var $no_items = $('#id_galleryitem_set-TOTAL_FORMS');
        $no_items.val( no_items+1 );
    }
    $('.add-gallery-item-button').live('click', add_gallery_item);

    // check for unique photo ID
    function check_gallery_changeform( $form ) {
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
        
        // If the form validates, delete values from empty inputs
        if (rv) {
            $('.gallery-items-sortable .inline-related').filter( function() {
                return $(this).find('input.target_id').val() == ''
            }).each( function() {
                $(this).find(':input.target_ct,:input.item-order').val('');
            });
        }
        
        return rv;
    }
    $('#gallery_form').data('validation', check_gallery_changeform);
    
    function init_gallery(root) {
        if ( ! root ) root = document;
        var $sortables = $(root).find('.gallery-items-sortable').not('ui-sortable');
        if ($sortables.length == 0) return;
        $sortables.children().filter( function() {
            return $(this).find('input.target_id').val();
        }).addClass('sortable-item');
        $sortables.sortable({
            distance: 20,
            items: '.sortable-item',
            update: function(evt, ui) {
                var $target = $( evt.target );
                $target.find('input.item-order').each( function(i) {
                    var ord = i+1;
                    $(this).val( ord ).change();
                    $(this).siblings('h4:first').find('span:first').text( ord );
                });
                $target.children().removeClass('last-related');
                $target.children(':last').addClass('last-related');
            }
        });
        
        // make sure only the inputs with a selected photo are sortable
        $(root).find('input.target_id').change( function() {
            if ($(this).val()) $(this).closest('.inline-related').addClass('sortable-item');
        });
        
        // initialize order for empty listing
        $sortables.find('.item-order').each( function() {
            if ( ! $(this).val() ) $(this).val( max_order() + 1 );
        });
        
        // update the preview thumbs and headings
        function update_gallery_item_thumbnail() {
            var $input = $(this);
            var id = $input.val();
            
            var $img     = $input.siblings('img:first');
            var $heading = $input.siblings('h4:first');
            if ($heading.length == 0) {
                $heading = $('<h4>#<span></span> &mdash; <span></span></h4>').insertAfter($img);
            }
            $img.attr({
                src: '',
                alt: ''
            });
            $heading.find('span').empty();
            
            if (!id) {
                $heading.remove();
                return;
            }
            
            $.ajax({
                url: BASE_PATH + '/photos/photo/' + id + '/thumb/',
                success: function(response_text) {
                    var res;
                    try { res = JSON.parse(response_text); }
                    catch(e) {
                        carp('thumb update error: successful response container unexpected text: ' + response_text);
                    }
                    
                    // thumbnail
                    var thumb_url = res.data.thumb_url;
                    var title     = res.data.title;
                    $img.attr({
                        src: thumb_url,
                        alt: title
                    });
                    
                    // heading
                    var order = $( '#' + $input.attr('id').replace(/-target_id$/, '-order') ).val();
                    $heading.find('span:first').text( order );
                    $heading.find('span:eq(1)').text( title );
                },
            });
        }
        $(root).find('input.target_id').not('.js-updates-thumb').addClass('js-updates-thumb').change( update_gallery_item_thumbnail );
        
        // add a new empty gallery item
        $(root).find('input.target_id').not('.js-adds-empty').addClass('js-adds-empty').change( function() {
            if ($('.gallery-item input.target_id').filter( function() { return ! $(this).val(); } ).length == 0) {
                add_gallery_item();
            }
        });
        
        // create desired input rows for loaded preset
        $('#gallery_form').bind('preset_load_initiated', function(evt, preset) {
            var desired_no;
            for (var i = 0; i < preset.data.length; i++) {
                var o = preset.data[i];
                if (o.name == 'galleryitem_set-TOTAL_FORMS') {
                    desired_no = new Number( o.value );
                }
            }
            var no_items = $('.gallery-items-sortable input.target_id').length;
            // add gallery items if necessary
            for (var i = no_items; i < desired_no; i++) {
                add_gallery_item();
            }
            // remove gallery items if necessary
            for (var i = no_items; i > desired_no; i--) {
                $('.gallery-items-sortable .inline-related:last').remove();
            }
            // reset the fields
            var $rows = $('.gallery-items-sortable .inline-related');
            $rows.find('input.target_id,input.item-order').val('');
            $rows.find('img.thumb').attr({src:'', alt:''});
            $rows.find('h4').remove();
        })
        // and get their thumbnails
        .bind('preset_load_completed', function(evt) {
            $('.gallery-items-sortable input.target_id').each( update_gallery_item_thumbnail );
            init_gallery( evt.target );
        });
    }
    init_gallery();
    
    $(document).bind('content_added', function(evt) {
        $('#gallery_form').removeData('validation').data('validation', check_gallery_changeform);
        init_gallery( evt.target );
    });
    
})(jQuery);
