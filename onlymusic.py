import cv2
import mediapipe as mp
import pyautogui  # لمحاكاة ضغطات الكيبورد

# تهيئة Mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

# دالة لحساب المسافة بين نقطتين (مع مراعاة العمق Z)
def calculate_distance_3d(point1, point2):
    return ((point1[0] - point2[0])**2 +
            (point1[1] - point2[1])**2 +
            (point1[2] - point2[2])**2)**0.5

# تشغيل الكاميرا
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # معالجة الصورة
    image = cv2.flip(image, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks, hand_label in zip(results.multi_hand_landmarks, results.multi_handedness):
            # رسم معالم اليد

            # تحديد اليد (Left أو Right)
            label = hand_label.classification[0].label  # الحصول على اسم اليد

        if label == "Right":  # استخدام اليد اليمنى فقط
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # استخراج معالم اليد
            landmarks = hand_landmarks.landmark
            thumb_tip = (landmarks[4].x, landmarks[4].y, landmarks[4].z)  # طرف الإبهام
            index_tip = (landmarks[8].x, landmarks[8].y, landmarks[8].z)  # طرف السبابة
            middle_tip = (landmarks[12].x, landmarks[12].y, landmarks[12].z)  # طرف الوسطى
            ring_tip = (landmarks[16].x, landmarks[16].y, landmarks[16].z)  # طرف البنصر

            if calculate_distance_3d(thumb_tip, middle_tip) < 0.05:
                pyautogui.press('nexttrack')  # محاكاة الضغط على PgDown
                print("nexttrack")

            if calculate_distance_3d(thumb_tip, index_tip) < 0.05:
                    pyautogui.press('playpause')  # محاكاة الضغط على PgDown
                    print("playpause")

                # إيماءة 2: لمس الإبهام للبنصر -> PgUp
            if calculate_distance_3d(thumb_tip, ring_tip) < 0.05:
                pyautogui.press('prevtrack')  # محاكاة الضغط على PgUp
                print("prevtrack")



    # عرض الصورة
    cv2.imshow('Hand Gesture Control', image)

    if cv2.waitKey(1) & 0xFF == 27:  # اضغط Escape للخروج
        break

cap.release()
cv2.destroyAllWindows()
