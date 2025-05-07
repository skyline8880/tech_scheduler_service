import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from bitrix.bitrix_api import BitrixMethods
from bitrix.bitrix_params import create_deal_result
from database.database import Database
from request.request import Request
from scheduler.scheduler import Tracker

app = FastAPI()


@app.post('/')
async def send_to_scheduler(request: Request):
    db = Database()
    bm = await BitrixMethods(
        department_sign=request.department_id).collect_portal_data()
    if bm.token is None:
        raise HTTPException(status_code=400)
    if request.token != bm.token:
        raise HTTPException(status_code=401)
    data = await db.get_current_request_of_department(
        department_id=request.department_id, bitrix_deal_id=request.deal_id)
    if data is None:
        raise HTTPException(status_code=404)
    await Tracker().request_timetracker(
        start_date=request.start_date,
        deal_id=request.deal_id,
        department_id=request.department_id)


@app.get('/deals/{deal_id}&{department_id}')
async def get_deal_data(deal_id: int, department_id: int):
    db = Database()
    data = await db.get_current_request_of_department(
        department_id=department_id, bitrix_deal_id=deal_id)
    if data is None:
        raise HTTPException(status_code=404)
    return create_deal_result(data=data)


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8887)
