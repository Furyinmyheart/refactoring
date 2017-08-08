jQuery(function($) {
      $('[data-toggle="tooltip"]').tooltip();

    $('.messages')
        .on('click', '.message-set-read', function(e){
            e.preventDefault();
            var btn = $(this);
            $.ajax({
                type: "put",
                url: "/api/messages/read/"+btn.data('message-id'),
                data: {
                    'is_read': true
                },
                dataType: 'json',
                success: function (data) {
                    btn.closest('tr').find('.unread-label').remove();
                    btn.addClass('hidden');
                },
                error: function (request, status) {
                    alert_status('danger', '<strong>Ошибка HTTP ' + status + ':</strong> ' + request.responseText);
                }
            });
        })
    ;

});