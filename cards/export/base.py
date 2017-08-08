from io import BytesIO
from textwrap import wrap

from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from cards.models import Request, MAX_TEST_VALUE


class CardExportBase:
    output = None
    pages = []
    na_value = '-'
    template = ""

    def __init__(self, output, request: Request, stantion_info=None):
        self.packet = BytesIO()
        # create a new PDF with Reportlab
        self.can = canvas.Canvas(self.packet)
        self.output = output
        self.request = request

        self.stantion_info = stantion_info

        pdfmetrics.registerFont(TTFont('Arial', './static/fonts/ArialRegular.ttf'))

    def compile(self):

        self.make_data_first_page()
        self.can.showPage()

        self.make_data_second_page()
        self.can.showPage()

        self.can.save()

        # move to the beginning of the StringIO buffer
        self.packet.seek(0)
        new_pdf = PdfFileReader(self.packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open(self.template, "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)

        page = existing_pdf.getPage(1)
        page.mergePage(new_pdf.getPage(1))
        output.addPage(page)
        # finally, write "output" to a real file
        output.write(self.output)
        return self.output

    def make_data_first_page(self):
        self.draw_card_reg_num(self.request.diagcard_num)
        self.draw_expire_date(self.request.expire_date.strftime('%d%m%Y'))

        if self.stantion_info and self.stantion_info['org_title'] and self.stantion_info['reg_number']:
            self.draw_operator("{}, № в реестре {}".format(self.stantion_info['org_title'],
                                                           self.stantion_info['reg_number']))
            self.draw_operator_address(self.stantion_info['point_address'])

        self.draw_first_check()

        # ts
        self.draw_ts_reg_num(self.request.ts_reg_num)
        self.draw_ts_vin(self.request.ts_vin)
        self.draw_ts_frame_num(self.request.ts_frame_num)
        self.draw_ts_body_num(self.request.ts_body_num)
        self.draw_mark_model(self.request.ts_mark, self.request.ts_model)
        self.draw_ts_category(
            "{} ({})".format(self.request.get_ts_category_display(), self.request.get_ts_category_okp()))
        self.draw_ts_year(str(self.request.ts_year))
        self.draw_doc("{type_display} {request.doc_serial} № {request.doc_num} выдан "
                      "{request.doc_issued_by} "
                      "{doc_issued_date}".format(request=self.request, type_display=self.request.get_doc_type_display(),
                                                 doc_issued_date=self.request.doc_issued_date.strftime('%d.%m.%Y')))

        test_values = self.request.get_test_values()
        for code in range(1, MAX_TEST_VALUE + 1):
            if code not in test_values:
                self.draw_test_value_na(code)

    def make_data_second_page(self):
        self.draw_notes(self.request.notes)
        self.draw_ts_mass_base(self.request.ts_mass_base)

        fuel_type = ''
        if self.request.ts_dual_fuel:
            fuel_type = self.request.get_ts_dual_fuel_display()
        elif self.request.ts_fuel_type:
            fuel_type = self.request.get_ts_fuel_type_display()
        self.draw_ts_fuel_type(fuel_type)
        self.draw_ts_brakes_type(self.request.get_ts_brakes_type_display() if self.request.ts_brakes_type else '')
        self.draw_ts_tyre_vendor(self.request.ts_tyre_vendor)

        self.draw_ts_mass_max(self.request.ts_mass_max)
        self.draw_ts_mileage(self.request.ts_mileage)

        self.draw_user_fio("{request.user_last_name} {request.user_first_name} {request.user_middle_name}"
                           "".format(request=self.request))

        self.draw_date_done(self.request.date_done.strftime('%d%m%Y'))
        self.draw_diagcard_num(self.request.diagcard_num)
        if self.stantion_info:
            self.draw_export_fio(self.stantion_info['expert_name'])
            if self.stantion_info.get('stamp_image'):
                self.draw_stamp(image=self.stantion_info['stamp_image'])
            if self.stantion_info.get('signature_image'):
                self.draw_signature(image=self.stantion_info['signature_image'])

    def draw_card_reg_num(self, diagcard_num: str = ''):
        y = 793
        for index, x in enumerate((88, 102, 116, 130, 144, 159, 173, 187, 201, 215, 229, 243, 257, 272, 286)):
            self.can.drawString(x, y, diagcard_num[index])

    def draw_expire_date(self, expire_date: str = ''):
        y = 793
        for index, x in enumerate((422, 436, 450, 465, 480, 494, 508, 522)):
            self.can.drawString(x, y, expire_date[index])

    def draw_operator(self, operator: str):
        self.can.setFont("Arial", 10)
        self.can.drawString(159, 768, operator)

    def draw_operator_address(self, address: str):
        self.can.setFont("Arial", 10)
        self.can.drawString(159, 747, address)

    def draw_first_check(self):
        self.can.setFont("Arial", 10)
        self.can.drawString(121, 731, 'X')

    def draw_second_check(self):
        self.can.setFont("Arial", 10)
        self.can.drawString(539, 731, 'X')

    def draw_ts_reg_num(self, ts_reg_num: str):
        self.can.setFont("Arial", 7)
        self.can.drawString(121, 722, ts_reg_num)

    def draw_ts_vin(self, ts_vin: str):
        self.can.setFont("Arial", 7)
        if not ts_vin:
            ts_vin = 'Отсутствует'
        self.can.drawString(121, 711, ts_vin)

    def draw_ts_frame_num(self, ts_frame_num: str):
        self.can.setFont("Arial", 7)
        if not ts_frame_num:
            ts_frame_num = 'Отсутствует'
        self.can.drawString(121, 700, ts_frame_num)

    def draw_ts_body_num(self, ts_body_num: str):
        self.can.setFont("Arial", 7)
        if not ts_body_num:
            ts_body_num = 'Отсутствует'
        self.can.drawString(121, 689, ts_body_num)

    def draw_mark_model(self, mark: str, model: str):
        self.can.setFont("Arial", 7)
        self.can.drawString(377, 722, "{} {}".format(mark, model))

    def draw_ts_category(self, category: str):
        self.can.setFont("Arial", 7)
        self.can.drawString(377, 711, category)

    def draw_ts_year(self, year: str):
        self.can.setFont("Arial", 7)
        self.can.drawString(377, 695, year)

    def draw_doc(self, doc: str):
        self.can.setFont("Arial", 7)
        self.can.drawString(200, 675, doc)

    def draw_ts_mass_base(self, ts_mass_base: int):
        self.can.setFont("Arial", 7)
        self.can.drawString(160, 572, "{} кг".format(ts_mass_base))

    def draw_ts_fuel_type(self, ts_fuel_type: str):
        self.can.setFont("Arial", 7)
        self.can.drawString(160, 561, ts_fuel_type)

    def draw_ts_brakes_type(self, ts_brakes_type: str):
        self.can.setFont("Arial", 7)
        self.can.drawString(160, 549, ts_brakes_type)

    def draw_ts_tyre_vendor(self, ts_tyre_vendor: str):
        self.can.setFont("Arial", 7)
        self.can.drawString(160, 537, ts_tyre_vendor)

    def draw_ts_mass_max(self, ts_mass_max: int):
        self.can.setFont("Arial", 7)
        self.can.drawString(457, 572, "{} кг".format(ts_mass_max))

    def draw_ts_mileage(self, ts_mileage: int):
        self.can.setFont("Arial", 7)
        self.can.drawString(457, 561, "{} км".format(ts_mileage))

    def draw_user_fio(self, fio: str):
        self.can.setFont("Arial", 10)
        self.can.drawString(170, 363, fio)

    def draw_date_done(self, date_done: str):
        y = 302
        for index, x in enumerate((58, 72, 86, 101, 115, 129, 143, 157)):
            self.can.drawString(x, y, date_done[index])

    def draw_diagcard_num(self, diagcard_num: str):
        self.can.setFont("Arial", 10)
        self.can.drawString(263, 304, diagcard_num)

    def draw_export_fio(self, expert_fio: str):
        self.can.setFont("Arial", 10)
        self.can.drawString(155, 276, expert_fio)

    def draw_test_value_na(self, code: int):
        if code <= 22:
            # col 1
            x = 198
            y_base = [601, 573, 545, 520, 493, 465, 442, 416, 387, 360, 339, 297, 269, 248, 225, 201, 180, 126, 102, 83,
                      60, 36]
            y = y_base[code - 1]

        elif 23 <= code <= 42:
            # col 2
            x = 378
            y_base = [630, 573, 545, 520, 465, 442, 416, 387, 360, 339, 297, 269, 248, 225, 201, 154, 126, 102, 83,
                      60]
            y = y_base[code - 22 - 1]
        elif 43 <= code <= 67:
            # col 3
            x = 576
            y_base = [630, 601, 573, 545, 520, 493, 465, 442, 416, 387, 360, 339, 320, 297, 269, 248, 225, 201, 180,
                      154, 126, 102, 83, 60, 36]
            y = y_base[code - 42 - 1]
        else:
            raise ValueError
        self.can.drawString(x, y, self.na_value)

    def draw_stamp(self, image):
        if type(image) is BytesIO:
            image = ImageReader(image)
        self.can.drawImage(image, 430, 30, width=125, height=125, mask='auto',
                           preserveAspectRatio=True)

    def draw_signature(self, image):
        if type(image) is BytesIO:
            image = ImageReader(image)
        self.can.drawImage(image, 80, 15, width=125, height=125, mask='auto',
                           preserveAspectRatio=True)

    def draw_notes(self, notes):
        t = self.can.beginText()
        t.setFont('Arial', 10)
        t.setTextOrigin(20, 635)

        t.textLines("\n".join(wrap(notes, 105)))
        self.can.drawText(t)
