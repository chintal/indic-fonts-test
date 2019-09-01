#!/usr/bin/env python
# -*- coding: utf-8 -*-


# pillow

from PIL import Image as pilImage
from PIL import ImageDraw as pilImageDraw
from PIL import ImageFont as pilImageFont
# libraqm should be installed from sources.
# Install to /usr/local/lib and LD_PRELOAD the resulting libraqm.so
# The package in ubuntu repo seems to segfault. (?)
# Even the compiled library seems to segfault if it is loaded via
# LD_LIBRARY_PATH and ldconfig instead of LD_PRELOAD.


# wand

from wand.color import Color as wandColor
from wand.image import Image as wandImage
from wand.drawing import Drawing as wandDrawing


# pyvips
import pyvips

# See https://github.com/libvips/pyvips


# kivy

import os
os.environ['KIVY_TEXT'] = 'pango'  # noqa
# See https://github.com/kivy/kivy/blob/master/kivy/core/text/text_pango.py

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout

try:
    from ebs.iot.linuxnode.widgets import ColorLabel
except ImportError:

    class ColorLabel(Label):
        def __init__(self, *args, **kwargs):
            kwargs.pop('bgcolor', None)
            super(ColorLabel, self).__init__(*args, **kwargs)


# make sure you have the fonts locally in a fonts/ directory
font_sakalbharati = '../fonts/Sakalbharati.ttf'
font_arialuni = '../fonts/ARIALUNI.TTF'
font_freesans = '../fonts/FreeSans.ttf'

fonts = [font_sakalbharati, font_arialuni, font_freesans]
font = font_sakalbharati

display_pil_output = True
display_wand_output = True
display_pyvips_output = True

pil_render_dir = os.path.join(os.path.join(os.getcwd(), 'pil'))
wand_render_dir = os.path.join(os.path.join(os.getcwd(), 'wand'))
pyvips_render_dir = os.path.join(os.path.join(os.getcwd(), 'pyvips'))

_language_strings = {
    'English': u'English Keyboard',
    'Hindi': u'हिंदी कीबोर्ड ',
    'Telugu': u'తెలుగులో టైప్',
    'Kannada': u'ಕನ್ನಡ ಕೀಲಿಮಣೆ',
    'Bengali': u'বাংলা কিবোর্ড',
    'Tamil*': u'தமிழ் விசைப்பலகை',    # Source text unknown
    'Marathi*': u'मराठी कळफलक',       # Source text unknown
    'Punjabi*': u'ਪੰਜਾਬੀ ਦੇ ਬੋਰਡ',        # Source text unknown
    'Urdu*': u'اردوبورڈ',              # Source text unknown
    'Malyalam*': u'മലയാളം കീബോര്‍ഡ് ',  # Source text unknown
    'Oriya*': u'ଉତ୍କଳଲିପି',            # Source text unknown
}


def render_pil_image(lang, text):
    W, H = (400, 75)
    background = (0, 140, 150)
    fontsize = 30
    pilfont = pilImageFont.truetype(font, fontsize)

    image = pilImage.new('RGBA', (W, H), background)
    draw = pilImageDraw.Draw(image)

    w, h = pilfont.getsize(text)
    draw.text(((W - w) / 2, (H - h) / 2), text, fill='white', font=pilfont)
    image.save(os.path.join(pil_render_dir, '{0}.png'.format(lang)))


def render_wand_image(lang, text):
    with wandDrawing() as draw:
        with wandImage(width=400, height=75, background=wandColor('rgb(0, 140, 150)')) as img:
            draw.font = font
            draw.font_size = 30
            draw.push()
            draw.fill_color = wandColor('rgb(255, 255, 255)')
            draw.text_alignment = 'center'
            draw.text(int(img.width / 2), int(img.height / 2 + 10), text)
            draw.pop()
            draw(img)
            img.save(filename=os.path.join(wand_render_dir, '{0}.png'.format(lang)))


def render_pyvips_image(lang, text):
    # See https://stackoverflow.com/questions/55164438/overlay-text-with-php-vips
    # See https://github.com/libvips/libvips/issues/1119
    image = pyvips.Image.new_from_memory(bytes([0, 140, 150] * 90000),
                                         width=400, height=75, bands=3, format='uchar')

    textrender = pyvips.Image.text(text, width=350, height=40, align='centre', fontfile=font)
    white = pyvips.Image.new_from_image(textrender, [255, 255, 255]).copy(interpretation='srgb')
    textoverlay = white.bandjoin(textrender)

    output = image.composite(textoverlay, "over",
                             x=int(200 - textrender.width / 2),
                             y=int((75 - textrender.height)/2))
    output.write_to_file(os.path.join(pyvips_render_dir, "{0}.png".format(lang)))


class LangDisplay(BoxLayout):
    def __init__(self, lang, text, *args, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        super(LangDisplay, self).__init__(*args, **kwargs)
        self.spacing = '5px'

        self.add_widget(ColorLabel(text=lang, bgcolor=(0, 0, 0), size_hint_x=0.5,
                                   font_size='20sp', font_name=font))

        self.add_widget(ColorLabel(text=text, bgcolor=(0, 140/255, 150/255),
                                   font_size='24sp', font_name=font))

        if display_pil_output:
            pil_image = Image(source=os.path.join(pil_render_dir, '{0}.png'.format(lang)),
                              size_hint=(1, 1), allow_stretch=True, keep_ratio=True,)
            self.add_widget(pil_image)

        if display_pyvips_output:
            pyvips_image = Image(source=os.path.join(pyvips_render_dir, '{0}.png'.format(lang)),
                                 size_hint=(1, 1), allow_stretch=True, keep_ratio=True,)
            self.add_widget(pyvips_image)

        if display_wand_output:
            wand_image = Image(source=os.path.join(wand_render_dir, '{0}.png'.format(lang)),
                               size_hint=(1, 1), allow_stretch=True, keep_ratio=True,)
            self.add_widget(wand_image)


class IndicFontTestApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', spacing='3px')
        title = BoxLayout(orientation='horizontal')
        title.add_widget(Label(text="Language", font_size='20sp', size_hint_x=0.5))
        title.add_widget(Label(text="Kivy (pango)", font_size='20sp'))
        if display_pil_output:
            title.add_widget(Label(text="pillow (raqm)", font_size='20sp'))
        if display_pyvips_output:
            title.add_widget(Label(text="pyvips", font_size='20sp'))
        if display_wand_output:
            title.add_widget(Label(text="Wand", font_size='20sp'))
        root.add_widget(title)
        for lang in _language_strings.keys():
            root.add_widget(LangDisplay(lang, _language_strings[lang]))
        return root


if __name__ == '__main__':
    os.makedirs(pil_render_dir, exist_ok=True)
    os.makedirs(wand_render_dir, exist_ok=True)
    os.makedirs(pyvips_render_dir, exist_ok=True)
    for lang in _language_strings.keys():
        print(lang)
        render_pil_image(lang, _language_strings[lang])
        render_wand_image(lang, _language_strings[lang])
        render_pyvips_image(lang, _language_strings[lang])
    IndicFontTestApp().run()
