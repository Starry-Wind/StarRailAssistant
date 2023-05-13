import httpx
import tqdm.asyncio
from pathlib import Path
from typing import Dict, Optional, Any, Union, Tuple


async def get(url: str,
                *,
                headers: Optional[Dict[str, str]] = None,
                params: Optional[Dict[str, Any]] = None,
                timeout: Optional[int] = 20,
                **kwargs) -> httpx.Response:
    """
    说明：
        httpx的get请求封装
    参数：
        :param url: url
        :param headers: 请求头
        :param params: params
        :param data: data
        :param json: json
        :param timeout: 超时时间
    """
    async with httpx.AsyncClient() as client:
        return await client.get(url,
                                headers=headers,
                                params=params,
                                timeout=timeout,
                                **kwargs)

async def post(url: str,
                *,
                headers: Optional[Dict[str, str]] = None,
                params: Optional[Dict[str, Any]] = None,
                timeout: Optional[int] = 20,
                **kwargs) -> httpx.Response:
    """
    说明：
        httpx的post请求封装
    参数：
        :param url: url
        :param headers: 请求头
        :param params: params
        :param data: data
        :param json: json
        :param timeout: 超时时间
    """
    async with httpx.AsyncClient() as client:
        return await client.post(url,
                                headers=headers,
                                params=params,
                                timeout=timeout,
                                **kwargs)

async def download(url: str, save_path: Path):
    """
    说明：
        下载文件(带进度条)
    参数：
        :param url: url
        :param save_path: 保存路径
    """
    save_path.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient().stream(method='GET', url=url, follow_redirects=True) as datas:
        size = int(datas.headers.get('Content-Length', 0))
        f = save_path.open('wb')
        async for chunk in tqdm.asyncio.tqdm(iterable=datas.aiter_bytes(1),
                                                desc=url.split('/')[-1],
                                                unit='iB',
                                                unit_scale=True,
                                                unit_divisor=1024,
                                                total=size,
                                                colour='green'):
            f.write(chunk)
        f.close()
