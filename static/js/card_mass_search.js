$(function() {
    function search_next_card() {
        $('#card_search_result_table').find('tr[data-done="false"]').first().each(function () {
            if ($(this).data('num')) {

                $(this).find('.reg_num').html('<span class="fa fa-spinner fa-pulse fa-fw"></span>');
                load_task_result($(this).data('num'));
            }
        });
    }
    search_next_card();

    function load_task_result(num) {
        setTimeout(function(){
            $.ajax({
                type: "post",
                url: "/api/cards/search_card",
                dataType: 'json',
                data: {
                    'diagcard_num': num
                },
                success: function (data) {
                    var row = $('#card_search_result_table').find('tr[data-num="'+num+'"]');
                    row.attr('data-done','true');
                    row.find('.reg_num').html('');
                    row.find('.reg_num').text(data['reg_num']);
                    row.find('.ts_mark_model').text(data['ts_mark_model']);
                    row.find('.date_done').text(data['date_done']);
                    row.find('.expire_date').text(data['expire_date']);
                    row.find('.ts_reg_num').text(data['ts_reg_num']);
                    row.find('.stantion_name').text(data['stantion_name']);

                    search_next_card();
                },
                error: function (request, status) {
                    var res, ct = request.getResponseHeader("content-type") || '';
                    var erorr_msg;
                    if (ct.indexOf('json') > -1) {
                        var result = $.parseJSON(request.responseText);
                        // process the response here
                        erorr_msg = result['detail'];
                    } else {
                         erorr_msg  = request.responseText;
                    }
                    var row = $('#card_search_result_table').find('tr[data-num="'+num+'"]');
                    row.attr('data-done','true');
                    row.find('.reg_num').text('Ошибка: '+erorr_msg);
                    search_next_card();
                }
            });
        }, 5000);
    }

});