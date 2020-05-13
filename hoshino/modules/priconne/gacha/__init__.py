import random
from collections import defaultdict

from hoshino import util
from hoshino import NoneBot, CommandSession, MessageSegment, Service, Privilege as Priv
from hoshino.util import silence, concat_pic, pic2b64, DailyNumberLimiter

from .gacha import Gacha
from ..chara import Chara

sv = Service('gacha')
jewel_limit = DailyNumberLimiter(6000)
tenjo_limit = DailyNumberLimiter(1)

GACHA_DISABLE_NOTICE = '本群转蛋功能已禁用\n如欲开启，请与维护组联系'
# JEWEL_EXCEED_NOTICE = f'你保底了，19母'
# TENJO_EXCEED_NOTICE = f'你下井保底了，570母'
JEWEL_EXCEED_NOTICE = f'您今天已经抽过{jewel_limit.max}钻了，欢迎明早5点后再来！'
TENJO_EXCEED_NOTICE = f'您今天已经抽过{tenjo_limit.max}张天井券了，欢迎明早5点后再来！'
SWITCH_POOL_TIP = 'β>发送"选择卡池"可切换'

POOL = ('MIX', 'JP', 'TW', 'BL')
DEFAULT_POOL = POOL[0]
_group_pool = defaultdict(lambda: DEFAULT_POOL)

gacha_10_aliases = ('十连', '十连！', '十连抽', '来个十连', '来发十连', '来次十连', '抽个十连', '抽发十连', '抽次十连', '十连扭蛋', '扭蛋十连',
                    '10连', '10连！', '10连抽', '来个10连', '来发10连', '来次10连', '抽个10连', '抽发10连', '抽次10连', '10连扭蛋', '扭蛋10连',
                    '十連', '十連！', '十連抽', '來個十連', '來發十連', '來次十連', '抽個十連', '抽發十連', '抽次十連', '十連轉蛋', '轉蛋十連',
                    '10連', '10連！', '10連抽', '來個10連', '來發10連', '來次10連', '抽個10連', '抽發10連', '抽次10連', '10連轉蛋', '轉蛋10連')
gacha_1_aliases = ('单抽', '单抽！', '来发单抽', '来个单抽', '来次单抽', '扭蛋单抽', '单抽扭蛋',
                   '單抽', '單抽！', '來發單抽', '來個單抽', '來次單抽', '轉蛋單抽', '單抽轉蛋')
gacha_300_aliases = ('抽一井', '来一井', '来发井', '抽发井', '天井扭蛋', '扭蛋天井', '天井轉蛋', '轉蛋天井')
gacha_6_aliases = ('ccc十连')

def cardram():
    x = random.randint(1,1000)
    cx = 6
    if x < 600:
        cx = 6
    elif x >= 600 and x < 835:
        cx = 5
    elif x >= 835 and x < 935:
        cx = 4
    elif x >= 935 and x < 985:
        cx = 3
    elif x >= 985 and x < 995:
        cx = 2
    else:
        cx = 1
    return cx

def cardram10():
    d1 = 0
    d2 = 0
    d3 = 0
    d4 = 0
    d5 = 0
    d6 = 0
    for i in range(10):
        dc = cardram()
        if dc == 1:
            d1 = d1+1
        elif dc == 2:
            d2 = d2+1
        elif dc == 3:
            d3 = d3+1
        elif dc == 4:
            d4 = d4+1
        elif dc == 5:
            d5 = d5+1
        else:
            d6 = d6+1
    if d6 == 10:
        d6 = 9
        d5 = 1
    return d1,d2,d3,d4,d5,d6


def cardmjs(self):
    sx = 0
    mx = 0
    xx = 0
    if self == 1:
        sx = 40
        mx = 5
        xx = 5
    elif self == 2:
        sx = 20
        mx = 5
        xx = 3
    elif self == 3:
        sx = 5
        mx = 1
        xx = 3
    elif self == 4:
        sx = 1
        mx = 1
        xx = 2
    elif self == 5:
        sx = 0
        mx = 1
        xx = 1
    elif self == 6:
        sx = 0
        mx = 1
        xx = 0
    return sx,mx,xx


@sv.on_command('卡池资讯', deny_tip=GACHA_DISABLE_NOTICE, aliases=('查看卡池', '看看卡池', '康康卡池', '卡池資訊','看看up','看看UP'), only_to_me=False)
async def gacha_info(session:CommandSession):
    gid = session.ctx['group_id']
    gacha = Gacha(_group_pool[gid])
    up_chara = gacha.up
    if sv.bot.config.IS_CQPRO:
        up_chara = map(lambda x: str(Chara.fromname(x).icon.cqcode) + x, up_chara)
    up_chara = '\n'.join(up_chara)
    await session.send(f"本期卡池主打的角色：\n{up_chara}\nUP角色合计={(gacha.up_prob/10):.1f}% 3★出率={(gacha.s3_prob)/10:.1f}%\n{SWITCH_POOL_TIP}")


POOL_NAME_TIP = '请选择以下卡池\n> 选择卡池 jp\n> 选择卡池 tw\n> 选择卡池 bilibili\n> 选择卡池 mix'
@sv.on_command('切换卡池', aliases=('选择卡池', '切換卡池', '選擇卡池'), only_to_me=False)
async def set_pool(session:CommandSession):
    if not sv.check_priv(session.ctx, required_priv=Priv.ADMIN):
        session.finish('只有群管理才能切换卡池', at_sender=True)
    name = util.normalize_str(session.current_arg_text)
    if not name:
        session.finish(POOL_NAME_TIP, at_sender=True)
    elif name in ('国', '国服', 'cn'):
        session.finish('请选择以下卡池\n> 选择卡池 b服\n> 选择卡池 台服')
    elif name in ('b', 'b服', 'bl', 'bilibili'):
        name = 'BL'
    elif name in ('台', '台服', 'tw', 'sonet'):
        name = 'TW'
    elif name in ('日', '日服', 'jp', 'cy', 'cygames'):
        name = 'JP'
    elif name in ('混', '混合', 'mix'):
        name = 'MIX'
    else:
        session.finish(f'未知服务器地区 {POOL_NAME_TIP}', at_sender=True)
    gid = session.ctx['group_id']
    _group_pool[gid] = name
    await session.send(f'卡池已切换为{name}池', at_sender=True)


async def check_jewel_num(session):
    uid = session.ctx['user_id']
    if not jewel_limit.check(uid):
        await session.finish(JEWEL_EXCEED_NOTICE, at_sender=True)

async def check_tenjo_num(session):
    uid = session.ctx['user_id']
    if not tenjo_limit.check(uid):
        await session.finish(TENJO_EXCEED_NOTICE, at_sender=True)


@sv.on_command('gacha_1', deny_tip=GACHA_DISABLE_NOTICE, aliases=gacha_1_aliases, only_to_me=True)
async def gacha_1(session:CommandSession):

    await check_jewel_num(session)
    uid = session.ctx['user_id']
    jewel_limit.increase(uid, 150)

    gid = session.ctx['group_id']
    gacha = Gacha(_group_pool[gid])
    chara, hiishi = gacha.gacha_one(gacha.up_prob, gacha.s3_prob, gacha.s2_prob)
    silence_time = hiishi * 60

    cardo = cardram()
    card = Chara.cardimg(cardo).cqcode

    res = f'{chara.name} {"★"*chara.star}'
    if sv.bot.config.IS_CQPRO:
        res = f'{chara.icon.cqcode} {res}'

    await silence(session.ctx, silence_time)
    await session.send(f'素敵な仲間が増えますよ！\n{res}\n{card}', at_sender=True)
	
@sv.on_command('gacha_6', deny_tip=GACHA_DISABLE_NOTICE, aliases=gacha_6_aliases, only_to_me=True)
async def gacha_1(session:CommandSession):

    await check_jewel_num(session)
    uid = session.ctx['user_id']
    jewel_limit.increase(uid, 150)

    gid = session.ctx['group_id']
    gacha = Gacha(_group_pool[gid])
    chara, hiishi = gacha.gacha_one(gacha.up_prob, gacha.s3_prob, gacha.s2_prob)
    silence_time = hiishi * 60

    res = f'{chara.name} {"★"*chara.star}'
    if sv.bot.config.IS_CQPRO:
        res = f'{chara.icon.cqcode} {res}'

    await silence(session.ctx, silence_time)
    await session.send(f'素敵な仲間が増えますよ！\n{res}', at_sender=True)


@sv.on_command('gacha_10', deny_tip=GACHA_DISABLE_NOTICE, aliases=gacha_10_aliases, only_to_me=True)
async def gacha_10(session:CommandSession):
    SUPER_LUCKY_LINE = 170

    await check_jewel_num(session)
    uid = session.ctx['user_id']
    jewel_limit.increase(uid, 1500)
    
    gid=session.ctx['group_id']
    gacha = Gacha(_group_pool[gid])
    result, hiishi = gacha.gacha_ten()
    silence_time = hiishi * 6 if hiishi < SUPER_LUCKY_LINE else hiishi * 60

    cardo = [cardram(),cardram(),cardram(),cardram(),cardram(),cardram(),cardram(),cardram(),cardram(),cardram()]
    if (cardo[0] + cardo[1] + cardo[2] + cardo[3] + cardo[4] + cardo[5] + cardo[6] + cardo[7] + cardo[8] + cardo[9]) == 60:
        cardo[9] = 5
    cardu = [Chara.cardimg(cardo[0]),Chara.cardimg(cardo[1]),Chara.cardimg(cardo[2]),Chara.cardimg(cardo[3]),Chara.cardimg(cardo[4]),Chara.cardimg(cardo[5]),Chara.cardimg(cardo[6]),Chara.cardimg(cardo[7]),Chara.cardimg(cardo[8]),Chara.cardimg(cardo[9])]
    card = Chara.gen_card_pic(cardu, star_slot_verbose=False)
    card = pic2b64(card)
    card = MessageSegment.image(card)

    cardm1 = cardmjs(cardo[0])[0] + cardmjs(cardo[1])[0] + cardmjs(cardo[2])[0] + cardmjs(cardo[3])[0] + cardmjs(cardo[4])[0] + cardmjs(cardo[5])[0] + cardmjs(cardo[6])[0] + cardmjs(cardo[7])[0] + cardmjs(cardo[8])[0] + cardmjs(cardo[9])[0]
    cardm2 = cardmjs(cardo[0])[1] + cardmjs(cardo[1])[1] + cardmjs(cardo[2])[1] + cardmjs(cardo[3])[1] + cardmjs(cardo[4])[1] + cardmjs(cardo[5])[1] + cardmjs(cardo[6])[1] + cardmjs(cardo[7])[1] + cardmjs(cardo[8])[1] + cardmjs(cardo[9])[1]
    cardm3 = cardmjs(cardo[0])[2] + cardmjs(cardo[1])[2] + cardmjs(cardo[2])[2] + cardmjs(cardo[3])[2] + cardmjs(cardo[4])[2] + cardmjs(cardo[5])[2] + cardmjs(cardo[6])[2] + cardmjs(cardo[7])[2] + cardmjs(cardo[8])[2] + cardmjs(cardo[9])[2]
    cardmax = f'获得角色碎片x{cardm1}，母猪石x{cardm2}，公主之心碎片x{cardm3}'

    if sv.bot.config.IS_CQPRO:
        res1 = Chara.gen_team_pic(result[ :5], star_slot_verbose=False)
        res2 = Chara.gen_team_pic(result[5: ], star_slot_verbose=False)
        res = concat_pic([res1, res2])
        res = pic2b64(res)
        res = MessageSegment.image(res)
        result = [f'{c.name}{"★"*c.star}' for c in result]
        res1 = ' '.join(result[0:5])
        res2 = ' '.join(result[5:])
        res = f'{res}\n{res1}\n{res2}'
    else:
        result = [f'{c.name}{"★"*c.star}' for c in result]
        res1 = ' '.join(result[0:5])
        res2 = ' '.join(result[5:])
        res = f'{res1}\n{res2}'

    if hiishi >= SUPER_LUCKY_LINE:
        await session.send('恭喜海豹！おめでとうございます！')
    await session.send(f'素敵な仲間が増えますよ！\n{res}\n{card}\n{cardmax}', at_sender=True)
    await silence(session.ctx, silence_time)


@sv.on_command('gacha_300', deny_tip=GACHA_DISABLE_NOTICE, aliases=gacha_300_aliases, only_to_me=True)
async def gacha_300(session:CommandSession):

    await check_tenjo_num(session)
    uid = session.ctx['user_id']
    tenjo_limit.increase(uid)

    gid=session.ctx['group_id']
    gacha = Gacha(_group_pool[gid])
    result = gacha.gacha_tenjou()
    up = len(result['up'])
    s3 = len(result['s3'])
    s2 = len(result['s2'])
    s1 = len(result['s1'])

    d1 = 0
    d2 = 0
    d3 = 0
    d4 = 0
    d5 = 0
    d6 = 0
    cardm1 = 0
    for i in range(30):
        if cardm1 < 145:
            card10 = cardram10()
            d1 = d1 + card10[0]
            d2 = d2 + card10[1]
            d3 = d3 + card10[2]
            d4 = d4 + card10[3]
            d5 = d5 + card10[4]
            d6 = d6 + card10[5]
            cardm1 = d1 * 40 + d2 * 20 + d3 * 5 + d4
            cardp = i + 1
            cardpsp = f'，你在第{cardp}发十连获得可拼角色的碎片数量'
        else:
            card10 = cardram10()
            d1 = d1 + card10[0]
            d2 = d2 + card10[1]
            d3 = d3 + card10[2]
            d4 = d4 + card10[3]
            d5 = d5 + card10[4]
            d6 = d6 + card10[5]
            cardm1 = d1 * 40 + d2 * 20 + d3 * 5 + d4

    cardm2 = d1 * 5 + d2 * 5 + d3 + d4 + d5 + d6
    cardm3 = d1 * 5 + d2 * 3 + d3 * 3 + d4 * 2 + d5
    cardmax = f'累计获得一等{d1}次，二等{d2}次，三等{d3}次{cardpsp}\n获得角色碎片x{cardm1}，母猪石x{cardm2}，公主之心碎片x{cardm3}'

    res = [*(result['up']), *(result['s3'])]
    random.shuffle(res)
    lenth = len(res)
    if lenth <= 0:
        res = "竟...竟然没有3★？！"
    else:
        step = 4
        pics = []
        for i in range(0, lenth, step):
            j = min(lenth, i + step)
            pics.append(Chara.gen_team_pic(res[i:j], star_slot_verbose=False))
        res = concat_pic(pics)
        res = pic2b64(res)
        res = MessageSegment.image(res)

    msg1 = [
        f"\n素敵な仲間が増えますよ！ {res}\n{cardmax}"
    ]
    msg = [
        f"\n★★★×{up+s3} ★★×{s2} ★×{s1}",
        f"获得记忆碎片×{100*up}与女神秘石×{50*(up+s3) + 10*s2 + s1}！\n第{result['first_up_pos']}抽首次获得up角色" if up else f"获得女神秘石{50*(up+s3) + 10*s2 + s1}个！"
    ]

    if up == 0 and s3 == 0:
        msg.append("太惨了，咱们还是退款删游吧...")
    elif up == 0 and s3 > 7:
        msg.append("up呢？我的up呢？")
    elif up == 0 and s3 <= 3:
        msg.append("这位酋长，梦幻包考虑一下？")
    elif up == 0:
        msg.append("据说天井的概率只有12.16%")
    elif up <= 2:
        if result['first_up_pos'] < 50:
            msg.append("你的喜悦我收到了，滚去喂鲨鱼吧！")
        elif result['first_up_pos'] < 100:
            msg.append("已经可以了，您已经很欧了")
        elif result['first_up_pos'] > 290:
            msg.append("标 准 结 局")
        elif result['first_up_pos'] > 250:
            msg.append("补井还是不补井，这是一个问题...")
        else:
            msg.append("期望之内，亚洲水平")
    elif up == 3:
        msg.append("抽井母五一气呵成！多出30等专武～")
    elif up >= 4:
        msg.append("记忆碎片一大堆！您是托吧？")
    # msg.append(SWITCH_POOL_TIP)

    await session.send('\n'.join(msg1), at_sender=True)
    await session.send('\n'.join(msg), at_sender=True)
    silence_time = (100*up + 50*(up+s3) + 10*s2 + s1) * 1
    await silence(session.ctx, silence_time)


@sv.on_rex(r'^氪金$', normalize=False)
async def kakin(bot:NoneBot, ctx, match):
    if ctx['user_id'] not in bot.config.SUPERUSERS:
        return
    count = 0
    for m in ctx['message']:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
            jewel_limit.reset(uid)
            tenjo_limit.reset(uid)
            count += 1
    if count:
        await bot.send(ctx, f"已为{count}位用户充值完毕！谢谢惠顾～")
