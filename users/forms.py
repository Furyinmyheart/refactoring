from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from mptt.forms import TreeNodeChoiceField

from users.models import MyUser


class UserCreateFrom(forms.ModelForm):
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )
    groups = forms.ModelChoiceField(queryset=Group.objects.all(), label='Статус')

    def __init__(self, parent, groups, *args, **kwargs):
        super(UserCreateFrom, self).__init__(*args, **kwargs)
        self.fields['groups'].queryset = groups
        self.parent_user = parent

    class Meta:
        model = MyUser
        fields = ['username', 'password', 'fio', 'email', 'groups', 'city', 'timezone',
                  'price_a', 'price_b', 'price_c', 'price_d', 'price_trailer', 'limit_per_day', 'credit',
                  'is_test_access', 'notification_settings', 'notification_weekly_day', 'is_https', ]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password'), self.instance)
        return password

    def clean_groups(self):
        data = self.cleaned_data['groups']
        return [data]

    def clean_credit(self):
        credit = self.cleaned_data['credit']
        if not credit:
            credit = 0
        return credit

    def clean(self):
        clean_data = super().clean()

        if self.cleaned_data.get('parent'):
            parent = self.cleaned_data['parent']
        else:
            parent = self.parent_user

        if self.cleaned_data.get('notification_settings') == 'weekly' and \
                not self.cleaned_data.get('notification_weekly_day'):
            self.add_error('notification_weekly_day', 'Это поле обязательно.')

        if not parent is None:
            price_fields = ('price_a', 'price_b', 'price_c', 'price_d', 'price_trailer', )
            for field in price_fields:
                if clean_data.get(field) < getattr(self.parent_user, field):
                    self.add_error(field, 'Цена не может быть меньше, чем у вышестоящего партнера.')
        return clean_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.parent = self.parent_user
            user.save()
            # install limits
            MyUser.objects.filter(pk=user.pk).update(requests_available=user.limit_per_day)
            self.save_m2m()
        return user


class UserCreateWithMoveFrom(UserCreateFrom):
    parent = TreeNodeChoiceField(label="Вышестоящий агент", queryset=MyUser.objects.all())

    def __init__(self, to_user_qs, *args, **kwargs):
        """
        rewrite initial parent_id
        """
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = to_user_qs

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            if self.cleaned_data['parent']:
                user.parent = self.cleaned_data['parent']

            user.save()

            # install limits
            MyUser.objects.filter(pk=user.pk).update(requests_available=user.limit_per_day)
            self.save_m2m()
        return user


class UserCreateAdminForm(UserCreateWithMoveFrom):
    use_only_self_stantions = forms.BooleanField(label="Может использовать только свои станции", required=False)
    can_delete_card = forms.BooleanField(label="Может удалять заявки", required=False)

    class Meta:
        model = MyUser
        fields = ['username', 'password', 'fio', 'email', 'groups', 'city', 'timezone',
                  'price_a', 'price_b', 'price_c', 'price_d', 'price_trailer', 'limit_per_day', 'credit',
                  'is_test_access', 'notification_settings', 'notification_weekly_day', 'is_https',
                  'stantion_order_type', ]


class UserEditForm(UserCreateFrom):
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        required=False,
        help_text=_("Введите новый пароль, чтобы изменить."),
    )
    groups = forms.ModelChoiceField(queryset=Group.objects.all(), label='Статус')

    class Meta:
        model = MyUser
        fields = ['username', 'password', 'fio', 'email', 'groups', 'city', 'timezone', 'is_active',
                  'price_a', 'price_b', 'price_c', 'price_d', 'price_trailer', 'limit_per_day', 'credit',
                  'is_test_access', 'use_only_self_stantions', 'notification_settings', 'notification_weekly_day',
                  'is_https', 'is_archive', ]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            self.instance.username = self.cleaned_data.get('username')
            password_validation.validate_password(self.cleaned_data.get('password'), self.instance)
        return password

    def clean_groups(self):
        data = self.cleaned_data['groups']
        return [data]

    def save(self, commit=True):
        user = super().save(commit=False)

        update_fields = self.Meta.fields.copy()
        if 'groups' in update_fields:
            update_fields.remove('groups')
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])
        elif 'password' in update_fields:
            update_fields.remove('password')
        if commit:
            user.save(update_fields=update_fields)
            self.save_m2m()
        return user


class UserEditWithMoveForm(UserEditForm):
    parent = TreeNodeChoiceField(label="Вышестоящий агент", queryset=MyUser.objects.none())

    def __init__(self, to_user_qs, *args, **kwargs):
        """
        rewrite initial parent_id
        """
        initial = kwargs.pop('initial', {})
        instance = kwargs.get('instance')
        initial['parent'] = instance.parent
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = to_user_qs.exclude(pk=instance.pk)

    def save(self, commit=True):
        user = super().save(commit=False)

        update_fields = self.Meta.fields.copy()
        if 'groups' in update_fields:
            update_fields.remove('groups')
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])
        elif 'password' in update_fields:
            update_fields.remove('password')
        if commit:
            # detect update parent
            if self.cleaned_data['parent']:
                # move only if change
                if not user.parent or self.cleaned_data['parent'].pk != user.parent_id:
                    user.parent = self.cleaned_data['parent']
                    update_fields.append('parent')
            else:
                # set root, if not root already
                if not user.is_root_node():
                    user.parent = None
                    update_fields.append('parent')

            user.save(update_fields=update_fields)
            self.save_m2m()
        return user


class UserEditAdminForm(UserEditWithMoveForm):
    use_only_self_stantions = forms.BooleanField(label="Может использовать только свои станции", required=False)
    can_delete_card = forms.BooleanField(label="Может удалять заявки", required=False)

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        instance = kwargs.get('instance')
        initial['use_only_self_stantions'] = instance.use_only_self_stantions
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    class Meta:
        model = MyUser
        fields = ['username', 'password', 'fio', 'email', 'groups', 'city', 'timezone', 'is_active',
                  'price_a', 'price_b', 'price_c', 'price_d', 'price_trailer', 'limit_per_day', 'credit',
                  'is_test_access', 'use_only_self_stantions', 'notification_settings', 'notification_weekly_day',
                  'is_https', 'stantion_order_type', 'is_archive', ]


class UserMoveChildForm(forms.Form):
    parent = TreeNodeChoiceField(label="Вышестоящий агент", queryset=MyUser.objects.all())

    def __init__(self, user_qs, from_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = user_qs.exclude(pk__in=from_user.get_descendants(
            include_self=True).values_list('pk'))


class UserMoveChildSelectUserForm(forms.Form):
    parent = TreeNodeChoiceField(label="Текущий вышестоящий агент", queryset=MyUser.objects.none())

    def __init__(self, to_user_qs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = to_user_qs


class UserEmailChange(forms.Form):
    password = forms.CharField(label=_("Password"), strip=False,
                               widget=forms.PasswordInput(attrs={'autofocus': ''}))
    email = forms.EmailField(label='Email')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        """
        Validates that the password field is correct.
        """
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise forms.ValidationError(
                _("Your old password was entered incorrectly. Please enter it again."),
                code='password_incorrect',
            )
        return password


class UserEmailAdd(forms.Form):
    email = forms.EmailField(label='Email')
