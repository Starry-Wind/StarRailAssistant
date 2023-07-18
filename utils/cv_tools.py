'''
Author: Xe-No
Date: 2023-05-17 21:45:43
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-06-27 17:36:19
Description: 一些cv工具

Copyright (c) 2023 by Xe-No, All Rights Reserved. 
'''

from utils.get_angle import get_angle
import time 
import cv2 as cv
import numpy as np
import win32gui, win32api, win32con
import pyautogui


def cart_to_polar(xy):
    x,y = xy
    angle = np.degrees(np.arctan2(y, x))
    r = np.linalg.norm([x, y])
    return angle, r

def get_vec(pos1,pos2):
    x1,y1 =pos1
    x2,y2 =pos2
    return  [x2-x1,y2-y1]

def draw_lines(img, point_list, color=(0, 255, 0), thickness=2):
    '''
    在给定的图像上绘制多条线段。

    Args:
        img: 待绘制的原始图像，可以是 numpy.ndarray 类型。
        point_list: 包含多个点坐标的列表，用来表示需要连接的线段的端点坐标。
        color: 线段颜色，可以是元组类型，例如 (0, 255, 0) 表示绿色，默认为 (0, 255, 0)。
        thickness: 线段宽度，用来控制线段的粗细程度，默认为 2。

    Returns:
        绘制完成后的图像。

    Raises:
        TypeError: 如果输入参数格式不正确，则会抛出类型错误异常。
    '''
    if not isinstance(img, np.ndarray):
        raise TypeError('The input `img` parameter must be a numpy.ndarray type.')
    # if not isinstance(color, tuple) or not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
    #     raise TypeError('The input `color` parameter must be a tuple of integers between 0 and 255.')
    if not isinstance(thickness, int) or thickness < 1:
        raise TypeError('The input `thickness` parameter must be a positive integer.')

    for i in range(len(point_list)-1):
        pt1 = point_list[i]
        pt2 = point_list[i+1]
        cv.line(img, pt1, pt2, color, thickness)

    return img

def get_sorted_waypoints(map_hsv, points):
    hcolor = {}
    hcolor['start'] = 180 / 2
    hcolor['pioneer'] = 60 / 2
    hcolor['hunt'] = 10 / 2
    hcolor['garbage'] = 40 / 2

    waypoints = []
    for point in points:
        waypoint = {}
        waypoint['pos'] = point
        h, s, v = map_hsv[point[1], point[0]]
        waypoint['s'] = s
        waypoint['type'] = [k for k, val in hcolor.items() if val == h][0]
        waypoints.append(waypoint)

    waypoints = sorted(waypoints, key=lambda x: x['s'])
    si, sp = [[i, waypoint] for i, waypoint in enumerate(waypoints) if waypoint['type'] == 'start'][0]
    sorted_waypoints = [sp]
    sp['index'] = 0
    waypoints.pop(si)
    cp = sp
    count = 1
    while 1:

        if len(waypoints) == 0:
            break
        # 根据s，找s==最大值的列表
        max_s = max(waypoints, key=lambda x: x['s'])['s']
        print(max_s)
        max_list = [[i, waypoint] for i, waypoint in enumerate(waypoints) if waypoint['s'] == max_s]

        print(max_list)
        # 找到最近的点并排序
        ci, cp = min(max_list, key=lambda x: np.linalg.norm(get_vec(x[1]['pos'], cp['pos'])))
        # 最大值列表必然位于前面
        # ci = [ i for i, p in enumerate(max_list) if p['pos'] == cp['pos']][0]
        cp['index'] = count
        waypoints.pop(ci)
        sorted_waypoints.append(cp)
        count += 1
    return sorted_waypoints

def find_cluster_points(mask):
    retval, labels, stats, centroids = cv.connectedComponentsWithStats(mask, connectivity=8)
    # 输出每个聚类的中心坐标
    result = []
    # cv.imwrite('debug/mask.png', mask)
    for i in range(1, len(stats)):
        x = int(stats[i][0] + stats[i][2] / 2)
        y = int(stats[i][1] + stats[i][3] / 2)
        result.append([x, y])
    return result
def find_color_points(img, bgr_color, max_sq = 64):
    mask = np.sum((img-bgr_color)**2,axis=-1)<= max_sq
    mask = np.uint8(mask)*255
    cv.imwrite('debug/mask.png', mask)
    return find_cluster_points(mask)

def find_color_points_inrange(img, lowerb, upperb):
    mask = cv.inRange(img, lowerb, upperb)
    return find_cluster_points(mask)

def find_nearest_point(points, target):
    """
    在一个点的列表中找到离目标点最近的点
    :param points: 一个包含多个点的列表，每个点都是二元组 (x, y)
    :param target: 目标点，二元组 (x, y)
    :return: 离目标点最近的点，二元组 (x, y)
    """
    # 将点的列表转换为 NumPy 数组
    points_array = np.array(points)
    
    # 将目标点转换为 NumPy 数组，并将其扩展为与 points_array 相同的形状
    target_array = np.array(target)
    target_array = np.expand_dims(target_array, axis=0)
    target_array = np.repeat(target_array, points_array.shape[0], axis=0)
    
    # 计算每个点与目标点之间的距离
    distances = np.linalg.norm(points_array - target_array, axis=1)
        
    # 找到距离最小的点的索引
    nearest_index = np.argmin(distances)
    
    # 返回距离最小的点
    return nearest_index, points[nearest_index]


# def find_color_points(img, color):
# 	ys, xs = np.where(np.all(img == color, axis=-1))[:]
# 	points = np.array([xs,ys]).T
# 	return points

def dilate_img(img, iterations = 3):
	kernel = np.ones((3, 3), np.uint8)
	dilation = cv.dilate(img, kernel, iterations=iterations)
	return dilation

def get_binary(img, threshold=200):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, binary = cv.threshold(gray, threshold, 255, cv.THRESH_BINARY)
    return binary

def show_img(img, scale=1, title='Image'):
    # cv.namedWindow('image', cv.WINDOW_NORMAL)
    h, w = img.shape[:2]
    img = cv.resize( img ,(int(w*scale), int(h*scale))  )
    cv.imshow(title, img)
    cv.waitKey(0)  # 显示图像并等待1秒
    cv.destroyAllWindows()  

def show_imgs(imgs, title='Image'):
    cv.imshow(title, np.hstack(imgs))
    cv.waitKey(0)
    cv.destroyAllWindows()  



def show_imgs(imgs, scale=1, title='Image'):
    img = np.hstack(imgs)
    show_img(img, scale, title)

def get_loc(im, imt):
    result = cv.matchTemplate(im, imt, cv.TM_CCORR_NORMED)
    return cv.minMaxLoc(result)

def take_screenshot(rect):
    # 返回RGB图像
    hwnd = win32gui.FindWindow("UnityWndClass", "崩坏：星穹铁道")
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    rect[0] += left
    rect[1] += top 
    temp = pyautogui.screenshot(region=rect)
    screenshot = np.array(temp)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
    return screenshot

def take_minimap(rect = [47,58,187,187]):
    return take_screenshot(rect)

def take_fine_screenshot(rect = [47,58,187,187], n = 5, dt=0.01, dy=200):
    total = take_screenshot(rect)
    n = 5
    for i in range(n):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -dy, 0, 0)
        mask = cv.compare(total, take_screenshot(rect), cv.CMP_EQ )
        total = cv.bitwise_and(total, mask )
        time.sleep(dt)
    time.sleep(0.1)
    for i in range(n):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, dy, 0, 0)
        mask = cv.compare(total, take_screenshot(rect), cv.CMP_EQ )
        total = cv.bitwise_and(total, mask )
        time.sleep(dt)
    minimap = cv.bitwise_and(total, mask )
    return minimap

def get_mask(img, color_range):
    lower, upper = color_range
    return cv.inRange(img, lower, upper)

def get_mask_mk2(img_r):
	img_hsv = cv.cvtColor(img_r, cv.COLOR_BGR2HSV)
	h, s, v = cv.split(img_hsv)
	# 筛选白色 H S<10  V 60~90%
	mask1 = (s <25)*(v>255*0.6)*(v<255*0.9)
	# 筛选蓝色摄像头扫过的白色
	mask2 = (95 <h)*(h<105)*(0<s)*(s<50)*(200<v)*(v<240)
	mask = mask1 | mask2
	img_mask = mask.astype(np.uint8)*255
	return img_mask

def get_mask_mk3(map_bgra):
	b,g,r,a = cv.split(map_bgra)
	mask = (a>250) & (b>80)
	return mask.astype(np.uint8)*255

def get_camera_fan(color = [130, 130, 60],angle=0, w=187, h=187, delta=90, dimen =3, radius= 90):
    center = (w//2, h//2)
    # radius = min(h, w)//2
    fan = np.zeros((h, w, dimen), np.uint8)
    # 计算圆心位置
    cx, cy = w // 2, h // 2
    axes = (w // 2, h // 2) 
    
    startAngle, endAngle = angle -45, angle +45 # 画90度

    cv.ellipse(fan, (cx, cy), axes, 0, startAngle, endAngle, color , -1)
    return fan

def get_gradient_mask(w,h):
    center = [w // 2, h // 2]
    radius = 0.8 *w
    # 创建渐变掩码
    gradient_mask = np.zeros((w, h), dtype=np.uint8)
    for r in range(gradient_mask.shape[0]):
        for c in range(gradient_mask.shape[1]):
            dist = np.sqrt((r-center[1])**2 + (c-center[0])**2)
            value =  max(0, min(1 - 2*dist/radius, 1))
            gradient_mask[r,c] = int(value * 255)
    return gradient_mask


def filter_contours_surround_point(gray, point):
    """过滤掉不包围指定点的轮廓"""
    contours, hierarchy = cv.findContours(gray, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    # 过滤掉所有不包含指定点的轮廓
    filtered_contours = []
    for i in range(len(contours)):
        if cv.pointPolygonTest(contours[i], point, False) < 0:
            filtered_contours.append(contours[i])
            
    # 过滤掉所有不包围指定点的轮廓
    surrounded_contours = []
    for i in range(len(filtered_contours)):
        rect = cv.boundingRect(filtered_contours[i])
        if rect[0] <= point[0] <= rect[0] + rect[2] and \
           rect[1] <= point[1] <= rect[1] + rect[3]:
            surrounded_contours.append(filtered_contours[i])
            
    return surrounded_contours


def sift_match(img1, img2):
    # 创建SIFT对象
    sift = cv.SIFT_create()

    # 检测关键点和描述符
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)


    # 建立FLANN匹配对象
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv.FlannBasedMatcher(index_params, search_params)

    # 根据描述符进行匹配
    matches = flann.knnMatch(des1, des2, k=2)

    # 筛选最优匹配
    good_matches = []
    for m, n in matches:
        if m.distance < 0.9 * n.distance:
            good_matches.append(m)

    # 绘制匹配结果
    img_match = cv.drawMatches(img1, kp1, img2, kp2, good_matches, None, flags=2)

    return img_match

def match_scaled(img, template, scale, mask=False):
    # 返回最大相似度，中心点x、y
    t0 = time.time()
    # finish = cv.imread(".imgs/finish_fighting.jpg")
    # while True:
    #     result = calculated.scan_screenshot(finish,pos=(0,95,100,100))
    #     if result["max_val"] > 0.98:
    #         print("未进入战斗")                       
    #         break

    resized_template = cv.resize(template, (0,0), fx=scale, fy=scale)
    if mask ==False:
        res = cv.matchTemplate(img, resized_template, cv.TM_CCORR_NORMED)
    else:
        res = cv.matchTemplate(img, resized_template, cv.TM_CCORR_NORMED, mask=resized_template)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    h, w = resized_template.shape[:2]
    x, y = max_loc[0] + w/2, max_loc[1] + h/2
    return max_val, (int(x), int(y))

def find_best_match(img, template, scale_range=(140, 170, 1)):
    """
    说明:
        缩放图片并与进行模板匹配
    参数:
        :param img: 图片
        :param img: 匹配的模板
        :param img: 缩放区间以及步长
    返回:
        最佳缩放大小, 最大匹配度, 最近位置, 模板缩放后的长度, 模板缩放后的宽度
    """
    best_match = None
    max_corr = 0
    length = 0
    width = 0
    
    for scale_percent in range(scale_range[0], scale_range[1],scale_range[2]):
        
        # width = int(template.shape[1] * scale_percent / 100)
        # height = int(template.shape[0] * scale_percent / 100)
        # dim = (width, height)
        # resized_template = cv.resize(template, dim, interpolation=cv.INTER_AREA)
        resized_template = cv.resize(template, (0,0), fx=scale_percent/100.0, fy=scale_percent/100.0)

        res = cv.matchTemplate(img, resized_template, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        log.debug(f'正在匹配 {scale_percent}，相似度{max_loc}')
        if max_val > max_corr:
            length, width, __ = resized_template.shape
            length = int(length)
            width = int(width)
            max_corr = max_val

    return scale_percent, max_corr, max_loc, length, width