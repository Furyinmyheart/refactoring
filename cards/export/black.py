from cards.export.base import CardExportBase


class BlackExport(CardExportBase):
    stamp_image = None
    template = "./cards/export/templates/black.pdf"
