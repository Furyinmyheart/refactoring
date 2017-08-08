from cards.export.base import CardExportBase


class ColorExport(CardExportBase):
    stamp_image = None
    template = "./cards/export/templates/color.pdf"
