import cv2
import numpy as np

class PreProcessor:
    def crop_image(self, original_image):

        gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)  # 그레이 스케일 적용

        _, binary_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)  # 이미지 이진화

        # 우리가 인식하고자 하는 영양성분표는 테이블 내에 수평선, 수직선들이 있음
        # 따라서 해당 형태의 테이블의 윤곽선을 인식하기 위해 cv2로 대략적인 구조를 잡아줌
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
        vertical_lines = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
        horizontal_lines = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

        table_structure = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)

        # 윤곽선 검출
        contours, _ = cv2.findContours(table_structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        largest_contour = max(contours, key=cv2.contourArea)

        x, y, w, h = cv2.boundingRect(largest_contour)

        cropped_image = original_image[y:y + h, x:x + w]
        return cropped_image

        # 이후, 영양성분표만 잘라낸 이미지를 크롭하여 따로 저장
        # output_path = "../test_image/output/cropped_table_enhanced.jpg"
        # cv2.imwrite(output_path, cropped_image)

    def preprocess_image(self, image):
        cropped_image = self.crop_image(image)
        # 1. 이진화 (Binarization)
        # 그레이스케일로 변환
        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

        #
        # kernel_sharpening = np.array([[-1,-1,-1],
        #                              [-1,9,-1],
        #                             [-1,-1,-1]])
        # sharpened = cv2.filter2D(gray, -1, kernel_sharpening)



        # # 결과 이미지 표시
        # cv2.imshow("Processed", sharpened)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return cropped_image

if __name__ == "__main__":
    image = cv2.imread('../test_image/input/test3.jpg',cv2.IMREAD_COLOR)
    preprocessor = PreProcessor()
    preprocessor.preprocess_image(image)



