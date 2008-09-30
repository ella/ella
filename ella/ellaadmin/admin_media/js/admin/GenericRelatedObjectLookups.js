/* File GenericRelatedObjectLookups.js
 * Adds to the any of input.target_id special button, which opens a window with a list of object (kind of an object defined in the corresponding select.target_ct)
 * Author: Maxim Izmaylov (izmaylov.maxim@netcentrum.cz)
 * Copyright: NetCentrum @2007
 * Requirements: jquery.js
 */

$(function(){
	var selects = $('select.target_ct');
	var targets = $('input.target_id');
	for(var x = 0; x < selects.length; x++){
		var nLt = document.getElementById('lookup_' + targets[x].id) || false;
		if(!nLt){
			var newLoupe = document.createElement('img');
			newLoupe.src = adminmediapath + 'img/admin/selector-search.gif';
			newLoupe.style.cssText = 'cursor: pointer;';
			newLoupe.id = 'lookup_' + targets[x].id;
			newLoupe.alt = x;
		} else {
			newLoupe = nLt;
		}
		targets[x].parentNode.appendChild(document.createTextNode(' '));
		targets[x].parentNode.appendChild(newLoupe);
		$('#lookup_' + targets[x].id).click(function(){
			var num = this.alt;
			if(this.className == 'new'){
				selects = $('select.target_ct');
			}
			var objectList = function(id){
				var name = id.replace(/^lookup_/, '').replace(/\./g, '___');
				var path = adminapps[selects[num].value].path.replace('.', '/');
				var prefix = typeof(admin_url) != "undefined" ? admin_url : '../../../';
				var addr = prefix + path + '/?pop=1';
				var win = window.open(addr, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
				win.focus();
			}
			if(selects[num].selectedIndex > 0){
				objectList(this.id);
			} else {
				try {
					$('#' + this.id.replace(/^lookup_/, '').replace(/\./g, '___').replace('_id', '_ct')).val(defaultId);
					objectList(this.id);
				} catch(e){
					alert('Choose "Target ct"');
				}
			}
		});
	}
});
