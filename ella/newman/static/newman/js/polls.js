/** 
 * Poll change forms
 * requires: jQuery 1.4.2+, 
 *          str_concat() function (effective string concatenation).
 *          LoggingLib object (utils.js).
 *
 */
// polls logging
log_polls = new LoggingLib('POLLS:', false);

(function() {
	// remaining-poll-question-inputs
	$('.remaining-poll-question-inputs').remove(); 
    
    // Edit the question text by clicking on it
    $('.js-edit-poll-question-text').live('click', function(evt) {
        if (evt.button != 0) return;
        $(this).closest('.js-poll-question-text-container').children('span').toggle()
        .find('textarea').focus();
    });
    
    // Delete / Undelete answer option
    function reflect_choice_deletion(el) {
        var $cont = $(el).closest('.js-poll-choice-container');
        var $del = $cont.find('.js-delete-poll-choice');
        var $input = $cont.find('.js-poll-choice-delete-input');
        
        if ($input.val() == 'off') {
            $cont.removeClass('poll-choice-deleted');
            $del.show().text(gettext('Delete'));
        }
        else if ($cont.find(':input.js-edit-poll-choice-text').val() == '') {
            $cont.removeClass('poll-choice-deleted');
            $del.hide();
        }
        else {
            $cont.addClass('poll-choice-deleted');
            $del.show().text(gettext('Undelete'));
        }
    }
    function delete_choice(el) {
        var $input = $(el).is('.js-poll-choice-delete-input')
        ? $(el)
        : $(el).closest('.js-poll-choice-container').find('.js-poll-choice-delete-input');
        $input.val('on');
        reflect_choice_deletion(el);
    }
    function undelete_choice(el) {
        var $input = $(el).is('.js-poll-choice-delete-input')
        ? $(el)
        : $(el).closest('.js-poll-choice-container').find('.js-poll-choice-delete-input');
        $input.val('off');
        reflect_choice_deletion(el);
    }
    function toggle_choice_deletion(el) {
        var $input = $(el).is('.js-poll-choice-delete-input')
        ? $(el)
        : $(el).closest('.js-poll-choice-container').find('.js-poll-choice-delete-input');
        
        if ($input.val() == 'on') {
            undelete_choice($input);
        }
        else {
            delete_choice($input);
        }
    }
    $('.js-delete-poll-choice').live('click', function(evt) {
        if (evt.button != 0) return;
        toggle_choice_deletion(this)
    });

	// Right answer radios
	$('.js-reset-poll-right-answer').live('click', function(){
		var $all = $(this).parents('.js-poll-choices');
		$all.find('input.js-poll-choice-points').val('0');
		$all.find('a.js-poll-choice-points').html('0');
		var $clicked = $(this).parents('.js-poll-choice-text-container');
		$clicked.find('input.js-poll-choice-points').val('1');
		$clicked.find('a.js-poll-choice-points').html('1');
	});
    
    // Edit answer option
    function edit_answer_option(evt) {
        if (evt && evt.button != 0) return;
        var $cont = $(this).closest('.js-poll-choice-container');
        if ($cont.is('.poll-choice-deleted')) return;
        $cont.find('a.js-edit-poll-choice-text').hide();
        $cont.find(':input.js-edit-poll-choice-text').show().focus();
    }
    $('a.js-edit-poll-choice-text').live('click', edit_answer_option);
    
    // Edit points for answer option
    $('a.js-poll-choice-points').live('click', function(evt) {
        if (evt.button != 0) return;
        $(this).closest('p').find('.js-poll-choice-points').toggle()
        .filter('input').focus();
    });

	$('.js-poll-choice-points').live('keypress',function(e){
		return ( e.which!=8 && e.which!=0 && (e.which<48 || e.which>57)) ? false : true;
	}).live('keyup',function(e){
		var number = $(this).val() - 0 || 0;
		var code = (e.keyCode ? e.keyCode : e.which);
		if (code == 38 || code == 39) {
			$(this).val(++number);
		} else if (code == 40 || code == 37) {
			var dec = ((number >= 1) ? --number : 0);
			$(this).val(dec);
		}
	});
    
    function add_question() {
        var $last_question = $('.js-poll-question-container:last');
        var $new_question = $last_question.clone();
        var $new_options = $new_question.find('.js-poll-choice-container');
        
        // reset the question text
        $new_question.find('span:first').addClass('js-empty-poll-question-text').find('a').addClass('icn btn eclear').text(gettext('Click to edit question'));
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
            this.name = this.name.replace(/set-\d+-/, str_concat('set-'+new_no+'-'));
        });
        
        // reset rich text field
        var newman_text_area_settings = {
            toolbar: FloatingOneToolbar
        };
        var $rich_text = $new_question.find('.rich_text_area');
        $rich_text
        .newmanTextAreaRemove()
        .attr({ id: 'id_'+$rich_text.attr('name') })
        .newmanTextArea(newman_text_area_settings);

		$new_question.find('.js-poll-question-input .markItUp').addClass('small');
        
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
        $new_option.find('a.js-poll-choice-points').text('0');
        
        // set names of inputs related to this answer option
        var q_meta = /\D*\d+/.exec( $question.find('[name=choices_widget]').val() );
        var q_prefix = q_meta[0];
        var choice_no = $question.find('.js-poll-choice-container').length;
        ++choice_no;

		var n_replacer = function(element, atts){
			var attributes = atts.split(',');
			for (i in attributes){
	            var attr_parts = /\d+(\D*)(\d*)(.*)/.exec( element.attr(attributes[i]) );
	            if ( ! attr_parts ) return;
	            var post_q_no = attr_parts[1];
	            var opt_no = attr_parts[2];
	            var tail = attr_parts[3];
	            element.attr( 
                    attributes[i], 
                    str_concat(q_prefix , post_q_no , (opt_no.length ? choice_no : '') , tail)
                );
			}
		}

        $new_option.find(':input').each( function() {
			n_replacer($(this), 'name');
        });
		$question.find('.js-poll-options').find('label').each( function() {
			n_replacer($(this), 'for');
        });
		$question.find('.js-poll-options').find('input').each( function() {
			n_replacer($(this), 'name,id');
        });
        
        $question.find('.js-poll-choices:first').append( $new_option );
        
        non_live_handlers();
    }
    
    function non_live_handlers() {
		var cancelTimer;
        
        // Done editing question text
        function reflect_question_input_change(area) {
            var $area = $(area);
            var $cont = $area.closest('.js-poll-question-text-container');
            var $label = $cont.find('span:first');
            
            $label.find('a').text( $area.val() || gettext('Click to edit question') );
            
            //log_polls.log('>>> label:',$label.get(0));
            if ( $area.val() == '' ) {
                $label.addClass('js-empty-poll-question-text');
                $label.find('a').addClass('icn btn eclear');
            }
            else  {
                $label.removeClass('js-empty-poll-question-text');
                $label.find('a').removeClass('icn btn eclear');
                if ( $cont.closest('.js-poll-question-container').find('.js-poll-choice-container').length == 0 ) {
                    add_option($cont.closest('.js-poll-question-container'));
                }
            }
        }

        $('.js-poll-question-text-container textarea').unbind('blur.hide').bind('blur.hide', function() {
			var area = this;
			
			cancelTimer = setTimeout(function(){
	
	            var $cont = $(area).closest('.js-poll-question-text-container');
	            $cont.children('span').toggle();
            
                reflect_question_input_change(area);
            
	            // Add an empty question when there's none more
	            if ( $cont.closest('fieldset').find('.js-empty-poll-question-text').length == 0 ) {
	                add_question();
	            }

			}, 200);
			
        });

		// Cancel editing question text if focus returned to area in 200ms (i.e. button in rich area header is clicked)
		$('.js-poll-question-text-container textarea').bind('focus', function(){
			clearTimeout(cancelTimer);
		});
        
        // Done editing answer option text
        function reflect_answer_input_change(input) {
            var $cont = $(input).closest('.js-poll-choice-container');
            
            $cont
            .find('a.js-edit-poll-choice-text span')
            .text( $(input).val() || gettext('Click to edit option') );
            
            if ( $(input).val() == '' ) {
                $cont.find('a.js-edit-poll-choice-text span').addClass('empty-poll-choice');
            }
            else {
                $cont.find('a.js-edit-poll-choice-text span').removeClass('empty-poll-choice');
            }
        }

        $(':input.js-edit-poll-choice-text').unbind('blur.hide').bind('blur.hide', function() {
            var $cont = $(this).closest('.js-poll-choice-container');
            $cont.find('.js-edit-poll-choice-text').toggle();
            
            reflect_answer_input_change(this);
            
            if ( $(this).val() == '' ) {
                delete_choice(this);
            }
            else {
                undelete_choice(this);
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
        function reflect_points_input_change(input) {
            $(input).closest('p').find('a.js-poll-choice-points').text( $(input).val() );
        }
        $('input.js-poll-choice-points').unbind('blur.hide').bind('blur.hide', function() {
            if ( $(this).val() == '' ) $(this).val('0');
            $(this).closest('p').find('.js-poll-choice-points').toggle();
            reflect_points_input_change(this);
        });
        
        
        //// Preset loading

        function add_inline_item($inline, $last_item) {
            var $new_item = $last_item.clone(true);
            var no_items = $inline.find('input.target_id').length;

            $new_item.find('h4').remove();
            $new_item.insertAfter( $last_item );
            var $no_items = $('#id_result_set-TOTAL_FORMS');
            $no_items.val( no_items + 1 );
        }

        function recount_inline_items($inline) {
            var no_items = 0;
            var no_re = /result_set-\d+-/;
            var row_class = /row\d+/;

            function process_row() {
                var actual_result_set = ['result_set-', no_items, '-'].join('');
                if (no_re.test( this.name )) {
                    var newname = this.name.replace(no_re, actual_result_set);
                    $(this).attr({name: newname});
                }
                if (no_re.test( this.id )) {
                    var newid = this.id.replace(no_re, actual_result_set);
                    $(this).attr({id: newid});
                }
                
                // init values
                if ( $(this).is('input,textarea') ) {
                    $(this).val('');
                }
            }

            $inline.find('tr').each( function() {
                $(this).find('*').each( process_row );
                if ($(this).find('th').length == 0 && row_class.test($(this).attr('class'))) {
                    no_items ++;
                }
            });
        }

        function load_poll_from_preset(evt, preset) {
            log_polls.log('preset load initiated (poll). evt=' , evt , ' , preset=' , preset);
            $('.js-poll-question-container:gt(0)').remove();
            $('.js-poll-choice-container:gt(0)'  ).remove();
            var last_q_no = 0;
            var option_counts = [0];
            var desired_no = 0;
            for (var i = 0; i < preset.data.length; i++) {
                var o = preset.data[i];
                if (o.name == 'result_set-TOTAL_FORMS') {
                    desired_no = new Number( o.value );
                }
                var name = preset.data[i].name;
                var q_no_match = /question_set-(\d+)/.exec( name );
                if ( ! q_no_match ) continue;
                var q_no = q_no_match[1] - 0;
                if (q_no > last_q_no) {
                    add_question();
                    option_counts.push(0);
                    last_q_no = q_no;
                }
                if ( /question_set-\d+-choices$/.test(name) ) {
                    var opt_count = ++option_counts[ q_no ];
                    var $last_question = $('.js-poll-question-container:last');
                    if ( opt_count > $last_question.find('.js-poll-choice-container').length ) {
                        add_option( $last_question );
                    }
                }
            }

            var $inline = $('input[name=result_set-TOTAL_FORMS]').closest('.inline-related');
            var $last_item = $inline.find('tbody tr:last');
            var no_items = $inline.find('tbody tr').length;
            // add gallery items if necessary
            for (var i = no_items; i < desired_no; i++) {
                add_inline_item($inline, $last_item);
            }
            recount_inline_items($inline);
        }
        
        // Adjust the number of inputs (questions and their answer options) to fit the preset
        $('#quiz_form,#contest_form').unbind('preset_load_process.poll');
        $('#quiz_form,#contest_form').bind('preset_load_process.poll', load_poll_from_preset);
        
        // Display the loaded values
        $('#quiz_form,#contest_form').unbind('preset_load_completed.poll');
        $('#quiz_form,#contest_form').bind('preset_load_completed.poll', 
            function() {
                log_polls.log('displaying loaded values (poll)');
                $(':input.js-poll-choice-points').each( function() {
                    reflect_points_input_change(this);
                });
                $(':input.js-edit-poll-choice-text').each( function() {
                    reflect_answer_input_change(this);
                    reflect_choice_deletion(this);
                });
                $('.js-poll-question-text-container textarea').each( function() {
                    reflect_question_input_change(this);
                });
                // TODO remove values from inputs when adding new
                if ( /\/add\/$/.test(document.location) ) {
                    // question_set-3-choices-id  (array)
                    // question_set-3-id
                    // question_set-3-quiz
                    NewmanInline.remove_inlineadmin_element_value(
                        '.js-poll-question-container input[name^=question_set-]',
                        '[0-9]+-id$'
                    );
                    NewmanInline.remove_inlineadmin_element_value(
                        '.js-poll-question-container input[name^=question_set-]',
                        'quiz$'
                    );
                    NewmanInline.remove_inlineadmin_element_value(
                        '.js-poll-question-container input[name^=question_set-]',
                        'choices-id$',
                        '0'
                    );
                }

            }
        );
    }
    non_live_handlers();
    $(document).bind('content_added', non_live_handlers);
    
})();
