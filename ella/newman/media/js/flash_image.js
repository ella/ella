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
        ;;; carp('success:', xhr);
        show_ok('successfully uploaded photo');
//        AjaxFormLib.show_ajax_success(xhr.responseText);
    }
    window.on_upload_error = function(xhr) {
        ;;; carp('error:', xhr);
        show_err('failed uploading photo');
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
        for (field in {title:1,description:1,slug:1,source:1,authors:1}) {
            var val = $('#id_'+field).val();
            if ($('#id_'+field+'_suggest').length) {
                val = val.replace(/#.*/, '');
            }
            data[ field ] = val;
        }
        IMAGE_OPTIONS.url = get_adr('json/');
        flash_obj.saveData(data, IMAGE_OPTIONS);
        ;;; carp('URL passed to flash: ' + IMAGE_OPTIONS.url);
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
