jQuery(function ($) {

    $('[data-toggle="popover"]').popover();
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


});