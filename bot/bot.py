import datetime as dt
import urllib.parse

import aiohttp
from aiogram.utils import markdown

from constants.buttons_init import ActionButtons, CurrentRequestActionButtons
from core.secrets import TGSecrets
from filters.callback_filters import (CurrentRequestActionCallbackData,
                                      UserActionsCallbackData)


class TechBot:
    def __init__(self, department_id: int) -> None:
        self.department_id = department_id
        self.base_url = f'https://api.telegram.org/bot{TGSecrets.BOT_TOKEN}'
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Tech Bot Scheduler',
            'Content-Type': 'application/json'
        }

    async def group_id(self, department_id):
        GROUPS = {
            1: None,
            2: TGSecrets.MSK_GROUP,
            3: TGSecrets.VLK_GROUP,
            4: TGSecrets.NKR_GROUP,
            5: TGSecrets.BTV_GROUP
        }
        group_id = None
        try:
            group_id = GROUPS[int(department_id)]
        except Exception:
            print(
                'telegram group not found by'
                f'department_id = {department_id}')
        finally:
            return group_id

    def create_current_request_menu(
            self, current_deal, group_message_id=None, is_private=False):
        menu_button = [
            {
                'text': ActionButtons.MENU.value,
                'callback_data': UserActionsCallbackData(
                    action=ActionButtons.MENU).pack()
            }
        ]
        (
            bitrix_deal_id,
            deal_department_id,
            department_name,
            status_id,
            status_name,
            creator_telegram_id,
            creator_username,
            creator_full_name,
            creator_phone,
            creator_department_id,
            creator_department,
            creator_position_id,
            creator_position,
            creator_photo,
            short_description,
            detailed_description,
            executor_telegram_id,
            creator_username,
            creator_full_name,
            creator_phone,
            executor_department_id,
            executor_department,
            executor_position_id,
            executor_position,
            executor_photo,
            report,
            create_date,
            creator_last_name,
            creator_first_name,
            executor_last_name,
            executor_first_name) = current_deal
        fbutton = CurrentRequestActionButtons.INROLE
        url = None
        second_row_buttons = []
        if 1 < status_id and status_id < 5:
            fbutton = CurrentRequestActionButtons.DONE
            group_message_id = (
                '' if group_message_id is None else group_message_id)
            if not is_private:
                params = urllib.parse.quote(
                    string=(
                        f'{deal_department_id}-{bitrix_deal_id}'
                        f'-{group_message_id}'),
                    encoding="utf-8")
                url = (
                    f'https://t.me/{TGSecrets.BOT_USERNAME}'
                    f'?start={params}')
            second_row_buttons = [
                {
                    'text': CurrentRequestActionButtons.HANDOVERMGR.value,
                    'callback_data': CurrentRequestActionCallbackData(
                        current_act=CurrentRequestActionButtons.HANDOVERMGR,
                        status_id=status_id,
                        department_id=deal_department_id,
                        cur_act_deal=bitrix_deal_id
                            ).pack()
                },
                {
                    'text': CurrentRequestActionButtons.HANGON.value,
                    'callback_data': CurrentRequestActionCallbackData(
                        current_act=CurrentRequestActionButtons.HANGON,
                        status_id=status_id,
                        department_id=deal_department_id,
                        cur_act_deal=bitrix_deal_id
                            ).pack()
                }
            ]
        first_row_button = [
                {
                    'text': fbutton.value,
                    'callback_data': CurrentRequestActionCallbackData(
                        current_act=fbutton,
                        status_id=status_id,
                        department_id=deal_department_id,
                        cur_act_deal=bitrix_deal_id
                            ).pack(),
                    'url': url
                }
            ]
        kbrd = [first_row_button]
        if second_row_buttons != []:
            kbrd.append(second_row_buttons)
        if is_private:
            kbrd.append(menu_button)
        return {
            'inline_keyboard': kbrd
        }

    def request_detail_message(self, request_data):
        executor = request_data[19]
        executor_fullname = f'{request_data[29]} {request_data[30]}'
        report = request_data[25]
        if executor is None:
            executor = ' - '
            executor_fullname = 'Не принят в работу'
        if report is None:
            report = 'Работа не проведена'
        deal_id = f'{request_data[1]}/{request_data[0]}'
        # creator_fullname = f'{request_data[29]} {request_data[30]}'
        time = dt.datetime.strftime(request_data[26], "%H:%M")
        return markdown.text(
            markdown.text(
                markdown.markdown_decoration.quote('Номер задачи:'),
                f'{markdown.bold(deal_id)}'),
            markdown.text(
                markdown.markdown_decoration.quote('Дата создания:'),
                f'{markdown.bold(request_data[26].date())}',
                f'{markdown.bold(time)}'),
            markdown.text(
                markdown.markdown_decoration.quote('Отделение:'),
                f'{markdown.bold(request_data[2])}'),
            markdown.text(
                markdown.markdown_decoration.quote('Статус:'),
                f'{markdown.bold(request_data[4])}'),
            # markdown.text(
            # markdown.markdown_decoration.quote('Постановщик:'),
            # f'{markdown.bold(creator_fullname)}'),
            # markdown.text(
            # markdown.markdown_decoration.quote('Телефон:'),
            # f'{markdown.bold(request_data[8])}'),
            # markdown.text(
            # markdown.markdown_decoration.quote('Зона:'),
            # f'{markdown.bold(request_data[13])}'),
            # markdown.text(
            # markdown.markdown_decoration.quote('Вид неисправности:'),
            # f'{markdown.bold(request_data[14])}'),
            markdown.text(
                markdown.markdown_decoration.quote('Заголовок задачи:'),
                f'{markdown.bold(request_data[14])}'),
            markdown.text(
                markdown.markdown_decoration.quote('Детальное описание:'),
                f'{markdown.bold(request_data[15])}'),
            markdown.text(
                markdown.markdown_decoration.quote('Исполнитель:'),
                f'{markdown.bold(executor_fullname)}'),
            markdown.text(
                markdown.markdown_decoration.quote('Телефон:'),
                f'{markdown.bold(executor)}'),
            markdown.text(
                markdown.markdown_decoration.quote('Отчёт:'),
                f'{markdown.bold(report)}'),
            sep='\n')

    def handover_or_hangon_request_message(self, request_data):
        deal_id = f'{request_data[1]}/{request_data[0]}'
        time = dt.datetime.strftime(request_data[26], "%H:%M")
        return markdown.text(
            markdown.text(
                markdown.markdown_decoration.quote('Запрос:'),
                markdown.code(deal_id)),
            markdown.text(
                markdown.markdown_decoration.quote('Дата создания:'),
                f'{markdown.bold(request_data[26].date())}',
                f'{markdown.bold(time)}'),
            markdown.text(
                markdown.markdown_decoration.quote('Отделение:'),
                f'{markdown.bold(request_data[2])}'),
            markdown.text(
                markdown.markdown_decoration.quote('Изменён статус:'),
                f'{markdown.bold(request_data[4])}'),
            sep='\n')

    async def edit_message(self, request_data, group_msg_id):
        print(self.create_current_request_menu(
                current_deal=request_data,
                group_message_id=group_msg_id
            ))
        json = {
            'chat_id': await self.group_id(department_id=self.department_id),
            'message_id': group_msg_id,
            'caption': self.request_detail_message(
                request_data=request_data),
            'parse_mode': 'MarkdownV2',
            'reply_markup': self.create_current_request_menu(
                current_deal=request_data,
                group_message_id=group_msg_id
            )
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=f'{self.base_url}/editMessageCaption',
                    headers=self.headers,
                    json=json) as response:
                return await response.json()

    async def send_message(self, request_data, chat_id, msg_to_reply):
        print(self.handover_or_hangon_request_message(
                request_data=request_data))
        json = {
            'chat_id': chat_id,
            'text': self.handover_or_hangon_request_message(
                request_data=request_data),
            'reply_to_message_id': msg_to_reply,
            'parse_mode': 'MarkdownV2',
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=f'{self.base_url}/sendMessage',
                    headers=self.headers,
                    json=json) as response:
                return await response.json()
