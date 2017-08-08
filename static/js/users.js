jQuery(function($) {


    add_input_value_duplicate_btn(
        $('#id_price_a'),
        [$('#id_price_b'), $('#id_price_c'), $('#id_price_d'), $('#id_price_trailer')],
        'Продублировать цены'
    );

    var add_required_label = function(){
        $('#user_form').find('[required]').each(function(){
            var label_el = $(this).closest('.form-group').find('.control-label');
            label_el.html(label_el.html()+'<span class="text-danger">*</span>')
        });
    };
    add_required_label();

    $('#id_notification_settings').on('change', function (e) {
        update_notification_settings_view($(this).val());
    });

    function update_notification_settings_view(value) {
        if (value == 'weekly') {
            $('#id_notification_weekly_day').closest('div.form-group').removeClass('hidden');
        } else {
            $('#id_notification_weekly_day').closest('div.form-group').addClass('hidden');
        }
    }

    update_notification_settings_view($('#id_notification_settings').val());

});