from django.urls import reverse_lazy
from django.views.generic import CreateView

from alert_messages.models import Message
from cards.forms import RequestEditForm
from cards.models import Request, TyreVendor
from users.forms import UserEmailAdd


class DashboardView(CreateView):
    template_name = 'dashboard.html'
    form_class = RequestEditForm
    model = Request

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_messages'] = Message.objects.filter(to_user_id=self.request.user.pk, is_read=False)
        context['last_message'] = Message.objects.filter(to_user_id=self.request.user.pk).first()
        context['requests'] = Request.objects.filter(author_id=self.request.user.pk).order_by('-date_created')[:5]
        context['tyre_vendors'] = TyreVendor.objects.all()
        context['form_add_email'] = UserEmailAdd()
        context['pay_alert_show'] = False
        if self.request.user.balance < 0:
            context['pay_alert'] = Message.objects.filter(to_user_id=self.request.user.pk, is_pay_alert=True,
                                                          is_pay_alert_hide=False).first()
            if context['pay_alert']:
                context['pay_alert_show'] = True
        return context

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.author_id = self.request.user.pk
        return super().form_valid(form)

    def get_success_url(self):

        return reverse_lazy('dashboard')
