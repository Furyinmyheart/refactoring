from django.http import HttpResponse

from cards.export.black import BlackExport
from cards.export.color import ColorExport
from cards.export.stamp import make_stamp
from dc import settings
from .views import RequestDetailView

STAMP_BASE_FILE = './cards/export/templates/stamp_base.png'
STAMP_BASE_TEXT_WIDTH = 300


class ExportBaseView(RequestDetailView):
    export_class = None
    new_stantion_info = False
    draw_stamp = False
    draw_signature = False

    def get_export_class_kwargs(self, **kwargs):
        kwargs['stantion_info'] = self.get_object().get_print_stantion_info(user_settings_first=self.new_stantion_info)
        if self.draw_stamp:
            if kwargs['stantion_info'].get('stamp_image'):
                pass
            elif not kwargs['stantion_info'].get('stamp_image') and kwargs['stantion_info'].get('org_title'):
                kwargs['stantion_info']['stamp_image'] = make_stamp(kwargs['stantion_info'].get('org_title'),
                                                                    STAMP_BASE_FILE, STAMP_BASE_TEXT_WIDTH)
            else:
                kwargs['stantion_info']['stamp_image'] = settings.DEFAULT_STAMP_IMAGE
        else:
            kwargs['stantion_info']['stamp_image'] = None

        if self.draw_signature:
            kwargs['stantion_info']['signature_image'] = settings.DEFAULT_SIGNATURE_IMAGE
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="card{}.pdf"'.format(self.object.diagcard_num)

        return self.export_class(**self.get_export_class_kwargs(output=response, request=self.object)).compile()


class ExportBlackStampView(ExportBaseView):
    export_class = BlackExport
    draw_stamp = True
    draw_signature = True

class ExportBlackView(ExportBaseView):
    export_class = BlackExport


class ExportColorView(ExportBaseView):
    export_class = ColorExport


class ExportColorStampView(ExportBaseView):
    export_class = ColorExport
    draw_stamp = True
    draw_signature = True
