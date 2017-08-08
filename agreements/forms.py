from django import forms
from django.core.validators import RegexValidator

from .models import Agreement

repr_fields_required = ('repr_user_last_name', 'repr_user_first_name', 'repr_birthday', 'repr_document_verified_by',
                        'repr_passport_seria', 'repr_passport_number', 'repr_passport_date', 'repr_passport_org',
                        'repr_address_reg', 'repr_address_fact')


class AgreementCreateForm(forms.ModelForm):
    ts_vin = forms.CharField(label='VIN', required=False, max_length=255,
                             help_text='Если отсутствует, то не заполняется',
                             validators=[RegexValidator('^[0-9A-HJ-NPR-Za-hj-npr-z]+$',
                                                        message='Введен запрещенный символ')])

    class Meta:
        model = Agreement
        fields = '__all__'
        widgets = {
            'seller_passport_org': forms.Textarea(attrs={'rows': 1}),
            'seller_address_reg': forms.Textarea(attrs={'rows': 1}),
            'seller_address_fact': forms.Textarea(attrs={'rows': 1}),
            'repr_document_verified_by': forms.Textarea(attrs={'rows': 1}),
            'repr_passport_org': forms.Textarea(attrs={'rows': 1}),
            'repr_address_reg': forms.Textarea(attrs={'rows': 1}),
            'repr_address_fact': forms.Textarea(attrs={'rows': 1}),
            'buyer_passport_org': forms.Textarea(attrs={'rows': 1}),
            'buyer_address_reg': forms.Textarea(attrs={'rows': 1}),
            'buyer_address_fact': forms.Textarea(attrs={'rows': 1}),
        }

    def clean(self):
        cleaned_data = super().clean()

        is_repr = cleaned_data.get('is_repr')
        if is_repr:
            for field in repr_fields_required:
                if not cleaned_data.get(field):
                    self.add_error(field, _('This field is required.'))

        return cleaned_data
