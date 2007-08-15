/* File editor.js
 * This script turns any textarea to a WYSISYM (markdown syntax) editor by appending classname 'editor' to it
 * Author: Maxim Izmaylov [izmaylov.maxim@netcentrum.cz]
 * Powered with the Prototype javascript library [www.prototypejs.org] and MagicDom [http://amix.dk/blog/viewEntry/19199]
 * Requirements: prototype.js, MagicDOM.js, showdown.js
 */

Editor = function(area){
	this.container = area.parentNode;
	nopreview = false;
	onChangeTimeoutLength = 50;
	onChangeTimeout = false;
	preview = {
		init:			function(area, container){
			converter = (typeof(Showdown) != 'undefined') ? new Showdown.converter : false;
			if(!area.className.include('nopreview') && converter){
				this.container = container;
				preView = DIV({'class': 'preview'}, '');
				var NS = area.nextSiblings();
				if(NS.length < 1){
					this.container.appendChild(preView);
				} else {
					this.container.insertBefore(preView, NS[0]);
				}
				Event.observe(area, 'keyup', this.refresh.bind(this));
				Event.observe(area, 'paste', this.refresh.bind(this));
				Event.observe(area, 'input', this.refresh.bind(this));
				this.refresh();
				nopreview = false;
			} else {
				nopreview = true;
			}
		},
		refresh:			function(){
			if(!nopreview){
				if(onChangeTimeout){
					window.clearTimeout(onChangeTimeout);
				}
				onChangeTimeout = window.setTimeout(function(){
					preView.update(converter.makeHtml(area.value));
				}, onChangeTimeoutLength);
			}
		}
	}
	this.toolBar = {
		enabled:		true,
		button:			function(container, text, title, callback, attrs){
			handlers = {
				getValue: function(){
					return area.value;
				},
				getSelection: function(){
					if(!!document.selection)
						return document.selection.createRange().text;
					else if(!!area.setSelectionRange)
						return area.value.substring(area.selectionStart,area.selectionEnd);
					else
						return false;
				},
				replaceSelection: function(text){
					if(!!document.selection){
						area.focus();
						var old = document.selection.createRange().text;
						var range = document.selection.createRange();
						if(old == ''){
							area.value += text;//area.innerHTML in original. Doesn't work in opera.
						} else {
							range.text = text;
							range -= old.length - text.length;
						}
					} else if(!!area.setSelectionRange){
						var selection_start = area.selectionStart;
						area.value = area.value.substring(0, selection_start) + text + area.value.substring(area.selectionEnd);
						area.setSelectionRange(selection_start + text.length,selection_start + text.length);
					}
					preview.refresh();
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
					this.replaceSelection((before || '') + $A(this.getSelection().split("\n")).inject([],callback).join("\n") + (after || ''));
				},
				insertBeforeEachSelectedLine: function(text, before, after){
					this.injectEachSelectedLine(function(lines, line){
						lines.push(text + line);
						return lines;
					}, before, after);
				}
			}
			if(container){
				this.callback = callback;
				var newButton = LI({'title': title}, text);
				if(MagicDOM.isDict(attrs)){
					for(k in attrs){
						var attr = attrs[k];
						if(k == "style"){
							newButton.style.cssText = attr;
						} else if(k == "class" || k == 'className'){
							newButton.className = attr;
						} else {
							newButton.setAttribute(k, attr);
						}
					}
				}
				newButton.onclick = function(){return false;}
				Event.observe(newButton, 'click', callback.bindAsEventListener(area));
				container.appendChild(newButton);
			}
		},
		init:			function(area, container){
			this.container = container;
			if(this.enabled){
				// Construct the entire toolbar first,
				this.bar = UL({'class': 'toolbar'}, '');
				// Add buttons...
				/* --- Bold ---*/
				new this.button(this.bar, 'B', 'Makes the selection bold', function(){
					handlers.wrapSelection('**','**');
				}, {'class': 'b'});
				/* --- Italic ---*/
				new this.button(this.bar, 'I', 'Makes the selection italic', function(){
					handlers.wrapSelection('*','*');
				}, {'class': 'i'});
				/* --- URL ---*/
				new this.button(this.bar, 'A', 'Inserts a hyperlink', function(){
					var selection = handlers.getSelection();
					var response = prompt('Enter Link URL','');
					if(response == null) return;
					handlers.replaceSelection('[' + (selection == '' ? 'Link Text' : selection) + '](' + (response == '' ? 'http://link_url/' : response).replace(/^(?!(f|ht)tps?:\/\/)/,'http://') + ')');
				}, {'class': 'a'});
				/* --- Image ---*/
				new this.button(this.bar, 'IMG', 'Inserts an image', function(){
					var selection = handlers.getSelection();
					var response = prompt('Enter Image URL','');
					if(response == null) return;
					handlers.replaceSelection('![' + (selection == '' ? 'Image Alt Text' : selection) + '](' + (response == '' ? 'http://image_url/' : response).replace(/^(?!(f|ht)tps?:\/\/)/,'http://') + ')');
				}, {'class': 'img'});
				/* --- Headings ---*/
				new this.button(this.bar, 'H1', 'Inserts header', function(){
					var selection = handlers.getSelection();
					if(selection == ''){
						selection = 'Heading';
					}
					var str = '';
					(Math.max(5, selection.length)).times(function(){
						str += '-';
					});
					handlers.replaceSelection(selection + "\n" + str + "\n");
				}, {'class': 'h'});
				/* --- Unordered list ---*/
				new this.button(this.bar, 'UL', 'Unordered list', function(event){
					handlers.injectEachSelectedLine(function(lines, line){
						lines.push((event.shiftKey ? (line.match(/^\*{2,}/) ? line.replace(/^\*/, '') : line.replace(/^\*\s/,'')) : (line.match(/\*+\s/) ? '*' : '* ') + line));
						return lines;
					});
				}, {'class': 'ul'});
				/* --- Ordered list ---*/
				new this.button(this.bar, 'OL', 'Ordered list', function(event){
					var i = 0;
					handlers.injectEachSelectedLine(function(lines, line){
						if(!line.match(/^\s+$/)){
							++i;
							lines.push((event.shiftKey ? line.replace(/^\d+\.\s/, '') : (line.match(/\d+\.\s/) ? '' : i + '. ') + line));
						}
						return lines;
					});
				}, {'class': 'ol'});
				/* --- Quote ---*/
				new this.button(this.bar, 'Quote', 'Inserts a quotation', function(event){
					handlers.injectEachSelectedLine(function(lines,line){
						lines.push((event.shiftKey ? line.replace(/^\> /, '') : '> ' + line));
						return lines;
					});
				}, {'class': 'ol'});
				/* --- Code ---*/
				new this.button(this.bar, 'Code', 'Inserts a code block', function(event){
					handlers.injectEachSelectedLine(function(lines, line){
						lines.push((event.shiftKey ? line.replace(/    /, '') : '    ' + line));
						return lines;
					});
				}, {'class': 'ol'});
				// And then show it
				this.container.insertBefore(this.bar, area);
			}
		}
	}
	preview.init(area, this.container);
	this.toolBar.init(area, this.container);
}

Event.observe(window, 'load', function(){
	var elements = document.getElementsByClassName('rich_text_area');
	if(elements.length > 0){
		var e = elements[0];
		var tagname = new String(e.tagName);
		if(tagname.toLowerCase() == 'textarea'){
			var newEditor = new Editor(e);
		}
	}
});
