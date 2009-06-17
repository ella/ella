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

var getIdFromPath = function(path){
    var id;
    $.each(AVAILABLE_CONTENT_TYPES, function(i){
        if(this.path == '/'+path.replace('.','/')+'/'){
            id = i;
            return;
        }
    });
    return id;
}

MARKITUP_SETTINGS = {
    previewParserPath:    BASE_URL + 'nm/editor-preview/',
    previewParserVar:   "text",
    onShiftEnter:		{keepDefault:false, openWith:'\n\n'},
    markupSet: [
        { name: gettext('Italic'), className: 'italic', key: 'I', openWith: '*', closeWith: '*' },
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
            $('#id_box_obj_ct').val(getIdFromPath('photos.photo')).trigger('change');// 20 is value for photos.photo is the select box
            $('#lookup_id_box_obj_id').trigger('click');
        }},
        { name: gettext('Gallery'), className: 'gallery', call: function(){
            $('#rich-box').dialog('open');
            $('#id_box_obj_ct').val(getIdFromPath('galleries.gallery')).trigger('change');// 37 is value for galleries.gallery
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
            $('<div id="rich-photo-format" style="margin: 3px 0;">\n\
            <label for="id_box_photo_size" style="display:inline;">Velikost</label>\n\
            <select name="box_photo_size" id="id_box_photo_size">\n\
                <option value="velka">velká</option>\n\
                <option value="standard" selected="selected">standard</option>\n\
                <option value="mala">malá</option>\n\
            </select>\n\
            <label for="id_box_photo_format" style="display:inline;">Poměr stran</label>\n\
            <select name="box_photo_format" id="id_box_photo_format">\n\
                <option value="ctverec">čtverec</option>\n\
                <option value="obdelnik_na_sirku">obdélník na šířku</option>\n\
                <option value="obdelnik_na_vysku">obdélník na výšku</option>\n\
                <option value="nudle_na_sirku">nudle na šířku</option>\n\
                <option value="nudle_na_vysku">nudle na výšku</option>\n\
            </select></div>').hide().insertAfter('#lookup_id_box_obj_id');
            $('#id_box_obj_ct').bind('change', function(){
                if(getTypeFromPath($('#id_box_obj_ct').val()) == 'photos.photo'){
                    $('#rich-photo-format').show();
                } else {
                    $('#rich-photo-format').hide();
                }
            });
            $('#lookup_id_box_obj_id').bind('click', function(e){
                e.preventDefault();
                open_overlay(getTypeFromPath($('#id_box_obj_ct').val()), function(id){
                    $('#id_box_obj_id').val(id);
                });
            });
            $('#rich-object').bind('submit', function(e){
                e.preventDefault();
                if($('#id_box_obj_ct').val()){
                    var type = getTypeFromPath($('#id_box_obj_ct').val());
                    if(!!type){
                        var id = $('#id_box_obj_id').val() || '0';
                        var params = $('#id_box_obj_params').val().replace(/\n+/g, ' ');
                        // Add format and size info for photo
                        var addon = '';
                        if(getTypeFromPath($('#id_box_obj_ct').val()) == 'photos.photo'){
                            addon = '_'+$('#id_box_photo_size').val()+'_'+$('#id_box_photo_format').val();
                        }
                        // Insert code
                        $.markItUp({
                            openWith:'{% box inline'+addon+' for '+type+' with pk '+$('#id_box_obj_id').val()+' %}'+((params) ? '\n'+params+'\n' : '')+'{% endbox %}'
                        });
                        // Reset and close dialog
                        $('#rich-object').trigger('reset');
                        $('#rich-box').dialog('close');
                        $('#id_box_obj_ct').trigger('change');
                    }
                }
            });
        });
        $('#rich-box').dialog({
            modal: false,
            autoOpen: false,
            width: 420,
            height: 350
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
