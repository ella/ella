// Poll change forms
(function() {
    
    // Edit the question text by clicking on it
    $('.js-edit-poll-question-text').live('click', function(evt) {
        if (evt.button != 0) return;
        $(this).closest('.poll-question-text-container').children('span').toggle()
        .find(':input').focus();
    });
    
    // Delete / Undelete answer option
    function toggle_choice_deletion(el) {
        var $cont = $(el).closest('.poll-choice-container');
        var $del = $cont.find('.js-delete-poll-choice');
        if ($cont.is('.poll-choice-deleted')) {
            $cont.removeClass('poll-choice-deleted').find('.poll-choice-delete-input').val('off');
            $del.text(gettext('Delete'));
        }
        else {
            $cont.addClass('poll-choice-deleted').find('.poll-choice-delete-input').val('on');
            $del.text(gettext('Undelete'));
        }
    }
    $('.js-delete-poll-choice').live('click', function(evt) {
        if (evt.button != 0) return;
        toggle_choice_deletion(this)
    });
    
    // Edit answer option
    $('a.js-edit-poll-choice-text').live('click', function(evt) {
        if (evt.button != 0) return;
        var $cont = $(this).closest('.poll-choice-container');
        if ($cont.is('.poll-choice-deleted')) return;
        $cont.find('.js-edit-poll-choice-text').toggle()
        .filter(':input').focus();
    });
    
    // Edit points for answer option
    $('a.poll-choice-points').live('click', function(evt) {
        if (evt.button != 0) return;
        $(this).closest('p').find('.poll-choice-points').toggle()
        .filter('input').focus();
    });
    
    function non_live_handlers() {
        
        // Done editing question text
        $('.poll-question-text-container textarea').unbind('blur.hide').bind('blur.hide', function() {
            var $cont = $(this).closest('.poll-question-text-container');
            var $label = $cont.find('span:first');
            $cont.children('span').toggle();
            
            $label.find('a').text( $(this).val() || gettext('Click to edit question') );
            
            if ( $(this).val() == '' ) $label.addClass('empty-poll-question-text');
            else $label.removeClass('empty-poll-question-text');
        });
        
        // Done editing answer option text
        $(':input.js-edit-poll-choice-text').unbind('blur.hide').bind('blur.hide', function() {
            var $cont = $(this).closest('.poll-choice-container');
            $cont.find('.js-edit-poll-choice-text').toggle()
            .filter('a').children('span').text( $(this).val() || gettext('Click to edit option') );
            if ( $(this).val() == '' ) {
                $('a.js-edit-poll-choice-text span').addClass('empty-poll-choice');
                if ( ! $cont.is('.poll-choice-deleted') ) {
                    toggle_choice_deletion(this);
                }
            }
            else {
                $('a.js-edit-poll-choice-text span').removeClass('empty-poll-choice');
            }
        });
        
        // Done editing points for answer option
        $('input.poll-choice-points').unbind('blur.hide').bind('blur.hide', function() {
            if ( $(this).val() == '' ) $(this).val('0');
            $(this).closest('p').find('.poll-choice-points').toggle()
            .filter('a').text( $(this).val() );
        });
        
    }
    non_live_handlers();
    $(document).bind('content_added', non_live_handlers);
    
})();
