#!/usr/bin/env python3
# Author AlisaCat
# -*- encoding:utf-8 -*-
# Created by AlisaCat at 2023/5/11

import os
import time
import shutil
import asyncio
import hashlib

from pathlib import Path
from tqdm import tqdm as tq
from zipfile import ZipFile, BadZipFile
from typing import Dict, Optional, Any, Union, Tuple, List

from .log import log
from .requests import *
from .exceptions import Exception
from .config import normalize_file_path, modify_json_file, read_json_file, CONFIG_FILE_NAME

tmp_dir = 'tmp'

async def verify_file_hash(json_path: Path, keep_file: Optional[List[str]] = []) -> bool:
    """
    说明：
        校验文件
    参数：
        :param json_path: 文件地址
    返回:
        :return bool
    """
    for data in json_path:
        file_path = Path() / data['path']
        if not os.path.exists(file_path):
            return False, file_path
        if os.path.isfile(file_path) and str(file_path) not in keep_file:
            if hashlib.md5(file_path.read_bytes()).hexdigest() != data['hash']:
                return False, file_path
    return True, None

async def unzip(zip, zip_path: Path):
    global tmp_dir
    with ZipFile(zip, 'r') as zf:
        for member in tq(zf.infolist(), desc='解压中'):
            if member.filename.startswith(zip_path):
                zf.extract(member, tmp_dir)
                log.debug(f'[资源文件更新]正在提取{member.filename}')

async def remove_file(folder_path: Path,keep_folder: Optional[List[str]] = [],keep_file: Optional[List[str]] = []) -> None:
    if os.path.exists(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path) and item not in keep_folder:
                shutil.rmtree(item_path)
            elif os.path.isfile(item_path) and item not in keep_file:
                os.remove(item_path)

async def move_file(src_folder: Path, dst_folder,keep_folder: Optional[List[str]] = [],keep_file: Optional[List[str]] = []) -> None:
    
    # 创建目标文件夹（如果不存在）
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    # 遍历源文件夹中的所有文件和文件夹
    for item in os.listdir(src_folder):
        # 构造源文件路径和目标文件路径
        src_path = os.path.join(src_folder, item)
        dst_path = os.path.join(dst_folder, item)
        if os.path.isdir(src_path) and item not in keep_folder:
            shutil.move(src_path, dst_path)
        elif os.path.isfile(src_path) and item not in keep_file:
            shutil.move(src_path, dst_path)

async def update_file(url_proxy: str="",
                      raw_proxy: str="",
                      rm_all: bool=False, 
                      skip_verify: bool=True,
                      type: str="",
                      version: str="",
                      url_zip: str="",
                      unzip_path: str="",
                      keep_folder: Optional[List[str]] = [],
                      keep_file: Optional[List[str]] = [],
                      zip_path: str="",
                      name: str="") -> bool:
    """
    说明：
        更新文件
    参数：
        :param url_proxy: github代理
        :param raw_proxy: rawgithub代理
        :param rm_all: 是否强制删除文件
        :param skip_verify: 是否跳过检验
        :param type: 更新文件的类型 map\temp
        :param version: 版本验证地址 map
        :param url_zip: zip下载链接
        :param unzip_path: 解压地址（删除用）
        :param keep_folder: 保存的文件夹
        :param keep_file: 保存的文件
        :param zip_path: 需要移动的文件地址
        :param name: 更新的文件名称
    """
    global tmp_dir

    url_version = f'{raw_proxy}https://raw.githubusercontent.com/Starry-Wind/Honkai-Star-Rail/{version}/version.json' if 'http' in raw_proxy or raw_proxy == '' else f'https://raw.githubusercontent.com/Starry-Wind/Honkai-Star-Rail/{version}/version.json'.replace('raw.githubusercontent.com', raw_proxy)
    url_zip = url_proxy+url_zip if 'http' in url_proxy or url_proxy == '' else url_zip.replace('github.com', url_proxy)
    url_list = f'{raw_proxy}https://raw.githubusercontent.com/Starry-Wind/Honkai-Star-Rail/{version}/{type}_list.json' if 'http' in raw_proxy or raw_proxy == '' else f'https://raw.githubusercontent.com/Starry-Wind/Honkai-Star-Rail/{version}/{type}_list.json'.replace('raw.githubusercontent.com', raw_proxy)
    
    #tmp_zip = os.path.join(tmp_dir, f'{type}.zip')
    tmp_zip = Path() / tmp_dir / f'{type}.zip'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    if not os.path.exists(unzip_path):
        os.makedirs(unzip_path)
        modify_json_file(CONFIG_FILE_NAME, f"{type}_version", "0")
    elif rm_all:
        modify_json_file(CONFIG_FILE_NAME, f"{type}_version", "0")

    log.info(f'[资源文件更新]正在检查远程版本是否有更新...')

    for index, _ in enumerate(range(3)):
        try:
            remote_version = await get(url_version)
            remote_version = remote_version.json()['version']
            break
        except BaseException as e:
            if index < 2:
                log.info(f'[资源文件更新]获取远程版本失败, 正在重试: {e}')
            else:
                log.info(f'[资源文件更新]获取远程版本失败: {e}')
            log.info("将在10秒后重试")
            await asyncio.sleep(10)
    else:
        log.info(f'[资源文件更新]重试次数已达上限，退出程序')
        raise Exception(f'[资源文件更新]重试次数已达上限，退出程序')

    log.info(f'[资源文件更新]获取远程版本成功: {remote_version}')

    local_version = read_json_file(CONFIG_FILE_NAME).get(f'{type}_version', '0')

    if remote_version != local_version:
        log.info(f'[资源文件更新]本地版本与远程版本不符，开始更新资源文件->{url_zip}')
        for _ in range(3):
            try:
                await download(url_zip, tmp_zip)
                log.info(f'[资源文件更新]下载更新包成功, 正在覆盖本地文件: {local_version} -> {remote_version}')
                await unzip(tmp_zip, zip_path)
                break
            except BadZipFile:
                log.info(f'[资源文件更新]下载压缩包失败, 重试中: BadZipFile')
            except BaseException as e:
                log.info(f'[资源文件更新]下载压缩包失败: {e}')
            log.info("将在10秒后重试")
            await asyncio.sleep(10)
        else:
            log.info(f'[资源文件更新]重试次数已达上限，退出程序')
            raise Exception(f'[资源文件更新]重试次数已达上限，退出程序')


        #shutil.rmtree('..\Honkai-Star-Rail-beta-2.7')
        await remove_file(unzip_path, keep_folder, keep_file)
        await move_file(os.path.join(tmp_dir, zip_path), unzip_path, [], keep_file)

        log.info(f'[资源文件更新]正在校验资源文件')
        for _ in range(3):
            try:
                map_list = await get(url_list)
                map_list = map_list.json()
                break
            except BaseException as e:
                log.info(f'[资源文件更新]校验文件下载失败: {e}')
            log.info("将在10秒后重试")
            await asyncio.sleep(10)
        else:
            log.info(f'[资源文件更新]重试次数已达上限，退出程序')
            raise Exception(f'[资源文件更新]重试次数已达上限，退出程序')
        
        verify, path = await verify_file_hash(map_list, keep_file)
        if not verify:
            raise Exception(f"[资源文件更新]{path}校验失败, 程序退出")

        log.info(f'[资源文件更新]校验完成, 更新本地{name}文件版本号 {local_version} -> {remote_version}')

        # 更新版本号
        modify_json_file(CONFIG_FILE_NAME, f"{type}_version", remote_version)

        log.info(f'[资源文件更新]删除临时文件{tmp_dir}')
        shutil.rmtree(tmp_dir, ignore_errors=True)
    else:
        log.info(f'[资源文件更新]资源文件已是最新版本 {local_version} = {remote_version}')
        if not skip_verify:
            log.info(f'[资源文件更新]准备校验资源文件')
            for index, _ in enumerate(range(3)):
                try:
                    remote_map_list = await get(url_list)
                    remote_map_list = remote_map_list.json()
                    break
                except BaseException as e:
                    if index < 2:
                        log.info(f'[资源文件更新]获取{name}文件列表失败, 正在重试: {e}')
                    else:
                        log.info(f'[资源文件更新]获取{name}文件列表失败: {e}')
                    log.info("将在10秒后重试")
                    await asyncio.sleep(10)
            else:
                log.info(f'[资源文件更新]获取{name}文件列表重试次数已达上限，退出程序')
                raise Exception(f'[资源文件更新]获取{name}文件列表重试次数已达上限，退出程序')

            log.debug(f'[资源文件更新]获取{name}文件列表成功.')


            verify, path = await verify_file_hash(remote_map_list, keep_file)
            if not verify:
                log.error(f"[资源文件更新]{path}发现文件缺失, 3秒后将使用远程版本覆盖本地版本")
                return "rm_all"
            log.info(f'[资源文件更新]文件校验完成.')

    log.info(f'[资源文件更新]更新完成.')
    return True


def update_file_main(url_proxy: str="",
                    raw_proxy: str="",
                    rm_all: bool=False, 
                    skip_verify: bool=True,
                    type: str="",
                    version: str="",
                    url_zip: str="",
                    unzip_path: str="",
                    keep_folder: Optional[List[str]] = [],
                    keep_file: Optional[List[str]] = [],
                    zip_path: str="",
                    name: str=""):
    """
    说明：
        更新文件
    参数：
        :param url_proxy: github代理
        :param raw_proxy: rawgithub代理
        :param skip_verify: 是否跳过检验
        :param type: 更新文件的类型 map\temp
        :param version: 版本验证地址 map
        :param url_zip: zip下载链接
        :param unzip_path: 解压地址（删除用）
        :param keep_folder: 保存的文件夹
        :param keep_file: 保存的文件
        :param zip_path: 需要移动的文件地址
        :param name: 更新的文件名称
    """
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    log.info(f'[资源文件更新]即将资源文件更新，本操作会覆盖本地{name}文件..')
    check_file_status = asyncio.run(update_file(url_proxy,raw_proxy,False,skip_verify,type,version,url_zip,unzip_path,keep_folder,keep_file,zip_path,name))
    if check_file_status == "rm_all":
        time.sleep(3)
        check_file_status = asyncio.run(update_file(url_proxy,raw_proxy,True,skip_verify,type,version,url_zip,unzip_path,keep_folder,keep_file,zip_path,name))
    elif check_file_status == "download_error":
        check_file_status = asyncio.run(update_file(url_proxy,raw_proxy,False,skip_verify,type,version,url_zip,unzip_path,keep_folder,keep_file,zip_path,name))
