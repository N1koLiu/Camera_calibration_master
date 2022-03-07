import cv2
import numpy as np
import glob

# 找棋盘格角点
# 阈值
# 设置寻找亚像素角点的参数，采用的停止准则是最大循环次数30和最大误差容限0.001
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# 棋盘格模板规格
w = 9  # 内角点个数，内角点是和其他格子连着的点
h = 7

# 获取标定板角点的位置
# 世界坐标系中的棋盘格点,例如(0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)，去掉Z坐标，记为二维矩阵
objp = np.zeros((w * h, 3), np.float32)
objp[:, :2] = np.mgrid[0:w, 0:h].T.reshape(-1, 2)

# 储存棋盘格角点的世界坐标和图像坐标对
objpoints = []  # 在世界坐标系中的三维点
imgpoints = []  # 在图像平面的二维点
a = 0
# 读取照片
images = glob.glob('Source/*.jpg')
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 找到棋盘格角点
    # 棋盘图像(8位灰度或彩色图像)  棋盘尺寸  存放角点的位置
    ret, corners = cv2.findChessboardCorners(gray, (w, h), None)
    # 如果找到足够点对，将其存储起来

    if ret == True:
        # 角点精确检测
        # 参数：输入图像 角点初始坐标 搜索窗口为2*winsize+1 死区 求角点的迭代终止条件
        cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        objpoints.append(objp)
        imgpoints.append(corners)
        # 将角点在图像上显示
        cv2.drawChessboardCorners(img, (w, h), corners, ret)
        a += 1
        cv2.imwrite("Result1/{}.jpg".format(a), img)
        cv2.waitKey(10)
cv2.destroyAllWindows()

# 标定、去畸变
# 输入：世界坐标系里的位置 像素坐标 图像的像素尺寸大小 3*3矩阵，相机内参数矩阵 畸变矩阵
# 输出：标定结果 相机的内参数矩阵 畸变系数 旋转矩阵 平移向量
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
# mtx：内参数矩阵
# dist：畸变系数
# rvecs：旋转向量 （外参数）
# tvecs ：平移向量 （外参数）
print("标定结果 ret:", ret)
print("内参矩阵 mtx:\n", mtx)  # 内参数矩阵
print("畸变系数 dist:\n", dist)  # 畸变系数   distortion cofficients = (k_1,k_2,p_1,p_2,k_3)
print("旋转向量(外参) rvecs:\n", np.array(rvecs))  # 旋转向量  # 外参数
print("平移向量(外参) tvecs:\n", np.array(tvecs))  # 平移向量  # 外参数

# 反投影误差
# 通过反投影误差，我们可以来评估结果的好坏。越接近0，说明结果越理想。
# 通过之前计算的内参数矩阵、畸变系数、旋转矩阵和平移向量，使用cv2.projectPoints()计算三维点到二维图像的投影，
# 然后计算反投影得到的点与图像上检测到的点的误差，最后计算一个对于所有标定图像的平均误差，这个值就是反投影误差。
total_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
    total_error += error
print(("total error: "), total_error / len(objpoints))

print('Starting Gesture_Draw...')


# 绘制简单的坐标系，调用此函数记得将下面的坐标修改为axis_axis


# 绘制简单的坐标系，调用此函数记得将下面的坐标修改为axis_axis
def draw_axis(img, corners, imgpts):
    imgpts = np.int32(imgpts).reshape(-1, 2)
    img = cv2.line(img, tuple(imgpts[0]), tuple(imgpts[4]), (255, 0, 0), 5)
    img = cv2.line(img, tuple(imgpts[0]), tuple(imgpts[1]), (255, 0, 255), 5)
    img = cv2.line(img, tuple(imgpts[0]), tuple(imgpts[3]), (0, 0, 255), 5)

    return img


# 绘制立体方块在Pattern上，调用此函数记得将下面的坐标修改为axis_cube
axis_cube = np.float32([[0, 0, 0], [0, 2, 0], [2, 2, 0], [2, 0, 0], [0, 0, -2], [0, 2, -2], [2, 2, -2], [2, 0, -2]])
axis_axis = np.float32([[0, 0, 0], [0, 3, 0], [3, 3, 0], [3, 0, 0], [0, 0, -3], [0, 3, -3], [3, 3, -3], [3, 0, -3]])


# 绘制立体方块在Pattern上，调用此函数记得将下面的坐标修改为axis_cube
def draw_cube(img, corners, imgpts):
    imgpts = np.int32(imgpts).reshape(-1, 2)
    # draw ground floor in green
    img = cv2.drawContours(img, [imgpts[:4]], -1, (0, 255, 0), -3)
    # draw pillars in blue color
    for i, j in zip(range(4), range(4, 8)):
        img = cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (255), 3)
    # draw top layer in red color
    img = cv2.drawContours(img, [imgpts[4:]], -1, (0, 0, 255), 3)

    return img


criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((7 * 9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:7].T.reshape(-1, 2)

img = cv2.imread('Source/IMG_20220306_150308.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
ret, corners = cv2.findChessboardCorners(gray, (9, 7), None)
if ret == True:
    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    # Find the rotation and translation vectors.
    _, rvecs, tvecs, inliers = cv2.solvePnPRansac(objp, corners2, mtx, dist)
    # project 3D points to image plane
    imgpts, jac = cv2.projectPoints(axis_cube, rvecs, tvecs, mtx, dist)
    img = draw_cube(img, corners2, imgpts)

    imgpts, jac = cv2.projectPoints(axis_axis, rvecs, tvecs, mtx, dist)
    img = draw_axis(img, corners2, imgpts)


    cv2.imwrite('3Daxes.jpg', img)
a=0
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (9, 7), None)
    if ret == True:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        # Find the rotation and translation vectors.
        _, rvecs, tvecs, inliers = cv2.solvePnPRansac(objp, corners2, mtx, dist)
        # project 3D points to image plane
        imgpts, jac = cv2.projectPoints(axis_cube, rvecs, tvecs, mtx, dist)
        img = draw_cube(img, corners2, imgpts)

        imgpts, jac = cv2.projectPoints(axis_axis, rvecs, tvecs, mtx, dist)
        img = draw_axis(img, corners2, imgpts)
        a+=1
        cv2.imwrite('Result2/{}_3Daxes_3DSquare.jpg'.format(a), img)


print('Gesture_Draw Finised')
