"""
Author: AlisaCat
Date: 2023-05-11 21:45:43
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-06-02 00:44:46
Description: 

Copyright (c) 2023 by AlisaCat, All Rights Reserved. 
"""

import os
import time
import shutil
import asyncio
import hashlib
import flet as ft

from pathlib import Path
from tqdm import tqdm as tq
from zipfile import ZipFile, BadZipFile
from typing import Dict, Optional, Any, Union, Tuple, List

from .log import log
from .requests import *
from .exceptions import Exception
from .config import normalize_file_path, modify_json_file, read_json_file, get_file, CONFIG_FILE_NAME, _

tmp_dir = "tmp"

class update_file:
    def __init__(self, page: ft.Page=None, pb: ft.ProgressBar=None) -> None:
        """
        说明:
            文件更新
        参数:
            :param page: GUI继承函数
        """
        self.page = page
        self.pb = pb

    async def verify_file_hash(self, json_path: Path, keep_file: Optional[List[str]] = []) -> bool:
        """
        说明：
            校验文件
        参数：
            :param json_path: 文件地址
        返回:
            :return bool
        """
        for i,data in enumerate(json_path):
            file_path = Path() / data["path"]
            if not os.path.exists(file_path) and str(file_path) not in keep_file:
                return False, file_path
            if os.path.isfile(file_path) and str(file_path) not in keep_file:
                log.debug(hashlib.md5(file_path.read_bytes()).hexdigest())
                if hashlib.md5(file_path.read_bytes()).hexdigest() != data["hash"]:
                    return False, file_path
            if self.pb:
                self.pb.value = 100/len(json_path) * i * 0.01
            if self.page:
                self.page.update()
        return True, None

    async def unzip(self, zip, zip_path: Path):
        global tmp_dir
        with ZipFile(zip, "r") as zf:
            for i,member in enumerate(tq(zf.infolist(), desc=_("解压中"))):
                if member.filename.startswith(zip_path):
                    zf.extract(member, tmp_dir)
                    log.debug(_("[资源文件更新]正在提取{member.filename}").format(member=member))
                    if self.pb:
                        self.pb.value = len(zf.infolist())/100 * i * 0.01
                    if self.page:
                        self.page.update()

    async def remove_file(self, folder_path: Path,keep_folder: Optional[List[str]] = [],keep_file: Optional[List[str]] = []) -> None:
        if os.path.exists(folder_path):
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path) and item not in keep_folder:
                    shutil.rmtree(item_path)
                elif os.path.isfile(item_path) and item not in keep_file:
                    os.remove(item_path)

    async def move_file(self, src_folder: Path, dst_folder,keep_folder: Optional[List[str]] = [],keep_file: Optional[List[str]] = []) -> None:
        for item in get_file(src_folder,keep_folder,keep_file, True):
            if dst_folder in item:
                dst_path = item.replace(src_folder, "./")
                # 创建目标文件夹（如果不存在）
                if not os.path.exists(dst_path.rsplit("/",1)[0]) and dst_path.rsplit("/",1)[0] != ".":
                    os.makedirs(dst_path.rsplit("/",1)[0])
                #dst_path = os.path.join(dst_folder, item)
                shutil.copy(item, dst_path)
        # 遍历源文件夹中的所有文件和文件夹
        """
        for item in os.listdir(src_folder):
            # 构造源文件路径和目标文件路径
            src_path = os.path.join(src_folder, item)
            dst_path = os.path.join(dst_folder, item)
            if os.path.isdir(src_path) and item not in keep_folder:
                shutil.copy(src_path, dst_path)
            if os.path.isfile(src_path) and item not in keep_file:
                shutil.copy(src_path, dst_path)
        """

    async def copy_files(self, source_path:Path, destination_path:Path, copy:List=[]):
        #if os.path.exists(new_folder):
            #shutil.rmtree(new_folder)
        #os.makedirs(new_folder, exist_ok=True)
        # 创建目标文件夹
        os.makedirs(destination_path, exist_ok=True)
        # 遍历文件和文件夹列表
        for item in copy:
            item_path = source_path / item
            destination2_path = destination_path / item
            # 如果是文件
            if os.path.isfile(item_path):
                shutil.copy2(item_path, destination_path)
            # 如果是文件夹
            elif os.path.isdir(item_path):
                shutil.copytree(item_path, destination2_path, dirs_exist_ok=True)
            
    async def update_file(self, url_proxy: str="",
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

        url_version = f"{raw_proxy}https://raw.githubusercontent.com/Starry-Wind/StarRailAssistant/{version}/version.json" if "http" in raw_proxy or raw_proxy == "" else f"https://raw.githubusercontent.com/Starry-Wind/StarRailAssistant/{version}/version.json".replace("raw.githubusercontent.com", raw_proxy)
        url_zip = url_proxy+url_zip if "http" in url_proxy or url_proxy == "" else url_zip.replace("github.com", url_proxy)
        url_list = f"{raw_proxy}https://raw.githubusercontent.com/Starry-Wind/StarRailAssistant/{version}/{type}_list.json" if "http" in raw_proxy or raw_proxy == "" else f"https://raw.githubusercontent.com/Starry-Wind/StarRailAssistant/{version}/{type}_list.json".replace("raw.githubusercontent.com", raw_proxy)
        
        #tmp_zip = os.path.join(tmp_dir, f"{type}.zip")
        tmp_zip = Path() / tmp_dir / f"{type}.zip"
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        if not os.path.exists(unzip_path):
            os.makedirs(unzip_path)
            modify_json_file(CONFIG_FILE_NAME, f"{type}_version", "0")
        elif rm_all:
            modify_json_file(CONFIG_FILE_NAME, f"{type}_version", "0")

        log.info(_("[资源文件更新]正在检查远程版本是否有更新..."))

        for index, __ in enumerate(range(3)):
            try:
                remote_version = await get(url_version)
                remote_version = remote_version.json()["version"]
                break
            except BaseException as e:
                if index < 2:
                    log.info(_("[资源文件更新]获取远程版本失败, 正在重试: {e}").format(e=e))
                else:
                    log.info(_("[资源文件更新]获取远程版本失败: {e}").format(e=e))
                log.info(_("将在10秒后重试"))
                await asyncio.sleep(10)
        else:
            log.info(_("[资源文件更新]重试次数已达上限，退出程序"))
            raise Exception(_("[资源文件更新]重试次数已达上限，退出程序"))

        log.info(f"[资源文件更新]获取远程版本成功: {remote_version}")

        local_version = read_json_file(CONFIG_FILE_NAME).get(f"{type}_version", "0")

        if remote_version != local_version:
            if name == _("脚本"):
                await self.copy_files(Path(), Path() / "StarRailAssistant_backup", ["utils", "temp", "map", "config.json", "get_width.py", "Honkai_Star_Rail.py", "gui.py"])
            log.info(_("[资源文件更新]本地版本与远程版本不符，开始更新资源文件->{url_zip}").format(url_zip=url_zip))
            for __ in range(3):
                try:
                    await download(url_zip, tmp_zip, self.page, self.pb)
                    log.info(_("[资源文件更新]下载更新包成功, 正在覆盖本地文件: {local_version} -> {remote_version}").format(local_version=local_version,remote_version=remote_version))
                    await self.unzip(tmp_zip, zip_path)
                    break
                except BadZipFile:
                    log.info(_("[资源文件更新]下载压缩包失败, 重试中: BadZipFile"))
                except BaseException as e:
                    log.info(_("[资源文件更新]下载压缩包失败: {e}").format(e=e))
                log.info(_("将在10秒后重试"))
                await asyncio.sleep(10)
            else:
                log.info(_("[资源文件更新]重试次数已达上限，退出程序"))
                raise Exception(_("[资源文件更新]重试次数已达上限，退出程序"))


            #shutil.rmtree("..\StarRailAssistant-beta-2.7")
            #await self.remove_file(unzip_path, keep_folder, keep_file)
            await self.move_file(os.path.join(tmp_dir, zip_path), unzip_path, [], keep_file)

            log.info(_("[资源文件更新]正在校验资源文件"))
            for __ in range(3):
                try:
                    map_list = await get(url_list)
                    map_list = map_list.json()
                    break
                except BaseException as e:
                    log.info(_("[资源文件更新]校验文件下载失败: {e}").format(e=e))
                log.info(_("将在10秒后重试"))
                await asyncio.sleep(10)
            else:
                log.info(_("[资源文件更新]重试次数已达上限，退出程序"))
                raise Exception(_("[资源文件更新]重试次数已达上限，退出程序"))
            
            verify, path = await self.verify_file_hash(map_list, keep_file)
            if not verify:
                raise Exception(_("[资源文件更新]{path}校验失败, 程序退出").format(path=path))

            log.info(_("[资源文件更新]校验完成, 更新本地{name}文件版本号 {local_version} -> {remote_version}").format(name=name, local_version=local_version, remote_version=remote_version))

            # 更新版本号
            modify_json_file(CONFIG_FILE_NAME, f"{type}_version", remote_version)

            shutil.rmtree(tmp_dir, ignore_errors=True)
            log.info(_("[资源文件更新]删除临时文件{tmp_dir}").format(tmp_dir=tmp_dir))
        else:
            log.info(_("[资源文件更新]资源文件已是最新版本 {local_version} = {remote_version}").format(local_version=local_version, remote_version=remote_version))
            if not skip_verify:
                log.info(_("[资源文件更新]准备校验资源文件"))
                for index, __ in enumerate(range(3)):
                    try:
                        remote_map_list = await get(url_list)
                        remote_map_list = remote_map_list.json()
                        break
                    except BaseException as e:
                        if index < 2:
                            log.info(_("[资源文件更新]获取{name}文件列表失败, 正在重试: {e}").format(name=name, e=e))
                        else:
                            log.info(_("[资源文件更新]获取{name}文件列表失败: {e}").format(name=name, e=e))
                        log.info(_("将在10秒后重试"))
                        await asyncio.sleep(10)
                else:
                    log.info(_("[资源文件更新]获取{name}文件列表重试次数已达上限，退出程序").format(name=name, e=e))
                    raise Exception(_("[资源文件更新]获取{name}文件列表重试次数已达上限，退出程序").format(name=name))

                log.debug(_("[资源文件更新]获取{name}文件列表成功.").format(name=name))


                verify, path = await self.verify_file_hash(remote_map_list, keep_file)
                if not verify:
                    log.error(_("[资源文件更新]{path}发现文件缺失, 3秒后将使用远程版本覆盖本地版本").format(path=path))
                    return "rm_all"
                log.info(_("[资源文件更新]文件校验完成."))
                shutil.rmtree(tmp_dir, ignore_errors=True)
                log.info(_("[资源文件更新]删除临时文件{tmp_dir}").format(tmp_dir=tmp_dir))

        log.info(_("[资源文件更新]更新完成."))
        return True

    def update_file_main(self, url_proxy: str="",
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
        log.info(_("[资源文件更新]即将资源文件更新，本操作会覆盖本地{name}文件..").format(name=name))
        check_file_status = asyncio.run(self.update_file(url_proxy,raw_proxy,False,skip_verify,type,version,url_zip,unzip_path,keep_folder,keep_file,zip_path,name))
        if check_file_status == "rm_all":
            time.sleep(3)
            check_file_status = asyncio.run(self.update_file(url_proxy,raw_proxy,True,skip_verify,type,version,url_zip,unzip_path,keep_folder,keep_file,zip_path,name))
        elif check_file_status == "download_error":
            check_file_status = asyncio.run(self.update_file(url_proxy,raw_proxy,False,skip_verify,type,version,url_zip,unzip_path,keep_folder,keep_file,zip_path,name))
    