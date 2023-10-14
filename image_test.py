import unittest
import cv2

from utils.nutrition_runner import nutrition_run

def colored_text(text: str, color_code: str) -> str:
    return f"\033[{color_code}m{text}\033[0m"

class TestOCRAccuracy(unittest.TestCase):
    EXPECTED_VALUES = {
        'test1.jpg': {'칼로리': 480, '탄수화물': 49, '지방': 29, '단백질': 5.5},
        'test2.jpg': {'칼로리': 500, '탄수화물': 77, '지방': 16, '단백질': 12},
        'test3.jpg': {'칼로리': 175, '탄수화물': 14, '지방': 9, '단백질': 9},
        'test4.jpg': {'칼로리': 139, '탄수화물': 10, '지방': 7, '단백질': 9},
        'test5.jpg': {'칼로리': 365, '탄수화물': 67, '지방': 7, '단백질': 8},
        'test6.jpg': {'칼로리': 446, '탄수화물': 99, '지방': 3, '단백질': 7},
        'test7.jpg': {'칼로리': 505, '탄수화물': 84, '지방': 15, '단백질': 9},
        'test8.jpeg': { '칼로리': 200, '탄수화물': 43, '지방': 1.1, '단백질': 4},
        'test9.jpeg': {'칼로리': 525, '탄수화물': 69, '지방': 25, '단백질': 6},
        'test10.jpg': { '칼로리': 505, '탄수화물': 78, '지방': 17, '단백질': 10},
        'test11.jpg': { '칼로리': 545, '탄수화물': 84, '지방': 17, '단백질': 14},

    }

    def print_results(self, label: str, values: dict, color_code: str):
        print(colored_text(label, color_code), end=" ")
        for key, val in values.items():
            if val == 'F':
                print(f"{key}: {colored_text(val, '91')}", end=", ")
            else:
                print(f"{key}: {val}", end=", ")
        print()

    def test_ocr_for_images(self):
        total_matched = 0
        total_elements = 0

        for image_name, expected_value in self.EXPECTED_VALUES.items():
            file_name = f'test_image/input/{image_name}'
            image = cv2.imread(file_name, cv2.IMREAD_COLOR)
            ocr_result = nutrition_run(image)

            self.print_results("기대", expected_value, "96")  # 96: Bright Cyan for expected

            if not isinstance(ocr_result, dict):  # OCR 실패 시
                print(colored_text("영양성분표 인식에 실패했습니다.", "91"))
                self.print_results("실제", {key: 'F' for key in expected_value.keys()}, "91")
                print(f"정확도: 0%")
                print('-' * 40)
                total_elements += 5
                continue

            actual_values_colored = {}
            num_matched = 0
            for key, expected_val in expected_value.items():
                actual_val = ocr_result.get(key)
                if actual_val == expected_val:
                    actual_values_colored[key] = colored_text(str(actual_val), "92")  # 92: Bright Green
                    num_matched += 1
                else:
                    actual_values_colored[key] = colored_text(str(actual_val), "91")  # 91: Bright Red

            self.print_results("실제", actual_values_colored, "97")  # 97: Default for actual

            total_matched += num_matched
            total_elements += len(expected_value)

            accuracy = (num_matched / len(expected_value)) * 100
            print(f"정확도: {accuracy:.2f}%")
            print('-' * 40)

        overall_accuracy = (total_matched / total_elements) * 100
        print(f"일치도: {total_matched}/{total_elements}, 정확도: {overall_accuracy:.2f}%")

if __name__ == "__main__":
    unittest.main()




