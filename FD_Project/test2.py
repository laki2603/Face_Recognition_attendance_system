import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2
import numpy as np
import face_recognition
from datetime import datetime
import os
import pandas as pd

#class for mainwindow
class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.VBL = QVBoxLayout() #adding a layout

        self.FeedLabel = QLabel() # creating a label
        self.VBL.addWidget(self.FeedLabel)  # adding label to our layout

        self.CancelBTN = QPushButton("Close") # creating a pushbutton
        self.CancelBTN.clicked.connect(self.CancelFeed) #creating a signel when push button is clicked
        self.VBL.addWidget(self.CancelBTN) # adding the push button to our layout

        self.Worker1 = Worker1() # creating instance of our worker1 class (Inherited from QThread) in mainwindow class because we have to use it in mainwindow

        self.Worker1.start() # Starting the worker1 class since it is a thread
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot) # recieving the signal (i.e a image) from run function of worker1 and passing it to the imageslot function as parameter
        self.setLayout(self.VBL)

    def ImageUpdateSlot(self, Image): #seting the recieved image in the label as QPixmap
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def CancelFeed(self): #use to stop the feed when pushButton is pressed
        self.Worker1.stop() # stops the Worker1 since it is a thread
        self.Worker1.Capture.release() # releasing the camera
        cv2.destroyAllWindows() # to close all windows
#
class Worker1(QThread): # a worker1 class which is inherited from QThread
    ImageUpdate = pyqtSignal(QImage)

    def markAttendance(self,name): # a function to mark the Attendance
        # print("yes")
        with open(R'E:\LCS\FD_Project\Attendance.csv', 'r+') as f: # to open the file and set the mode as read and write
            mydatalist = f.readlines() # read the lines from the files and store it in mydatalist
            namelist = [] # a list to store the names in the Attendance.csv file

            for line in mydatalist: # Loop used to iterate through each and every line and store the name in namelist
                entry = line.split(",")
                namelist.append(entry[0])

            if name not in namelist: # To check whether the name is not in the list if true add it in the file
                now = datetime.now() # to get date and time
                stime = now.strftime("%H:%M:%S") #strip only time and store it in the format hours:minutes:seconds
                sdate = now.date() # get the date
                f.writelines(f'\n{name},{sdate},{stime}') #write the date and time in the attendance.csv file

    def run(self): # This function runs at the instance of the class Worker1 is created
        self.ThreadActive = True # A boolean to check whether the thread is true and it is set as True initialy
        Capture = cv2.VideoCapture(0) # To access the webcam
        while self.ThreadActive: # Runs till thread is active
            ret, img = Capture.read() # returns a true/false and frame which is stored in ret and img respectively

            if ret: # till ret is true

                imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25) # resize the image to 1/4th of its original value so that operation performed on it will be faster
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB) # openCv reads the image in BGR it has to be coverted to RGB because all the functions in face recognition module uses RGB image

                facescurframe = face_recognition.face_locations(imgS) # gives list of coordinates of the face location
                encodescurframe = face_recognition.face_encodings(imgS, facescurframe) #encode the face in numbers

                for encodeface, faceloc in zip(encodescurframe, facescurframe): #loop for different face encodings and face loacations
                    matches = face_recognition.compare_faces(encodelistknown, encodeface)  # matches the face in the video with the faces in the images folder
                    facedis = face_recognition.face_distance(encodelistknown, encodeface) # gives the distance of match (i.e is degree of match) lesser the distance greater the match

                    matchindex = np.argmin(facedis)
                    minm = np.min(facedis)
                    print(minm)

                    if matches[matchindex] and minm < 0.43:
                        name = Names[matchindex].upper()
                        print(name)
                        y1, x2, y2, x1 = faceloc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv2.rectangle(imgS, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        self.markAttendance(name)

                    else:
                        print("Member does not registered")

                FlippedImage = cv2.flip(imgS, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
    def stop(self):
        self.ThreadActive = False
        self.quit()


def findencodings(images):
    encodelist = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        # print(encode)
        encodelist.append(encode)
    return encodelist
def storeData():
    with open(r"E:\LCS\FD_Project\data_file.csv",'r') as f:
        datas = f.readlines()
        for data in datas:
            entry = data.split(',')
            Names.append(entry[0])
            Depts.append(entry[1])
            DOB.append(entry[2])


if __name__ == "__main__":
    path = R"E:\LCS\FD_Project\images"
    images = []
    classNames = []

    Names= []
    Depts = []
    DOB = []


    mylist = os.listdir(path)
    storeData()
    print(mylist)



    for cl in mylist:
        curimg = cv2.imread(f'{path}/{cl}')
        images.append(curimg)
        #classNames.append(os.path.splitext(cl)[0])
    print(Names)
    global encodelistknown
    encodelistknown = findencodings(images)

    print('Encoding Complete')

    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())
