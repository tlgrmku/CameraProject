'''Video recording after motion capture and send a message to telegram. Checks CPU temperature Raspberry Pi.'''
import cv2
import time
from pyrogram import Client
from pyrogram import enums
import os

admin = 000000000 # Telegram user id
videodir = '/path/' # directory videofiles
nameclient = 'bot' # name Pyrogram client
numbercam = 0 # Number camera


app = Client(nameclient)
cap = cv2.VideoCapture(numbercam)
# cap = cv2.VideoCapture(numbercam, cv2.CAP_DSHOW) - For Windows

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
cat_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalcatface.xml')

detection = False
detection_time = None
timer_started = False
second_after_rec = 15 # time after detect

frame_size = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')


async def video_tg(name):
    temp = os.popen('vcgencmd measure_temp').readline()
    caption_text = name + ' ' + temp
    await app.start()
    await app.send_chat_action(admin, enums.ChatAction.UPLOAD_VIDEO)
    await app.send_video(admin, f'{videodir}{name}.mp4', caption=caption_text, has_spoiler=True)
    await app.stop()


while True:
    try:
        _, img = cap.read()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face = face_cascade.detectMultiScale(gray, 1.3, 5)
        body = body_cascade.detectMultiScale(gray, 1.3, 5)
        cat = cat_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in face:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        for (x, y, w, h) in cat:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        for (x, y, w, h) in body:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        if len(face) + len(cat) + len(body) > 0:
            if detection:
                timer_started = False
            else:
                detection = True
                now_time = time.strftime('%H%M%S_%d%m%y')
                out = cv2.VideoWriter(f'{videodir}{now_time}.mp4', fourcc, 10, frame_size)
                print('Record.')
        elif detection:
            if timer_started:
                if time.time() - detection_time >= second_after_rec:
                    detection = False
                    timer_started = False
                    out.release()
                    print('Record stop.')
                    app.run(video_tg(now_time))
            else:
                timer_started = True
                detection_time = time.time()

        if detection: #4
            out.write(img)

    except KeyboardInterrupt:
        print('Stop script.')
        break

cap.release()
