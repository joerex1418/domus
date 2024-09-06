import asyncio

from httpx import Limits
from httpx import Request
from httpx import Response
from httpx import Client, AsyncClient

from ._ptext import log_response



async def _fetch_request(client: AsyncClient, req: Request, **kwargs):
    # if kwargs.get("rebuild_with_client") == True:
    #     req = client.build_request(req.method, req.url, headers=req.headers)
    
    r = await client.send(req)
    
    if r.status_code != 200:
        log_response(r)

        return r
    
    return r


async def _fetch_bulk(request_list: list[Request], **kwargs):
    limits = Limits(
        max_connections=kwargs.get("max_connections", 500), 
        max_keepalive_connections=kwargs.get("max_keepalive_connections", 500)
    )

    async with AsyncClient(limits=limits) as client:
        tasks = (asyncio.create_task(_fetch_request(client, req, **kwargs)) for req in request_list)
        responses = await asyncio.gather(*tasks)
        return responses


def fetch_bulk(request_list: list[Request], **kwargs) -> list[Response]:
    if isinstance(request_list, Request):
        request_list = [request_list]
    return asyncio.run(_fetch_bulk(request_list, **kwargs))



def send_request(req: Request, existing_client: Client | None = None):
    if existing_client == None:
        client = Client()
    else:
        client = existing_client

    r = client.send(req)
    
    if r.status_code != 200:
        log_response(r)

    if existing_client == None:
        client.close()

    return r