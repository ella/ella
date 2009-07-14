// Poll change forms
(function() {
    
    // Edit the question text by clicking on it
    $('.js-edit-poll-question-text').live('click', function(evt) {
        if (evt.button != 0) return;
        $(this).closest('.js-poll-question-text-container').children('span').toggle()
        .find(':input').focus();
    });
    
    // Delete / Undelete answer option
    function toggle_choice_deletion(el) {
        var $cont = $(el).closest('.js-poll-choice-container');
        var $del = $cont.find('.js-delete-poll-choice');
        if ($cont.is('.poll-choice-deleted')) {
            $cont.removeClass('poll-choice-deleted').find('.js-poll-choice-delete-input').val('off');
            $del.text(gettext('Delete'));
            var $opt_text = $cont.find(':input.js-edit-poll-choice-text');
            if ($opt_text.val() == '') {
                $opt_text.each(edit_answer_option);
            }
        }
        else {
            $cont.addClass('poll-choice-deleted').find('.js-poll-choice-delete-input').val('on');
            $del.text(gettext('Undelete'));
        }
    }
    $('.js-delete-poll-choice').live('click', function(evt) {
        if (evt.button != 0) return;
        toggle_choice_deletion(this)
    });
    
    // Edit answer option
    function edit_answer_option(evt) {
        if (evt && evt.button != 0) return;
        var $cont = $(this).closest('.js-poll-choice-container');
        if ($cont.is('.poll-choice-deleted')) return;
        $cont.find('.js-edit-poll-choice-text').toggle()
        .filter(':input').focus();
    }
    $('a.js-edit-poll-choice-text').live('click', edit_answer_option);
    
    // Edit points for answer option
    $('a.js-poll-choice-points').live('click', function(evt) {
        if (evt.button != 0) return;
        $(this).closest('p').find('.js-poll-choice-points').toggle()
        .filter('input').focus();
    });
    
    function add_question() {
        var $last_question = $('.js-poll-question-container:last');
        var $new_question = $last_question.clone();
        var $new_options = $new_question.find('.js-poll-choice-container');
        
        // reset the question text
        $new_question.find('span:first').addClass('js-empty-poll-question-text').find('a').text(gettext('Click to edit question'));
        $new_question.find(':input.js-edit-poll-choice-text').val('');
        
        // get rid of silly ID's
        $new_question.find('[id]').removeAttr('id');
        
        // set the question's inputs' names
        var last_qid = $last_question.find('input[name=choices_widget]').val();
        var last_no = /\d+/.exec( last_qid )[0];
        var new_no = new Number(last_no) + 1;
        // choices_widget
        var new_qid = last_qid.replace(/\d+/, new_no);
        $new_question.find('input[name=choices_widget]').val( new_qid );
        // question text
        var last_qt = $last_question.find('.js-poll-question-input :input').attr('name');
        var new_qt = last_qt.replace(/\d+/, new_no);
        $new_question.find('.js-poll-question-input :input').attr('name', new_qt);
        $new_question.find('.js-question-foreign-key-fields :input').each( function() {
            // question_set-0-id   => question_set-1-id
            // question_set-0-quiz => question_set-1-quiz
            this.name = this.name.replace(/set-\d+-/, 'set-'+new_no+'-');
        });
        
        // reset rich text field
        var $rich_text = $new_question.find('.rich_text_area');
        $rich_text
        .markItUpRemove()
        .attr({ id: 'id_'+$rich_text.attr('name') })
        .markItUp(MARKITUP_SETTINGS);
        
        // let new question have one empty option
        $new_options.remove();
        add_option( $new_question );
        
        $new_question.insertAfter( $last_question );
        
        // update question count
        $('#id_question_set-TOTAL_FORMS').val(
            $('.js-poll-question-container').length
        );
        
        non_live_handlers();
    }
    function add_option($question) {
        var $last_option = $('.js-poll-choice-container:last');
        var $new_option = $last_option.clone();
        
        // clear text
        $new_option.find('.js-edit-poll-choice-text span').addClass('empty-poll-choice').text(gettext('Click to edit option'));
        $new_option.find('.js-edit-poll-choice-text').val('');
        
        // set votes to zero and don't show them
        $new_option.find('input.js-poll-choice-votecount').val(0);
        $new_option.find('.js-edit-poll-choice-text span').removeAttr('title');
        
        // new question is not deleted
        $new_option
        .removeClass('poll-choice-deleted')
        .find('input.js-poll-choice-delete-input').val('off')
        .end().find('.js-delete-poll-choice').text(gettext('Delete'));
        
        // default to zero points
        $new_option.find('input.js-poll-choice-points').val ( 0 );
        $new_option.find(    'a.js-poll-choice-points').text('0');
        
        // set names of inputs related to this answer option
        var q_meta = /\D*\d+/.exec( $question.find('[name=choices_widget]').val() );
        var q_prefix = q_meta[0];
        var choice_no = $question.find('.js-poll-choice-container').length;
        ++choice_no;
        $new_option.find(':input').each( function() {
            var name_parts = /\d+(\D*)(\d*)(.*)/.exec( $(this).attr('name') );
            if ( ! name_parts ) return;
            var post_q_no = name_parts[1];
            var opt_no = name_parts[2];
            var tail = name_parts[3];
            $(this).attr( 'name', q_prefix + post_q_no + (opt_no.length ? choice_no : '') + tail );
        });
        
        $question.find('.js-poll-choices:first').append( $new_option );
        
        non_live_handlers();
    }
    
    function non_live_handlers() {
        
        // Done editing question text
        $('.js-poll-question-text-container textarea').unbind('blur.hide').bind('blur.hide', function() {
            var $cont = $(this).closest('.js-poll-question-text-container');
            var $label = $cont.find('span:first');
            $cont.children('span').toggle();
            
            $label.find('a').text( $(this).val() || gettext('Click to edit question') );
            
            if ( $(this).val() == '' ) $label.addClass('js-empty-poll-question-text');
            else  {
                $label.removeClass('js-empty-poll-question-text');
                if ( $cont.closest('.js-poll-question-container').find('.js-poll-choice-container').length == 0 ) {
                    add_option($cont.closest('.js-poll-question-container'));
                }
            }
            
            // Add an empty question when there's none more
            if ( $cont.closest('fieldset').find('.js-empty-poll-question-text').length == 0 ) {
                add_question();
            }
        });
        
        // Done editing answer option text
        $(':input.js-edit-poll-choice-text').unbind('blur.hide').bind('blur.hide', function() {
            var $cont = $(this).closest('.js-poll-choice-container');
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
            
            // Add an empty option when there's none more for this question
            if ( $cont
                .closest('.js-poll-question-container')
                .find(':input.js-edit-poll-choice-text')
                .filter( function() { return $(this).val() == ''; } )
                .length == 0
            ) {
                add_option( $cont.closest('.js-poll-question-container') );
            }
        });
        
        // Done editing points for answer option
        $('input.js-poll-choice-points').unbind('blur.hide').bind('blur.hide', function() {
            if ( $(this).val() == '' ) $(this).val('0');
            $(this).closest('p').find('.js-poll-choice-points').toggle()
            .filter('a').text( $(this).val() );
        });
        
    }
    non_live_handlers();
    $(document).bind('content_added', non_live_handlers);
    
})();
