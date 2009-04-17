$(function(){
	var workers = {
		area: false,
		getSelection: function(){
			if(!!document.selection){
				return document.selection.createRange().text;
			} else if(!!this.area.setSelectionRange){
				return this.area.value.substring(this.area.selectionStart, this.area.selectionEnd);
			} else {
				return false;
			}
		},
		replaceSelection: function(text){
			if(!!document.selection){
				this.area.focus();
				var old = document.selection.createRange().text;
				var range = document.selection.createRange();
				if(old == ''){
					this.area.value += text;
				} else {
					range.text = text;
					range -= old.length - text.length;
				}
			} else if(!!this.area.setSelectionRange){
				var selection_start = this.area.selectionStart;
				this.area.value = this.area.value.substring(0, selection_start) + text + this.area.value.substring(this.area.selectionEnd);
				this.area.setSelectionRange(selection_start + text.length,selection_start + text.length);
			}
			//refresh(); Пока никакого рефреша!!!
			this.area.focus();
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
				txt += (m > 0 ? "\n" : '') + lines[m];
			}
			this.replaceSelection((before || '') + txt + (after || ''));
		},
		insertBeforeEachSelectedLine: function(text, before, after){
			this.injectEachSelectedLine(function(lines, line){
				lines.push(text + line);
				return lines;
			}, before, after);
		},
		underlineWith: function(symbol){
			var selection = this.getSelection();
			if(selection == ''){
				selection = 'Heading';
			}
			var str = '';
			for(var l = 0; l < Math.max(5, selection.length); l++){
				str += symbol;
			}
			this.replaceSelection(selection + "\n" + str + "\n");
		}
	}
	$.fn.richie = function(){
		$(this).each(function(){
			var area = this;
			$(area).wrap('<div class="rich_wrap"></div>');
			$(area).before('<ul class="rich_toolbar"></ul>');
			$('.rich_toolbar', $(area).parent()).append(
				$('<li class="i">I</li>'),
				$('<li class="b">B</li>'),
				$('<li class="a">A</li>'),
				$('<li class="h1">H1</li>'),
				$('<li class="h2">H2</li>'),
				$('<li class="ul">UL</li>'),
				$('<li class="ol">OL</li>'),
				$('<li class="quote">Quote</li>'),
				$('<li class="box">Box</li>')
			).bind('click',function(e){
				var button = $(e.target).attr('class');
				workers.area = area;
				switch(button){
					case 'i':
						workers.wrapSelection('""', '""', area); break;
					case 'b':
						workers.wrapSelection('"""', '"""'); break;
					case 'a':
						var selection = workers.getSelection();
						var response = prompt('Enter Link URL', '');
						if(response == null) return;
						workers.replaceSelection('(' + (response == '' ? 'http://link_url/' : response).replace(/^(?!(f|ht)tps?:\/\/)/,'http://') + ' ' + (selection == '' ? 'Link Text' : selection) + ')');
						break;
					case 'h1':
						workers.wrapSelection('= ', ' ='); break;
					case 'h2':
						workers.wrapSelection('== ', ' =='); break;
					case 'ul':
						workers.injectEachSelectedLine(function(lines, line){
							lines.push((e.shiftKey ? (line.match(/^\s*-/) ? line.replace(/\s/, '') : line.replace(/-/, '')) : (line.match(/\s*-/) ? ' ' : '-') + line));
							return lines;
						});
						break;
					case 'ol':
						workers.injectEachSelectedLine(function(lines, line){
							lines.push((e.shiftKey ? (line.match(/^\s*1\./) ? line.replace(/\s/, '') : line.replace(/1\./, '')) : (line.match(/\s*1\./) ? ' ' : '1\.') + line));
							return lines;
						});
						break;
					case 'quote':
						workers.wrapSelection("§§\n", "\n§§"); break;
						break;
					case 'box':
						console.log('build box'); break;
				}
			});
		});
	}
	$('.rich_text_area').richie();
});