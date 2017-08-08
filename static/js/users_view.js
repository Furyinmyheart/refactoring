jQuery(function($) {

    var comment_user_id;
    $('#users_change_comment')
        .on('show.bs.modal', function(e){
            var btn = $(e.relatedTarget);
            var user_full_name = btn.data('user-full-name');
            comment_user_id = btn.data('user-id');
            $('.users-comment-username').text(user_full_name);
            if (page == 'user_list') {
                $('#id_comment').val($('#users_list_row_' + comment_user_id).find('td:first-child>a').data('original-title'));
            } else if (page == 'user_view') {
                $('#id_comment').val($('#user_comment').html());
            }
        })
        .on('click', '#users-comment-save', function(e){
            var btn = $(this);
            btn.attr('disabled', 'disabled');

            $.ajax({
                type: "post",
                url: "/api/users/comment",
                data: {
                    'comment': $('#id_comment').val(),
                    'user': comment_user_id
                },
                dataType: 'json',
                success: function (data) {
                    if (page == 'user_list') {
                        $('#users_list_row_' + comment_user_id).find('td:first-child>a').attr('data-original-title', $('#id_comment').val());
                        $('#users_list_row_' + comment_user_id).find('td:first-child>a').attr('title', $('#id_comment').val());
                    } else if (page == 'user_view') {
                        $('#user_comment').html($('#id_comment').val());
                    }
                    $('#users_change_comment').modal('hide');
                    btn.removeAttr('disabled', 'disabled');
                },
                error: function (request, status) {
                    alert_status('danger', '<strong>Ошибка HTTP ' + status + ':</strong> ' + request.responseText);
                    btn.removeAttr('disabled', 'disabled');
                }
            });
        })
    ;

});