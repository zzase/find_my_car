from time import sleep

import cv2
from darkflow.net.build import TFNet

import threading
import os, io

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path of google_jason"

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

options = {
    'model': 'C:\\HC\\darkflow\\cfg\\parking-yolo-obj.cfg',
    'load': 'C:\\HC\\darkflow\\bin\\parking20_04_03_8000.weights',
    'threshold': 0.6
}  # weights파일, cfg파일 설정
# -----------환경설정부분----------




# ------------변수선언부분-----------
# height, width, number of channels in image
# height = img.shape[0]
# # width = img.shape[1]
# # channels = img.shape[2]
# -----------참고부분 -----

#OCR돌리는 함수
def detect_text(num):
    fw = open('C:\\HC\\afterCrop\\ocr'+str(num)+'.text', 'w', -1, "utf-8")
    vstr = ""

    path = os.path.join(
        os.path.dirname(__file__),
        'C:\\HC\\afterCrop\\cropYolo' + str(num) + '.jpg')

    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:

        print('\n"{}"'.format(text.description))
        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))
        vstr = vstr + str(text.description)+"\n"
    try:
        fw.writelines(vstr.split("\n")[0]+"\n"+vstr.split("\n")[1])
        fw.close()
    except IndexError:
        fw.write("parknum is not found")
        fw.close()


#최신 동영상 파일 찾는 함수
def find_recent_video():
    files_path = "C:\\HC\\videoList\\"
    file_list = []
    for f_name in os.listdir(f"{files_path}"):
        written_time = os.path.getctime(f"{files_path}{f_name}")
        file_list.append((f_name, written_time))
    # 생성시간 역순으로 정렬
    sorted_file_list = sorted(file_list, key=lambda x: x[1], reverse=True)
    # 가장 앞에있는 파일을 넣어줌
    recent_file = sorted_file_list[1]
    recent_file_name = recent_file[0]
    check_video_path = files_path + str(recent_file_name)

    return check_video_path

def cropTextImg(index):
    # read 는 cv2함수 open pil함수
    img = cv2.imread("C:\\HC\\imgList\\" + "test_" + str(index) + ".jpg", cv2.IMREAD_UNCHANGED)
    # img = cv2.imread("C:\\HC\\imgList\\" + "test_" + str(index) + ".jpg", cv2.IMREAD_GRAYSCALE)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = tfnet.return_predict(img)
    if result == list() :
        print("텍스트를 찾지 못햇습니다.")
        return 0
    else :
        cropImg = img.copy()

        imgHeight = img.shape[0]
        imgWidth = img.shape[1]
        flag = True

        topleftX = result[0]['topleft']['x']
        topleftY = result[0]['topleft']['y']
        bottomRightX = result[0]['bottomright']['x']
        bottomRightY = result[0]['bottomright']['y']

        if (topleftX - 50) > 0 :
            topleftX = topleftX -50

        if (bottomRightX + 50) < imgWidth :
            bottomRightX = bottomRightX + 50

        if (topleftY - 50) > 0 :
            topleftY = topleftY -50

        if (bottomRightY + 50) < imgHeight :
            bottomRightY = bottomRightY +50

        cropImg = img[int(topleftY):int(bottomRightY), int(topleftX):int(bottomRightX)]
        # cropImg = img[0:100, 300:400]

        # print("위 topleftX 값 : " + str(topleftX) + "\n")
        # print("위 topleftY 값 : " + str(topleftY) + "\n")
        # print("아래 bottomRightX 값 : " + str(bottomRightX) + "\n")
        # print("아래 bottomRightY 값 : " + str(bottomRightY) + "\n")
        print("C:\\HC\\afterCrop\\cropYolo" + str(index) + ".jpg를 성공적으로 저장 했습니다." )
        cv2.imwrite("C:\\HC\\afterCrop\\cropYolo" + str(index) + ".jpg", cropImg)

    cv2.destroyAllWindows()


def reversePlay():
    global capture
    global find_parknum_flag
    listNumber = 1
    captureCount = 1

    # check for camera openning
    if capture.isOpened() is False:
        print("Error opening video")

    # Get the total number of frames
    frame_idx = capture.get(cv2.CAP_PROP_FRAME_COUNT) - 1
    print("Starting Frame: '{}'".format(frame_idx))

    # Read until video is finished:
    while capture.isOpened() and frame_idx >= 0:

        # Set the current frame position to start:
        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

        # 비디오로부터 프레임을 읽음
        ret, frame = capture.read()

        if ret is True:
            # 동영상 시작될때 이름?
            cv2.imshow('Frame in Reverse', frame)

            # 내가 추가 할 부분
            results = tfnet.return_predict(frame)
            for result in results:
                if result['label'] == 'parknum':
                    cv2.imwrite("C:\\HC\\imgList\\" + "test_" + str(listNumber) + ".jpg", frame)
                    captureCount += 1
                    listNumber += 1
                    print("찰칵스")
                    find_parknum_flag = True

            # 사진을 3개저장하면종료.
            if captureCount > 3:
                return captureCount;
                break;

            # 프레임을 뒤로 감소시키며 거꾸로 재생
            print("Next index: '{}'".format(frame_idx))
            frame_idx = frame_idx - 5

            if count > 5:
                capture.release()
                return 0


            # Q를 누르면 꺼짐
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
        # Break the while loop
        else:
            break

def Out_In_decision():
    global count
    timer = threading.Timer(1, Out_In_decision)
    timer.start()

    count += 1
    print("흐른 시간초 : " + str(count))
    if find_parknum_flag==True:
        timer.cancel()

    if count > 5:
        timer.cancel()
        sleep(1)
        reversePlay_OnlyCapture()


def reversePlay_OnlyCapture():
    listNumber = 1
    captureCount = 1
    capture = cv2.VideoCapture('C:\\HC\\videoList\\test.mp4')

    # check for camera openning
    if capture.isOpened() is False:
        print("Error opening video")

    # Get the total number of frames
    frame_idx = capture.get(cv2.CAP_PROP_FRAME_COUNT) - 1
    print("Starting Frame: '{}'".format(frame_idx))

    # Read until video is finished:
    while capture.isOpened() and frame_idx >= 0:

        # Set the current frame position to start:
        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

        # 비디오로부터 프레임을 읽음
        ret, frame = capture.read()

        if ret is True:

            # cv2.imshow('Frame in Reverse', frame)

            cv2.imwrite("C:\\HC\\onlyCaptureList\\" + "onlyCapture_" + str(listNumber) + ".jpg", frame)
            captureCount += 1
            listNumber += 1

            # 사진을 3개저장하면종료.
            if captureCount > 3:
                break;

            # 프레임을 뒤로 감소시키며 거꾸로 재생
            print("Next index: '{}'".format(frame_idx))
            frame_idx = frame_idx - 50

            # Q를 누르면 꺼짐
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
        # Break the while loop
        else:
            break


# capture = cv2.VideoCapture(find_recent_video())


capture = cv2.VideoCapture(find_recent_video())
tfnet = TFNet(options)

find_parknum_flag = False
saveCount = 0
count = 0
def main():
    Out_In_decision()
    # 동영상을 거꾸로 돌려서 기둥 (ParkNum 캡쳐)
    saveCount = reversePlay()
    # 캡쳐된 이미지를 OCR돌리기위해 자름.
    for i in range(1, saveCount):
        try:
            cropTextImg(i)
            detect_text(i)
        except IndexError:
            i += 1

    # Release the VideoCapture object:
    capture.release()
    cv2.destroyAllWindows()

main()

