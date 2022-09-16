import face_recognition as fr
import os
import glob
import cv2
import face_recognition
import mysql.connector
import numpy as np
from time import sleep
from datetime import datetime

attendance = "A";
sid="";
connection = mysql.connector.connect(host='localhost',
                                         database='attendance_project',
                                         user='root',
                                         password='')
cursor = connection.cursor();


def insertData ():
    attendance = "A";
    ssql = '''INSERT INTO attendance (sid, name) SELECT sid, Name FROM student''';
    cursor.execute(ssql)
    connection.commit()

insertData()

def get_encoded_faces():
    """
    looks through the faces folder and encodes all
    the faces

    :return: dict of (name, image encoded)
    """

    encoded = {}

    for dirpath, dnames, fnames in os.walk("E:/School work/Automatic_Ai_Attendance_System/server/images"):
        for f in fnames:
            if f.endswith(".jpg") or f.endswith(".png") or f.endswith(".PNG"):
                face = fr.load_image_file("E:/School work/Automatic_Ai_Attendance_System/server/images/" + f)
                encoding = fr.face_encodings(face)[0]
                encoded[f.split(".")[0]] = encoding

    return encoded


def unknown_image_encoded(img):
    """
    encode a face given the file name
    """
    face = fr.load_image_file("E:/School work/Automatic_Ai_Attendance_System/server/images/" + img)
    encoding = fr.face_encodings(face)[0]

    return encoding


def classify_face(im):
    """
    will find all of the faces in a given image and label
    them if it knows what they are

    :param im: str of file path
    :return: list of face names
    """
    faces = get_encoded_faces()
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())

    img = cv2.imread(im, 1)
    # img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    # img = img[:,:,::-1]

    face_locations = face_recognition.face_locations(img)
    unknown_face_encodings = face_recognition.face_encodings(img, face_locations)
    if len(unknown_face_encodings) > 0:
        unknown_face_encoding = unknown_face_encodings[0]

    face_names = []
    nm = "a";
    for face_encoding in unknown_face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(faces_encoded, face_encoding)
        name = "Unknown"

        # use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        face_names.append(name)


        s = "SELECT sid FROM student WHERE Name = %s"
        sid = (name,)
        cursor.execute(s, sid)

        myresult = cursor.fetchall()

        print(name)
        fitem ='None'
        for fitem in myresult:
            print('item',fitem)

        def markAttendance(sid, name, attendance, date, time):

            # sql = '''Update attendance  SET (sid, name, attendance, date, time) VALUES (%s, %s, %s, %s, %s) WHERE name = name '''
            # val = (sid, name, attendance, date, time)
            # s = cursor.execute(sql, val)
            s= cursor.execute("UPDATE attendance SET sid=%s, name=%s, attendance= %s, date= %s, time=%s WHERE name=%s", (sid, name, attendance, date, time, name))

            print('s', s)
            connection.commit()




        #mycursor.execute(sql, val)
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Draw a box around the face
            cv2.rectangle(img, (left - 20, top - 20), (right + 20, bottom + 20), (0, 255, 0), 2)

            # Draw a label with a name below the face
            cv2.rectangle(img, (left - 20, bottom - 15), (right + 20, bottom + 20), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(img, name, (left - 20, bottom + 15), font, 1.0, (255, 255, 255), 2)

        curTime = datetime.now().time()
        curDate = datetime.now().date()

        if name!=nm and name!= "Unknown":
            attendance = "P"
            markAttendance(fitem[0], name, attendance, str(curDate), str(curTime))
            nm = name


    while True:

     cv2.imshow('Video', img)
     if cv2.waitKey(1) & 0xFF == ord('q'):
      return face_names

#print(classify_face("o.jpg"))
ts = 0
found = None
for file_name in glob.glob('E:/School work/Automatic_Ai_Attendance_System/server/class_images/*'):
    fts = os.path.getmtime(file_name)
    if fts > ts:
        ts = fts
        found = file_name

print('found', found)
i = cv2.imread(found)
print(classify_face(found))


#p = cv2.imread('class/3.jpg')
# cv2.imshow('img', i)
#print(classify_face("i"))
#cv2.imshow("i")
cv2.waitKey(0)


