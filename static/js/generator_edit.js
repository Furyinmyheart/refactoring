$(function() {

    $('#generator_edit_form')
        .on('click', '#forms-generator-add-regnum', function (e) {
            e.preventDefault();

            var type = 'form';
            var selector = '.forms-generator-regnums>tbody>tr:last';
            var newElement = $(selector).clone(true);
            var total = $('#id_' + type + '-TOTAL_FORMS').val();
            newElement.find(':input').each(function () {
                var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
                var id = 'id_' + name;
                $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
            });
            newElement.find('label').each(function () {
                var newFor = $(this).attr('for').replace('-' + (total - 1) + '-', '-' + total + '-');
                $(this).attr('for', newFor);
            });
            total++;
            $('#id_' + type + '-TOTAL_FORMS').val(total);
            $(selector).after(newElement);

        })
    ;

});