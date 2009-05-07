URLS = {
    test: function($target) {
        alert($target.attr('id'));
        location.href = 'http://google.com';
    }
};

// mapping for containers to the URLs that give out their base content (what's there when the page loads)
BASES = {
    //content: '/password_change/'
    content: '/nm/'
};
