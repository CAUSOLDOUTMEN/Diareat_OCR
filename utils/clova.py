import os
import requests
import uuid
import time
import json


from utils.nutrition_parser import parse_nutrients_from_text



def clova_ocr(file, file_content):
    api_url = os.environ.get("API_URL")
    secret_key = os.environ.get("SECRET_KEY")

    request_json = {
        'images': [
            {
                'format': 'png',
                'name': 'demo'
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    files = {
        'message': (None, json.dumps(request_json), 'application/json'),
        'file': (file.filename, file_content, file.content_type)
    }

    headers = {
        'X-OCR-SECRET': secret_key
    }
    payload = {'message': json.dumps(request_json).encode('UTF-8')}

    response = requests.request("POST", api_url, headers=headers, files=files)

    res = json.loads(response.text.encode('utf8'))
    print(res)

    # 결과에서 Text만 추출하여 출력하기 위한 코드
    text = res['images'][0]['fields']
    answer = ''

    # fileds 배열의 길이만큼 반복하면서 inferText 값을 담고 공백을 붙여줌
    for i in range(len(text)):
        answer += text[i]['inferText'] + ' '
    return parse_nutrients_from_text(answer)