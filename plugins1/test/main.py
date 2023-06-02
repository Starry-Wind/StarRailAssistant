from . import *
import flet as ft
from utils.log import log

def main(e=None):
    if e:
        page:ft.Page = e
        page.clean()
        page.update()
    log.info("开始")

# 定义插件钩子函数
@hookimpl
def add_option(SRA, option_dict):
    return SRA.add_option(option_dict, "每日任务", main, 2)
