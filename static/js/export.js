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
    });


    $('input[name="daterange"]').on('cancel.daterangepicker', function (ev, picker) {
        $(this).val('');
        $('#id_daterange_start').val('');
        $('#id_daterange_end').val('');
    });


    add_select_all_btn($('#id_export_fields'), 'export_fields', 'Выделить всё');
    add_select_all_btn($('#id_user'), 'user', 'Выделить всё');


});