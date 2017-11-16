# -*- coding: utf-8 -*-

import os, sys, math
from PIL import Image, ImageDraw, ImageFont

class SuitImages(object):
    def __init__(self):
        self.img = Image.open('suits.png')

    def _get(self, idx):
        x = idx * 192
        return self.img.crop((x, 0, x + 192, 192))

class FontImages(object):
    def __init__(self, visualize=False):
        self.font = ImageFont.truetype("fonts/Acme-Regular.ttf", 160)
        self.chinese_font = ImageFont.truetype("fonts/NotoSerifCJKsc-Bold.otf", 144,
                                               encoding="unic")
        self.w, self.h = 120, 120
        sw, sh = self.special_dims = 140, 150

        self.numbers_img = Image.new("RGBA", (14 * self.w, self.h))
        self.specials_img = Image.new("RGBA", (4 * sw, sh))

        if visualize:
            self._visualize()

        self._make_numbers()
        # "龙龍凤鳳犬䲵雀"
        self._draw_chinese(u"鳳", 0)
        self._draw_chinese(u"龍", 1)
        self._draw_chinese(u"犬", 2)
        self._draw_chinese(u"䲵", 3)
        # self._draw_chinese(u"凤", 0)
        # self._draw_chinese(u"龙", 1)
        # self._draw_chinese(u"犬", 2)
        # self._draw_chinese(u"雀", 3)


    def _visualize(self):
        draw = ImageDraw.Draw(self.numbers_img)
        for n in range(14):
            color = "white" if n % 2 == 0 else "#dddddd"
            draw.rectangle((n*self.w, 0, (n+1)*self.w, self.h), color)

        draw = ImageDraw.Draw(self.specials_img)
        for n in range(4):
            color = "white" if n % 2 == 0 else "#dddddd"
            draw.rectangle((n*self.special_dims[0], 0,
                            (n+1)*self.special_dims[0], self.special_dims[1]), color)


    def _make_numbers(self):
        draw = ImageDraw.Draw(self.numbers_img)
        self._draw_single_char("A", 1)
        for n in range(2, 10):
            self._draw_single_char(str(n), n)

        # make 10 thinner
        thin_ten = self._make_ten().resize((self.w, self.h), Image.ANTIALIAS)
        self.numbers_img.paste(thin_ten, (10*self.w + 14, 0), thin_ten)

        self._draw_single_char("J", 11)
        self._draw_single_char("Q", 12)
        self._draw_single_char("K", 13)

    def _draw_single_char(self, t, position):
        draw = ImageDraw.Draw(self.numbers_img)
        tw, th = draw.textsize(t, font=self.font)
        x = position * self.w
        draw.text((int(x + self.w/2.0 - tw/2.0),
                   int(self.h/2.0 - th/2.0 - 24)),
                  t, font=self.font, fill="black")

    def _make_ten(self):
        ten_img = Image.new("RGBA", (int(1.2 * self.w), self.h))
        draw = ImageDraw.Draw(ten_img)
        tw1, th = draw.textsize("1", font=self.font)
        tw0, th = draw.textsize("0", font=self.font)

        shaved = 10
        tw = tw1 + tw0 - shaved
        left = int(self.w/2.0 - tw/2.0) - 13
        top = int(self.h/2.0 - th/2.0 - 24)

        draw.text((left, top), "1", font=self.font, fill="black")
        draw.text((left + tw1 - shaved, top), "0", font=self.font, fill="black")
        return ten_img

    def _draw_chinese(self, t, position):
        draw = ImageDraw.Draw(self.specials_img)
        sw, sh = self.special_dims
        tw, th = draw.textsize(t, font=self.chinese_font)
        x = position * sw
        draw.text((int(x + sw/2.0 - tw/2.0),
                   int(sh/2.0 - th/2.0 - 20)),
                  t, font=self.chinese_font, fill="black")


    def get_img(self, num):
        sw, sh = self.special_dims
        if num == "P":
            return self.specials_img.crop((0, 0, sw, sh))
        if num == "D":
            return self.specials_img.crop((sw, 0, 2*sw, sh))
        if num == "O":
            return self.specials_img.crop((2*sw, 0, 3*sw, sh))
        if num == "M":
            return self.specials_img.crop((3*sw, 0, 4*sw, sh))

        x = num * self.w
        return self.numbers_img.crop((x, 0, x+self.w, self.h))



if __name__ == "__main__":
    fi = FontImages(visualize=True)
    img = Image.new("RGBA", (fi.numbers_img.size[0], 400))
    img.paste(fi.numbers_img, (0, 0))
    img.paste(fi.specials_img, (0, 200))
    img.save("test.png")
