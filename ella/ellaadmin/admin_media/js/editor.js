/* File editor.js
 * Rich text editor for ELLA
 * Author: Maxim Izmaylov (izmaylov.maxim@netcentrum.cz)
 * Copyright: NetCentrum @2007
 * Requirements: jquery.js, showdown.js
 */

function refresh(){
	if(!nopreview){
		window.clearTimeout(onChangeTimeout);
		onChangeTimeout = window.setTimeout(function(){
			// Replace objects
			var boxRegexp = /{% box[^{]*{% endbox %}/g;
			bm = area.value.replace(boxRegexp, '<div class="box-object" title="Edit">Object</div>');
			// Save object properties for further use
			boxes = Array();
			if(area.value.match(boxRegexp)){
				$.each(area.value.match(boxRegexp), function(i, box){
					var type = box.match(/for (\w*\.?\w*) with/)[1];
					var method = box.match(/box (\w+)/)[1];
					var id = box.match(/pk (\w+) %/)[1];
					var params = box.match(/\}([\s\S]*)\{/)[1];
					boxes.push({
						type: type,
						method: method,
						id: id,
						parameters: params,
						full: box
					});
				});
			}
			// Then markdown
			$('div#rich_preview').html(converter.makeHtml(bm));
			// Then get all object in a preview pane and bind them with their codes in the textarea
			$('div.box-object').each(function(i){
				$(this).bind('click', function(){
					if(boxes && i < boxes.length){
						build(boxes[i]);
					}
				});
			});
		}, 50);
	}
}

var handlers = {
	getSelection: function(){
		if(!!document.selection){
			return document.selection.createRange().text;
		} else if(!!area.setSelectionRange){
			return area.value.substring(area.selectionStart, area.selectionEnd);
		} else {
			return false;
		}
	},
	replaceSelection: function(text){
		if(!!document.selection){
			area.focus();
			var old = document.selection.createRange().text;
			var range = document.selection.createRange();
			if(old == ''){
				area.value += text;
			} else {
				range.text = text;
				range -= old.length - text.length;
			}
		} else if(!!area.setSelectionRange){
			var selection_start = area.selectionStart;
			area.value = area.value.substring(0, selection_start) + text + area.value.substring(area.selectionEnd);
			area.setSelectionRange(selection_start + text.length,selection_start + text.length);
		}
		refresh();
		area.focus();
	},
	wrapSelection: function(before, after){
		this.replaceSelection(before + this.getSelection() + after);
	},
	insertBeforeSelection: function(text){
		this.replaceSelection(text + this.getSelection());
	},
	insertAfterSelection: function(text){
		this.replaceSelection(this.getSelection() + text);
	},
	injectEachSelectedLine: function(callback, before, after){
		var lines = Array();
		var txt = '';
		$.each(this.getSelection().split("\n"), function(i, line){
			callback(lines, line);
		});
		for(var m = 0; m < lines.length; m++){
			txt += lines[m] + '\n';
		}
		this.replaceSelection((before || '') + txt + (after || ''));
	},
	insertBeforeEachSelectedLine: function(text, before, after){
		this.injectEachSelectedLine(function(lines, line){
			lines.push(text + line);
			return lines;
		}, before, after);
	}
}

var Editor = function(){
	// Toolbar
	$('<ul id="rich_toolbar"></ul>').insertBefore(area).append(
		$('<li id="b">B</li>').bind('click', function(){
			handlers.wrapSelection('**', '**');
		}),
		$('<li id="i">I</li>').bind('click', function(){
			handlers.wrapSelection('*', '*');
		}),
		$('<li id="a">A</li>').bind('click', function(){
			var selection = handlers.getSelection();
			var response = prompt('Enter Link URL', '');
			if(response == null) return;
			handlers.replaceSelection('[' + (selection == '' ? 'Link Text' : selection) + '](' + (response == '' ? 'http://link_url/' : response).replace(/^(?!(f|ht)tps?:\/\/)/,'http://') + ')');
		}),
		$('<li id="h1">H1</li>').bind('click', function(){
			var selection = handlers.getSelection();
			if(selection == ''){
				selection = 'Heading';
			}
			var str = '';
			for(var l = 0; l < Math.max(5, selection.length); l++){
				str += '=';
			}
			handlers.replaceSelection(selection + "\n" + str + "\n");
		}),
		$('<li id="h2">H2</li>').bind('click', function(){
			var selection = handlers.getSelection();
			if(selection == ''){
				selection = 'Heading';
			}
			var str = '';
			for(var l = 0; l < Math.max(5, selection.length); l++){
				str += '-';
			}
			handlers.replaceSelection(selection + "\n" + str + "\n");
		}),
		$('<li id="ul">UL</li>').bind('click', function(event){
			handlers.injectEachSelectedLine(function(lines, line){
				lines.push((event.shiftKey ? (line.match(/^\*{2,}/) ? line.replace(/^\*/, '') : line.replace(/^\*\s/, '')) : (line.match(/\*+\s/) ? '*' : '* ') + line));
				return lines;
			});
		}),
		$('<li id="ol">OL</li>').bind('click', function(event){
			var i = 0;
			handlers.injectEachSelectedLine(function(lines, line){
				if(!line.match(/^\s+$/)){
					++i;
					lines.push((event.shiftKey ? line.replace(/^\d+\.\s/, '') : (line.match(/\d+\.\s/) ? '' : i + '. ') + line));
				}
				return lines;
			});
		}),
		$('<li id="quote">Quote</li>').bind('click', function(event){
			handlers.injectEachSelectedLine(function(lines,line){
				lines.push((event.shiftKey ? line.replace(/^\> /, '') : '> ' + line));
				return lines;
			});
		}),
		$('<li id="code">Code</li>').bind('click', function(event){
			handlers.injectEachSelectedLine(function(lines, line){
				lines.push((event.shiftKey ? line.replace(/    /, '') : '    ' + line));
				return lines;
			});
		}),
		$('<li id="box">Box</li>').bind('click', build)
	);
	// Preview
	converter = (typeof(Showdown) != 'undefined') ? new Showdown.converter : false;
	if(area.className.indexOf('nopreview') == -1 && converter){
		$('<div id="rich_preview"></div>').insertAfter(area);
		$(area).
		bind('keyup', refresh).
		bind('paste', refresh).
		bind('input', refresh);
		refresh();
		nopreview = false;
	} else {
		nopreview = true;
	}
}

/* ------| !Boxes functions |------ */
function build(box){
	// If there's edit mode for one of the boxes on the page
	if(box){
		edit = box.full;
	} else {
		edit = '';
	}
	// Wrapper
	back = $('<div id="boxWrapper"></div>').appendTo('body').css({
		height: (document.documentElement.scrollHeight || document.body.scrollHeight) + 'px'
	});
	// Build "select" from the list of objects
	var options = '';
	$.each(adminapps, function(i, item){
		options += '<option value="' + i + '"' + ((box.type && item.path == box.type) ? ' selected="selected"' : '') + '>' + item.name + '</option>';
	});
	// Main div
	pane = $('<div id="boxPane"></div>').
	appendTo('body').
	append(
		$('<a id="boxPaneClose" href="#close">&times;</a>').bind('click', { key: false }, destroy),
		$('<form action="" method="post"></form>').
		append(
			$('<h1>Vložit objekt</h1>'),
			$('<div class="title">Typ objektu</div>'),
			$('<div class="input"><select name="type">' + options + '</select></div>'),
			$('<div class="title">Nejčastěji používané typy:</div>'),
			$('<div class="input" id="quick"></div>').append(
				$('<a href="#fotka">Fotka</a>&nbsp;').bind('click', function(event){
					objectSelect(event, 'photos.photo');
				}),
				$('<a href="#fotogalerie">Fotogalerie</a>').bind('click', function(event){
					objectSelect(event, 'galleries.gallery');
				}),
				$('<a href="#infobox">Infobox</a>').bind('click', function(event){
					objectSelect(event, 'articles.infobox');
				}),
				/*$('<a href="#video">Video</a>').bind('click', function(event){
					objectSelect(event, 'videos.video');
				}),*/
				$('<a href="#clanek">Článek</a>').bind('click', function(event){
					objectSelect(event, 'articles.article');
				}),
				$('<a href="#anketa">Anketa</a>').bind('click', function(event){
					objectSelect(event, 'polls.poll');
				})
			),
			$('<div class="title">Mód</div>'),
			$('<div class="input"><input type="text" name="method" id="method" value="' + ((box.method) ? box.method : 'inline') + '" /></div>'),
			$('<div class="title">Identifikátor</div>'),
			$('<div class="input"><input type="text" name="id" id="id" value="' + ((box.id) ? box.id : '') + '" />&nbsp;</div>').append($('<input type="button" name="search" id="search" />').bind('click', objectSelect)),
			$('<div class="title">Parametry</div>'),
			$('<div class="input"><textarea name="parameters" cols="40" rows="5">' + ((box.parameters) ? box.parameters.replace(/^\n*/g, '').replace(/\n*$/g, '') : '') + '</textarea></div>'),
			$('<div id="submit"><input type="submit" value="Vložit" /></div>')
		).bind('submit', objectInsert)
	);
	// Effects
	back.animate({ opacity: 0.75 }, 'normal');
	pane.animate({ opacity: 1 }, 'normal');
	// Events
	$('select[name="type"]').bind('change', function(){
		$('input#id').val('');
	});
	$('body').bind('keypress', { key: true }, destroy);
}

function destroy(event){
	if(event.keyCode == '27' || !event.data.key){
		$('#boxWrapper, #boxPane').remove();
		$('body').unbind('keypress', destroy);
		event.preventDefault();
	}
}

function objectSelect(event, type){
	if(type){
		$('select[name="type"] option').each(function(){
			if(type == adminapps[this.value].path){
				this.selected = 'selected';
			}
		});
	}
	var path = ((type) ? type : adminapps[$('select[name="type"]').val()].path).replace('.', '/');
	var addr = '../../../' + path + '/?pop=1';
	var win = window.open(addr, 'id', 'height=500,width=800,resizable=yes,scrollbars=yes');
	win.focus();
	event.preventDefault();
}

function objectInsert(event){
	// Define type and id
	var type = adminapps[$('select[name="type"]').val()].path;
	var id = $('input#id').val() || 0;
	var method = $('input#method').val() || 'inline';
	// Result
	var obj = '{% box ' + method + ' for ' + type + ' with pk ' + id + ' %}' + (($('textarea[name="parameters"]').val()) ? '\n' + $('textarea[name="parameters"]').val().replace(/^\n*/g, '').replace(/\n*$/g, '') + '\n' : '') + '{% endbox %}';
	if(edit){
		var tv = area.value.replace(edit, obj);
		area.value = tv;
		refresh();
	} else {
		handlers.wrapSelection('', obj);
	}
	$('#boxWrapper, #boxPane').remove();
	$('body').unbind('keypress', destroy);
	event.preventDefault();
}
/* ------| !Boxes functions |------ */

$(function(){
	on = -1;
	pause = false;
	nopreview = false;
	onChangeTimeout = false;
	// include additional CSS
	$('<link rel="stylesheet" type="text/css" href="/static/admin_media/css/editor.css" />').appendTo('head');
	// Append editor to textareas
	$('textarea.rich_text_area').each(function(i){
		$(this).bind('focus', { element: this }, function(event){
			if(on != i){
				$('#rich_preview, #rich_toolbar').remove();
				area = event.data.element;
				new Editor();
				on = i;
			}
		});
	});
});
