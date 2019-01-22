'use strict';

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

let init_ajax_csrf = function () {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
};

let init_ajax_err_handelr = function () {
    $(document).ajaxError(function (event, jqxhr, settings, thrownError) {
        try {
            if (jqxhr && jqxhr.responseText) {
                let err = $.parseJSON(jqxhr.responseText);
                if (err.detail) {
                    $.dialog(err.detail);
                }
            }
        } catch (e) {
        }
    });
}


let getCookie = function (c_name) {
    if (document.cookie.length > 0) {
        let c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            let c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
};