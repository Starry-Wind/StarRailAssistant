'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-25 12:54:10
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-29 20:19:27
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import httpx
import tqdm.asyncio

from httpx_socks import AsyncProxyTransport
from pathlib import Path
from typing import Dict, Optional, Any, Union, Tuple

from .log import log
from .config import read_json_file, CONFIG_FILE_NAME

proxies=read_json_file(CONFIG_FILE_NAME).get("proxies", "")
transport = AsyncProxyTransport.from_url(proxies)

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
    async with httpx.AsyncClient(transport=transport) as client:
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
    async with httpx.AsyncClient(transport=transport) as client:
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
    async with httpx.AsyncClient(transport=transport).stream(method='GET', url=url, follow_redirects=True) as datas:
        size = int(datas.headers.get("Content-Length", 0))
        f = save_path.open("wb")
        pbar = tqdm.asyncio.tqdm(total=size, unit="MiB", unit_scale=True, unit_divisor=1024, colour="green")
        async for chunk in datas.aiter_bytes(1024 * 1024):
            f.write(chunk)
            pbar.update(len(chunk))
        pbar.close()
        f.close()

def webhook_and_log(message):
    log.info(message)
    url = read_json_file(CONFIG_FILE_NAME, False).get("webhook_url")
    if url == "" or url == None:
        return
    try:
        post(url, json={"content": message})
    except Exception as e:
        log.error(f"Webhook发送失败: {e}")
