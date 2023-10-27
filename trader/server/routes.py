from aiohttp import web


routes = web.RouteTableDef()

@routes.get('/health')
async def health_check(request: web.Request):
    return web.Response(status=200)

@routes.post('/trade')
async def handle_trade(request: web.Request):
    trader = request.app['trader']
    data = await request.json()
    request.app.loop.create_task(trader.handle_request(data))
    return web.Response(status=200)