'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-25 12:54:10
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-25 14:54:11
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import PySimpleGUI as psg


#设置窗体里面的内容，是以列表样式
'''
psg.set_options(font=("Arial Bold",14))
l1=psg.Text("Enter Name")
l2=psg.Text("Faculty")
l3=psg.Text("Subjects")
l4=psg.Text("Category")
l5=psg.Multiline(" ", expand_x=True, key='-OUT-', expand_y=True,justification='left')
t1=psg.Input("", key='-NM-')
rb=[]
rb.append(psg.Radio("Arts", "faculty", key='arts', enable_events=True,default=True))
rb.append(psg.Radio("Commerce", "faculty", key='comm', enable_events=True))
rb.append(psg.Radio("Science", "faculty", key='sci',enable_events=True))
cb=[]
cb.append(psg.Checkbox("History", key='s1'))
cb.append(psg.Checkbox("Sociology", key='s2'))
cb.append(psg.Checkbox("Economics", key='s3'))
a1=psg.Button("大世界")
a2=psg.Button("模拟宇宙")
a3=psg.Button("检查更新")
b1=psg.Button("OK")
b2=psg.Button("Exit")
layout=[[l1, t1],[rb],[cb],[b1, l5, b2]]
window = psg.Window('星穹铁道小助手', layout, size=(715,250))
while True:
    event, values = window.read()
    print (event, values)
    if event in (psg.WIN_CLOSED, 'Exit'): break
    if event == 'comm':
        if values['comm']==True:
            window['s1'].update(text="Accounting")
            window['s2'].update(text="Business Studies")
            window['s3'].update(text="Statistics")
    if event == 'sci':
        if values['sci']==True:
            window['s1'].update(text="Physics")
            window['s2'].update(text="Mathematics")
            window['s3'].update(text="Biology")
    if event == 'arts':
        if values['arts']==True:
            window['s1'].update(text="History")
            window['s2'].update(text="Sociology")
            window['s3'].update(text="Economics")
    if event=='OK':
        print(265151)
        subs=[x.Text for x in cb if x.get()==True]
        fac=[x.Text for x in rb if x.get()==True]
        out="""
        Name={}
        Faculty: {}
        Subjects: {}
        """.format(values['-NM-'], fac[0], " ".join(subs))
        print(out)
        window['-OUT-'].update(out)
window.close()
'''
psg.set_options(font=("Arial Bold",14))
a1=psg.Button("大世界")
a2=psg.Button("模拟宇宙")
a3=psg.Button("检查更新")
layout=[[a1, a2, a3]]
window = psg.Window('星穹铁道小助手', layout, size=(310,100))
while True:
    event, values = window.read()
    print (event, values)
    if event in (psg.WIN_CLOSED, 'Exit'): break
    if event=='大世界':
        ...
    if event=='模拟宇宙':
        ...
    if event=='检查更新':
        ...
window.close()
