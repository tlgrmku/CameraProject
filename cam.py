'''By sending a message with the camera number to the telegram bot and get a photo or video in response.
Example 1: f0
Example 2: v0
f - foto, v - video, 0 - number camera.
'''
import cv2
import time
from pyrogram import Client, filters
from pyrogram import enums


admin = 000000000 # Telegram user id
cam = ['0', '1', '2', '3'] # Numbers camers
second_rec = 15 # Time record video
videodir = '/path/video/' # directory video
fotodir = '/path/foto/' # directory foto
nameclient = 'bot' # name Pyrogram client

app = Client(nameclient)


async def getimg(msg):
    cap = cv2.VideoCapture(int(msg.text[1]))
    st, img = cap.read()
    now_time = time.strftime('%H%M%S_%d%m%Y')
    cv2.imwrite(f'{fotodir}{now_time}.jpg', img)
    cap.release()
    await app.send_photo(msg.chat.id, f'{fotodir}{now_time}.jpg')
    await app.delete_messages(msg.chat.id, msg.id)


async def getvideo(msg):
    rec = False
    cap = cv2.VideoCapture(int(msg.text[1]))
    frame_size = (int(cap.get(3)), int(cap.get(4)))
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    start_time = time.time()
    while True:
        try:
            _, img = cap.read()
            if rec == False:
                rec = True
                now_time = time.strftime('%H%M%S_%d%m%Y')
                out = cv2.VideoWriter(f'{videodir}{now_time}.mp4', fourcc, 20, frame_size)
            elif time.time() - start_time >= second_rec:
                rec = False
                out.release()
                break
            if rec:
                out.write(img)
        except:
            print('Error.')
            break
    await app.send_chat_action(msg.chat.id, enums.ChatAction.UPLOAD_VIDEO)
    await app.delete_messages(msg.chat.id, msg.id)
    await app.send_video(msg.chat.id, f'{videodir}{now_time}.mp4', caption=now_time, has_spoiler=True)
    cap.release()

    
@app.on_message(filters.user(admin))
async def botmsg(client, msg):
    print(msg.from_user.id, msg.from_user.username, msg.text)
    if msg.text[0].lower() == 'f' and msg.text[1] in cam:
        try:
            await getimg(msg)
        except:
            await app.send_message(msg.chat.id, f'Camera {msg.text} not work.')
    elif msg.text[0].lower() == 'v' and msg.text[1] in cam:
        try:
            await getvideo(msg)
        except:
            await app.send_message(msg.chat.id, f'Camera {msg.text} not work.')


app.run()

