# utility file for emotion recognition from realtime webcam feed
import cv2
import sys
from keras.models import load_model
import time
import numpy as np
import datetime
import csv
from decimal import Decimal
from model_utils import define_model, model_weights
import os


# load and resize an image
def resize_img(image_path):
    img = cv2.imread(image_path, 1)
    img = cv2.resize(img, (48, 48))
    return True


# runs the realtime emotion detection
def realtime_emotions(incoming_variable):
    # load keras model
    model = define_model()
    model = model_weights(model)
    print('Model loaded')

    # save location for image
    save_loc = 'save_loc/1.jpg'
    # numpy matrix for strong prediction
    result = np.array((1, 7))
    # for knowing whether prediction has started or not
    once = False
    # load haar cascade for face
    faceCascade = cv2.CascadeClassifier(r'haarcascades/haarcascade_frontalface_default.xml')
    # list of given emotions
    emotions = ['Angry', 'Disgusted', 'Fearful', 'Happy', 'Sad', 'Surprised', 'Neutral']
    # list of column headers required in csv file
    column_headers = ['DATETIME', 'Angry', 'Disgusted', 'Fearful', 'Happy', 'Sad', 'Surprised', 'Neutral']
    # check the number of files in 'records/' folder
    path = '../../Reports/' + incoming_variable
    filename = path + '/raw/' + incoming_variable + '_Facial'

    # store the emoji corresponding to different emotions
    emoji_faces = []
    for index, emotion in enumerate(emotions):
        emoji_faces.append(cv2.imread('emojis/' + emotion + '.png', -1))

    # set video capture device , webcam in this case
    video_capture = cv2.VideoCapture(0)
    video_capture.set(3, 640)  # WIDTH
    video_capture.set(4, 480)  # HEIGHT

    # save current time
    prev_time = time.time()

    header_added = False

    # start webcam feed
    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        # mirror the frame
        frame = cv2.flip(frame, 1, 0)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # find face in the frame
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            # required region for the face
            roi_color = frame[y - 90:y + h + 70, x - 50:x + w + 50]

            # save the detected face
            cv2.imwrite(save_loc, roi_color)
            # draw a rectangle bounding the face
            cv2.rectangle(frame, (x - 10, y - 70),
                          (x + w + 20, y + h + 40), (15, 175, 61), 4)

            # keeps track of waiting time for emotion recognition
            curr_time = time.time()
            # do prediction only when the required elapsed time has passed
            if curr_time - prev_time >= 1:
                # read the saved image
                img = cv2.imread(save_loc, 0)

                if img is not None:
                    # indicates that prediction has been done atleast once
                    once = True
                    # resize image for the model
                    img = cv2.resize(img, (48, 48))
                    img = np.reshape(img, (1, 48, 48, 1))
                    # do prediction
                    result = model.predict(img)

                """ For Per Second based Data """
                list_storage = []
                total_sum = np.sum(result[0])
                print("Number of Faces in Frame:\t" + str(len(faces)))
                # print(emotions[np.argmax(result[0])])
                for index, emotion in enumerate(emotions):
                    text = str(round(Decimal(result[0][index] / total_sum * 100), 2)) + "%"
                    # for drawing progress bar
                    cv2.rectangle(frame, (100, index * 20 + 10),
                                  (100 + int(result[0][index] * 100), (index + 1) * 20 + 4),
                                  (255, 0, 0), -1)
                    # for putting emotion labels
                    cv2.putText(frame, emotion, (10, index * 20 + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (7, 109, 16), 2)
                    # for putting percentage confidence
                    cv2.putText(frame, text, (105 + int(result[0][index] * 100), index * 20 + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

                    # print(str(index) + "\t" + str(datetime.datetime.now()) + "\t" + emotions[index] + "\t" + text)
                    list_storage.append(text[:-1])
                now = datetime.datetime.now()
                now = now.strftime('%Y-%m-%d %H:%M:%S')
                payload = {
                    'DATETIME': str(now),
                    'Angry': list_storage[0],
                    'Disgusted': list_storage[1],
                    'Fearful': list_storage[2],
                    'Happy': list_storage[3],
                    'Sad': list_storage[4],
                    'Surprised': list_storage[5],
                    'Neutral': list_storage[6]
                }
                print(payload)
                with open(filename + '.csv', 'a', newline='') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=column_headers)
                    if not header_added:
                        # add header
                        print("writing header in csv....")
                        writer.writeheader()
                        header_added = True
                    else:
                        print("writing row in csv....")
                        print(payload)
                        writer.writerow(payload)
                    csv_file.close()

                # save the time when the last face recognition task was done
                prev_time = time.time()

            if once:
                """ For Milliseconds based data """
                # list_storage = []
                # total_sum = np.sum(result[0])
                # select the emoji face with highest confidence
                emoji_face = emoji_faces[np.argmax(result[0])]
                for index, emotion in enumerate(emotions):
                    text = str(round(Decimal(result[0][index] / total_sum * 100), 2)) + "%"
                    # for drawing progress bar
                    cv2.rectangle(frame, (100, index * 20 + 10),
                                  (100 + int(result[0][index] * 100), (index + 1) * 20 + 4),
                                  (255, 0, 0), -1)
                    # for putting emotion labels
                    cv2.putText(frame, emotion, (10, index * 20 + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (7, 109, 16), 2)
                    # for putting percentage confidence
                    cv2.putText(frame, text, (105 + int(result[0][index] * 100), index * 20 + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

                    # print(str(index) + "\t" + str(datetime.datetime.now()) + "\t" + emotions[index] + "\t" + text)
                    # list_storage.append(text[:-1])
                # payload = {
                #     'Timestamp': str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                #     'Angry': list_storage[0],
                #     'Disgusted': list_storage[1],
                #     'Fearful': list_storage[2],
                #     'Happy': list_storage[3],
                #     'Sad': list_storage[4],
                #     'Surprised': list_storage[5],
                #     'Neutral': list_storage[6]
                # }
                # print("Number of Faces in Frame:\t" + str(len(faces)))
                # with open(filename + '.csv', 'a', newline='') as csv_file:
                #     writer = csv.DictWriter(csv_file, fieldnames=column_headers)
                #     if not header_added:
                #         # add header
                #         print("writing header in csv....")
                #         writer.writeheader()
                #         header_added = True
                #     else:
                #         print("writing row in csv....")
                #         print(payload)
                #         writer.writerow(payload)
                #     csv_file.close()

                # overlay emoji on the frame for all the channels
                for c in range(0, 3):
                    # for doing overlay we need to assign weights to both foreground and background
                    foreground = emoji_face[:, :, c] * (emoji_face[:, :, 3] / 255.0)
                    background = frame[350:470, 10:130, c] * (1.0 - emoji_face[:, :, 3] / 255.0)
                    frame[350:470, 10:130, c] = foreground + background
            break

        # Display the resulting frame
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()