import cv2 
import numpy as np


class SkinToneClassifier:
    def __init__(self):
    
    # 얼굴 검출용 Haar Cascade 로드
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + './haarcascade_frontalface_default.xml')
    
    
    
    def _get_face_region(self, image):
    
        image = cv2.imread(image)
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # 얼굴이 하나만 검출된 경우에만 진행
        if len(faces) == 1: 
            x, y, w, h = faces[0]
            cropped_face = image[y:y + h, x: x + w]
            return cropped_face
        else:
            return None
    
    def classify_skin_tone(self, image):
        # 얼굴 영역 가져오기
        cropped_face = self._get_face_region(image)

        if cropped_face is not None:
            # 얼굴 영역의 높이와 너비 구하기
            h, w = cropped_face.shape[:2]

            # 크롭한 사진의 상대좌표를 통해 중앙 턱 왼쪽뺨 머리카락 부분의 좌표 구하기
            center_x, center_y = h // 2, w // 2
            chin_x, chin_y = h // 2, h - (w // 12)
            left_cheek_x, left_cheek_y = h // 4,  h - (w//3)
            left_hair_x, left_hair_y = h//20 , w//5 # 왼쪽 머리
            right_hair_x, right_hair_y = w - (h//20), w//5 # 오른쪽 머리

            # 좌표 색상 추출
            center_color = cropped_face[center_y, center_x]
            chin_color = cropped_face[chin_y, chin_x]
            left_cheek_color = cropped_face[left_cheek_y, left_cheek_x]
            left_hair_color = cropped_face[left_hair_y, left_hair_x]
            right_hair_color = cropped_face[right_hair_y, right_hair_x]

            # 색상 평균 계산
            avg_skin_color = np.mean([center_color, chin_color, left_cheek_color], axis=0).astype(np.uint8)
            avg_hair_color = np.mean([left_hair_color, right_hair_color], axis=0).astype(np.uint8)

            # 평균 색상의 LAB 값 계산
            skin_bgr_array = np.array([[avg_skin_color]], dtype=np.uint8)
            skin_color_lab = cv2.cvtColor(skin_bgr_array, cv2.COLOR_BGR2LAB)[0][0]
            skin_l, skin_a, skin_b = skin_color_lab

            # 헤어 평균색상의 LAB값 계산
            hair_bgr_array = np.array([[avg_hair_color]], dtype=np.uint8)
            hair_color_lab = cv2.cvtColor(hair_bgr_array, cv2.COLOR_BGR2LAB)[0][0]
            hair_l, hair_a, hair_b = hair_color_lab

            # L contrast
            contrast = skin_l - hair_l

            # 피부톤 분류 (웜톤 쿨톤)
            if skin_a + 3 > skin_b: # 쿨톤의 사진도 a가 낮은 경우가 많아서 약간의 가중치가 필요
                skin_tone = 'cool'
            else:
                skin_tone = 'warm'
            
            if skin_tone == 'warm':
                if contrast > 50:
                    skin_tone = 'spring_warm'
                else:
                    skin_tone = 'fall_warm'
            else:
                if contrast > 50:
                    skin_tone = 'winter_cool'
                else:
                    skin_tone = 'summer_cool'

            return skin_tone

        else:
            return "얼굴이 검출되지 않거나, 여러 개의 얼굴이 검출되었습니다."

