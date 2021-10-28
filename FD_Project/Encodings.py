import face_recognition
import os
import cv2

def findencodings(images):

    encodelist = []
    for img in images:

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        encode = face_recognition.face_encodings(img)[0]
        # print(encode)
        encodelist.append(encode)
    return encodelist

images = []
path = R"E:\LCS\FD_Project\images"
mylist = os.listdir(path)
for cl in mylist:
    curimg = cv2.imread(f'{path}/{cl}')
    images.append(curimg)
#print(images)
elist = findencodings(images)
print(elist)