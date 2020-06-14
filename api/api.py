from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import re
import motor.motor_asyncio

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient

myclient = client("mongodb://10.1.1.142:27017/setu")

mydb = myclient["setu"]


async def find(condition, num):  # collection为str参数
    result = await mydb.command(
        'aggregate', 'setu_all_v3',
        pipeline=[{'$match': condition},
                  {'$sample': {'size': num}}],
        explain=False)
    return result['cursor']['firstBatch']


@app.get("/setu")
async def setu_v1(tag: str = Query('', max_length=35), r18: bool = False):
    print('{0}SETU_V1: tag:[{1}] r18:[{2}]{3}'.format('>' * 20, tag, r18, '<' * 20))
    try:
        data_re = re.compile(tag)
        condition = {'tags': data_re}
        if r18:
            condition['type'] = 'sexy'
            data = await find(condition, 1)
        else:
            condition['type'] = 'porn'
            data = await find(condition, 1)
        setu = list(data)
        setus_num = len(setu)
        if setus_num != 0:
            setu_full = setu[0]
            setu_full['code'] = 200
            return setu_full
        else:
            return JSONResponse(status_code=404, content={'code': 404, 'msg': '色图库中没找到色图~'})
    except Exception as error:
        return JSONResponse(status_code=500, content={'code': 500, 'msg': '爆炸啦~', 'error': str(error)})


@app.get("/setu_v2")
async def setu_v2(tag: str = Query('', max_length=45), num: int = Query(1, ge=1, le=10), r18: bool = False):
    print('{0}SETU_V2: tag:[{1}] r18:[{2}] num:[{3}]{4}'.format('>' * 20, tag, r18, num, '<' * 20))
    try:
        data_re = re.compile(tag)
        condition = {'tags': data_re}
        if r18:
            condition['type'] = 'porn'
            data = await find(condition, num)
        else:
            condition['type'] = 'sexy'
            data = await find(condition, num)
        setu = list(data)
        setus_num = len(setu)
        if setus_num != 0:
            for i in range(setus_num):  # 兼容v2
                setu[i]['page'] = 'p{}'.format(setu[i]['page'])
            setu_full = {'code': 200}
            setu_full['data'] = setu
            return setu_full
        else:
            return JSONResponse(status_code=404, content={'code': 404, 'msg': '色图库中没找到色图~'})
    except Exception as error:
        return JSONResponse(status_code=500, content={'code': 500, 'msg': '爆炸啦~', 'error': str(error)})


ways_v3 = {'normal': 'normal', 'sexy': 'sexy', 'porn': 'porn'}


@app.get("/setu_v3")
async def setu_v3(tag: str = Query('', max_length=45), num: int = Query(1, ge=1, le=10),
                  type: str = Query('', max_length=15)):
    print('{0}SETU_V3: tag:[{1}] type:[{2}] num:[{3}]{4}'.format('>' * 20, tag, type, num, '<' * 20))
    try:
        data_re = re.compile(tag)
        if type == '' or type.isspace():
            condition = {'tags': data_re}
            data = await find(condition, num)
        else:
            condition = {'tags': data_re, 'type': ways_v3[type]}
            data = await find(condition, num)
        setu = list(data)
        setus_num = len(setu)
        if setus_num != 0:
            setu_full = {'code': 200}
            setu_full['data'] = setu
            return setu_full
        else:
            return JSONResponse(status_code=404, content={'code': 404, 'msg': '色图库中没找到色图~'})
    except Exception as error:
        return JSONResponse(status_code=500, content={'code': 500, 'msg': '爆炸啦~', 'error': str(error)})
