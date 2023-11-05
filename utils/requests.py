'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-25 12:54:10
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-06-02 00:55:10
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import flet as ft
import httpx
import tqdm.asyncio
from httpx_socks import AsyncProxyTransport

from .config import CONFIG_FILE_NAME, _, sra_config_obj
from .log import log

proxies=sra_config_obj.proxies
transport = AsyncProxyTransport.from_url(proxies) if proxies else None

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
    async with httpx.AsyncClient(transport=transport if transport else None) as client:
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
    async with httpx.AsyncClient(transport=transport if transport else None) as client:
        return await client.post(url,
                                headers=headers,
                                params=params,
                                timeout=timeout,
                                **kwargs)

async def download(url: str, save_path: Path, page: ft.Page=None, pb: ft.ProgressBar=None):
    """
    说明：
        下载文件(带进度条)
    参数：
        :param url: url
        :param save_path: 保存路径
    """
    import time
    save_path.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(transport=transport if transport else None).stream(method='GET', url=url, follow_redirects=True) as datas:
        size = int(datas.headers.get("Content-Length", 0))
        f = save_path.open("wb")
        pbar = tqdm.asyncio.tqdm(total=size, unit="iB", desc=url.split('/')[-1], unit_scale=True, unit_divisor=1024, colour="green")
        i=0
        async for chunk in datas.aiter_bytes(1024 * 1024):
            i+=len(chunk)
            f.write(chunk)
            if pb:
                pb.value = 100/size * i * 0.01
            if page:
                page.update()
            pbar.update(len(chunk))
        pbar.close()
        f.close()

def webhook_and_log(message):
    log.info(message)
    url = sra_config_obj.webhook_url
    if url == "" or url == None:
        return
    try:
        post(url, json={"content": message})
    except Exception as e:
        log.error(_("Webhook发送失败: {e}").format(e=e))
