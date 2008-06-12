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
		suitable = $('select.listing_category')[byCategory];
	} else if(byEmptiness || byEmptiness === 0){
		suitable = $('select.listing_category')[byEmptiness];
	}
	// Place a button behind it
	if(suitable){
		$(suitable.parentNode).append(
			$('<input type="button" class="ignore" value="&uarr; Main category">').bind('click', function(){
				suitable.selectedIndex = document.getElementById('id_category').selectedIndex;
			})
		);
	}
}

$(placeButton);
