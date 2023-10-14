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

    def print_colored_result(self, key: str, is_matched: bool):
        if is_matched:
            print(colored_text(f"{key}: P", "92"), end=", ")  # 92: Bright Green
        else:
            print(colored_text(f"{key}: F", "91"), end=", ")  # 91: Bright Red

    def test_ocr_for_images(self):
        total_matched = 0
        total_elements = 0

        for image_name, expected_value in self.EXPECTED_VALUES.items():
            file_name = f'test_image/input/{image_name}'
            image = cv2.imread(file_name, cv2.IMREAD_COLOR)
            ocr_result = nutrition_run(image)

            if not isinstance(ocr_result, dict):
                print(colored_text(f"Failed to recognize text for {image_name}", "91"))
                for key in expected_value:
                    self.print_colored_result(key, False)
                print("\n정확도: 0%")
                print('-' * 40)
                total_elements += 5
                continue

            num_matched = 0
            for key, expected_val in expected_value.items():
                is_matched = ocr_result.get(key) == expected_val
                if is_matched:
                    num_matched += 1
                self.print_colored_result(key, is_matched)

            total_matched += num_matched
            total_elements += len(expected_value)

            accuracy = (num_matched / len(expected_value)) * 100
            print(f"\n정확도: {accuracy:.2f}%")
            print('-' * 40)

        overall_accuracy = (total_matched / total_elements) * 100
        print(f"일치도: {total_matched}/{total_elements}, 정확도: {overall_accuracy:.2f}%")


if __name__ == "__main__":
    unittest.main()




