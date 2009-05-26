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

mySettings = {
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
        { name: gettext('Photo'), className: 'photo', openWith: '> ' },
        { name: gettext('Gallery'), className: 'gallery', openWith: '> ' },
        { name: gettext('Box'), className: 'box', call: function(){
            $('#rich-box').dialog('open');
        }},
        { separator: '---------------' },
        { name: gettext('Preview'), call: 'preview', className: 'preview'}
    ]
}

$(function(){
    if(!$('#rich-box').length){
        $('<div id="rich-box" title="Box"></div>').hide().appendTo('body');
        $.getJSON('/static/newman_media/js/boxes.js', function(data){
            if(!!data){
                // HTML
                $('#rich-box').append('<form id="rich-object"></form>');
                $('#rich-object')
                    .append('<ul id="o-quick"></ul>')
                    .append('<div style="clear:left;"><select id="rich-select"></select></div>')
                    .append('<div><input type="text" id="rich-object-id" autocomplete="off" /> <input type="button" id="rich-object-choose" value="Choose" /></div>')
                    .append('<div><textarea id="rich-object-parameters" cols="30" rows="5"></textarea></div>')
                    .append('<div><input type="submit" value="Add box" /> <input type="reset" value="CLear" /></div>');
                $.each(data, function(i, item){
                    $('#rich-select').append('<option value="'+i+'" class="rich-object-'+i+'">'+item.name+'</option>');
                    if(item.quick){
                        $('#o-quick').append('<li title="'+i+'">'+item.name+'</li>');
                    }
                });
                // Events
                $('#rich-select').bind('change', function(){
                    if($(this).val() == 'photos.photo' || $(this).val() == 'galleries.gallery'){
                        $('#rich-object-choose').show();
                    } else {
                        $('#rich-object-choose').hide();
                    }
                });
                $('#o-quick').bind('click', function(e){
                    if(e.target.tagName.toLowerCase() == 'li'){
                        $('option[value='+$(e.target).attr('title')+']', '#rich-select').attr('selected', 'selected');
                        $('#rich-select').trigger('change');
                    }
                });
                $('#rich-object').bind('submit', function(e){
                    e.preventDefault();
                    var type = $('#rich-select').val();
                    if(!!type){
                        var id = $('#rich-object-id').val() || '0';
                        var params = $('#rich-object-parameters').val().replace(/\n+/g, ' ');
                        // Insert code
                        $.markItUp({
                            openWith:'{% box inline for '+type+' with pk '+$('#rich-object-id').val()+' %}\n'+params+'\n{% endbox %}'
                        });
                        // Reset and close dialog
                        $('#rich-object').trigger('reset');
                        $('#rich-box').dialog('close');
                    }
                }).bind('reset', function(){
                    $('#rich-object-choose').show();
                });
                $('#rich-object-choose').bind('click', function(){
                    open_overlay($('#rich-select').val(), function(id){
                        $('#rich-object-id').val(id);
                    });
                })
            }
        });
        $('#rich-box').dialog({
            modal: true,
            autoOpen: false,
            width: 400,
            height: 300
        });
    }
    $('.rich_text_area').markItUp(mySettings);
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
