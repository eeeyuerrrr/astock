'use strict';

let init_ajax_csrf = function () {
    $.ajaxSetup({
        headers: {"X-CSRFToken": getCookie("csrftoken")}
    });
};

let init_ajax_err_handelr = function () {
    $(document).ajaxError(function (event, jqxhr, settings, thrownError) {
        try{
            alert_ajax_error_detail(jqxhr);
        }catch(e){
        }
    });
}

let alert_ajax_error_detail = function (xhr) {
    if (xhr && xhr.responseText && xhr.status == 400) {
        let err = $.parseJSON(xhr.responseText);
        if (err.detail) {
            $.dialog(err.detail);
        }
    }
};

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