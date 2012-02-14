$('.js-category-redir').live('click', function(evt) {
    if (evt.button != 0) return;
    var cat = GenericSuggestLib.get_value($('#id_category_suggest'));
    if (cat == '') return;
    adr('category/'+cat+'/', {evt:evt});
});
