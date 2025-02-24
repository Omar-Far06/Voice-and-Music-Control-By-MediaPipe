import cv2
import mediapipe as mp
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
import time
import csv


# إعداد Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.9)
mp_drawing = mp.solutions.drawing_utils

# إعداد التحكم في الصوت
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# جلب نطاق الصوت
min_vol, max_vol = volume.GetVolumeRange()[:2]

# فتح الكاميرا
cap = cv2.VideoCapture(0)


def calculate_distance(point1, point2):
    """
    حساب المسافة بين نقطتين باستخدام النظرية الإقليدية.
    """
    return math.hypot(point2.x - point1.x, point2.y - point1.y)


def is_hand_open(landmarks):
    """
    تحديد ما إذا كانت اليد مفتوحة باستخدام المسافات النسبية بين أطراف الأصابع وقواعدها.
    """
    fingers_open = 0
    finger_tips = [8, 12, 16, 20]  # أطراف الأصابع
    finger_bases = [5, 9, 13, 17]  # قواعد الأصابع

    # حساب المسافة بين راحة اليد والمعصم (نقطة 0 ونقطة 9)
    palm_base_distance = calculate_distance(landmarks[0], landmarks[9])

    for tip, base in zip(finger_tips, finger_bases):
        # حساب المسافة بين طرف وقاعدة كل إصبع
        finger_distance = calculate_distance(landmarks[tip], landmarks[base])

        # مقارنة المسافة مع نسبة من مسافة راحة اليد
        if finger_distance > palm_base_distance * 0.4:  # نسبة 40% يمكن تعديلها
            fingers_open += 1

    # اليد تعتبر مفتوحة إذا كان 3 أصابع على الأقل مفتوحة
    return fingers_open >= 3


# إعداد ملف CSV لتخزين البيانات
with open("hand_data.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["distance_thumb_index", "distance_index_middle", "is_open"])  # أسماء الأعمدة

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("فشل في قراءة الإطار من الكاميرا.")
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = hand_landmarks.landmark

            # التحكم في الصوت بناءً على حالة اليد (مفتوحة أو مغلقة)
            if is_hand_open(landmarks):  # إذا كانت اليد مفتوحة
                current_volume = volume.GetMasterVolumeLevel()
                new_volume = min(current_volume + 0.5, max_vol)  # زيادة الصوت
                volume.SetMasterVolumeLevel(new_volume, None)
                cv2.putText(frame, "Hand Open: Volume Up", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:  # إذا كانت اليد مغلقة
                current_volume = volume.GetMasterVolumeLevel()
                new_volume = max(current_volume - 0.5, min_vol)  # خفض الصوت
                volume.SetMasterVolumeLevel(new_volume, None)
                cv2.putText(frame, "Hand Closed: Volume Down", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # عرض نسبة الصوت
            current_volume = volume.GetMasterVolumeLevel()
            volume_percent = int(((current_volume - min_vol) / (max_vol - min_vol)) * 100)
            cv2.putText(frame, f'Volume: {volume_percent}%', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # عرض الإطار
    cv2.imshow('Volume Control', frame)

    # الضغط على "q" للخروج
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
