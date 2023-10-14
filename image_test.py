import unittest
import cv2

from utils.nutrition_runner import nutrition_run

def colored_text(text: str, color_code: str) -> str:
    return f"\033[{color_code}m{text}\033[0m"

class TestOCRAccuracy(unittest.TestCase):
    EXPECTED_VALUES = {
        'test5.jpg': {'내용량': 490, '칼로리':365, '탄수화물': 67, '지방': 7, '단백질': 8},
        'test6.jpg': {'내용량': 110, '칼로리': 446, '탄수화물': 99, '지방': 3, '단백질': 7},
        'test7.jpg': {'내용량': 120, '칼로리': 505, '탄수화물': 84, '지방': 15, '단백질': 9},

    }

    def print_results(self, label: str, values: dict, color_code: str):
        print(colored_text(label, color_code), end=" ")
        for key, val in values.items():
            print(f"{key}: {val}", end=", ")
        print()

    def test_ocr_for_images(self):
        total_matched = 0
        total_elements = 0

        for image_name, expected_value in self.EXPECTED_VALUES.items():
            file_name = f'test_image/input/{image_name}'
            image = cv2.imread(file_name, cv2.IMREAD_COLOR)
            ocr_result = nutrition_run(image)

            if not isinstance(ocr_result, dict):
                print(colored_text(f"Failed to recognize text for {image_name}", "91"))
                continue

            self.print_results("기대", expected_value, "96")  # 96: Bright Cyan for expected

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



