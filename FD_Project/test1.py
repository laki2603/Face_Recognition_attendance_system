import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import Encodings




# def findencodings(images):
#     encodelist = []
#     for img in images:
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         encode = face_recognition.face_encodings(img)[0]
#         # print(encode)
#         encodelist.append(encode)
#     return encodelist


def markAttendance(name):
    with open(R'E:\LCS\FD_Project\Attendance.csv', 'r+') as f:
        mydatalist = f.readlines()
        namelist = []
        for line in mydatalist:
            entry = line.split(",")
            namelist.append(entry[0])
        if name not in namelist:
            now = datetime.now()
            dtstring = now.strftime("%H:%M:%S")
            dt = now.date()
            f.writelines(f'\n{name},{dt},{dtstring}')
if __name__ == "__main__":
    path = R"E:\LCS\FD_Project\images"
    images = []
    classNames = []
    mylist = os.listdir(path)
    print(mylist)

    for cl in mylist:
        curimg = cv2.imread(f'{path}/{cl}')
        images.append(curimg)
        classNames.append(os.path.splitext(cl)[0])
    print(classNames)
    print(images)
    encodelistknown = Encodings.findencodings(images)
    print(images[0])
    print('Encoding Complete')

    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facescurframe = face_recognition.face_locations(imgS)
        encodescurframe = face_recognition.face_encodings(imgS, facescurframe)
        print(facescurframe)
        if len(facescurframe)>1:
            print("Error")

        for encodeface, faceloc in zip(encodescurframe, facescurframe):
            matches = face_recognition.compare_faces(encodelistknown, encodeface)
            facedis = face_recognition.face_distance(encodelistknown, encodeface)

            matchindex = np.argmin(facedis)
            minm = np.min(facedis)
            print(minm)

            if matches[matchindex] and minm < 0.43:
                name = classNames[matchindex].upper()

                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                markAttendance(name)
            else:
                print("Member does not registered")

        cv2.imshow('webcam', img)
        k = cv2.waitKey(1)
        if k == 27:  # press 'ESC' to quit
            break
    cap.release()
    cv2.destroyAllWindows()

