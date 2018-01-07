# -*- coding: utf-8 -*-

import os, sys, math, json
from PIL import Image, ImageDraw, ImageFont
from helpers import SuitImages, FontImages, GridMaker
from puzzle_cards import PuzzleText, PuzzleRound
from card import Card, W, H, SAFE_W, SAFE_H

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


def make_deck(guides="C", imgdir=None, spacing=0):
    if imgdir is not None:
        if not os.path.exists(imgdir):
            os.makedirs(imgdir)
    cm = CardMaker()
    fulldeck = Image.new("RGBA", (13 * (int(W) + 2 * spacing),
                                  5 * (int(H) + 2 * spacing)))

    def paste_or_save(card, filename, (c, r)):
        # TODO: make option
        img = Image.new("RGBA", card.img.size)
        img.paste(card.img, (0, 0), card.cut_mask())
        if imgdir is not None:
            img.save(os.path.join(imgdir, filename))
        else:
            fulldeck.paste(img, (c * (int(W) + 2 * spacing) + spacing,
                                 r * (int(H) + 2 * spacing) + spacing), img)

    # back
    back = Card(guides=guides)
    # ["#2891c4", "#ddcb8d", "#5a8da6", "#ea3944", "#5f5f5f"]
    # blue, tan, gray-blue, pink, dark gray
    back.draw_back()
    paste_or_save(back, "back.png", (0, 0))

    # specials
    special_names = ["phoenix", "dragon", "dog", "mahjong"]
    for idx, special in enumerate("PDOM"):
        card = cm.make_special(special, guides=guides)
        paste_or_save(card, special_names[idx] + ".png", (idx + 1, 0))

    # teachus
    f = open("puzzle_data.json", "r")
    puzzle_data = json.loads(f.read())
    f.close()

    ptext = PuzzleText(guides=guides).make_card()
    paste_or_save(ptext, "teachus.png", (5, 0))
    for idx, round_data in enumerate(puzzle_data):
        num = idx + 1
        codes, tricks, scores = round_data
        card = PuzzleRound(num, codes, tricks, scores, guides=guides).make_card()
        paste_or_save(card, "round" + str(num) + ".png", (num + 5, 0))

    # 52 cards
    for suit in range(4):
        for num in range(1, 14):
            if num <= 10:
                card = cm.make_card(num, suit, guides=guides)
            else:
                card = cm.make_facecard(num, suit, guides=guides)

            suit_name = ["star", "pagoda", "sword", "gem"]
            num_name = "A" if num == 1 else str(num)
            paste_or_save(card, suit_name[suit] + num_name + ".png",
                          (num - 1, suit + 1))

    fulldeck.save("test.png")

make_deck(guides="", spacing=-36)
#make_deck(guides="", imgdir="cards")
