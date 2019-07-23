add_referrer = function(url, current_title) {
    if (url.includes('?'))  { var conn = '&' } else { var conn = '?' };
    var new_url = url.concat(conn, 'ref=', current_title, '&ref_scroll=', window.scrollY);
    return new_url;
};

add_referrer_and_load = function(url, current_title) {
    window.location.href = add_referrer(url, current_title);
};
