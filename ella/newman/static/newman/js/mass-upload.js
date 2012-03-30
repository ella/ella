(function($) {
    var log_mass_upload2 = new LoggingLib('MASS UPLOAD2:', true);
    var UPLOADED_PHOTOS = [];
    
    $(document).bind('media_loaded', function() {
        var $wrapper = $('.js-mass-file-upload');
        if ($wrapper.length == 0) return;
        if ($wrapper.is('.js-initialized')) return;
        
        $wrapper
        .data({files:[]})
        .fileupload({
            dataType: 'json',
            url: $('.js-mass-file-upload').prop('action'),
            done: function(evt, data) {
                var $cont = $('.mass-upload2');
                var $rows = _get_rows_by_files(data.files, $cont);
                $rows.addClass('Done OK');
                post_upload(data.jqXHR);
                check_all_done($cont);
            },
            add: function(evt, data) {
                add_files(data);
                (function(tf) {
                    tf.push.apply(tf, data.files);
                })( $(this).data('files') );
            },
            fail: function(evt, data) {
                var $cont = $('.mass-upload2');
                var $rows = _get_rows_by_files(data.files, $cont);
                $rows.addClass('Done Failed');
                
                _adapt_ids_in_response_to_row(data.jqXHR, $rows);
                AjaxFormLib.ajax_submit_error.call(
                    {_form: $rows},
                    data.jqXHR
                );
                
                // check_all_done($cont);
            },
            multipart: true
        })
        .bind({
            submit: function(evt) {
                evt.preventDefault();
                
                var fs = $(this).data('files');
                var $fileupload = $(this);
                
                var $rows = $('.js-photos-container .row').not('.Done.OK');
                var $common_fields_cleaned = AjaxFormLib.clean_inputs($('.js-common-image-fields'));
                var default_values = $common_fields_cleaned.serializeObject();
                
                var incrementable_names = {};
                $common_fields_cleaned.filter('.js-Incrementable *').each(function() {
                    incrementable_names[ $(this).prop('name') ] = true;
                });
                var default_valued_field_counter = 0;
                
                $rows.each( function() {
                    var values = AjaxFormLib.clean_inputs($(this)).serializeObject();
                    var incremented_default_valued_field_counter = false;
                    
                    for (k in values) {
                        if (!values[k] && default_values[k]) {
                            
                            var suffix = '';
                            if (k in incrementable_names) {
                                if (!incremented_default_valued_field_counter) {
                                    default_valued_field_counter++;
                                    incremented_default_valued_field_counter = true;
                                }
                                suffix = ' ' + default_valued_field_counter;
                            }
                            
                            values[k] = default_values[k] + suffix;
                        }
                    }
                    
                    var file = $(this).data('jfu_file');
                    values.file_name = file.name;
                    
                    $fileupload.fileupload('send', {
                        files: [file],
                        formData: values
                    });
                });
            },
            all_done: function(evt) {
                NewmanLib.pop_adrstack({photos: UPLOADED_PHOTOS});
                UPLOADED_PHOTOS = [];
            }
        })
        .addClass('js-initialized');

        // hide "save to gallery" button if we're coming from a gallery anyway
        (function(stack_top) {
            if (stack_top && /galleries.gallery.(add|\d+)/.test( stack_top.from )) {
                $('.js-mass-file-upload .js-upload-to-gallery').hide();
            }
        })(NewmanLib.ADR_STACK[NewmanLib.ADR_STACK.length-1]);
        
        // for some reason, textareas in template retain values from
        // previously-rendered textareas of identical fields from change-form
        // (probably a backend issue)
        $('.template textarea').val('').html('');

        // populate the "common image data" fieldset
        var $common_fields = $('.template .field').clone(true);
        $common_fields
        .each(function() { add_suffices($(this), '_common') })
        .appendTo('.js-common-image-fields');
        $common_fields
        .filter(':has(#id_title_common)')
        .addClass('js-Incrementable');
        $common_fields.trigger('common_fields_populated');
        
        // save photos received from server to action table
        $('#mass-upload2-form-post-save').data({ callback: function() {
            var action_table = this;
            var data = action_table.vars.response_data;
            if (data && data.data && data.data.photos) {
                action_table.vars.photos = data.data.photos;
            }   
            return {};
        }});
        
        // mass-upload form is tricky to restore -- we need custom serialization routine
        $('.change-form').data({
            get_form_data_for_restoring: function() {
                var rv = {
                    images: [],
                    common_fields: $('.js-common-image-fields :input').serializeArray()
                };
                $('.js-photos-container .row').each( function() {
                    rv.images.push({
                        row_form_data: $(this).find(':input').serializeArray(),
                        add_file_args: [
                            $(this).data('jfu_file'),
                            $(this).data('jfu_data')
                        ]
                    });
                });
                return rv;
            },
            onreturn_callback: function(popped) {
                var form_data;
                form_data = popped.form_data;
                
                $(document).one('content_added', function(evt) {
                    $.each( form_data.images, function(i,data) {
                        var $row = add_file.apply(this, data.add_file_args);
                        NewmanLib.restore_form(JSON.stringify({data: data.row_form_data}), $row, {});
                    });
                    
                    $(document).one('common_fields_populated', function(evt) {
                        NewmanLib.restore_form(JSON.stringify({data: form_data.common_fields}), $('.js-common-image-fields'), {});
                        
                        if (popped.oid) {
                            popped.selection_callback(popped.oid,{str: popped.str});
                        }
                        
                    });
                    
                });
            }
        });
    });

    $('.js-photos-container .Del').live('click', function(evt) {
        if (evt.button != 0) return;
        
        var $row = $(evt.target).closest('.row');
        var data = $row.data('jfu_data');
        var file = $row.data('jfu_file');
        
        if (!data.jqXHR) {
            // remove the file from the array
            var files = $('.js-mass-file-upload').data('files');
            var found = false;
            for (var i = 0; i < files.length; i++) {
                if (files[i] === file) {
                    found = true;
                    break;
                }
            }
            if (found) {
                files.splice(i,1);
            }
        }
        else {
            data.jqXHR.abort();
        }
        
        $row.remove();
    });

    $('.js-mass-file-upload .js-upload-to-gallery').live('click', function(evt) {
        if (evt.button != 0) return;
        var stack = NewmanLib.ADR_STACK;
        if (stack.length) {
            var stack_top = stack[stack.length-1];
            stack_top.to = '/galleries/gallery/add/';
            stack_top.onreturn = NewmanLib.adr_stack_default_onreturn_callback;
            stack_top.onsave   = NewmanLib.adr_stack_default_onsave_callback;
        }
        stack.push({
            from: '/galleries/gallery/add/',
            to: get_hashadr(''),
            onsave:   adr_stack_mass_upload_onsave_callback,
            onreturn: adr_stack_mass_upload_onreturn_callback,
            form_data: JSON.stringify({data:{}})
        });
        $(evt.target).closest('.js-mass-file-upload').submit();
    });

    $('.js-mass-file-upload .js-start-upload').live('click', function(evt) {
        if (evt.button != 0) return;
        $(evt.target).closest('.js-mass-file-upload').submit();
    });

    function add_files(data) {
        for (var i = 0; i < data.files.length; i++) {
            add_file(data.files[i], data);
        }
    }
    function add_file(file, data) {
        var $cont = $('.js-photos-container');
        var $row = $('.template').clone(true).removeClass('template');
        
        // suffix ID's, so that they stay unique
        var id_suf = '_' + $cont.find('.row').length;
        add_suffices($row,  id_suf);
        
        // the file-id is sent along with each file upload in a header,
        // so that the server can couple up the files with the metadata
        var file_id = 'file' + id_suf;
        $row.data({
            jfu_file: file,
            jfu_data: data,
            file_id: file_id,
            id_suf: id_suf
        });
        $row.find('.file-id').val(file_id);
        
        $row.appendTo($cont);
        
        loadImage(file, add_image, {maxWidth: 200});
        
        function add_image(img) {
            if ($(img).is('img')) {} else return;
            $row.find('.Img').append(img);
        }
        
        return $row;
    }

    function add_suffices($el, suf) {
        add_suffix('id',  suf);
        add_suffix('for', suf);
        function add_suffix(attr, suf) {
            $el.find('['+attr+']').each(function() {
                $(this).attr(
                    attr,
                    $(this).attr(attr).replace(/(_suggest)?$/, suf+'$1')
                );
            });
        }
    }

    function check_all_done($cont) {
        if ($cont.find('.row:not(.Done.OK)').length == 0) {
            $('.js-mass-file-upload').trigger('all_done');
        }
    }
    
    // returns all rows that have specified files
    function _get_rows_by_files(files, $cont) {
        return $cont.find('.row').filter( function() {
            var row_file = $(this).data('jfu_file');
            for (var i = 0; i < files.length; i++) {
                if (row_file === files[i]) return true;
            }
            return false;
        } );
    }

    $('.js-adrstack-push.js-custom-adrstack-callbacks.js-multi-upload').live('click', function(evt) {
        var stack_top = NewmanLib.ADR_STACK[ NewmanLib.ADR_STACK.length - 1 ];
        stack_top.input_id = $('#overlay-content').data('input_id');
        stack_top.onsave   = adr_stack_mass_upload_onsave_callback;
        stack_top.onreturn = adr_stack_mass_upload_onreturn_callback;
    });

    var adr_stack_mass_upload_onreturn_callback = function(popped, action_table) {
        $(document).one('media_loaded', function(evt) {
            // restore everything but gallery items
            NewmanLib.restore_form(popped.form_data, $('.change-form'), {});
            
            // restore previously-present gallery items
            var gallery_item_ids = [];
            for (var i = 0; i < popped.form_data.length; i++) {
                var item = popped.form_data[i];
                if (/^galleryitem_set-\d+-target_id$/.test(item.name)) {
                    gallery_item_ids.push(item.value);
                }
            }
            NewmanInline.get_handler_registry().gallery.restore_gallery_items(
                gallery_item_ids,
                $('.change-form')
            );
            
            // add the mass-uploaded photos to the gallery
            NewmanInline.get_handler_registry().gallery.restore_gallery_items(
                $.map(popped.photos, function(i){ if (i.id) return i.id }),
                $('.change-form')
            );
        });
    };
    var adr_stack_mass_upload_onsave_callback = function(popped, action_table) {
        if (!action_table.vars.photos) {
            log_mass_upload2.log('Did not get IDs and titles of mass-uploaded photos -- not adding them to form');
            popped.photos = [];
        }
        else {
            popped.photos = action_table.vars.photos;
        }
    };

    function _adapt_ids_in_response_to_row(jqXHR, $row) {
        var id_suf = $row.data('id_suf');
        jqXHR.responseText = jqXHR.responseText.replace(
            /("id"\s*:\s*"[^"]+)/g,
            '$1' + id_suf
        );
    }

    function post_upload(jqXHR) {
        var data;
        try {
            data = JSON.parse(jqXHR.responseText);
        } catch(e) {
            ;;; log_mass_upload2.log('Unexpected response from upload', jqXHR.responseText);
            return;
        }
        if (data.data && data.data.object_id) {} else return;
        
        UPLOADED_PHOTOS.push({
            id:    data.data.object_id,
            title: data.data.object_title
        });
    }
})(jQuery);
