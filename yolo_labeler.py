import cv2
import numpy as np
import os


# 해당 txt 파일이 있나
def file_check(image_name):
    global path_dir

    # 이미지 이름만 받아온다
    image_name_split = image_name.split('.')
    image_name = image_name_split[0]

    txt_name = path_dir + '/' + image_name + ".txt"

    return os.path.isfile(txt_name)


# 텍스트 파일에 저장된 박스 정보를 불러온다
def file_read(image_name):
    global path_dir

    # 이미지 이름만 받아온다
    image_name_split = image_name.split('.')
    image_name1 = image_name_split[0]

    txt_name = path_dir + '/' + image_name1 + ".txt"

    # 텍스트 파일이 없으면 0,0,0,0으로 저장하고 불러온다
    if not os.path.isfile(txt_name):
        f = open(txt_name, 'w+')
        f.write(class_name + " 0 0 0 0")
        set_position(0, 0, 0, 0)
        f.close()
        return

    # 텍스트 파일이 있으면 좌표정보를 읽어온다
    f = open(txt_name, 'r+')
    line = f.read()
    line_split = line.split(' ')
    set_position(line_split[1], line_split[2], line_split[3], line_split[4])
    f.close()


# 폴더에 어떻게 저장할지
def file_write(image_name):
    global class_name, path_dir

    # 이미지 이름만 받아온다
    image_name_split = image_name.split('.')
    image_name = image_name_split[0]

    txt_name = path_dir + '/' + image_name + ".txt"

    # 기존 파일내용을 지워버리고 새로 씀, 없으면 새로 만든다
    f = open(txt_name, 'w+')

    data = class_name + " {} {} {} {}".format(yolo_x, yolo_y, yolo_w, yolo_h)
    f.write(data)

    f.close()


# 박스를 어떻게 그릴 건지
def box_write(s_x, s_y, e_x, e_y):
    global yolo_x, yolo_y, yolo_w, yolo_h

    if s_y > e_y:
        s_y, e_y = e_y, s_y
    if s_x > e_x:
        s_x, e_x = e_x, s_x

    yolo_x = ((s_x + e_x) // 2) / frame_width
    yolo_y = ((s_y + e_y) // 2) / frame_height
    yolo_w = (e_x - s_x) / frame_width
    yolo_h = (e_y - s_y) / frame_height


# 파일에서 읽은 yolo 좌표를 실제 이미지에서의 픽셀 위치로 변환
def set_position(x, y, w, h):
    global s_x, s_y, e_x, e_y, frame_width, frame_height

    s_x = int(frame_width * float(x) - frame_width * float(w) / 2)
    e_x = int(frame_width * float(x) + frame_width * float(w) / 2)
    s_y = int(frame_height * float(y) - frame_height * float(h) / 2)
    e_y = int(frame_height * float(y) + frame_height * float(h) / 2)


# 사각형을 그리는 마우스 콜백
def mouse_callback(event, x, y, flags, param):
    global frame, frame_show, s_x, s_y, e_x, e_y, mouse_pressed

    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_pressed = True
        s_x, s_y = x, y
        frame_show = np.copy(frame)

    elif event == cv2.EVENT_MOUSEMOVE:
        if mouse_pressed:
            frame_show = np.copy(frame)
            cv2.rectangle(frame_show, (s_x, s_y), (x, y), (0, 255, 0), 1)

    elif event == cv2.EVENT_LBUTTONUP:
        mouse_pressed = False
        e_x, e_y = x, y

        # 좌표 조정
        if s_y > e_y:
            s_y, e_y = e_y, s_y
        if s_x > e_x:
            s_x, e_x = e_x, s_x


# 트랙바가 움직일 때마다 실행되는 콜백 함수
def trackbar_callback(idx):
    global index, trackbar_changed, frame, frame_show, frame_width, frame_height
    global s_x, s_y, e_x, e_y
    global file_list_jpg

    # 트랙바 위치의 주소로 index 변경
    index = idx

    # 트랙바가 움직인 후 새로운 위치에 있는 사진을 불러온다
    frame = cv2.imread(path_dir + '/' + file_list_jpg[index], cv2.IMREAD_COLOR)
    frame_show = np.copy(frame)
    frame_width, frame_height = frame.shape[1], frame.shape[0]

    # 새로운 위치에 있는 사진에 대해 박스를 새로 설정하고 그린다
    file_read(file_list_jpg[index])
    cv2.rectangle(frame_show, (s_x, s_y), (e_x, e_y), (0, 255, 0), 1)


# 여기서부터 메인함수 -------------------------------------
print("###################################\n")
print("Usage : a키를 누르면 뒤로가기, s키를 누르면 앞으로 가기\n")
print("박스를 그리고 이동하면 자동으로 저장됩니다. (단, 트랙바로 이동시에는 저장되지 않음)\n")
print("폴더 경로는 사진 파일이 저장되어 있는 디렉터리의 절대경로를 입력해주세요.\n")
print("###################################\n")

class_name = input("클래스 이름 : ")
path_dir = input("폴더 경로 : ")

file_list = os.listdir(path_dir)
file_list_jpg = [file for file in file_list if file.endswith(".jpg")]

# 파일 이름 순으로 정렬
file_list_jpg.sort()

file_len = len(file_list_jpg)
index = 0
initial_frame = True
mouse_pressed = False
trackbar_changed = False
s_x = s_y = e_x = e_y = 0

if file_len != 0:
    cv2.namedWindow('labeling')
    cv2.setMouseCallback('labeling', mouse_callback)
    cv2.createTrackbar('number', 'labeling', 0, file_len - 1, lambda v: trackbar_callback(v))

# index에 해당하는 프레임 읽기
frame = cv2.imread(path_dir + '/' + file_list_jpg[index], cv2.IMREAD_COLOR)
frame_show = np.copy(frame)
frame_width, frame_height = frame.shape[1], frame.shape[0]

# 처음 사진에 대해 박스 위치를 읽어서 그린다
file_read(file_list_jpg[index])
cv2.rectangle(frame_show, (s_x, s_y), (e_x, e_y), (0, 255, 0), 1)


while True:
    cv2.imshow('labeling', frame_show)
    k = cv2.waitKey(1)

    # a는 이전 이미지로, s는 다음 이미지로 이동
    if k == ord('a'):
        # 맨 처음 이미지이면 뒤로갈수 없다 ㅜㅜ
        if index == 0:
            continue
        # 트랙바 움직이기 전 박스 정보 저장
        box_write(s_x, s_y, e_x, e_y)
        file_write(file_list_jpg[index])
        # 트랙바 및 프레임 이동
        index -= 1
        cv2.setTrackbarPos('number', 'labeling', index)

    elif k == ord('s'):
        # 맨 마지막 이미지면 앞으로 갈 수 없다 ㅜㅜ
        if index == file_len - 1:
            continue
        # 트랙바 움직이기 전 박스 정보 저장
        box_write(s_x, s_y, e_x, e_y)
        file_write(file_list_jpg[index])
        # 트랙바 및 프레임 이동
        index += 1
        cv2.setTrackbarPos('number', 'labeling', index)

    # ESC 키를 누르면 종료
    elif k == 27:
        file_write(file_list_jpg[index])
        break


cv2.destroyAllWindows()


