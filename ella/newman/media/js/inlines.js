/** 
 * Newman inlines.
 * requires: jQuery 1.4.2+, 
 *          gettext() function.
 *          carp(),
 *          str_concat(),
 *          NewmanLib object.
 *
 * provides:
 *          NewmanInline object,
 *          FormHandler object (interface),
 *          GalleryFormHandler object.
 *
 */
var NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER = 1000;

// encapsulate functionality into NewmanInline object
var NewmanInline = function() {
    var me = {};

    // Newman form handler (handles form customised functionality, inline customisations, etc.)
    var registered_handler_objects = [];
    var active_handlers = [];

    function clean_handler_registry() {
        var i;
        var len = registered_handler_objects.length;
        for (i = 0; i < len; i++) {
            registered_handler_objects.pop();
        }

        len = active_handlers.length;
        for (i = 0; i < len; i++) {
            active_handlers.pop();
        }
    }
    me.clean_handler_registry = clean_handler_registry;

    function get_handler_registry() {
        return registered_handler_objects;
    }
    me.get_handler_registry = get_handler_registry;

    function register_form_handler(handler_object) {
        registered_handler_objects.push(handler_object);
    }
    me.register_form_handler = register_form_handler;

    function run_form_handlers() {
        var i;
        var handler;
        for (i = 0; i < registered_handler_objects.length; i++) {
            handler = registered_handler_objects[i];
            if (!handler.is_suitable()) continue;

            active_handlers.push(handler);
            handler.initialize();
            var form = $('.change-form');
            form.bind( 'preset_load_initiated.' + handler.name, handler.preset_load_initiated );
            form.bind( 'preset_load_completed.' + handler.name, handler.preset_load_completed );
        }
    }
    me.run_form_handlers = run_form_handlers;

    return me;
}();

// TODO jednotne rozhrani pro JS osetrovani formularu, customizace plneni formu z presetu atp., osetreni specialit v inlines..
// FormHandler class (used in terms of interface or abstract class)
var __FormHandler = function () {
    // initializes form, register custom event handlers, etc.
    this.init = function (name) {
        if (!name) {
            this.name = 'unset'; // should be set to the name useful for identifying concrete FormHandler object.
        }
    };

    // detects whether form handler should be used or not.
    this.is_suitable = function () {
        return false;
    };

    // called when preset is being loaded into the form
    this.preset_load_initiated = function (evt, preset) {
    };

    // called when preset loading completed
    this.preset_load_completed = function (evt) {
    };

    this.validate_form = function ($form) {
        return true;
    };

    // handles adding of new inline item
    this.add_inline_item = function (evt) {
    };

    return this;
};
var FormHandler = to_class(__FormHandler);

(function($) {
    
    function add_inline($template, no) {
        $template.before(
            $template.html()
            .replace(/<!--|-->/g, '')
            .replace(/-#-/g, '--')
            .replace(/__NO__/g, no)
        ).parent().trigger('content_added');
        carp('add_inline: content_added triggered');
    }
    $('.remove-inline-button').live('click', function(evt) {
        if (evt.button != 0) return;
        $(this).closest('.inline-item').remove();
    });

    function remove_inlineadmin_element_value(element_selector, name_tail, new_value) {
        var nval = '';
        if (new_value) {
            nval = new_value;
        }
        var regex = new RegExp(name_tail);
        // removes IDs created when preset is loaded
        function remove_element_value() {
            if ( regex.test(this.name) ) {
                $(this).val(nval);
                //carp('Blanking value [' , nval , '] for input with name: ' , this.name);
            }
        }

        $(element_selector).each(
            remove_element_value // callback
        );
    }
    NewmanInline.remove_inlineadmin_element_value = remove_inlineadmin_element_value;

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
    $(document).bind('preset_load_completed', init_main_category_button);

    // Comments (ellacomments)
    function remove_ellacomments_ids() {
        remove_inlineadmin_element_value(
            'input[name^=ellacomments-commentoptionsobject-target_ct-target_id-0-]',
            'id'
        );
    }
    $('.change-form').bind('preset_load_completed', remove_ellacomments_ids);
    carp('remove_ellacomments_ids bind');

    
})(jQuery);


// Gallery inlines
//var GalleryFormHandler = Object.beget(FormHandler);
var __GalleryFormHandler = function () {
    this.super_class = FormHandler;

    this.init = function() {
        FormHandler.call(this, 'gallery');
    };

    this.is_suitable = function () {
        var sortables = $(document).find('.gallery-items-sortable').not('ui-sortable');
        if (sortables.length == 0) {
            return false;
        }
        return true;
    };

    // called when preset is being loaded into the form
    this.preset_load_initiated = function (evt, preset) {
        carp('Preset load initiated ' + preset);
    };

    // called when preset loading completed
    this.preset_load_completed = function (evt) {
        carp('Preset load completed ' + evt);
    };

    return this;
};
var GalleryFormHandler = to_class(__GalleryFormHandler);

var __TestFormHandler = function() {
    this.super_class = FormHandler;

    this.init = function() {
        FormHandler.call(this, 'testhandler');
    };

    function is_suitable() {
        var found = $(document).find('.js-poll-question-container');
        return found.length != 0;
    }
    this.is_suitable = is_suitable;

    function preset_load_initiated(evt, preset) {
        //alert('TEST!');
    }
    this.preset_load_initiated = preset_load_initiated;

    return this;
};
var TestFormHandler = to_class(__TestFormHandler);

(function($) {
    //// gallery items
    function max_order() {
        return Math.max.apply(this, $.map( $.makeArray( $('.gallery-items-sortable input.item-order') ), function(e) {
            var n = new Number( $(e).val() );
            if (n > 0) return n;
            else return 0;
        }));
    }

    function delete_unsaved_gallery_item(evt) {
        var $item = $( evt.target ).closest('.sortable-item');
        if ($item.length > 0) {
            $item.remove();
            gallery_inlines_recount_ids();
        }
    }

    function gallery_recount_ids_and_names_callback(element, counter) {
        var ITEM_SET = 'galleryitem_set-';
        var no_re = /galleryitem_set-\d+-/;
        var $element = $(element);
        if (no_re.test( element.name )) {
            var newname = element.name.replace(no_re, str_concat(ITEM_SET, counter,'-') );
            $element.attr('name', newname);
        }
        if (no_re.test( element.id )) {
            var newid = element.id.replace(no_re, str_concat(ITEM_SET, counter,'-') );
            $element.attr('id', newid);
            if (/\-DELETE/.test(newid)) {
                $element.unbind('click', delete_unsaved_gallery_item);
                $element.bind('click', delete_unsaved_gallery_item);
            }
        }
        if (no_re.test( $element.attr('for') )) {
            var newid = $element.attr('for').replace(no_re, str_concat(ITEM_SET, counter,'-') );
            $element.attr('for', newid);
        }
    }

    function gallery_inlines_recount_ids() {
        var $items = $('.gallery-items-sortable .inline-related');
        var no_items = $('.gallery-items-sortable input.target_id').length;
        var counter = 0;
        $items.each(
            function() {
                $(this).find('*').each( 
                    function() {
                        gallery_recount_ids_and_names_callback(this, counter);
                    }
                )
                counter ++;
            }
        );
    }
    
    function add_gallery_item(evt) {
        if (evt && evt.button != 0) return;
        var $last_item = $('.gallery-items-sortable .inline-related:last');
        var $new_item = $last_item.clone(true);
        var no_items = $('.gallery-items-sortable input.target_id').length;
        $last_item.removeClass('last-related');
        
        var no_re = /galleryitem_set-\d+-/;
        $new_item.find('*').each( function() {
            var ITEM_SET = 'galleryitem_set-';
            var $this = $(this);
            if (no_re.test( this.name )) {
                var newname = this.name.replace(no_re, str_concat(ITEM_SET,no_items,'-') );
                $this.attr('name', newname);
            }
            if (no_re.test( this.id )) {
                var newid = this.id.replace(no_re, str_concat(ITEM_SET,no_items,'-') );
                $this.attr('id', newid);
                if (/\-DELETE/.test(newid)) {
                    $this.unbind('click', delete_unsaved_gallery_item);
                    $this.bind('click', delete_unsaved_gallery_item);
                }
            }
            if (no_re.test( $this.attr('for') )) {
                var newid = $this.attr('for').replace(no_re, str_concat(ITEM_SET,no_items,'-') );
                $this.attr('for', newid);
            }
           
            // init values
            if ($this.is('.target_id' )) $(this).val('');
            if ($this.is('img.thumb'  )) $(this).attr({src:'', alt:''});
            if ($this.is('.item-order')) {
                // count order
                var degree = get_gallery_ordering_degree( $this );
                var ord = max_order() + (1 * degree);
                $this.val(ord);
            }
        });
        $new_item.find('h4').remove();
        $new_item.insertAfter( $last_item );
        var $no_items = $('#id_galleryitem_set-TOTAL_FORMS');
        $no_items.val( no_items+1 );
    }
    $('.add-gallery-item-button').live('click', add_gallery_item);

    // make target_id fields not editable
    function disable_gallery_target_id() {
        function disable_field() {
            var $target_field = $(this).find('input.target_id');
            //$target_field.attr('disabled', true); // doesn't worked out
            $target_field.hide();
        }

        var $filter = $('.gallery-items-sortable .inline-related').each(
            disable_field
        );
    }
    NewmanInline.disable_gallery_target_id = disable_gallery_target_id;

    // check for unique photo ID
    function check_gallery_changeform( $form ) {
        function unhighlight_duplicates(evt) {
            evt.data.$elems.unbind('click', unhighlight_duplicates);
            evt.data.$elems.removeClass(ITEM_ERROR_CLASS);
        }

        var used_ids = {};
        var rv = true;
        var ITEM_ERROR_CLASS = 'gallery-item-error';

        $form.find('.gallery-item .target_id').each( function() {
            if (rv == false) return;
            var val = $(this).val();
            if (val == '') return;
            var $gallery_item = $(this).closest('.gallery-item');
            if ($gallery_item.hasClass(ITEM_ERROR_CLASS)) {
                $gallery_item.removeClass(ITEM_ERROR_CLASS);
            }
            if (val in used_ids) {

                // if item is marked for delete, ommit this item
                var $delete_input = $gallery_item.children('.delete').find('input');
                var $previous_delete_input = $('#' + used_ids[ val ]).closest('.gallery-item').children('.delete').find('input');
                if ($delete_input.attr('checked') || $previous_delete_input.attr('checked')) {
                    return;
                }
                // highlight red
                var $duplicates = $(str_concat('#' , used_ids[ val ], ',', '#' , this.id)).closest('.gallery-item');
                $duplicates.bind('click', {$elems: $duplicates}, unhighlight_duplicates);
                $duplicates.addClass(ITEM_ERROR_CLASS);
                alert(gettext('Duplicate photo'));
                $(this).focus();
                rv = false;
                return;
            }
            used_ids[ val ] = this.id;
        });

        if (rv) {
            var $filter = $('.gallery-items-sortable .inline-related').filter(
                function() {
                    var $res = $(this).find('input.target_id');
                    var res = $res.val();
                    return res == '';
                }
            );
            $filter.each(
                function() {
                    $(this).find(':input.target_ct,:input.item-order').val('');
                }
            );
        }

        disable_gallery_target_id();
        
        return rv;
    }
    $('#gallery_form').data('validation', check_gallery_changeform);
    NewmanInline.check_gallery_changeform = check_gallery_changeform;
    NewmanInline.gallery_ordering_modified = false;

    function gallery_ordering_recount() {
        NewmanLib.register_post_submit_callback_once(function(submit_succeeded) {
            if (!submit_succeeded) {
                carp('NewmanInline.gallery_ordering_modified not changed');
                return;
            }
            NewmanInline.gallery_ordering_modified = false;
            carp('NewmanInline.gallery_ordering_modified = false;');
        });

        // ordering-number magic to avoid problems with saving GalleryItems with changed ordering (unique key collision)
        var $form = $('#gallery_form');
        if (NewmanInline.gallery_ordering_modified) {
            carp('GalleryItems won\'t be recounted.(reason: already recounted)');
            return;
        }
        $form.find('.gallery-item .item-order').each( function() {
            if (!this.value) return;
            var value = parseInt(this.value);
            var multiplier = 1;
            if (value >= 1 && value <= 99) {
                multiplier = NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER;
            } else if (value >= NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER && value <= (99 * NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER)) {
                multiplier = 1.0 / NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER;
            }
            var res = Math.floor(Number(value) * multiplier);// force res to be a whole number
            carp('Recounting ' , value , ' to ' , res , ' for element ' , this);
            this.value = res.toString();
            NewmanInline.gallery_ordering_modified = true;
            carp('GalleryItems recounted');
        });
    }

    function get_gallery_ordering_degree($element) {
        var value = parseInt( $element.val() );
        var degree = 1;
        if (value / NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER >= 1.0) {
            degree = NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER;
        }
        return degree;
    }

    function gallery_recount_ordering($target) {
        var degree = 1;
        var ord;
        $target.find('input.item-order').each( function(i) {
            // get actual order degree
            if (i == 0) {
                degree = get_gallery_ordering_degree( $(this) );
            }
            ord = (i + 1) * degree;
            $(this).val( ord ).change();
            // $(this).siblings('h4:first').find('span:first').text( ord ); // hide ordering
            var $del = $(this).siblings('.delete-item:first');
            if ($del.hasClass('noscreen')) {
                $del.removeClass('noscreen');
            }
        });
        $target.children().removeClass('last-related');
        $target.children(':last').addClass('last-related');
    }

    function gallery_sortable_update_callback(evt, ui) {
        var $target = $( evt.target );
        gallery_recount_ordering($target);
    }

    function remove_gallery_item_ids() {
        // remove ids (input with name="galleryitem_set-0-id")
        // remove gallery (input with name="galleryitem_set-0-gallery")
        NewmanInline.remove_inlineadmin_element_value(
            '.gallery-items-sortable input[name^=galleryitem_set-]',
            '-id$'
        );
        NewmanInline.remove_inlineadmin_element_value(
            '.gallery-items-sortable input[name^=galleryitem_set-]',
            'gallery$'
        );
    }
    
    function init_gallery(root) {
        if ( ! root ) root = document;
        var $sortables = $(root).find('.gallery-items-sortable').not('ui-sortable');
        if ($sortables.length == 0) return;
        $sortables.children().filter( 
            function() {
                var $target_id = $(this).find('input.target_id');
                return $target_id.length != 0;
            }
        ).addClass('sortable-item');
        $sortables.sortable({
            distance: 20,
            items: '.sortable-item',
            update: gallery_sortable_update_callback
        });
        // recount before save
        NewmanLib.register_pre_submit_callback(gallery_ordering_recount);
        
        // make sure only the inputs with a selected photo are sortable
        $(root).find('input.target_id').change( function() {
            if ($(this).val()) {
                $(this).closest('.inline-related').addClass('sortable-item');
            }
        });
        
        // initialize order for empty listing
        var degree = 0;
        $sortables.find('.item-order').each( function() {
            if (degree === 0) {
                degree = get_gallery_ordering_degree( $(this) );
            }
            if ( ! $(this).val() ) $(this).val( 
                (max_order() + 1) * degree 
            );
        });
        
        // update the preview thumbs and headings
        function update_gallery_item_thumbnail() {
            var $input = $(this);
            var id = $input.val();
            
            var $img     = $input.siblings('img:first');
            var $heading = $input.siblings('h4:first');
            if ($heading.length == 0) {
                $heading = $('<h4><span></span> <span></span></h4>').insertAfter($img);
            }
            $img.attr({
                src: '',
                alt: ''
            });
            $heading.find('span').empty();
           
            // remove items with deleted id
            if (!id) {
                $heading.remove();
                return;
            }
            
            $.ajax({
                url: str_concat(BASE_PATH , '/photos/photo/' , id , '/thumb/'),
                success: function(response_text) {
                    var res;
                    try { res = JSON.parse(response_text); }
                    catch(e) {
                        carp('thumb update error: successful response container unexpected text: ' , response_text);
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
                    //$heading.find('span:first').text( order ); // don't show ordering value
                    $heading.find('span:eq(1)').text( title );

                    // enable delete fake button
                    var $del = $input.siblings('.delete-item:first');
                    if ($del.hasClass('noscreen')) {
                        $del.removeClass('noscreen');
                    }
                    gallery_inlines_recount_ids();
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
        $('#gallery_form').bind('preset_load_initiated.gallery', function(evt, preset) {
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
            remove_gallery_item_ids();
            gallery_recount_ordering( $('.gallery-items-sortable') );
        });

    }
    init_gallery();
    carp('CALLED init_gallery');
    
    $(document).bind('content_added', function(evt) {
        $('#gallery_form').removeData('validation').data('validation', check_gallery_changeform);
        init_gallery( evt.target );
    });
})(jQuery);

//ommit registration when running in nosetests environment
if (typeof nosejs !== "undefined") {
} else {
    NewmanInline.register_form_handler( new GalleryFormHandler() );
    NewmanInline.register_form_handler( new TestFormHandler() );

    // Run relevant form handlers.
    NewmanInline.run_form_handlers();
}
