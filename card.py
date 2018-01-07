import os, sys, math
from PIL import Image, ImageDraw, ImageFont

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
            draw_rounded_rect(self.img, ul+br, 50, "black", 10)
        if "S" in guides:
            ul = (W/2 - SAFE_W/2, H/2 - SAFE_H/2)
            br = (W/2 + SAFE_W/2, H/2 + SAFE_H/2)
            draw_rounded_rect(self.img, ul+br, 40, "red", 2)

    def cut_mask(self):
        ul = (W/2 - CUT_W/2, H/2 - CUT_H/2)
        br = (W/2 + CUT_W/2, H/2 + CUT_H/2)
        mask = Image.new("RGBA", self.img.size)
        draw_rounded_rect(mask, ul+br, 50, "black", int(CUT_W - 1))
        return mask

    def size(self):
        return self.img.size

    def draw_back(self, color="#ea3944"): # red
        ul = (W/2 - SAFE_W/2, H/2 - SAFE_H/2)
        br = (W/2 + SAFE_W/2, H/2 + SAFE_H/2)
        mask = Image.new("RGBA", self.img.size)
        draw_rounded_rect(mask, ul+br, 40, "black", int(SAFE_W - 1))

        pattern = Image.new("RGBA", self.img.size)
        draw = ImageDraw.Draw(pattern)
        draw.rectangle((0,0) + pattern.size, fill=color)

        suits = Image.open("images/suits.png")
        suits = suits.resize((256, 64), Image.ANTIALIAS)

        # # hatched pattern
        # draw.rectangle((0,0) + pattern.size, fill="#ddcb8d")
        # for x in range(pattern.size[0]):
        #     for y in range(pattern.size[1]):
        #         a, b = (x + y), (x - y)
        #         if (a % 70) <= 9 or (b % 70) <= 9:
        #             draw.point((x, y), "#9e8634")

        self.img.paste(pattern, (0, 0), mask)
        self.paste(suits, int(W/2), int(H/4))
        self.paste(suits.transpose(Image.ROTATE_180), int(W/2), int(3*H/4))


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
