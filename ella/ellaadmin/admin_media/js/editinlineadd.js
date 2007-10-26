/* File editinlinehead.js
 * Add new objects on the fly
 * Script searches for a tables that are the childrens of the fieldset.module, which previous siblings have an id that ends with '-COUNT'.
 * Script automatically adds buttons '+1' and '+10' to the end of the every table that meet the conditions above. That buttons increases number of objects (rows) of the table by cloning the first <tr> of that table which have a class name row1 or row2.
 * All the event listeners of the new object would be updated in order to save functionality.
 * Author: Maxim Izmaylov (izmaylov.maxim@netcentrum.cz)
 * Copyright: NetCentrum @2007
 * Requirements: jquery.js
 */

$(function(){
	row = Array();
	$('fieldset.module').each(function(index){
		if(/-COUNT$/.test($(this).prev().attr('id'))){
			var counter = $(this).prev();
			var table = $($(this).parent().find('table')[0]);
			row[index] = table.find('tr:last').clone();
			$(this).append(
				$('<input type="button" value="+1">').click(function(){
					addObject(table, index, counter, 1);
				}),
				$(' <input type="button" value="+10">').click(function(){
					addObject(table, index, counter, 10);
				})
			);
		}
	});
});

function addObject(table, rowIndex, counter, count){
	var rows = table.find('tr.row1, tr.row2').length;
	for(var x = 0; x < count; x++){
		var newRow = row[rowIndex].clone();
		newRow.appendTo(table);
		if(rows % 2){
			newRow.removeClass('row1').addClass('row2');
		} else {
			newRow.removeClass('row2').addClass('row1');
		}
		newRow.find('input, select, img, a').each(function(){
			if($(this).attr('id')){
				$(this).attr('id', $(this).attr('id').replace(/-\d+/, '-' + (rows + x)));
			}
			if($(this).attr('name')){
				$(this).attr('name', $(this).attr('name').replace(/-\d+/, '-' + (rows + x)));
			}
			if($(this).attr('alt')){
				$(this).attr({
					alt: $(this).attr('alt').replace(/\d+/, rows + x),
					class: 'new'
				});
			}
		});
		newRow.find('.ignore').hide();
		rows++;
	}
	// Update value of the binded hidden input
	counter.val(rows + count);
}