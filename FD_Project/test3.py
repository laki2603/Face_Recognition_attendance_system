import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import *
import cv2
import numpy as np
import face_recognition
from datetime import datetime
import os
import threading

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        loadUi("Test3.ui", self)
        self.count = str(0)
        self.CancelButton.clicked.connect(self.CancelFeed)

        self.Worker1 = Worker1()
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.ImageName.connect(self.ImageNameDisplay)
        self.Worker1.ImageDept.connect(self.ImageDeptDisplay)
        #self.Worker1.Error.connect(self.showMsgDisplay)


        self.t1 = threading.Thread(target=self.startThread)
        self.t1.start()

        self.show()

    def startThread(self):
        while True:
            self.ShowPersonCount()
            self.ShowDate()
    def ShowPersonCount(self):
        # print(count_)
        # print("PersonCount")
        with open(r'E:\LCS\FD_Project\Attendance.csv','r') as f:
            datas = f.readlines()

            for data in datas:
                values = data.split(',')

                if values[0]!='\n':
                    self.count = values[3]
        self.lb_CountDisplay.setText(self.count)

    def ShowDate(self):
        DateTime = datetime.now()
        date = DateTime.date()
        time_ = DateTime.strftime("%H:%M:%S")
        self.lb_DateDisplay.setText(str(date))
        self.lb_TimeDisplay.setText(str(time_))

    def showMsgDisplay(self,error):
        self.Worker1.stop()
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(error)
        msg.buttonClicked.connect(self.msgOkButtonClicked)
        x = msg.exec_()

    def msgOkButtonClicked(self):
        self.Worker1.start()



    def ImageDeptDisplay(self, department):
        self.lb_DeptDisplay.setText(department)

    def ImageNameDisplay(self, names_):
        self.lb_NameDisplay.setText(names_)

    def ImageUpdateSlot(self, Image):

        self.VideoFrame.setPixmap(QPixmap.fromImage(Image))

    def CancelFeed(self):                      #use to stop the feed when pushButton is pressed
        self.Worker1.stop()                    # stops the Worker1 since it is a thread
        self.Worker1.Capture.release()         # releasing the camera
        self.t1.terminate()
        cv2.destroyAllWindows()                # to close all windows


class Worker1(QThread):                 # a worker1 class which is inherited from QThread
    def __init__(self):
        super(Worker1,self).__init__()
        self.k = 0
    ImageUpdate = pyqtSignal(QImage)
    ImageName = pyqtSignal(str)
    ImageDept = pyqtSignal(str)
    Error = pyqtSignal(str)

    def markAttendance(self,name):               # a function to mark the Attendance
        with open(R'E:\LCS\FD_Project\Attendance.csv', 'r+') as f:          # to open the file and set the mode as read and write
            mydatalist = f.readlines()      # read the lines from the files and store it in mydatalist
            namelist = []          # a list to store the names in the Attendance.csv file

            for line in mydatalist:        # Loop used to iterate through each and every line and store the name in namelist
                entry = line.split(",")
                namelist.append(entry[0])
                if entry[0] != '\n':
                    count_ = entry[3]

            if name not in namelist:                 # To check whether the name is not in the list if true add it in the file
                count_ = int(count_)
                count_ += 1
                now = datetime.now()                 # to get date and time
                stime = now.strftime("%H:%M:%S")     #strip only time and store it in the format hours:minutes:seconds
                sdate = now.date() # get the date
                f.writelines(f'\n{name},{sdate},{stime},{count_}')      #write the date and time in the attendance.csv file

    def run(self):                          # This function runs at the instance of the class Worker1 is created

        self.ThreadActive = True            # A boolean to check whether the thread is true and it is set as True initialy
        Capture = cv2.VideoCapture(0)
        while self.ThreadActive:
            ret, img = Capture.read()
            if ret:

                imgSs = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                facescurframe = face_recognition.face_locations(imgS)
                encodescurframe = face_recognition.face_encodings(imgS, facescurframe)

                for encodeface, faceloc in zip(encodescurframe, facescurframe):
                    matches = face_recognition.compare_faces(encodelistknown, encodeface)
                    facedis = face_recognition.face_distance(encodelistknown, encodeface)

                    matchindex = np.argmin(facedis)
                    minm = np.min(facedis)
                    print(minm)

                    if matches[matchindex] and minm < 0.43 and not len(facescurframe)>1:
                        name = Names[matchindex+1].upper()
                        department = Depts[matchindex+1].upper()
                        print(name)
                        print(department)
                        self.ImageName.emit(name)
                        self.ImageDept.emit(department)

                        y1, x2, y2, x1 = faceloc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv2.rectangle(imgS, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        self.markAttendance(name)

                    elif len(facescurframe)>1:
                        #self.Error.emit("Can detect only one face at a time")
                        pass

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
    Names = []
    Depts = []
    DOB = []
    mylist = os.listdir(path)
    print(mylist)
    storeData()
    print(Names)
    for cl in mylist:
        curimg = cv2.imread(f'{path}/{cl}')
        images.append(curimg)
        #classNames.append(os.path.splitext(cl)[0])
    #print(classNames)

    # for name in classNames:
    #     d = name.split('_')
    #     dept.append(d[1])
    #     names.append(d[0])
    # print(dept)
    # print(names)

    global encodelistknown
    encodelistknown = findencodings(images)

    print('Encoding Complete')
    app = QApplication(sys.argv)
    ui = Ui()
    sys.exit(app.exec_())

