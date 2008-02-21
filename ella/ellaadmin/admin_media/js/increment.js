/* File increment.js
 * Autoincrement the value of selected fields.
 * Author: Maxim Izmaylov (izmaylov.maxim@netcentrum.cz)
 * Copyright: NetCentrum @2007
 * Requirements: jquery.js
 */

$(function(){
	$('.increment').each(function(i){
		this.id = 'inc-' + i;
		$(this).focus(function(){
			if($(this).val() == ''){
				var elId = $(this).attr('id').replace('inc-', '') - 0;
				var order = $('#inc-' + (elId - 1)).val();
				if(elId > 0 && order != '' && /^\d+$/.test(order)){
					$(this).val(order - 0 + 10);
				} else if(elId > 1 && (order == '' || /\w/.test(order))){
					for(var x = elId - 2; x >= 0; x--){
						order = $('#inc-' + x).val();
						if(order != '' && /^\d+$/.test(order)){
							$(this).val(order - 0 + 10);
							return;
						}
					}
					$(this).val(10);
				} else {
					$(this).val(10);
				}
			}
		}).keyup(function(event){
			var c = event.keyCode;
			var changeValue = function(element, change){
				var val = element.val();
				if(/\d+/.test(val)){
					element.val(val - 0 + change);
				}
			}
			switch(c){
				case 27:
					$(this).val('');
					$(this).blur();
					break;
				case 32:
					$(this).val('');
					$(this).blur();
					$(this).focus();
					break;
				case 38:
					changeValue($(this), 1);
					break;
				case 39:
					changeValue($(this), 1);
					break;
				case 37:
					changeValue($(this), -1);
					break;
				case 40:
					changeValue($(this), -1);
					break;
			}
		});
	});
});
