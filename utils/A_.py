#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 12:38:58 2017

@author: ming
"""


import cv2
import time
import numpy as np

from .log import log
        
def a_(img, start_pos, end_pos):
    start_time = time.time()
    maps=cv2.cvtColor(img, cv2.IMREAD_GRAYSCALE)#读取地图图像，灰度读入。灰度大于222表示障碍物
    maps_size=np.array(maps)#获取图像行和列大小
    hight=maps_size.shape[0]#行数->y
    width=maps_size.shape[1]#列数->x

    star={'位置':start_pos,'代价':700,'父节点':start_pos}#起点
    end={'位置':end_pos,'代价':0,'父节点':end_pos}#终点

    openlist=[]#open列表，存储可能路径
    closelist=[star]#close列表，已走过路径
    step_size=4#搜索步长。
    #步长太小，搜索速度就太慢。步长太大，可能直接跳过障碍，得到错误的路径
    #步长大小要大于图像中最小障碍物宽度
    while 1:
        if time.time()-start_time > 30:
            break
        add=([0,step_size],[0,-step_size],[step_size,0],[-step_size,0])#可能运动的四个方向增量
        s_point=closelist[-1]['位置']#获取close列表最后一个点位置，S点
        for i in range(len(add)):
            x=s_point[0]+add[i][0]#检索超出图像大小范围则跳过
            if x<0 or x>=width:
                continue
            y=s_point[1]+add[i][1]
            if y<0 or y>=hight:#检索超出图像大小范围则跳过
                continue
            G=abs(x-star['位置'][0])+abs(y-star['位置'][1])#计算代价
            H=abs(x-end['位置'][0])+abs(y-end['位置'][1])#计算代价
            F=G+H
            if H<20:#当逐渐靠近终点时，搜索的步长变小
                step_size=1
            addpoint={'位置':(x,y),'代价':F,'父节点' :s_point}#更新位置
            count=0
            for ii in openlist:
                if ii['位置']==addpoint['位置']:
                    count+=1
            for ii in closelist:
                if ii['位置']==addpoint['位置']:
                    count+=1
            if count==0:#新增点不在open和close列表中
                if maps[y,x] < 222:#非障碍物 
                    openlist.append(addpoint)
        t_point={'位置':(50,50),'代价':10000,'父节点':(50,50)}
        for j in range(len(openlist)):#寻找代价最小点
            if openlist[j]['代价']<t_point['代价']:
                t_point=openlist[j]
        for j in range(len(openlist)):#在open列表中删除t点
            if t_point==openlist[j]:
                openlist.pop(j)
                break
        closelist.append(t_point)#在close列表中加入t点
        #cv2.circle(informap,t_point['位置'],1,(200,0,0),-1)
        if t_point['位置']==end['位置']:#找到终点！！
            log.info("找到终点")
            break
    #log.debug(closelist)
    
    #逆向搜索找到路径
    road=[]
    road.append(closelist[-1])
    point=road[-1]
    k=0
    
    while 1:
        for i in closelist:
            if i['位置']==point['父节点']:#找到父节点
                point=i
                #log.debug(point)
                road.append(point)
        if point==star:
            log.info("路径搜索完成")
            break
    road = [i['位置'] for i in road] #导航路径
    return road
