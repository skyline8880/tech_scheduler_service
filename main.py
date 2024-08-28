import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from bitrix.bitrix_api import BitrixMethods
from database.database import Database
from request.request import Request
from scheduler.scheduler import Tracker

app = FastAPI()


@app.post('/')
async def send_to_scheduler(request: Request):
    bm = await BitrixMethods(
        department_sign=request.department_id).collect_portal_data()
    if bm.token is None:
        raise HTTPException(status_code=400)
    if request.token != bm.token:
        raise HTTPException(status_code=401)
    await Tracker().request_timetracker(
        start_date=request.start_date,
        deal_id=request.deal_id,
        department_id=request.department_id)


@app.get('/deals/{deal_id}&{department_id}')
async def get_deal_data(deal_id: int, department_id: int):
    db = Database()
    data = await db.get_current_request_of_department(
        department_id=department_id, bitrix_deal_id=deal_id)
    return {
        'bitrix_deal_id': data[0],
        'department_id': data[1],
        'department_name': data[2],
        'status_id': data[3],
        'status_name': data[4],
        'AS creator_telegram_id': data[5],
        'creator_username': data[6],
        'creator_full_name': data[7],
        'creator_phone': data[8],
        'creator_department_id': data[9],
        'creator_department': data[10],
        'creator_position_id': data[11],
        'creator_position': data[12],
        'zone': data[13],
        'brake_type': data[14],
        'creator_photo': data[15],
        'short_description': data[16],
        'detailed_description': data[17],
        'executor_telegram_id': data[18],
        'executor_username': data[19],
        'executor_full_name': data[20],
        'executor_phone': data[21],
        'executor_department_id': data[22],
        'executor_department': data[23],
        'executor_position_id': data[24],
        'executor_position': data[25],
        'executor_photo': data[26],
        'report': data[27],
        'create_date': data[28],
        'creator_last_name': data[29],
        'creator_first_name': data[30],
        'executor_last_name': data[31],
        'executor_first_name': data[32]
    }


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8887)
