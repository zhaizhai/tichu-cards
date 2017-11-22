# -*- coding: utf-8 -*-

import os, sys, math
from PIL import Image, ImageDraw, ImageFont



class GridMaker(object):
    def __init__(self, dims, margin_w=0, margin_h=0):
        self.W, self.H = dims
        self.margin = (margin_w, margin_h)
        self.positions = [
            None, None,
            self.card_grid(2, 1),
            self.card_grid(3, 1),
            self.card_grid(2, 2),
            self.card_grid(2, 2) + [self.central(0.5)],
            self.card_grid(3, 2),
            self.card_grid(3, 2) + [self.central(0.25)],
            self.card_grid(3, 2) + [self.central(0.25), self.central(0.75)],
            self.card_grid(4, 2) + [self.central(0.5)],
            self.card_grid(4, 2) + [self.central(1.0/6), self.central(5.0/6)]
        ]

    def _grid(self, rows, cols, x, y, w, h):
        w, h = float(w), float(h)
        ret = []
        for i in range(rows):
            for j in range(cols):
                curx = (x + j * (w / (cols - 1)) if cols > 1 else x + w/2)
                cury = (y + i * (h / (rows - 1)) if rows > 1 else y + h/2)
                ret.append((int(curx), int(cury)))
        return ret

    def card_grid(self, rows, cols):
        mw, mh = self.margin
        return self._grid(rows, cols, mw, mh, self.W - 2*mw, self.H - 2*mh)

    def central(self, ratio):
        mw, mh = self.margin
        x = self.W/2
        y = mh + (self.H - 2*mh) * ratio
        return (int(x), int(y))

    def tilt(self, positions, slope=0.15):
        ret = []
        for (x, y) in positions:
            y2 = y - int((x - self.W/2) * slope)
            ret.append((x, y2))
        return ret

    def get_positions(self, num, tilt=None):
        if tilt is None:
            return self.positions[num]
        return self.tilt(self.positions[num], slope=tilt)



class SuitImages(object):
    def __init__(self):
        self.img = Image.open("images/suits.png")

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
        # self._draw_chinese(u"鳳", 0)
        # self._draw_chinese(u"龍", 1)
        # self._draw_chinese(u"犬", 2)
        # self._draw_chinese(u"䲵", 3)
        self._draw_chinese(u"凤", 0)
        self._draw_chinese(u"龙", 1)
        self._draw_chinese(u"犬", 2)
        self._draw_chinese(u"雀", 3)


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
        self._draw_letter("A", 1, height_ratio=1.05, adjust=(0, 3))
        for n in range(2, 10):
            self._draw_single_digit(str(n), n)

        # make 10 thinner
        thin_ten = self._make_ten().resize((self.w, self.h), Image.ANTIALIAS)
        self.numbers_img.paste(thin_ten, (10*self.w + 14, 0), thin_ten)

        self._draw_letter("J", 11, height_ratio=1.05, adjust=(0, 3))
        self._draw_letter("Q", 12, height_ratio=1.16, adjust=(0, 3))
        self._draw_letter("K", 13, height_ratio=1.05, adjust=(0, 3))

    def _draw_single_digit(self, t, position):
        draw = ImageDraw.Draw(self.numbers_img)
        tw, th = draw.textsize(t, font=self.font)
        x = position * self.w
        draw.text((int(x + self.w/2.0 - tw/2.0),
                   int(self.h/2.0 - th/2.0 - 24)),
                  t, font=self.font, fill="black")

    def _draw_letter(self, t, position, height_ratio=1.0, adjust=(0, 0)):
        lw, lh = self.w, int(height_ratio * self.h)
        letter_img = Image.new("RGBA", (lw, lh))
        draw = ImageDraw.Draw(letter_img)
        tw, th = draw.textsize(t, font=self.font)
        draw.text((int(lw/2.0 - tw/2.0),
                   int(lh/2.0 - th/2.0 - 24)),
                  t, font=self.font, fill="black")

        letter_img = letter_img.resize((self.w, self.h))
        self.numbers_img.paste(
            letter_img, (position * self.w + adjust[0], adjust[1]), letter_img)

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
