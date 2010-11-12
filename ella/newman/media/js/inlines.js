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

var log_inline = new LoggingLib('INLINE:', true);

// encapsulate functionality into NewmanInline object
var __NewmanInline = function() {
    // Newman form handler (handles form customised functionality, inline customisations, etc.)
    this.init = function() {
        this.registered_handler_objects = [];
    };

    this.clean_handler_registry = function () {
        var i;
        var len = this.registered_handler_objects.length;
        for (i = 0; i < len; i++) {
            this.registered_handler_objects.pop();
        }
    };

    this.get_handler_registry = function () {
        return this.registered_handler_objects;
    };

    this.register_form_handler = function (handler_object) {
        this.registered_handler_objects.push(handler_object);
    };

    this.run_form_handlers = function () {
        var i;
        var handler;
        var len = this.registered_handler_objects.length;
        var $doc = $(document);
        //log_inline.log('Choosing form handlers...');
        for (i = 0; i < len; i++) {
            handler = this.registered_handler_objects[i];
            if (!handler.is_suitable(document, $doc)) continue;

            //log_inline.log('Handler:', handler);
            try {
                handler.handle_form(document, $doc);
            } catch (e) {
                log_inline.log('Error occured during handle_form() call.', e.toString());
            }
            var form = $('.change-form');
            form.bind( 
                'preset_load_initiated.' + handler.name, 
                this_decorator(handler, handler.preset_load_initiated) 
            );
            form.bind( 
                'preset_load_completed.' + handler.name, 
                this_decorator(handler, handler.preset_load_completed)
            );
        }
        //log_inline.log('Form handlers done.');
        return true;
    };

    return this;
};
var NewmanInline = function () {
    var cls = to_class(__NewmanInline);
    return new cls();
}();

// TODO jednotne rozhrani pro JS osetrovani formularu, customizace plneni formu z presetu atp., osetreni specialit v inlines..
// FormHandler class (used in terms of interface or abstract class)
var __FormHandler = function () {
    // constructor
    this.init = function (name) {
        if (!name) {
            this.name = 'unset'; // should be set to the name useful for identifying concrete FormHandler object.
        } else {
            this.name = name;
        }
    };

    // initializes form, register custom event handlers, etc.
    this.handle_form = function (document_dom_element, $document) { };

    // detects whether form handler should be used or not.
    this.is_suitable = function (document_dom_element, $document) {
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

    // handles inline item addition
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
        //log_inline.log('add_inline: content_added triggered');
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
                //log_inline.log('Blanking value [' , nval , '] for input with name: ' , this.name);
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
            log_inline.log('add_listings_for_preset: template not found');
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
    //log_inline.log('remove_ellacomments_ids bind');

    
})(jQuery);

// Gallery inlines
var __GalleryFormHandler = function () {
    this.super_class = FormHandler;

    this.init = function() {
        FormHandler.call(this, 'gallery');
        this.$document = null;
        this.document = null;
        this.gallery_ordering_modified = false;
    };

    this.handle_form = function (document_dom_element, $document) {
        this.$document = $document;
        this.document = document_dom_element;
        //this.$doc.unbind('content_added', this.document_content_added_handler);
        //this.$doc.bind('content_added', {instance: this}, this.document_content_added_handler);
        this.document_content_added_handler();
        $('#gallery_form').data('validation', this_decorator(this, this.check_gallery_changeform) );
        $('.add-gallery-item-button').live('click', this_decorator(this, this.add_inline_item) );
        this.disable_gallery_target_id();
    };

    this.document_content_added_handler = function(evt) {
        $('#gallery_form').removeData('validation');
        $('#gallery_form').data('validation', this_decorator(this, this.check_gallery_changeform) );
        this.do_gallery( this.document );
    };

    this.max_order = function () {
        return Math.max.apply(this, $.map( $.makeArray( $('.gallery-items-sortable input.item-order') ), function(e) {
            var n = new Number( $(e).val() );
            if (n > 0) return n;
            else return 0;
        }));
    };

    // check for unique photo ID
    this.check_gallery_changeform = function ( $form ) {
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

        this.disable_gallery_target_id();
        
        return rv;
    };

    // make target_id fields not editable
    this.disable_gallery_target_id = function () {
        function disable_field() {
            var $target_field = $(this).find('input.target_id');
            //$target_field.attr('disabled', true); // doesn't worked out
            $target_field.hide();
        }

        var $filter = $('.gallery-items-sortable .inline-related').each(
            disable_field
        );
    };
    
    // update the preview thumbs and headings
    this.update_gallery_item_thumbnail = function ($input) {
        // Note context this inside this scope would be set by jQuery.
        //var $input = $(this);
        var me = this;
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
                    log_inline.log('thumb update error: successful response container unexpected text: ' , response_text);
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
                me.gallery_inlines_recount_ids();
            },
        });
    };

    this.delete_unsaved_gallery_item = function (evt) {
        var $item = $( evt.target ).closest('.sortable-item');
        if ($item.length > 0) {
            $item.remove();
            this.gallery_inlines_recount_ids();
        }
    };

    this.gallery_recount_ids_and_names_callback = function (element, counter) {
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
                $element.unbind('click');
                $element.bind('click',  this_decorator(this, this.delete_unsaved_gallery_item) );
            }
        }
        if (no_re.test( $element.attr('for') )) {
            var newid = $element.attr('for').replace(no_re, str_concat(ITEM_SET, counter,'-') );
            $element.attr('for', newid);
        }
    };

    this.gallery_inlines_recount_ids = function () {
        var $items = $('.gallery-items-sortable .inline-related');
        var no_items = $('.gallery-items-sortable input.target_id').length;
        var counter = 0;
        var me = this;
        $items.each(
            function() {
                $(this).find('*').each( 
                    function() {
                        me.gallery_recount_ids_and_names_callback(this, counter);
                    }
                )
                counter ++;
            }
        );
    };
    
    this.add_inline_item = function (evt) {
        if (evt && evt.button != 0) return;
        var me = this;
        if (evt && evt.data && evt.data.instance) {
            var me = evt.data.instance;
        }
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
                    $this.unbind('click');
                    $this.bind('click', this_decorator(me, me.delete_unsaved_gallery_item));
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
                var degree = me.get_gallery_ordering_degree( $this );
                var ord = me.max_order() + (1 * degree);
                $this.val(ord);
            }
        });
        $new_item.find('h4').remove();
        $new_item.insertAfter( $last_item );
        var $no_items = $('#id_galleryitem_set-TOTAL_FORMS');
        $no_items.val( no_items+1 );
    };

    this.gallery_ordering_recount = function () {
        var me = this;
        NewmanLib.register_post_submit_callback_once(function(submit_succeeded) {
            if (!submit_succeeded) {
                //log_inline.log('gallery_ordering_modified not changed');
                return;
            }
            me.gallery_ordering_modified = false;
            //log_inline.log('gallery_ordering_modified = false;');
        });

        // ordering-number magic to avoid problems with saving GalleryItems with changed ordering (unique key collision)
        var $form = $('#gallery_form');
        if (this.gallery_ordering_modified) {
            log_inline.log('GalleryItems won\'t be recounted.(reason: already recounted)');
            return;
        }
        $form.find('.gallery-item .item-order').each( function(index, element) {
            if (!this.value) return;
            var value = parseInt(this.value);
            var multiplier = 1;
            if (value >= 1 && value <= 99) {
                multiplier = NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER;
            } else if (value >= NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER && value <= (99 * NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER)) {
                //multiplier = 1.0 / NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER;
                multiplier = 1;
            }
            //var res = Math.floor(Number(value) * multiplier);// force res to be a whole number
            var res = Math.floor(Number(index + 1) * multiplier);// force res to be a whole number
            log_inline.log('Recounting ' , value , ' to ' , res , ' for element ' , this);
            this.value = res.toString();
            me.gallery_ordering_modified = true;
            log_inline.log('GalleryItems recounted');
        });
    };

    this.get_gallery_ordering_degree = function ($element) {
        var value = parseInt( $element.val() );
        var degree = 1;
        if (value / NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER >= 1.0) {
            degree = NEWMAN_GALLERY_ITEM_ORDER_DEGREE_MULTIPLIER;
        }
        return degree;
    };

    this.gallery_recount_ordering = function ($target) {
        var me = this;
        var degree = 1;
        var ord;
        $target.find('input.item-order').each( function(i) {
            // get actual order degree
            if (i == 0) {
                degree = me.get_gallery_ordering_degree( $(this) );
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
    };

    this.gallery_sortable_update_callback = function (evt, ui) {
        var $target = $( evt.target );
        this.gallery_recount_ordering($target);
    };

    this.remove_gallery_item_ids = function () {
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
    };

    this.do_gallery = function (root) {
        var me = this;
        if ( ! root ) root = me.document;
        var $sortables = $(root).find('.gallery-items-sortable').not('ui-sortable');
        if ($sortables.length == 0) return;
        $sortables.children().filter(
            function() {
                var $target_id = $(this).find('input.target_id');
                return $target_id.length != 0;
            }
        ).addClass('sortable-item');

        function wrap_sortable_update_callback(evt, ui) {
            me.gallery_sortable_update_callback(evt, ui);
        }
        $sortables.sortable({
            distance: 20,
            items: '.sortable-item',
            update: wrap_sortable_update_callback
        });
        // recount before save
        NewmanLib.register_pre_submit_callback(me.gallery_ordering_recount);
        
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
                degree = me.get_gallery_ordering_degree( $(this) );
            }
            if ( ! $(this).val() ) $(this).val( 
                (me.max_order() + 1) * degree 
            );
        });
        function wrap_update_gallery_item_thumbnail() {
            me.update_gallery_item_thumbnail($(this));
        }
        $(root).find('input.target_id').not('.js-updates-thumb').addClass('js-updates-thumb').change( 
            wrap_update_gallery_item_thumbnail
        );
        
        // add a new empty gallery item
        $(root).find('input.target_id').not('.js-adds-empty').addClass('js-adds-empty').change( function() {
            if (
                $('.gallery-item input.target_id').filter( 
                function() {
                    return ! $(this).val(); 
                } 
                ).length == 0
            ) {
                me.add_inline_item();
            }
        });
        
        $('#gallery_form').bind('preset_load_initiated.gallery', function(evt, preset) {
        });
        $('#gallery_form').bind('preset_load_completed', function(evt) {
        });
    };

    this.is_suitable = function (document_dom_element, $document) {
        var sortables = $document.find('.gallery-items-sortable').not('ui-sortable');
        if (sortables.length == 0) {
            return false;
        }
        return true;
    };

    // called when preset is being loaded into the form
    this.preset_load_initiated = function (evt, preset) {
        log_inline.log('Preset load initiated for ', this.name);
        // create desired input rows for loaded preset 
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
            this.add_inline_item();
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
        log_inline.log('Preset load init done for ', this.name);
    };

    // called when preset loading completed
    this.preset_load_completed = function (evt) {
        // and get their thumbnails
        var me = this;
        log_inline.log('THIS:', this);
        function each_callback() {
            me.update_gallery_item_thumbnail($(this));
        }
        $('.gallery-items-sortable input.target_id').each( 
           each_callback 
        );
        this.do_gallery( evt.target );
        this.remove_gallery_item_ids();
        this.gallery_recount_ordering( $('.gallery-items-sortable') );
        log_inline.log('Preset load completed for ', this.name);
    };

    return this;
};
var GalleryFormHandler = to_class(__GalleryFormHandler);

/**
 *  handles Tagging inline forms. Esp. preset loading.
 */
var __TagFormHandler = function() {
    this.super_class = FormHandler;

    this.init = function() {
        FormHandler.call(this, 'taghandler');
    };

    this.handle_form = function (document_dom_element, $document) {
        this.$document = $document;
        this.document = document_dom_element;
    };

    this.is_suitable = function (document_dom_element, $document) {
        // TagFormHandler handles input elements 
        // named 'tagging-taggeditem-content_type-object_id-0-id' .
        var found = $document.find('input[name=tagging-taggeditem-content_type-object_id-0-id]');
        return found.length != 0;
    };

    this.preset_load_initiated = function (evt, preset) {
    };

    this.preset_load_completed = function (evt) {
        NewmanInline.remove_inlineadmin_element_value('input[name^=tagging-taggeditem-content_type-object_id-]', '-id');
    };

    return this;
};
var TagFormHandler = to_class(__TagFormHandler);

/**
 *  handles ExportMeta inline form.
 */
var __ExportMetaFormHandler = function() {
    this.super_class = FormHandler;

    this.init = function() {
        FormHandler.call(this, 'exportmeta');
        this.INLINE_SELECTOR = '.inline-related';
    };

    this.swap_fields = function(index, element) {
        $(element).find('div.form-row.export').insertBefore(
            $(element).find('div.noscreen')
        );
    };

    this.move_delete_button = function(index, element) {
    };

    this.move_position_fields = function(index, noscreen_element) {
        var $title = $(noscreen_element).find('div.form-row.title');
        var $exp = $(noscreen_element).siblings('div.form-row.export');
        $(noscreen_element).find('div.form-row.position_from').insertAfter($exp);
        $(noscreen_element).find('div.form-row.position').insertAfter($exp);
        $(noscreen_element).find('div.form-row.position_to').insertBefore($title);
    };

    this.suggest_changed_handler = function(evt) {
        // suggest field has class GenericSuggestField
        // hidden field has class vForeignKeyRawIdAdminField hidden
        var $target = $(evt.target);
        var value = $target.val();
        if (value == '#' || value == '') {
            return true;
        }
        var placement_date_from = this.$document.find('#id_placement_set-0-publish_from').val();
        if (!placement_date_from) {
            return true;
        }
        var $inline = $target.closest(this.INLINE_SELECTOR);
        var $field = $inline.find('.form-row.position_from input.vDateTimeInput');
        if ($field.val() == '') {
            $field.val(placement_date_from);
        }
        return true;
    };

    this.show_additional_fields_handler = function(evt) {
        var $target = $(evt.target);
        var $noscreen = $target.parent().siblings('div.noscreen');
        //log_inline.log('CLICK!', $target, ' noscreen:', $noscreen);
        $noscreen.toggle();
        var display = $noscreen.css('display');
        if (display == 'none' || !display) {
            $target.html( gettext('Show additional fields') );
        } else {
            $target.html( gettext('Hide additional fields') );
        }
        return false;
    };

    this.change_style = function($fieldset) {
        function display_inline($elem) {
            $elem.css('display', 'inline');
            //$elem.css('max-width', '90px');
            //$elem.css('float', 'left');
        }
        var $div = $fieldset.find('div.collapse-button');
        display_inline($div);
        $div = $fieldset.find('div.form-row.position_from');
        display_inline($div);
    };

    this.handle_form = function (document_dom_element, $document) {
        this.$document = $document;
        this.document = document_dom_element;
        // hide several fields
        var $fieldset = $document.find('fieldset.exportmeta-inline');
        var $noscreens = $document.find('fieldset.exportmeta-inline > div.noscreen');
        $noscreens.hide();

        // move export field to the first position
        var $metas = $document.find('fieldset.exportmeta-inline');
        $metas.each( this_decorator(this, this.swap_fields) );

        // move position, position_from and position_to fields before title
        $noscreens.each( this_decorator(this, this.move_position_fields) );

        // move Delete button (in case of existing ExportMeta inlines)
        //$metas.each( this_decorator(this, this.move_delete_button) );

        // hide ugly hidden field's label
        $noscreens.find('div.form-row.position_id label').hide();

        // insert whole inline after Placement inline
        var $placement = $document.find('a.js-placement-main-category').closest('div.inline-group');
        this.$exportmeta_inline = $document.find('fieldset.exportmeta-inline:first').closest('div.inline-group');
        this.$exportmeta_inline.insertAfter($placement);

        // change style for several div elements
        this.change_style($fieldset);

        // suggester changed event
        var $field = this.$exportmeta_inline.find('.GenericSuggestField').siblings('.vForeignKeyRawIdAdminField');
        $field.bind('change', this_decorator(this, this.suggest_changed_handler) );
        $fieldset.find('a.js-export-show-additional-fields').live(
            'click', 
            this_decorator(this, this.show_additional_fields_handler)
        );
    };

    this.is_suitable = function (document_dom_element, $document) {
        var found = $document.find('fieldset.exportmeta-inline');
        return found.length > 0;
    };

    this.preset_load_initiated = function (evt, preset) {
    };

    this.preset_load_completed = function (evt) {
        NewmanInline.remove_inlineadmin_element_value('input[name^=exportmeta_set-]', '-publishable');
        NewmanInline.remove_inlineadmin_element_value('input[name^=exportmeta_set-]', '-id');
        NewmanInline.remove_inlineadmin_element_value('input[name^=exportmeta_set-]', '-position_id');
    };

    return this;
};
var ExportMetaFormHandler = to_class(__ExportMetaFormHandler);

(function($) {
    // Inline handlers registration
    NewmanInline.register_form_handler( new GalleryFormHandler() );
    NewmanInline.register_form_handler( new TagFormHandler() );
    NewmanInline.register_form_handler( new ExportMetaFormHandler() );

    function register_run_form_handlers() {
        function wrap() {
            NewmanInline.run_form_handlers();
        }
        $(document).bind('changeform_shown', wrap);
    }
    // Run relevant form handlers.
    register_run_form_handlers();
})(jQuery);
