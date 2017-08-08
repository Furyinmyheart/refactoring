jQuery(function($) {

    $('[data-toggle="tooltip"]').tooltip();

    $('#id_doc_issued_date').datetimepicker({
        format: 'DD.MM.YYYY'

    });

    var tyre_vendor_source = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: '/api/cards/tyre_vendor?q=%QUERY',
            wildcard: '%QUERY'
        }
    });


    $('#id_ts_tyre_vendor').typeahead(null,{
        name: 'tyre_vendor',
        display: 'name',
        source: tyre_vendor_source
    });

    var ts_mark_sources = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: '/api/cards/ts_mark?q=%QUERY',
            wildcard: '%QUERY'
        }
    });


    $('#id_ts_mark').typeahead(null,{
        name: 'ts_mark',
        display: 'name',
        source: ts_mark_sources
    });


    var ts_model_sources = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: '/api/cards/ts_model',
            //wildcard: '%QUERY',
            replace: function(url, uriEncodedQuery) {
                var res = (url + "?mark=" + $('#id_ts_mark').val() + "&q=" + encodeURIComponent(uriEncodedQuery));
                return res
            }
        }
    });


    $('#id_ts_model').typeahead(null,{
        name: 'ts_model',
        display: 'name',
        source: ts_model_sources
    });


    add_input_value_copy_btn($('#id_ts_body_num'), $('#id_ts_vin'), 'Скопировать VIN');
    add_input_value_copy_btn($('#id_ts_frame_num'), $('#id_ts_vin'), 'Скопировать VIN');

    $('#request_create_form')
        .on('change', '#id_user_type', function(e){
            user_type_update_view($(this));
        })
        .on('change', '#id_ts_category', function(e){
            ts_cateogory_update_view($(this));
        })
        .on('change', '#id_ts_fuel_type', function(e){
            ts_fuel_type_update_view($(this));
        })
    ;

    var user_type_update_view = function (user_type_el) {
        var org_title_group = $('#id_org_title').closest('.form-group');
        if (user_type_el.val()==2) {
            org_title_group.removeClass('hidden');
        } else {
            org_title_group.addClass('hidden');
        }
    };

    var ts_cateogory_update_view = function(ts_cateogory_el) {
        var ts_subcategory_group = $('#id_ts_sub_category').closest('.form-group');

        if (ts_cateogory_el.val()==2) {
            ts_subcategory_group.removeClass('hidden');
        } else {
            ts_subcategory_group.addClass('hidden');
        }

        var ts_mileage_group = $('#id_ts_mileage').closest('.form-group');
        var ts_fuel_type_group = $('#id_ts_fuel_type').closest('.form-group');
        var ts_dual_fuel_group = $('#id_ts_dual_fuel').closest('.form-group');
        if (ts_cateogory_el.val()==5 || ts_cateogory_el.val()==6) {
            ts_mileage_group.addClass('hidden');
            ts_fuel_type_group.addClass('hidden');
            ts_dual_fuel_group.addClass('hidden');
        } else {
            ts_mileage_group.removeClass('hidden');
            ts_fuel_type_group.removeClass('hidden');
            ts_dual_fuel_group.removeClass('hidden');
        }
    };

    var ts_fuel_type_update_view = function (fuel_type_el) {
        var ts_dual_fuel_group = $('#id_ts_dual_fuel').closest('.form-group');
        if (fuel_type_el.val()==1) {
            ts_dual_fuel_group.removeClass('hidden');
        } else {
            ts_dual_fuel_group.addClass('hidden');
        }
    };

    user_type_update_view($('#id_user_type'));
    ts_cateogory_update_view($('#id_ts_category'));
    ts_fuel_type_update_view($('#id_ts_fuel_type'));

    var add_required_label = function(){
        $('#request_create_form').find('[required]').each(function(){
            var label_el = $(this).closest('.form-group').find('.control-label');
            label_el.html(label_el.html()+'<span class="text-danger">*</span>')
        });

        var ts_mileage_label_el = $('#id_ts_mileage').closest('.form-group').find('.control-label');
        ts_mileage_label_el.html(ts_mileage_label_el.html()+'<span class="text-danger">*</span>')

        var id_org_title_label_el = $('#id_org_title').closest('.form-group').find('.control-label');
        id_org_title_label_el.html(id_org_title_label_el.html()+'<span class="text-danger">*</span>')
    };
    add_required_label();


    $('.requests').on('click','.btn-copy-new-data', function(e){
        var btn = $(this);
        $.ajax({
            type: "get",
            url: "/api/cards/request/"+btn.data('request-id'),
            data: {
                'is_read': true
            },
            dataType: 'json',
            success: function (data) {
                $('#id_user_type').val(data.user_type);
                $('#id_user_last_name').val(data.user_last_name);
                $('#id_user_first_name').val(data.user_first_name);
                $('#id_user_middle_name').val(data.user_middle_name);
                $('#id_org_title').val(data.org_title);
                $('#id_doc_type').val(data.doc_type);
                $('#id_user_contact').val(data.user_contact);
                $('#id_doc_serial').val(data.doc_serial);
                $('#id_doc_num').val(data.doc_num);
                $('#id_doc_issued_date').val(data.doc_issued_date);
                $('#id_doc_issued_by').val(data.doc_issued_by);
                $('#id_ts_category').val(data.ts_category);
                $('#id_ts_sub_category').val(data.ts_sub_category);
                $('#id_ts_reg_num').val(data.ts_reg_num);
                $('#id_ts_vin').val(data.ts_vin);
                $('#id_ts_body_num').val(data.ts_body_num);
                $('#id_ts_mark').typeahead('val', data.ts_mark);
                $('#id_ts_model').typeahead('val', data.ts_model);
                $('#id_ts_year').val(data.ts_year);
                $('#id_ts_mileage').val(data.ts_mileage);
                $('#id_ts_mass_base').val(data.ts_mass_base);
                $('#id_ts_mass_max').val(data.ts_mass_max);
                $('#id_ts_brakes_type').val(data.ts_brakes_type);
                $('#id_ts_tyre_vendor').typeahead('val', data.ts_tyre_vendor);
                $('#id_ts_fuel_type').val(data.ts_fuel_type);
                $('#id_ts_dual_fuel').val(data.ts_dual_fuel);
                $('#id_notes').val(data.notes);
                $('#id_ts_taxi').prop('checked', data.ts_taxi);
                $('#id_ts_training').prop('checked', data.ts_training);
                $('#id_ts_dangerous').prop('checked', data.ts_dangerous);
                $('#id_is_foreign').prop('checked', data.is_foreign);

                user_type_update_view($('#id_user_type'));
                ts_cateogory_update_view($('#id_ts_category'));
                ts_fuel_type_update_view($('#id_ts_fuel_type'));
            },
            error: function (request, status) {
                alert_status('danger', '<strong>Ошибка HTTP ' + status + ':</strong> ' + request.responseText);
            }
        });
    });
});