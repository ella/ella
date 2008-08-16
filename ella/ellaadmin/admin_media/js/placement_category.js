function placeButton(){

	var byCategory = false;
	var byEmptiness = false;
	var suitable = false;

	$('input#id_core-placement-target_ct-target_id-0-category').each(function(i){
		// Select the input with exactly the same category as the "Kategorie" field
		if(!(byCategory || byCategory === 0) && this.value == document.getElementById('id_category').value){
			byCategory = i;
		}
		// Select the first empty select
		if(!(byEmptiness || byEmptiness === 0) && this.value == ''){
			byEmptiness = i;
		}
	});
	// Check if there's at least one suiteable select
	if(byCategory || byCategory === 0){
		suitable = byCategory
	} else if(byEmptiness || byEmptiness === 0){
		suitable = byEmptiness
	}
	suitable_input = $('input#id_core-placement-target_ct-target_id-0-category')[suitable];
//	suitable_multi = $('#id_core-placement-target_ct-target_id-' + suitable + '-listings')[0];
	// Place a button behind it
	if(suitable_input){
		$(suitable_input.parentNode).append(
			$('<input type="button" value="&uarr; Main">').bind('click', function(){
				a = document.getElementById('id_category').value
				suitable_input.value = a;
//				suitable_multi.selectedIndex = a-1;
			})
		);
	}
}

$(placeButton);

