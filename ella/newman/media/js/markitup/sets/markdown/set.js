// -------------------------------------------------------------------
// markItUp!
// -------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// -------------------------------------------------------------------
// MarkDown tags example
// http://en.wikipedia.org/wiki/Markdown
// http://daringfireball.net/projects/markdown/
// -------------------------------------------------------------------
// Feel free to add more tags
// -------------------------------------------------------------------\

MARKITUP_SETTINGS = {
    previewParserPath:    BASE_URL + 'nm/editor-preview/',
    previewParserVar:   "text",
    onShiftEnter:		{keepDefault:false, openWith:'\n\n'},
    markupSet: [
        { name: gettext('Italic'), className: 'italic', key: 'I', openWith: '_', closeWith: '_' },
        { name: gettext('Bold'), className: 'bold', key: 'B', openWith: '**', closeWith: '**' },
        { separator: '---------------' },
        { name: gettext('Link'), className: 'url', key: 'L', openWith:'[', closeWith:']([![Url:!:http://]!] "[![Title]!]")', placeHolder: 'Text odkazu' },
        { separator: '---------------' },
        { name: gettext('Head 1'), className: 'h1', key:'1', placeHolder: 'Nadpis 1. úrovně', closeWith: function(markItUp) { return miu.markdownTitle(markItUp, '=') } },
        { name: gettext('Head 2'), className: 'h2', key:'2', placeHolder: 'Nadpis 2. úrovně', closeWith: function(markItUp) { return miu.markdownTitle(markItUp, '-') } },
        { name: gettext('Head 3'), className: 'h3', key:'3', placeHolder: 'Nadpis 3. úrovně', openWith: '### ' },
        { separator: '---------------' },
        { name: gettext('List unordered'), className: 'list-bullet', openWith: '- ' },
        { name: gettext('List ordered'), className: 'list-numeric', openWith:function(markItUp) {
            return markItUp.line+'. ';
        }},
        { separator: '---------------' },
        { name: gettext('Quote'), className: 'quote', openWith: '> ' },
        { separator: '---------------' },
        { name: gettext('Photo'), className: 'photo', call: function(){
            $('#rich-box').dialog('open');
			$('#id_box_obj_ct').val(20).trigger('change');// 20 is value for photos.photo is the select box
        }},
        { name: gettext('Gallery'), className: 'gallery', call: function(){
            $('#rich-box').dialog('open');
			$('#id_box_obj_ct').val(37).trigger('change');// 37 is value for galleries.gallery
        }},
        { name: gettext('Box'), className: 'box', call: function(){
            $('#rich-box').dialog('open');
        }},
        { separator: '---------------' },
        { name: gettext('Preview'), call: 'preview', className: 'preview'}
    ]
}

$(function(){
	var getTypeFromPath = function(id){
		var path = AVAILABLE_CONTENT_TYPES[id].path;
		return path.substring(1,path.length - 1).replace('/','.');
	}
	if(!$('#rich-box').length){
		$('<div id="rich-box" title="Box"></div>').hide().appendTo('body');
		$('#rich-box').load(BASE_URL+'nm/editor-box/', function(){
			$('#lookup_id_box_obj_id').bind('click', function(e){
				e.preventDefault();
				open_overlay(getTypeFromPath($('#id_box_obj_ct').val()), function(id){
					$('#id_box_obj_id').val(id);
				});
			});
			$('#rich-object').bind('submit', function(e){
				e.preventDefault();
				var type = getTypeFromPath($('#id_box_obj_ct').val());
				if(!!type){
					var id = $('#id_box_obj_id').val() || '0';
					var params = $('#id_box_obj_params').val().replace(/\n+/g, ' ');
					// Insert code
					$.markItUp({
						openWith:'{% box inline for '+type+' with pk '+$('#id_box_obj_id').val()+' %}\n'+params+'\n{% endbox %}'
					});
					// Reset and close dialog
					$('#rich-object').trigger('reset');
					$('#rich-box').dialog('close');
				}
			});
			$('<label for="id_box_photo_size">Velikost:</label><select id="id_box_photo_size" name="box_photo_size"><option>malá</option><option>malá, velká, střední</option><option>malá, velká, střední</option></select>')
			$('#id_box_obj_ct').bind('change', function(){
				if(getTypeFromPath($('#id_box_obj_ct').val()) == 'photos.photo'){
					
				} else {
					
				}
			});
		});
		$('#rich-box').dialog({
			modal: true,
			autoOpen: false,
			width: 400,
			height: 300
		});
	}
	$('.rich_text_area').markItUp(MARKITUP_SETTINGS);
});

// mIu nameSpace to avoid conflict.
miu = {
	markdownTitle: function(markItUp, char) {
		heading = '';
		n = $.trim(markItUp.selection||markItUp.placeHolder).length;
		for(i = 0; i < n; i++) {
			heading += char;
		}
		return '\n'+heading;
	}
}