// ----------------------------------------------------------------------------
// CzechTile set for MarkItUp!
//
// Based on example wiki set (http://markitup.jaysalvat.com/examples/wiki/)
// ----------------------------------------------------------------------------
CTTASettings = {
    nameSpace:          "ctta",
    previewParserPath:  "preview",
    previewParserVar:   "text",
    onCtrlEnter:       { keepDefault: false,
        replaceWith: '\n\n' },
    onShiftEnter:      { keepDefault: false,
        replaceWith: function (markitup) { return lac.append(markitup); } },
    markupSet:  [
	    { name: 'Zvýrazněně', className: 'italic', key: 'I',
	        openWith: '""', closeWith: '""' },
	    { name: 'Silně', className: 'bold', key: 'B',
	        openWith: '"""', closeWith: '"""' },
        { separator: '---------------' },
        { name: 'Odkaz', className: 'url',
            openWith: "([![URL odkazu:!:http://]!] ", closeWith:')', placeHolder: 'Text odkazu' },
        { separator: '---------------' },
        { name: 'Nadpis 1', className: 'h1', key:'1',
            openWith:'= ', closeWith:' =', placeHolder: 'Nadpis 1. úrovně' },
        { name:'Nadpis 2', className: 'h2', key:'2',
            openWith:'== ', closeWith:' ==', placeHolder: 'Nadpis 2. úrovně' },
        { name:'Nadpis 3', className: 'h3', key:'3',
            openWith:'=== ', closeWith:' ===', placeHolder: 'Nadpis 3. úrovně' },
        { separator: '---------------' },
        { name: 'Seznam s odrážkami', className: 'list-bullet',
            openWith: '\n - ',
            afterInsert: function (markitup) { return lac.afterInsert(markitup); } },
        { name: 'Číslovaný seznam', className: 'list-numeric', 
            openWith: '\n 1. ',
            afterInsert: function (markitup) { return lac.afterInsert(markitup); } },
        { separator: '---------------' },
        { name: 'Сitát', className: 'quote',
            openWith: '§§\n', closeWith: '\n§§' },
        { name: 'Box', className: 'box', call: function(){
			$('<div id="q1" title="Privet!">123</div>').dialog({
				modal: true
			});
			//((box inline photos.photo 209869 show_title=1 show_authors=1 show_detail=1))
		}},
        { name: 'Náhled', call: 'preview', className: 'preview'}
    ]
}

// list auto-creation
lac = {
    append: function (markitup) {
        return this.token ? this.token : '\n';
    },
    afterInsert: function (markitup) {
        this.token = markitup.openWith;
    },
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
		$('<form action="" method="post" id="mainForm"></form>').
		append(
			$('<h1>Vložit objekt</h1>'),
			$('<div class="title">Typ objektu</div>'),
			$('<div class="input"></div>').append(
				$('<select name="type">' + options + '</select>').change(function(){
					if($('option', this)[this.selectedIndex].innerHTML == 'Photo'){
						photo();
					} else {
						$('#photo').hide('normal', function(){
							$(this).remove();
						});
					}
				})
			),
			$('<div class="title">Nejčastěji používané typy:</div>'),
			$('<div class="input" id="quick"></div>').append(
				$('<a href="#fotka">Fotka</a>&nbsp;').bind('click', function(event){
					objectSelect(event, 'photos.photo');
					photo();
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
					link2object();
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
	// Object "photo"
	var parseParameters = function(checked, key){
		var lines = $('textarea[name="parameters"]').val().split('\n');
		var parameters = {};
		$.each(lines, function(i, line){
			var keyVal = line.split(':', 2);
			parameters[keyVal[0]] = keyVal[1];
		});
		if(checked && !parameters[key]){
			parameters[key] = '1';
			setParameters(parameters);
		} else if(!checked && parameters[key]){
			setParameters(parameters, key);
		}
	}
	var setParameters = function(parameters, exclude){
		var val = '';
		$.each(parameters, function(name, param){
			if(name != exclude && name != '' && param){
				val += name + ':' + param + '\n';
			}
		});
		$('textarea[name="parameters"]').val(val.replace(/^\n/, '').replace(/\n$/, ''));
	}
	var photo = function(){
		var p = $('textarea[name="parameters"]').val();
		$('#mainForm').append(
			$('<div id="photo"><h2>Možnosti</h2></div>').append(
				$('<div></div>').append(
					$('<input type="checkbox" id="title"' + ((p.indexOf('show_title') != -1) ? ' checked="checked"' : '') + ' /> <label for="title">Název</label>').change(function(){
						parseParameters(this.checked, 'show_title');
					})
				),
				$('<div></div>').append(
					$('<input type="checkbox" id="detail"' + ((p.indexOf('show_detail') != -1) ? ' checked="checked"' : '') + ' /> <label for="detail">Detailní náhled</label>').change(function(){
						parseParameters(this.checked, 'show_detail');
					})
				),
				$('<div></div>').append(
					$('<input type="checkbox" id="description"' + ((p.indexOf('show_description') != -1) ? ' checked="checked"' : '') + ' /> <label for="description">Popis</label>').change(function(){
						parseParameters(this.checked, 'show_description');
					})
				),
				$('<div></div>').append(
					$('<input type="checkbox" id="authors"' + ((p.indexOf('show_authors') != -1) ? ' checked="checked"' : '') + ' /> <label for="authors">Autoři</label>').change(function(){
						parseParameters(this.checked, 'show_authors');
					})
				)
			)
		);
		$('#photo').css({'display' : 'block', 'opacity' : '0'}).animate({ opacity: 1 }, 'normal');
	}
	if(box.type && box.type == 'photos.photo'){photo();}
	var link2object = function(){
		myFORM=document.getElementById('mainForm');
		myFORM.method.value='link';
		myFORM.parameters.value='text:'+myFORM.parameters.value;
	}
	if(box.type && box.type == 'articles.article'){link2object();}
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