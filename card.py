# -*- coding: utf-8 -*-

import os, sys, math
from PIL import Image, ImageDraw, ImageFont
from helpers import SuitImages, FontImages, GridMaker

W, H = 822.0, 1122.0 # bridge dims: 747.0, 1122.0
CUT_W, CUT_H = 750.0, 1050.0
SAFE_W, SAFE_H = 678.0, 978.0

def draw_rounded_rect(img, bbox, r, color, thickness):
    draw = ImageDraw.Draw(img)

    def thick_arc(box, corner):
        x1, y1, x2, y2 = box
        for x in range(x1, x2+1):
            for y in range(y1, y2+1):
                dist2 = (corner[0] - x)**2 + (corner[1] - y)**2
                if r - thickness - 0.5 < math.sqrt(dist2) < r + 0.5:
                    draw.point((x, y), color)

    rx1, ry1, rx2, ry2 = (int(_) for _ in bbox)
    draw.rectangle(((rx1 + r, ry1), (rx2 - r, ry1 + thickness)), fill=color)
    draw.rectangle(((rx1 + r, ry2 - thickness), (rx2 - r, ry2)), fill=color)
    draw.rectangle(((rx1, ry1 + r), (rx1 + thickness, ry2 - r)), fill=color)
    draw.rectangle(((rx2 - thickness, ry1 + r), (rx2, ry2 - r)), fill=color)

    thick_arc((rx1, ry1, rx1+r, ry1+r), (rx1+r, ry1+r))
    thick_arc((rx2-r, ry1, rx2, ry1+r), (rx2-r, ry1+r))
    thick_arc((rx1, ry2-r, rx1+r, ry2), (rx1+r, ry2-r))
    thick_arc((rx2-r, ry2-r, rx2, ry2), (rx2-r, ry2-r))


class Card(object):
    def __init__(self, guides=""):
        self.img = Image.new("RGBA", (int(W),int(H)), "white")

        draw = ImageDraw.Draw(self.img)
        if "C" in guides:
            ul = (W/2 - CUT_W/2, H/2 - CUT_H/2)
            br = (W/2 + CUT_W/2, H/2 + CUT_H/2)
            draw_rounded_rect(self.img, ul+br, 50, "blue", 5)
        if "S" in guides:
            ul = (W/2 - SAFE_W/2, H/2 - SAFE_H/2)
            br = (W/2 + SAFE_W/2, H/2 + SAFE_H/2)
            draw_rounded_rect(self.img, ul+br, 40, "red", 2)

    def draw_back(self):
        ul = (W/2 - SAFE_W/2, H/2 - SAFE_H/2)
        br = (W/2 + SAFE_W/2, H/2 + SAFE_H/2)
        mask = Image.new("RGBA", self.img.size)
        draw_rounded_rect(mask, ul+br, 40, "black", int(SAFE_W - 1))

        pattern = Image.new("RGBA", self.img.size)
        draw = ImageDraw.Draw(pattern)
        draw.rectangle((0,0) + pattern.size, fill="#ddcb8d")
        for x in range(pattern.size[0]):
            for y in range(pattern.size[1]):
                a, b = (x + y), (x - y)
                if (a % 70) <= 9 or (b % 70) <= 9:
                    draw.point((x, y), "#9e8634")
        self.img.paste(pattern, (0, 0), mask)

    def _paste(self, icon, x, y):
        w, h = icon.size
        # use icon as mask for itself
        self.img.paste(icon, (x, y, x + w, y + h), icon)

    def paste(self, icon, x, y):
        w, h = icon.size
        self._paste(icon, x - w/2, y - h/2)

    def pasten(self, icon, positions):
        w, h = icon.size
        for x, y in positions:
            self._paste(icon, x - w/2, y - h/2)


class CardMaker(object):
    def __init__(self):
        self.suits = SuitImages()
        self.gridmaker = GridMaker((int(W), int(H)), margin_w=280, margin_h=280)
        self.chinese_font = ImageFont.truetype("fonts/NotoSerifCJKsc-Bold.otf", 144,
                                               encoding="unic")
        self.font_imgs = FontImages()

    def make_special(self, value, guides=""):
        card = Card(guides=guides)

        if value is "P":
            img = Image.open("images/phx.png") # 400x600
            img = img.resize((540, 810), Image.ANTIALIAS)
            card.paste(img, int(W/2), int(H/2))
        elif value is "D":
            img = Image.open("images/dragon.png") # 480x300
            img = img.resize((640, 400), Image.ANTIALIAS)
            card.paste(img, int(W/2), int(H/2))
        elif value is "O":
            img = Image.open("images/dog.png") # 480x360
            img = img.resize((640, 480), Image.ANTIALIAS)
            card.paste(img, int(W/2), int(H/2))
        elif value is "M":
            img = Image.open("images/mahjong.png") # 480x480
            img = img.resize((640, 640), Image.ANTIALIAS)
            card.paste(img, int(W/2), int(H/2))
        else:
            assert False

        self._draw_corners(card, value, None, allfour=True)
        return card

    def make_card(self, num, suit, guides=""):
        assert 1 <= num <= 10
        assert 0 <= suit <= 3

        card = Card(guides=guides)
        suit_img = self.suits._get(suit)

        if num == 1:
            big_img = suit_img.resize((336, 336), Image.ANTIALIAS)
            card.paste(big_img, int(W/2), int(H/2))
        else:
            small_img = suit_img.resize((144, 144), Image.ANTIALIAS)
            positions = self.gridmaker.get_positions(num)

            upper, lower = [], []
            for x, y in positions:
                if y < H/2 - 0.01 * (x - W/2) + 1:
                    upper.append((x,y))
                else:
                    lower.append((x,y))
            card.pasten(small_img, upper)
            card.pasten(small_img.transpose(Image.ROTATE_180), lower)

        self._draw_corners(card, num, suit_img, allfour=True)
        return card


    def make_facecard(self, num, suit, guides=""):
        card = Card(guides=guides)

        draw = ImageDraw.Draw(card.img)
        padw, padh = 210, 200
        thickness = 4
        draw.rectangle((padw, padh, int(W) - padw, padh + thickness), "black")
        draw.rectangle((padw, int(H) - padh - thickness, int(W) - padw, int(H) - padh), "black")
        draw.rectangle((padw, padh, padw + thickness, int(H) - padh), "black")
        draw.rectangle((int(W) - padw + thickness, padh, int(W) - padw, int(H) - padh), "black")

        FACECARD_DATA = [
            [
                ["images/starJ.png", (900, 900), (540, 540), (-28, -28)],
                ["images/starQ.png", (900, 1260), (525, 735), (0, 0)],
                ["images/starK.png", (1080, 1380), (540, 690), (36, 25)],
            ],
            [
                ["images/pagodaJ.png", (660, 900), (495, 675), (4, 0)],
                ["images/pagodaQ.png", (1200, 1200), (600, 600), (0, 0)],
                ["images/pagodaK.png", (1200, 1320), (600, 660), (0, 30)],
            ],
            [
                ["images/swordJ.png", (600, 900), (400, 600), (0, 0)],
                ["images/swordQ.png", (997, 1400), (500, 700), (8, -28)],
                ["images/swordK.png", (1000, 1320), (500, 660), (-28, -28)],
            ],
            [
                ["images/gemJ.png", (480, 960), (330, 660), (0, 0)],
                ["images/gemQ.png", (720, 1200), (390, 650), (0, 0)],
                ["images/gemK.png", (960, 1200), (600, 750), (0, 0)],
            ],
        ]

        data = FACECARD_DATA[suit]
        assert 11 <= num <= 13
        filename, orig_dims, resize_dims, offsets = data[num - 11]
        img = Image.open(filename)
        img = img.resize(resize_dims, Image.ANTIALIAS)
        card.paste(img, int(W/2) + offsets[0], int(H/2) + offsets[1])

        suit_img = self.suits._get(suit)
        self._draw_corners(card, num, suit_img, allfour=True)
        return card

    def _draw_corners(self, card, num, suit_img,
                      adjust=(0,0), allfour=False):
        mw, mh = 130, 300
        mini = Image.new("RGBA", (mw, mh))
        draw = ImageDraw.Draw(mini)

        font_img = self.font_imgs.get_img(num)
        fw, fh = font_img.size
        mini.paste(font_img, (mw/2 - fw/2, 0))

        if suit_img is not None:
            small = suit_img.resize((120, 120), Image.ANTIALIAS)
            mini.paste(small, (mw/2 - 60, 132), small)

        ox = int((W - SAFE_W)/2 + mw/2 + adjust[0])
        oy = int((H - SAFE_H)/2 + mh/2 + adjust[1])
        card.paste(mini, ox, oy)
        card.paste(mini.transpose(Image.ROTATE_180), int(W) - ox, int(H) - oy)
        if allfour:
            card.paste(mini, int(W) - ox, oy)
            card.paste(mini.transpose(Image.ROTATE_180), ox, int(H) - oy)



fulldeck = Image.new("RGBA", (13 * int(W), 5 * int(H)))
cm = CardMaker()
for suit in range(4):
    for num in range(1, 14):
        if num <= 10:
            card = cm.make_card(num, suit, guides="C")
        else:
            card = cm.make_facecard(num, suit, guides="C")
        fulldeck.paste(card.img, ((num - 1) * int(W), (suit + 1) * int(H)))

back = Card(guides="C")
back.draw_back()
fulldeck.paste(back.img, (0, 0))
for idx, special in enumerate("PDOM"):
    card = cm.make_special(special, guides="C")
    fulldeck.paste(card.img, ((idx + 1) * int(W), 0))
fulldeck.save("test.png")

#CardMaker().make_card(1, 0, guides="CS").img.save("images/test.png")
#CardMaker().make_facecard(11, 1, guides="CS").img.save("images/test.png")
#CardMaker().make_special("M", guides="C").img.save("images/test.png")
