# -*- coding: utf-8 -*-

import os, sys, math, json
from PIL import Image, ImageDraw, ImageFont
from card import Card


class PuzzleText(object):
    def __init__(self, guides="CS"):
        self.acme = ImageFont.truetype("fonts/Acme-Regular.ttf", 60)

        self.images = images = {}
        images["P"] = Image.open("images/phx.png") # 400x600
        images["D"] = Image.open("images/dragon.png") # 480x300
        images["O"] = Image.open("images/dog.png") # 480x360
        images["M"] = Image.open("images/mahjong.png") # 480x480

        self.suits = {}
        suits_img = Image.open("images/suits.png") # each 192x192
        for idx, suit in enumerate(["star", "pagoda", "sword", "gem"]):
            self.suits[suit] = suits_img.crop((idx * 192, 0, (idx+1) * 192, 192))

        self.card = Card(guides=guides)

    def _draw_line(self, line, y):
        draw = ImageDraw.Draw(self.card.img)

        cur_x = 0
        pos_x = []
        for item in line:
            pos_x.append(cur_x)
            if isinstance(item, str):
                tw, _ = draw.textsize(item, font=self.acme)
                cur_x += tw
            else:
                cur_x += item.size[0]
        total_width = cur_x

        W, H = self.card.size()
        start_x = W/2 - total_width/2
        for item, x in zip(line, pos_x):
            if isinstance(item, str):
                draw.text((start_x + x, y), item, font=self.acme, fill="black")
            else:
                pos = (start_x + x, y + 50 - item.size[1]/2)
                self.card.img.paste(item, pos, item)

    def make_card(self):
        def rescale(img):
            a, b = 1, 3
            w, h = img.size
            return img.resize((w * a / b, h * a / b))
        def adjust(img, pad=0, yshift=0):
            w, h = img.size
            return img.crop((-pad, min(-yshift, 0), w + pad, max(h, h - yshift)))

        mahjong = adjust(rescale(self.images["M"]), pad=18)
        sword = adjust(self.suits["sword"].resize((96, 96)), pad=24, yshift=-16)

        star = adjust(self.suits["star"].resize((96, 96)), pad=20, yshift=-16)
        dog = adjust(rescale(self.images["O"]), pad=22, yshift=-30)

        dragon = adjust(rescale(self.images["D"]), pad=18, yshift=-16)
        phoenix = adjust(rescale(self.images["P"]), pad=16, yshift=8)

        gem = adjust(self.suits["gem"].resize((90, 90)), pad=0)
        pagoda = adjust(self.suits["pagoda"].resize((96, 96)), pad=10)

        lines = [["Teach us, in life,"],
                 ["  to be", mahjong, "and", sword, ","],
                 ["  to be", star, "and", dog, ","],
                 [" and as", dragon, "and", phoenix, ","],
                 ["to have   ", gem, pagoda, "."]]
        for idx, line in enumerate(lines):
            self._draw_line(line, 180 + idx * 160)
        return self.card


class PuzzleRound(object):
    def __init__(self, round_num, codes, tricks, scores, guides="CS"):
        self.acme_small = ImageFont.truetype("fonts/Acme-Regular.ttf", 40)
        self.acme_large = ImageFont.truetype("fonts/Acme-Regular.ttf", 60)
        self.uphand = Image.open("images/hand_up.png")
        self.downhand = Image.open("images/hand_down.png")

        self.round_num = round_num
        self.codes = codes
        assert len(codes) == 2
        self.tricks = tricks
        self.scores = (x if isinstance(x, str) else str(x) for x in scores)

        self.card = Card(guides=guides)
        self.W, self.H = self.card.size()
        self.hand_spacing = 60

    def _draw_numbered_hand(self, x, y, num, orientation):
        hand_img = (self.uphand if orientation == "u" else self.downhand)
        hand_img = hand_img.resize((75, 75))
        self.card.img.paste(hand_img, (x + self.hand_spacing/2 - 75/2, y), hand_img)
        w, h = hand_img.size

        draw = ImageDraw.Draw(self.card.img)
        tw, th = draw.textsize(str(num), font=self.acme_small)
        draw.text((x + self.hand_spacing/2 - tw/2, y + h/2 - th/2 - 6),
                  str(num), font=self.acme_small, fill="black")

    def _draw_code(self, code, y):
        cur_x = self.W/2 - sum(30 if x in (None, "-") else self.hand_spacing for x in code) / 2
        for idx, token in enumerate(code):
            if token in (None, "-"):
                if token == "-":
                    draw = ImageDraw.Draw(self.card.img)
                    draw.rectangle((cur_x + 8, y + 35, cur_x + 22, y + 39), fill="black")
                cur_x += 30
                continue

            orientation = token[-1]
            num = int(token[:-1])
            self._draw_numbered_hand(cur_x, y, num, orientation)
            cur_x += self.hand_spacing

    def _draw_scores(self):
        draw = ImageDraw.Draw(self.card.img)
        x0, y0 = self.W - 280, self.H - 200
        x1, y1 = x0 + 90, y0 + 50
        x2, y2 = x0 + 180, y0 + 100

        # draw cross
        draw.rectangle((x0, y1 - 2, x2, y1 + 2), fill="black")
        draw.rectangle((x1 - 2, y0, x1 + 2, y2), fill="black")

        s1, tot1, s2, tot2 = self.scores
        tw, th = draw.textsize(s1, font=self.acme_small)
        draw.text((x1 - tw - 10, y1 - th - 10), s1, font=self.acme_small, fill="black")
        tw, th = draw.textsize(s2, font=self.acme_small)
        draw.text((x2 - tw - 10, y1 - th - 10), s2, font=self.acme_small, fill="black")

        tw, th = draw.textsize(tot1, font=self.acme_small)
        draw.text((x1 - tw - 10, y2 - th - 10), tot1, font=self.acme_small, fill="blue")
        tw, th = draw.textsize(tot2, font=self.acme_small)
        draw.text((x2 - tw - 10, y2 - th - 10), tot2, font=self.acme_small, fill="blue")

    def make_card(self, guides=""):
        W, H = self.W, self.H

        cur_y = 100
        draw = ImageDraw.Draw(self.card.img)

        t = "Round " + str(self.round_num)
        tw, th = draw.textsize(t, font=self.acme_large)
        draw.text((W/2 - tw/2, cur_y), t, font=self.acme_large, fill="black")

        cur_y += 120
        self._draw_code(self.codes[0], cur_y)
        cur_y += 85
        self._draw_code(self.codes[1], cur_y)

        row_spacing = 45
        inner_w = 540
        cur_y += 110
        for idx, r in enumerate(self.tricks):
            r = r.replace("-", u"—")
            tokens = r.split(" ")
            r = "   ".join(tokens)
            r = r.replace(".", " . ")

            draw.text((W/2 - inner_w/2, cur_y + row_spacing * idx),
                      r, font=self.acme_small, fill="black")

        self._draw_scores()
        return self.card


if __name__ == "__main__":
    f = open("puzzle_data.json", "r")
    puzzle_data = json.loads(f.read())
    f.close()

    W, H = Card().img.size
    output = Image.new("RGBA", (6 * W, H))
    output.paste(PuzzleText().make_card().img, (0, 0))

    for idx, round_data in enumerate(puzzle_data):
        num = idx + 1
        codes, tricks, scores = round_data
        card = PuzzleRound(num, codes, tricks, scores).make_card()
        output.paste(card.img, (num * W, 0))
    output.save("test.png")
