import cv2
import time
import datetime
import os
import smtplib as s
from twilio.rest import Client
import keys # Loads keys.py
# ---------------------------------------------------------------------------------------------
# Function to send mail to the admin------------------------------------------------
# ---------------------------------------------------------------------------------------------


def sending_mail():
    ob = s.SMTP("smtp.gmail.com", 587)
    ob.starttls()
    ob.login(keys.sender_email, keys.email_password)
    subject = "Critical Security Alert !"
    body = """Hello! Arihantt nandi. This is to inform you that your motion
    activated camera
    detects a movement and it is recorded in the system. Please check out the
    system
    to watch the recording. Thank You..."""
    message = "Subject: {}\n\n{}".format(subject, body)
    ob.sendmail(keys.sender_email, keys.receiver_email, message)
    ob.quit()


def sending_sms():

    client = Client(keys.account_sid, keys.auth_token)
    message = client.messages.create(
        body="Security Alert! Your smart camera detected motion in your unauthorized area.",
        from_=keys.twilio_number,
        to=keys.target_number
    )


# ---------------------------------------------------------------------------------------------
# Capturing video frames and motion detection (Main program) ------------
# ---------------------------------------------------------------------------------------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
body_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_fullbody.xml")
detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5
frame_size = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
font2 = cv2.FONT_HERSHEY_DUPLEX
while True:
    _, frame = cap.read()

    y = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, "TIME: " + str(y), (50, 50), font2, 1, (0, 255, 0), 2)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    bodies = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) + len(bodies) > 0:
        if detection:
            timer_started = False
        else:
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            out = cv2.VideoWriter(
                f"{current_time}.mp4", fourcc, 20, frame_size)
            os.system("ok.mp3")
            sending_mail()
            sending_sms()
            print("Started Recording!")
    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                out.release()
                print('Stop Recording!')
        else:
            timer_started = True
            detection_stopped_time = time.time()
    if detection:
        out.write(frame)
        for (x, y, width, height) in faces:
            cv2.rectangle(frame, (x, y), (x + width,
                          y + height), (0, 255, 0), 3)
            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) == ord('q'):
                print("Smart security camera is now disabled!!")
                os.system("off.mp3")
                break
        out.release()
        cap.release()
cv2.destroyAllWindows()
