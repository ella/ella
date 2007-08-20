// Handles related-objects functionality: lookup link for raw_id_fields
// and Add Another links.

function showRelatedObjectLookupPopup(triggeringLink) {
    var name = triggeringLink.id.replace(/^lookup_/, '');
    // IE doesn't like periods in the window name, so convert temporarily.
    name = name.replace(/\./g, '___');
    var href;
    if (triggeringLink.href.search(/\?/) >= 0) {
        href = triggeringLink.href + '&pop=1';
    } else {
        href = triggeringLink.href + '?pop=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function dismissRelatedLookupPopup(win, chosenId){
    var name = win.name.replace(/___/g, '.');
    var elem = document.getElementById(name);
    if (elem.className.indexOf('vRawIdAdminField') != -1 && elem.value) {
        elem.value += ',' + chosenId;
    } else {
        document.getElementById(name).value = chosenId;
    }
    win.close();
}

function showAddAnotherPopup(triggeringLink) {
    var name = triggeringLink.id.replace(/^add_/, '');
    name = name.replace(/\./g, '___');
    href = triggeringLink.href
    if (href.indexOf('?') == -1) {
        href += '?_popup=1';
    } else {
        href  += '&_popup=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function dismissAddAnotherPopup(win, newId, newRepr) {
    var name = win.name.replace(/___/g, '.');
    var elem = document.getElementById(name);
    if (elem) {
        if (elem.nodeName == 'SELECT') {
            var o = new Option(newRepr, newId);
            elem.options[elem.options.length] = o;
            o.selected = true;
        } else if (elem.nodeName == 'INPUT') {
            elem.value = newId;
        }
    } else {
        var toId = name + "_to";
        elem = document.getElementById(toId);
        var o = new Option(newRepr, newId);
        SelectBox.add_to_cache(toId, o);
        SelectBox.redisplay(toId);
    }
    win.close();
}

/* ----| Makes makes this life easier! |---- */
/*paths = {
	0: '123',
	1: '321',
	2: '333'
}*/

function observe(element, event, observer){
	if(element.addEventListener){
		element.addEventListener(event, observer, false);
	} else if(element.attachEvent){
		element.attachEvent('on' + event, observer);
	}
}

observe(window, 'load', function(){
	selects = new Array();
	targets = new Array();
	loupes = new Array();
	// Selects
	var allSelects = document.getElementsByTagName('select');
	for(var s = 0; s < allSelects.length; s++){
		if(allSelects[s].id.indexOf('-target_ct') != -1){
			selects.push(allSelects[s]);
		}
	}
	// Targets
	var allTargets = document.getElementsByTagName('input');
	for(var s = 0; s < allTargets.length; s++){
		if(allTargets[s].id.indexOf('-target_id') != -1){
			targets.push(allTargets[s]);
			var nLt = document.getElementById('lookup_' + allTargets[s].id) || false;
			if(!nLt){
				var newLoupe = document.createElement('img');
				newLoupe.src = adminmediapath + 'img/admin/selector-search.gif';
				newLoupe.style.cssText = 'cursor: pointer;';
				newLoupe.id = 'lookup_' + allTargets[s].id;
				newLoupe.alt = loupes.length;
			} else {
				newLoupe = nLt;
			}
			observe(newLoupe, 'click', function(){
				var num = this.alt;
				if(selects[num].selectedIndex > 0){
					var name = this.id.replace(/^lookup_/, '').replace(/\./g, '___');
					var path = paths[selects[num].value];


					var addr = '../../../' + path + '/?pop=1';
					var win = window.open(addr, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
					win.focus();
				} else {
					alert('Choose "Target ct"');
				}
			});
			loupes.push(newLoupe);
			allTargets[s].parentNode.appendChild(document.createTextNode(' '));
			allTargets[s].parentNode.appendChild(newLoupe);
		}
	}
});
