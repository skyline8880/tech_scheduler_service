import datetime as dt

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bitrix.bitrix_api import BitrixMethods
from bitrix.bitrix_params import update_json
from bot.bot import TechBot
from database.database import Database


class Tracker():
    async def track_24_hours(self, deal_id, department_id):
        db = Database()
        current_deal = await db.get_current_request_of_department(
            department_id=department_id,
            bitrix_deal_id=deal_id)
        print('24 hours', current_deal[3])
        if current_deal[3] != 5 and current_deal[3] != 3:
            bm = await BitrixMethods(
                department_sign=department_id).collect_portal_data()
            json = update_json(
                deal_id=deal_id,
                params={
                    'STAGE_ID': f'C{bm.category_id}:{bm.onmgr}',
                    'ASSIGNED_BY_ID': bm.mgr_tech
                }
            )
            status = await bm.update_deal(json=json)
            print(status)
            if status == 200:
                await db.update_status_id_in_request(
                    status_id=3,
                    department_id=department_id,
                    bitrix_deal_id=deal_id)
                current_deal = await db.get_current_request_of_department(
                    department_id=department_id,
                    bitrix_deal_id=deal_id)
                msg_group_id = await db.get_group_msg_id_of_request(
                    department_id=department_id,
                    bitrix_deal_id=deal_id)
                (
                    message_id,
                    chat_id
                ) = await db.get_deal_msg_id_and_creator_of_request(
                    department_id=department_id,
                    bitrix_deal_id=deal_id)
                bot = TechBot(department_id=department_id)
                edit_msg = await bot.edit_message(
                    request_data=current_deal,
                    group_msg_id=msg_group_id)
                send_group = await bot.send_message(
                    request_data=current_deal,
                    chat_id=await bot.group_id(department_id=department_id),
                    msg_to_reply=msg_group_id)
                send_private = await bot.send_message(
                    request_data=current_deal,
                    chat_id=chat_id,
                    msg_to_reply=message_id)

    async def track_72_hours(self, deal_id, department_id):
        db = Database()
        current_deal = await db.get_current_request_of_department(
            department_id=department_id,
            bitrix_deal_id=deal_id)
        print('72 hours', current_deal[3])
        if current_deal[3] != 5 and current_deal[3] != 4:
            bm = await BitrixMethods(
                department_sign=department_id).collect_portal_data()
            json = update_json(
                deal_id=deal_id,
                params={
                    'STAGE_ID': f'C{bm.category_id}:{bm.hangon}',
                    'ASSIGNED_BY_ID': bm.head_tech
                }
            )
            status = await bm.update_deal(json=json)
            print(status)
            if status == 200:
                await db.update_status_id_in_request(
                    status_id=4,
                    department_id=department_id,
                    bitrix_deal_id=deal_id)
                current_deal = await db.get_current_request_of_department(
                    department_id=department_id,
                    bitrix_deal_id=deal_id)
                msg_group_id = await db.get_group_msg_id_of_request(
                    department_id=department_id,
                    bitrix_deal_id=deal_id)
                (
                    message_id,
                    chat_id
                ) = await db.get_deal_msg_id_and_creator_of_request(
                    department_id=department_id,
                    bitrix_deal_id=deal_id)
                bot = TechBot(department_id=department_id)
                edit_msg = await bot.edit_message(
                    request_data=current_deal,
                    group_msg_id=msg_group_id)
                send_group = await bot.send_message(
                    request_data=current_deal,
                    chat_id=await bot.group_id(department_id=department_id),
                    msg_to_reply=msg_group_id)
                send_private = await bot.send_message(
                    request_data=current_deal,
                    chat_id=chat_id,
                    msg_to_reply=message_id)

    async def request_timetracker(self, start_date, deal_id, department_id):
        scheduler_24_hours = AsyncIOScheduler(timezone='Europe/Moscow')
        scheduler_72_hours = AsyncIOScheduler(timezone='Europe/Moscow')
        scheduler_24_hours.add_job(
            func=self.track_24_hours,
            trigger='date',
            next_run_time=start_date + dt.timedelta(hours=24),
            kwargs={'deal_id': deal_id, 'department_id': department_id}
        )

        scheduler_72_hours.add_job(
            func=self.track_72_hours,
            trigger='date',
            next_run_time=start_date + dt.timedelta(hours=72),
            kwargs={'deal_id': deal_id, 'department_id': department_id}
        )
        scheduler_24_hours.start()
        scheduler_72_hours.start()
