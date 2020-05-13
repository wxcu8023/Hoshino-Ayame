import os
import pytz
import random
from datetime import datetime

import nonebot
from hoshino.service import Service

sv = Service('kc-reminder', enable_on_default=False)

@sv.scheduled_job('cron', hour='12', minute='01')
async def enshu_reminder12():
    msgs = [
        '农场装备提醒',
        '[CQ:at,qq=all] 午饭装备即将开始！',
    ]
    await sv.broadcast(msgs, 'enshu_reminder12', 0.2)

@sv.scheduled_job('cron', hour='20', minute='31')
async def enshu_reminder20():
    msgs = [
        '农场装备提醒',
        '[CQ:at,qq=all] 晚饭装备即将开始！',
    ]
    await sv.broadcast(msgs, 'enshu_reminder20', 0.2)


# @sv.scheduled_job('cron', day='10-14', hour='22')
# async def ensei_reminder():
#     now = datetime.now(pytz.timezone('Asia/Shanghai'))
#     remain_days = 15 - now.day
#     msgs = [
#         f'【远征提醒小助手】提醒您月常远征还有{remain_days}天刷新！',
#         f'[CQ:at,qq=all] 月常远征还有{remain_days}天刷新！',
#     ]
#     await sv.broadcast(msgs, 'ensei_reminder', 0.5)
