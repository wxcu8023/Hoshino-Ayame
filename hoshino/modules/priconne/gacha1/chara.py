import os
import base64

from io import BytesIO
from PIL import Image

import zhconv

from .priconne_data import _PriconneData
from hoshino.log import logger
from hoshino.res import R, ResImg

try:
    gadget_equip = R.img('priconne/gadget/equip.png').open()
    gadget_star = R.img('priconne/gadget/star.png').open()
    gadget_star_dis = R.img('priconne/gadget/star_disabled.png').open()
    gadget_star_pink = R.img('priconne/gadget/star_pink.png').open()
    unknown_chara_icon = R.img('priconne/unit/icon_unit_100031.png').open()
except Exception as e:
    logger.exception(e)


NAME2ID = {}

def gen_name2id():
    NAME2ID.clear()
    for k, v in _PriconneData.CHARA.items():
        for s in v:
            if s not in NAME2ID:
                NAME2ID[normname(s)] = k
            else:
                logger.warning(f'Chara.__gen_name2id: 出现重名{s}于id{k}与id{NAME2ID[s]}')


def normname(name:str) -> str:
    name = name.lower().replace('（', '(').replace('）', ')')
    name = zhconv.convert(name, 'zh-hans')
    return name

class Chara:
    
    UNKNOWN = 1000
    
    def __init__(self, id_, star=3, equip=0):
        self.id = id_
        self.star = star
        self.equip = equip

    def cardimg(self) -> ResImg:
        res = R.img(f'priconne/card/card0{self}.png')
        return res


    @staticmethod
    def fromid(id_, star=3, equip=0):
        '''Create Chara from her id. The same as Chara()'''
        return Chara(id_, star, equip)


    @staticmethod
    def fromname(name, star=3, equip=0):
        '''Create Chara from her name.'''
        id_ = Chara.name2id(name)
        return Chara(id_, star, equip)


    @property
    def name(self):
        return _PriconneData.CHARA[self.id][0] if self.id in _PriconneData.CHARA else _PriconneData.CHARA[Chara.UNKNOWN][0]


    @property
    def icon(self) -> ResImg:
        star = '3' if 1 <= self.star <= 5 else '6'
        res = R.img(f'priconne/unit/icon_unit_{self.id}{star}1.png')
        if not res.exist:
            res = R.img(f'priconne/unit/icon_unit_{self.id}31.png')
        if not res.exist:
            res = R.img(f'priconne/unit/icon_unit_{self.id}11.png')
        if not res.exist:
            res = R.img(f'priconne/unit/icon_unit_{Chara.UNKNOWN}31.png')
        return res

    def gen_icon_img(self, size, star_slot_verbose=True) -> Image:
        try:
            pic = self.icon.open().convert('RGBA').resize((size, size), Image.LANCZOS)
        except FileNotFoundError:
            logger.error(f'File not found: {self.icon.path}')
            pic = unknown_chara_icon.convert('RGBA').resize((size, size), Image.LANCZOS)

        l = size // 6
        star_lap = round(l * 0.15)
        margin_x = ( size - 6*l ) // 2
        margin_y = round(size * 0.05)
        if self.star:
            for i in range(5 if star_slot_verbose else min(self.star, 5)):
                a = i*(l-star_lap) + margin_x
                b = size - l - margin_y
                s = gadget_star if self.star > i else gadget_star_dis
                s = s.resize((l, l), Image.LANCZOS)
                pic.paste(s, (a, b, a+l, b+l), s)
            if 6 == self.star:
                a = 5*(l-star_lap) + margin_x
                b = size - l - margin_y
                s = gadget_star_pink
                s = s.resize((l, l), Image.LANCZOS)
                pic.paste(s, (a, b, a+l, b+l), s)
        if self.equip:
            l = round(l * 1.5)
            a = margin_x
            b = margin_x
            s = gadget_equip.resize((l, l), Image.LANCZOS)
            pic.paste(s, (a, b, a+l, b+l), s)
        return pic


    @staticmethod
    def gen_team_pic(team, size=64, star_slot_verbose=True):
        num = len(team)
        des = Image.new('RGBA', (num*size, size), (255, 255, 255, 255))
        for i, chara in enumerate(team):
            src = chara.gen_icon_img(size, star_slot_verbose)
            des.paste(src, (i * size, 0), src)
        return des

    def gen_card_pic(cardall, size=64, star_slot_verbose=True):
        imga = [cardall[0].open(),cardall[1].open(),cardall[2].open(),cardall[3].open(),cardall[4].open(),cardall[5].open(),cardall[6].open(),cardall[7].open(),cardall[8].open(),cardall[9].open()]
        img1 = imga[0].resize((64,64),Image.ANTIALIAS)
        img2 = imga[1].resize((64,64),Image.ANTIALIAS)
        img3 = imga[2].resize((64,64),Image.ANTIALIAS)
        img4 = imga[3].resize((64,64),Image.ANTIALIAS)
        img5 = imga[4].resize((64,64),Image.ANTIALIAS)
        img6 = imga[5].resize((64,64),Image.ANTIALIAS)
        img7 = imga[6].resize((64,64),Image.ANTIALIAS)
        img8 = imga[7].resize((64,64),Image.ANTIALIAS)
        img9 = imga[8].resize((64,64),Image.ANTIALIAS)
        img10 = imga[9].resize((64,64),Image.ANTIALIAS)
        des = Image.new('RGBA', (320, 128), (255, 255, 255, 255))
        loc1, loc2, loc3, loc4, loc5, loc6, loc7, loc8, loc9, loc10 = (0,0),(64,0),(128,0),(192,0),(256,0),(0,64),(64,64),(128,64),(192,64),(256,64)
        des.paste(img1, loc1)
        des.paste(img2, loc2)
        des.paste(img3, loc3)
        des.paste(img4, loc4)
        des.paste(img5, loc5)
        des.paste(img6, loc6)
        des.paste(img7, loc7)
        des.paste(img8, loc8)
        des.paste(img9, loc9)
        des.paste(img10, loc10)
        return des


    @staticmethod
    def name2id(name):
        name = normname(name)
        if not NAME2ID:
            gen_name2id()
        return NAME2ID[name] if name in NAME2ID else Chara.UNKNOWN
