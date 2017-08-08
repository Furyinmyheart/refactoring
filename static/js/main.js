$(function() {

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }


    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        traditional: true
    });

    alert_status = function(type,message,icon){
        $.notify({
            icon: icon,
            message: message

        }, {
            type: type,
            timer: 4000,
            placement: {
                from: "top",
                align: "center"
            }
        });
    };

    add_input_value_duplicate_btn = function (el, target, text) {

        var btn = $('<a href="#">'+text+' <span class="fa fa-chevron-down"></span></a>');

        btn.insertAfter(el);

        btn.on('click', function(e){
            e.preventDefault();

            var value = el.val();
            $.each(target, function(k, target_el){
                target_el.val(value)
            })
        });
    };

    add_input_value_copy_btn = function (el, source, text) {

        var btn = $('<a href="#"><span class="fa fa-copy"></span> '+text+'</a>');

        btn.insertAfter(el);

        btn.on('click', function(e){
            e.preventDefault();
            var value = source.val();
            el.val(value);
        });
    };

    add_select_all_btn = function (output, checkbox_name, text) {

        var btn = $('<a href="#" data-checked="0"><span class="fa fa-check"></span> '+text+'</a>');

        $('<div></div>').html(btn).insertBefore(output);

        btn.on('click', function(e){
            e.preventDefault();

            var is_checked = $(this).data('checked');

            is_checked = !is_checked;
            $(this).data('checked', is_checked);

            $('[name="'+checkbox_name+'"]').prop('checked', is_checked);
        });
    };

    var t;
    function startTime() {

        document.getElementById('calendar_time').innerHTML = moment().format('L') + ' '+ moment().format('LTS');
        t = setTimeout(function () {
            startTime()
        }, 500);
    }

    startTime();

});