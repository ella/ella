var IMAGE_OPTIONS = {
    maxWidth: 2048,
    maxHeight: 2048,
    formatConversion: {
        png:  'png',
        tiff: 'jpg.90',
        gif:  'png',
        jpg:  'jpg.85',
    }
};
( function($) {
    window.on_upload_success = function(xhr) {
        ;;; carp('success uploading photo:', xhr);
        show_ok(_('successfully uploaded photo'));
//        AjaxFormLib.show_ajax_success(xhr.responseText);
    }
    window.on_upload_error = function(xhr) {
        ;;; carp('error uploading photo:', xhr);
        show_err(_('failed uploading photo'));
//        AjaxFormLib.ajax_submit_error(xhr)
    }
    window.on_upload_progress = function(progress) {
        carp(progress+' uploaded');
    }
    
    function save_photo_handler(evt) {
        var $form = $(this).closest('#photo_form');
        if (evt.button > 0) return true;
        var flash_obj = ($.browser.msie ? window : document).PhotoUploader;
        if (!flash_obj) {
            show_err(_('Failed to get Flash movie') + ' PhotoUploader.');
            carp('Failed to get Flash movie PhotoUploader.');
            return false;
        }
        var data = {};
        $('#photo_form :input').each( function() {
            if (/_suggest/.test( this.id )) return;
            var val = $(this).val();
            if ($('#'+this.id+'_suggest').length) {
                val = val.replace(/#.*/, '');
            }
            data[ this.name ] = val;
        });
        IMAGE_OPTIONS.url = $('<a>').attr('href',get_adr('json/')).get(0).href;
        ;;; carp('URL passed to flash: ' + IMAGE_OPTIONS.url);
        var saved_data = flash_obj.saveData(data, IMAGE_OPTIONS);
        ;;; carp('flash returned: ', saved_data);
        return false;
    }
    function set_image_form_handlers() {
        if ($('#photo_form').length == 0) return;
        $('#photo_form .submit-row a.ok')
        .addClass('noautosubmit')
        .unbind('click', save_photo_handler)
        .bind(  'click', save_photo_handler);
        $('#photo_form')
        .unbind('submit.ajax_overload')
        .bind('submit', save_photo_handler);
    }
    $(document).bind('content_added', set_image_form_handlers);
    set_image_form_handlers();
})(jQuery);
