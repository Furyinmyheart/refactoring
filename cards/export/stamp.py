import io

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps


def make_stamp(org_title: str, base_file: str, org_title_width: int, output=None) -> io.BytesIO:
    img = Image.open(base_file)

    org_title = org_title.upper()
    font_filename = "./static/fonts/Stamp.ttf"
    font_size = 35
    font = ImageFont.truetype(font_filename, font_size)
    text_size = font.getsize(org_title)
    while text_size[0] > org_title_width:
        font_size -= 1
        font = ImageFont.truetype(font_filename, font_size)
        text_size = font.getsize(org_title)

    img_txt = Image.new('L', text_size)

    d = ImageDraw.Draw(img_txt)
    d.text((0, 0), org_title, fill=255, font=font)
    w = img_txt.rotate(-4.6, expand=1)

    img.paste(ImageOps.colorize(w, (0, 0, 0), (61, 62, 140)), (int(img.size[0]/2-text_size[0]/2),
                                                               int(img.size[1]/2-text_size[1]/2)), w)

    if output is None:
        output = io.BytesIO()
    img.save(output, format='PNG')
    return output


