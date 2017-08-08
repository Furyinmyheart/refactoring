jQuery(function($) {

    $('[data-toggle="tooltip"]').tooltip();

    var default_date_format = 'DD.MM.YYYY';

    $('#id_agreement_date').datetimepicker({format: default_date_format});
    $('#id_seller_birthday').datetimepicker({format: default_date_format});
    $('#id_seller_passport_date').datetimepicker({format: default_date_format});
    $('#id_repr_birthday').datetimepicker({format: default_date_format});
    $('#id_repr_document_issued_date').datetimepicker({format: default_date_format});
    $('#id_repr_passport_date').datetimepicker({format: default_date_format});
    $('#id_buyer_birthday').datetimepicker({format: default_date_format});
    $('#id_buyer_passport_date').datetimepicker({format: default_date_format});
    $('#id_pts_issued_date').datetimepicker({format: default_date_format});
    $('#id_srts_issued_date').datetimepicker({format: default_date_format});


    add_input_value_copy_btn($('#id_ts_body_num'), $('#id_ts_vin'), 'Скопировать VIN');
    add_input_value_copy_btn($('#id_ts_frame_num'), $('#id_ts_vin'), 'Скопировать VIN');

    var add_required_label = function () {
        $('#agreement_create_form').find('[required]').each(function () {
            var label_el = $(this).closest('.form-group').find('.control-label');
            label_el.html(label_el.html() + '<span class="text-danger">*</span>')
        });

    };
    add_required_label();

    $('#agreement_create_form')
        .on('change', '#id_is_repr', function(e){
            is_repr_update_view($(this));
        });

    var is_repr_update_view = function (is_repr_el) {
        var is_repr_group = $('.is_repr_group');
        if (is_repr_el.is(':checked')) {
            is_repr_group.removeClass('hidden');
        } else {
            is_repr_group.addClass('hidden');
        }
    };

    is_repr_update_view($('#id_is_repr'));

});