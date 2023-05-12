#!/usr/bin/env python3
# Author AlisaCat
# -*- encoding:utf-8 -*-
# Created by AlisaCat at 2023/5/11

import asyncio
import hashlib
import orjson
import os
import shutil
import time
from zipfile import ZipFile, BadZipFile

import aiohttp
from tqdm import tqdm
from typing import Dict, Optional, Any, Union, Tuple

from tool.config import normalize_file_path, modify_json_file
from tool.log import log


async def download_file(url, local_path, session):
    async with session.get(url) as response:
        with open(local_path, 'wb') as f:
            async for data in response.content.iter_chunked(1024):
                f.write(data)


async def fetch_version(url, session):
    async with session.get(url) as response:
        response_data = orjson.loads(await response.text())
        return response_data['version']


async def fetch_data(url, session):
    async with session.get(url) as response:
        response_data = orjson.loads(await response.text())
        return response_data


# 定义校验函数
def verify_file_hash(path, expected_hash):
    with open(path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    if file_hash == expected_hash:
        # log.info(f'{path} 校验通过')
        return True
    else:
        # log.warning(f'{path} 校验失败')
        return False


async def update_file(url_proxy: str="", rm_all: bool=False, skip_verify: bool=True) -> bool:
    if rm_all:
        shutil.rmtree(os.path.join('.', 'map'), ignore_errors=True)
        shutil.rmtree(os.path.join('.', 'temp'), ignore_errors=True)

    url_version = f'{url_proxy}https://raw.githubusercontent.com/Starry-Wind/Honkai-Star-Rail/map/version.json'
    url_zip = f'{url_proxy}https://github.com/Starry-Wind/Honkai-Star-Rail/archive/refs/heads/map.zip'
    url_map_list = f'{url_proxy}https://raw.githubusercontent.com/Starry-Wind/Honkai-Star-Rail/map/map_list.json'
    url_temp_list = f'{url_proxy}https://raw.githubusercontent.com/Starry-Wind/Honkai-Star-Rail/map/temp_list.json'
    config_path = normalize_file_path("config.json")
    tmp_dir = 'tmp'
    tmp_zip = os.path.join(tmp_dir, 'map.zip')
    temp_dir = os.path.join(".", 'temp')
    map_dir = os.path.join(".", 'map')

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    if not (os.path.exists(temp_dir) and os.path.exists(map_dir)):
        modify_json_file("config.json", "map_version", "0")

    async with aiohttp.ClientSession() as session:
        log.info(f'[资源文件更新]正在检查远程版本是否有更新...')

        for index, _ in enumerate(range(3)):
            try:
                remote_version = await fetch_version(url_version, session)
                break
            except Exception as e:
                if index < 2:
                    log.info(f'[资源文件更新]获取远程版本失败, 正在重试: {e}')
                else:
                    log.info(f'[资源文件更新]获取远程版本失败: {e}')
        else:
            log.info(f'[资源文件更新]重试次数已达上限，退出程序')
            raise Exception(f'[资源文件更新]重试次数已达上限，退出程序')

        log.info(f'[资源文件更新]获取远程版本成功: {remote_version}')

        with open(config_path, 'rb') as f:
            data = orjson.loads(f.read())
            local_version = data['map_version']

        if remote_version != local_version:
            log.info(f'[资源文件更新]本地版本与远程版本不符，开始更新资源文件->{url_zip}')
            for _ in range(3):
                for _ in range(3):
                    try:
                        await download_file(url_zip, tmp_zip, session)
                        break
                    except Exception as e:
                        log.info(f'[资源文件更新]下载压缩包失败: {e}')
                else:
                    log.info(f'[资源文件更新]重试次数已达上限，退出程序')
                    raise Exception(f'[资源文件更新]重试次数已达上限，退出程序')

                log.info(f'[资源文件更新]下载更新包成功, 正在覆盖本地文件: {local_version} -> {remote_version}')
                shutil.rmtree(os.path.join('.', 'map'), ignore_errors=True)
                shutil.rmtree(os.path.join('.', 'temp'), ignore_errors=True)
                try:
                    with ZipFile(tmp_zip, 'r') as zf:
                        for member in tqdm(zf.infolist(), desc='解压中'):
                            if member.filename.startswith('Honkai-Star-Rail-map/map/') or member.filename.startswith(
                                    'Honkai-Star-Rail-map/temp/'):
                                zf.extract(member, tmp_dir)
                                log.debug(f'[资源文件更新]正在提取{member.filename}')
                            if member.filename.startswith('Honkai-Star-Rail-map/map_') or member.filename.startswith(
                                    'Honkai-Star-Rail-map/temp_'):
                                zf.extract(member, tmp_dir)
                                log.debug(f'[资源文件更新]正在提取{member}')
                except BadZipFile:
                    log.info(f'[资源文件更新]下载压缩包失败, 重试中: BadZipFile')
                    continue
                break

            shutil.move(os.path.join(os.path.join(tmp_dir, 'Honkai-Star-Rail-map'), 'temp'), ".")
            shutil.move(os.path.join(os.path.join(tmp_dir, 'Honkai-Star-Rail-map'), 'map'), ".")

            log.info(f'[资源文件更新]正在校验资源文件')
            map_json_path = os.path.join(os.path.join(tmp_dir, 'Honkai-Star-Rail-map'), 'map_list.json')
            temp_json_path = os.path.join(os.path.join(tmp_dir, 'Honkai-Star-Rail-map'), 'temp_list.json')

            # 读取json文件
            with open(map_json_path, 'rb') as f:
                map_list = orjson.loads(f.read())
            with open(temp_json_path, 'rb') as f:
                temp_list = orjson.loads(f.read())

            # 遍历列表进行校验
            total_files = len(map_list + temp_list)
            for i, item in enumerate(map_list + temp_list):
                path = item['path']
                expected_hash = item['hash']
                # 输出校验进度
                progress = f'{i + 1}/{total_files}'
                log.debug(f'[资源文件更新][{progress}] {path} 校验完成')
                if not verify_file_hash(path, expected_hash):
                    raise Exception(f"[资源文件更新][{progress}]{path}校验失败, 程序退出")

            log.info(f'[资源文件更新]校验完成, 更新本地地图文件版本号 {local_version} -> {remote_version}')
            # 更新版本号
            data['map_version'] = remote_version
            with open(config_path, 'wb') as f:
                f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

            log.info(f'[资源文件更新]删除临时文件{tmp_dir}')
            shutil.rmtree(tmp_dir, ignore_errors=True)
            # os.remove(map_json_path)
            # os.remove(temp_json_path)
            # os.remove(tmp_zip)
            # os.rmdir(tmp_dir)

        else:
            log.info(f'[资源文件更新]资源文件已是最新版本 {local_version} = {remote_version}')
            if not skip_verify:
                log.info(f'[资源文件更新]准备校验资源文件')
                for index, _ in enumerate(range(3)):
                    try:
                        remote_map_list = await fetch_data(url_map_list, session)
                        break
                    except Exception as e:
                        if index < 2:
                            log.info(f'[资源文件更新]获取地图文件列表失败, 正在重试: {e}')
                        else:
                            log.info(f'[资源文件更新]获取地图文件列表失败: {e}')
                else:
                    log.info(f'[资源文件更新]获取地图文件列表重试次数已达上限，退出程序')
                    raise Exception(f'[资源文件更新]获取地图文件列表重试次数已达上限，退出程序')

                log.debug(f'[资源文件更新]获取地图文件列表成功, 正在获取temp文件列表.')

                for index, _ in enumerate(range(3)):
                    try:
                        remote_temp_list = await fetch_data(url_temp_list, session)
                        break
                    except Exception as e:
                        if index < 2:
                            log.info(f'[资源文件更新]获取temp文件列表失败, 正在重试: {e}')
                        else:
                            log.info(f'[资源文件更新]获取temp文件列表失败: {e}')
                else:
                    log.info(f'[资源文件更新]获取temp文件列表重试次数已达上限，退出程序')
                    raise Exception(f'[资源文件更新]获取temp文件列表重试次数已达上限，退出程序')

                log.debug(f'[资源文件更新]获取temp文件列表成功')
                total_files = len(remote_map_list + remote_temp_list)
                for i, item in enumerate(remote_map_list + remote_temp_list):
                    path = item['path']
                    expected_hash = item['hash']
                    # 输出校验进度
                    progress = f'{i + 1}/{total_files}'
                    log.debug(f'[资源文件更新][{progress}] {path} 校验完成')
                    try:
                        if not verify_file_hash(path, expected_hash):
                            log.error(f"[资源文件更新][{progress}]{path}校验失败 文件损坏, 3秒后将使用远程版本覆盖本地版本")
                            data['map_version'] = "0"
                            with open(config_path, 'wb') as f:
                                f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
                            return "rm_all"
                    except FileNotFoundError:
                        log.error(f"[资源文件更新][{progress}]{path}发现文件缺失, 3秒后将使用远程版本覆盖本地版本")
                        return "rm_all"
                log.info(f'[资源文件更新]文件校验完成.')
    log.info(f'[资源文件更新]更新完成.')
    return True


def update_file_main(url_proxy=""):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    log.info(f'[资源文件更新]即将资源文件更新，本操作会覆盖本地地图文件..')
    check_file_status = asyncio.run(update_file(url_proxy=url_proxy, rm_all=False))
    while True:
        if check_file_status == "rm_all":
            time.sleep(3)
            check_file_status = asyncio.run(update_file(url_proxy=url_proxy, rm_all=True))
        elif check_file_status == "download_error":
            check_file_status = asyncio.run(update_file(url_proxy=url_proxy, rm_all=False))
        else:
            break
