# -*- coding: utf-8 -*-

import os, sys, math
from PIL import Image, ImageDraw, ImageFont

W, H = 822.0, 1122.0 # bridge dims: 747.0, 1122.0
CUT_W, CUT_H = 750.0, 1050.0
SAFE_W, SAFE_H = 678.0, 978.0

class SuitImages(object):
    def __init__(self):
        self.img = Image.open('suits.png')

    def _get(self, idx):
        x = idx * 192
        return self.img.crop((x, 0, x + 192, 192))

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

def grid(rows, cols, x, y, w, h):
    w, h = float(w), float(h)
    ret = []
    for i in range(rows):
        for j in range(cols):
            curx = (x + j * (w / (cols - 1)) if cols > 1 else x + w/2)
            cury = (y + i * (h / (rows - 1)) if rows > 1 else y + h/2)
            ret.append((int(curx), int(cury)))
    return ret




class GridMaker(object):
    def __init__(self, margin_w, margin_h):
        self.margin = (margin_w, margin_h)

    def card_grid(self, rows, cols):
        mw, mh = self.margin
        return grid(rows, cols, mw, mh, W - 2*mw, H - 2*mh)

    def central(self, ratio):
        mw, mh = self.margin
        x = W/2
        y = mh + (H - 2*mh) * ratio
        return (int(x), int(y))

    def positions(self):
        return [
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

    def tilt(self, positions, slope=0.15):
        ret = []
        for (x, y) in positions:
            y2 = y - int((x - W/2) * slope)
            ret.append((x, y2))
        return ret


# "龙龍凤鳳犬䲵雀"
class CardMaker(object):
    def __init__(self):
        self.suits = SuitImages()
        self.gridmaker = GridMaker(280, 280)
        self.font = ImageFont.truetype("fonts/Acme-Regular.ttf", 160)
        self.chinese_font = ImageFont.truetype("fonts/NotoSerifCJKsc-Bold.otf", 144,
                                               encoding="unic")
    def make_special(self, value, guides=""):
        card = Card(guides=guides)

        if value is "P":
            img = Image.open("phx.png")
            # original is 400x600
            img = img.resize((540, 810), Image.ANTIALIAS)
            card.paste(img, int(W/2), int(H/2))
            self._draw_corners(card, None, u"凤",
                               adjust=(10,10),
                               font=self.chinese_font,
                               allfour=True)
            return card
        assert False

    def make_card(self, num, suit, guides=""):
        assert 1 <= num <= 13
        assert 0 <= suit <= 3

        card = Card(guides=guides)
        suit_img = self.suits._get(suit)
        suit_img = suit_img.resize((168, 168), Image.ANTIALIAS)

        if 2 <= num <= 10:
            positions = self.gridmaker.positions()[num]
            positions = self.gridmaker.tilt(positions)
            card.pasten(suit_img, positions)

        text = "A"
        if 2 <= num <= 10:
            text = str(num)
        elif num == 11:
            text = "J"
        elif num == 12:
            text = "Q"
        else:
            text = "K"
        self._draw_corners(card, suit_img, text)

        return card

    def _draw_corners(self, card, suit_img, text,
                      adjust=(0,0), font=None, allfour=False):
        if font is None:
            font = self.font

        mw, mh = 130, 300
        mini = Image.new("RGBA", (mw, mh))
        draw = ImageDraw.Draw(mini)
        tw, th = draw.textsize(text, font=font)
        print tw, th
        draw.text((mw/2 - tw/2, 36 - th/2),
                  text, font=font, fill="black")

        if suit_img is not None:
            small = suit_img.resize((120, 120), Image.ANTIALIAS)
            mini.paste(small, (mw/2 - 60, 140), small)

        ox = int((W - SAFE_W)/2 + mw/2 + adjust[0])
        oy = int((H - SAFE_H)/2 + mh/2 + adjust[1])
        card.paste(mini, ox, oy)
        card.paste(mini.transpose(Image.ROTATE_180), int(W) - ox, int(H) - oy)
        if allfour:
            card.paste(mini, int(W) - ox, oy)
            card.paste(mini.transpose(Image.ROTATE_180), ox, int(H) - oy)


#CardMaker().make_card(13, 3, guides="CS").img.save("test.png")
CardMaker().make_special("P", guides="C").img.save("test.png")
