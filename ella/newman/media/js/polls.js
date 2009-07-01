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
    
    function add_question() {
        var $last_question = $('.poll-question-container:last');
        var $new_question = $last_question.clone(true);
        var $new_options = $new_question.find('.poll-choice-container');
        
        // reset the question text
        $new_question.find('span:first').addClass('empty-poll-question-text').find('a').text(gettext('Click to edit question'));
        $new_question.find(':input.js-edit-poll-choice-text').val('');
        
        // set the question's inputs' names
        var last_qid = $last_question.find('input[name=choices_widget]').val();
        var last_no = /\d+/.exec( last_qid )[0];
        var new_no = new Number(last_no) + 1;
        // choices_widget
        var new_qid = last_qid.replace(/\d+/, new_no);
        $new_question.find('input[name=choices_widget]').val( new_qid );
        // question text
        var last_qt = $last_question.find('.poll-question-input :input').attr('name');
        var new_qt = last_qt.replace(/\d+/, new_no);
        $new_question.find('.poll-question-input :input').attr('name', new_qt);
        
        // let new question have one empty option
        $new_options.remove();
        add_option( $new_question );
        
        $new_question.insertAfter( $last_question );
        
        // update question count
        $(':input[name=question_set-TOTAL_FORMS]').val(
            $('.poll-question-container').length
        );
    }
    function add_option($question) {
        var $last_option = $('.poll-choice-container:last');
        var $new_option = $last_option.clone(true);
        
        // clear text
        $new_option.find('.js-edit-poll-choice-text span').addClass('empty-poll-choice').text(gettext('Click to edit option'));
        $new_option.find('.js-edit-poll-choice-text').val('');
        
        // set votes to zero and don't show them
        $new_option.find('input.poll-option-votecount').val(0);
        $new_option.find('.js-edit-poll-choice-text span').removeAttr('title');
        
        // new question is not deleted
        $new_option.removeClass('poll-choice-deleted').find('input.poll-choice-delete-input').val('off');
        
        // default to zero points
        $new_option.find('input.poll-choice-points').val ( 0 );
        $new_option.find(    'a.poll-choice-points').text('0');
        
        // set names of inputs related to this answer option
        var q_meta = /\D*\d+/.exec( $question.find('[name=choices_widget]').val() );
        var q_prefix = q_meta[0];
        var choice_no = $question.find('.poll-choice-container').length;
        ++choice_no;
        $new_option.find(':input').each( function() {
            var name_parts = /\d+(\D*)(\d*)(.*)/.exec( $(this).attr('name') );
            if ( ! name_parts ) return;
            var post_q_no = name_parts[1];
            var opt_no = name_parts[2];
            var tail = name_parts[3];
            $(this).attr( 'name', q_prefix + post_q_no + (opt_no.length ? choice_no : '') + tail );
        });
        
        $question.find('.poll-answers:first').append( $new_option );
    }
    
    function non_live_handlers() {
        
        // Done editing question text
        $('.poll-question-text-container textarea').unbind('blur.hide').bind('blur.hide', function() {
            var $cont = $(this).closest('.poll-question-text-container');
            var $label = $cont.find('span:first');
            $cont.children('span').toggle();
            
            $label.find('a').text( $(this).val() || gettext('Click to edit question') );
            
            if ( $(this).val() == '' ) $label.addClass('empty-poll-question-text');
            else  {
                $label.removeClass('empty-poll-question-text');
                if ( $cont.closest('.poll-question-container').find('.poll-choice-container').length == 0 ) {
                    add_option($cont.closest('.poll-question-container'));
                }
            }
            
            // Add an empty question when there's none more
            if ( $cont.closest('fieldset').find('.empty-poll-question-text').length == 0 ) {
                add_question();
            }
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
