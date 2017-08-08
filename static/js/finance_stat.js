jQuery(function ($) {

    $('select').select2();

    $('input[name="daterange"]').daterangepicker({
        timePicker: true,
        timePicker24Hour: true,
        locale: {
            format: 'DD.MM.YYYY HH:mm',
            cancelLabel: 'Очистить',
            applyLabel: 'Применить'
        }
    }, function(start, end, label){
        $('#id_daterange_start').val(start.format('DD.MM.YYYY HH:mm'));
        $('#id_daterange_end').val(end.format('DD.MM.YYYY HH:mm'));
        $(this).val(start.format('DD.MM.YYYY HH:mm') + ' - ' + end.format('DD.MM.YYYY HH:mm'));

        $('#id_daterange_end').closest("form").submit();
    });

    $('input[name="daterange"]').on('cancel.daterangepicker', function (ev, picker) {
        $(this).val('');
        $('#id_daterange_start').val('');
        $('#id_daterange_end').val('');
    });


});