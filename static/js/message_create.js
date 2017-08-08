jQuery(function($) {
    $('#messages_create_form')
        .on('change', '#id_to_type', function(e){
            upd_select_user_view();
        })
    ;

    function upd_select_user_view() {
        var select_el = $('#id_to_type');
        if (select_el.val() == 'select') {
            select_el.closest('.form-group').next('.form-group').removeClass('hidden')
        } else {
            select_el.closest('.form-group').next('.form-group').addClass('hidden')
        }
    }

    upd_select_user_view();

});