jQuery(function ($) {

    $('[data-toggle="tooltip"]').tooltip();

    $('select').select2();

    $('input[name="daterange"]').daterangepicker({
        locale: {
            format: 'DD.MM.YYYY',
            cancelLabel: 'Очистить',
            applyLabel: 'Применить'
        },
        "autoApply": true,
        "autoUpdateInput": false
    });

    $('input[name="daterange"]').on('apply.daterangepicker', function (ev, picker) {
        $('#id_daterange_start').val(picker.startDate.format('DD.MM.YYYY'));
        $('#id_daterange_end').val(picker.endDate.format('DD.MM.YYYY'));
        $(this).val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
    });

    $('input[name="daterange"]').on('cancel.daterangepicker', function (ev, picker) {
        $(this).val('');
        $('#id_daterange_start').val('');
        $('#id_daterange_end').val('');
    });

    $('#id_search_type').on('change', function (e) {
        if ($(this).val() == 'child') {
            $('#id_user').closest('div').removeClass('hidden');
            $('#id_user').trigger('change');
        } else {
            $('#id_user').closest('div').addClass('hidden');
        }
    });

});