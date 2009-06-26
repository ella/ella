(function() {
    $('.js-delete-poll-choice').live('click', function(evt) {
        if (evt.button != 0) return;
        var $cont = $(this).closest('.poll-choice-container');
        if ($cont.is('.poll-choice-deleted')) {
            $cont.removeClass('poll-choice-deleted').find('.poll-choice-delete-input').val('off');
            $(this).text(gettext('Delete'));
        }
        else {
            $cont.addClass('poll-choice-deleted').find('.poll-choice-delete-input').val('on');
            $(this).text(gettext('Undelete'));
        }
    });
    
    $('a.js-edit-poll-choice-text').live('click', function(evt) {
        if (evt.button != 0) return;
        var $cont = $(this).closest('.poll-choice-container');
        if ($cont.is('.poll-choice-deleted')) return;
        $cont.find('.js-edit-poll-choice-text').toggle()
        .filter(':input').focus();
    });
    
    $('a.poll-choice-points').live('click', function(evt) {
        if (evt.button != 0) return;
        $(this).closest('p').find('.poll-choice-points').toggle()
        .filter('input').focus();
    });
    
    function non_live_handlers() {
        $(':input.js-edit-poll-choice-text').unbind('blur.hide').bind('blur.hide', function() {
            $(this).closest('.poll-choice-container').find('.js-edit-poll-choice-text').toggle()
            .filter('a').text( $(this).val() );
        });
        $('input.poll-choice-points').unbind('blur.hide').bind('blur.hide', function() {
            $(this).closest('p').find('.poll-choice-points').toggle()
            .filter('a').text( $(this).val() );
        });
    }
    non_live_handlers();
    $(document).bind('content_added', non_live_handlers);
    
    /*$('.poll-choice-deleted').live('click', function(evt) {
        if ( $(evt.target).is('.js-delete-poll-choice') ) return;
        if (evt.button != 0) return;
        return false;
    });*/
})();
