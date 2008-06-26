/* File listing.js
 * Author: Izmaylov Maxim
 * Copyright: NetCentrum @2007
 * Requirements: jquery.js
 */

function placeButton(){
	// Select <select>
	var byCategory = false;
	var byEmptiness = false;
	var suitable = false;
	$('select.listing_category').each(function(i){
		// Select the <select> with exactly the same category as the "Kategorie" field
		if(!(byCategory || byCategory === 0) && this.selectedIndex == document.getElementById('id_category').selectedIndex){
			byCategory = i;
		}
		// Select the first empty select
		if(!(byEmptiness || byEmptiness === 0) && this.selectedIndex == ''){
			byEmptiness = i;
		}
	});
	// Check if there's at least one suiteable select
	if(byCategory || byCategory === 0){
		suitable = byCategory
	} else if(byEmptiness || byEmptiness === 0){
		suitable = byEmptiness
	}
	suitable_select = $('select.listing_category')[suitable];
	suitable_multi = $('#id_core-placement-target_ct-target_id-' + suitable + '-listings')[0];
	// Place a button behind it
	if(suitable_select){
		$(suitable_select.parentNode).append(
			$('<input type="button" class="ignore" value="&uarr; Main category">').bind('click', function(){
				a = document.getElementById('id_category').selectedIndex
				suitable_select.selectedIndex = a;
				suitable_multi.selectedIndex = a-1;
			})
		);
	}
}

$(placeButton);

