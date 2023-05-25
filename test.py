'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-25 12:54:10
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-25 14:09:23
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import PySimpleGUI as sg    
from hashlib import sha1
from loguru import logger
from utils.log import log,info
import os,shutil
#首先设置窗口样式
import sys
import traceback
def get_cur_info():

    """Return the frame object for the caller's stack frame."""

    try:

        raise Exception

    except:

        f = sys.exc_info()[2].tb_frame.f_back

    return (f.f_code.co_name, f.f_lineno,traceback.extract_stack()[-2].filename.split("\\")[-1].split(".")[0])

def callfunc():

    print(get_cur_info())

if __name__ == '__main__':
    callfunc()

'''
#设置窗体里面的内容，是以列表样式
layout = [
    [sg.Text('请输入站号：',size=15),sg.InputText(key='-INzhaohao-',size=(20,1))],
    [sg.Text('程序运行记录',justification='center')],
    [sg.Output(size=(70, 20),font=("宋体", 10))], 
    [sg.Button('查询'), sg.Exit()]
]  
#窗口实例化 并设置窗口名，把内容放进去    
window = sg.Window('区域站要素查询', layout)  
#主题循环
while True:
    #读取按键和各个插件的值    window.read()窗口显示
    #event获取按键值
    #values[‘控件的KEY’]                    
    event, values = window.read()
    #print(event, values)      
    if event in (None, 'Exit'):      
        break      
    elif event == '查询':
        shuju=None
        if shuju == None:
            #print('提示','找不到'+str(values['-INzhaohao-'])+'站的数据')
            info("eeee")
        else:
            sg.Print('This text is white on a green background', text_color='white', background_color='green', font='Courier 10')
            sg.Print('The first call sets some window settings like font that cannot be changed')
            sg.Print('This is plain text just like a print would display')
            sg.Print('White on Red', background_color='red', text_color='white')
            sg.Print('The other print', 'parms work', 'such as sep', sep=',')
            sg.Print('To not extend a colored line use the "end" parm', background_color='blue', text_color='white', end='')
            sg.Print('\nThis line has no color.')
#窗口关闭
window.close()
'''