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
    async with httpx.AsyncClient() as client:
        return await client.get(url,
                                headers=headers,
                                params=params,
                                timeout=timeout,
                                **kwargs)

async def download(url: str, save_path: Path):
    save_path.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient().stream(method='GET', url=url, follow_redirects=True) as datas:
        size = int(datas.headers['Content-Length'])
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