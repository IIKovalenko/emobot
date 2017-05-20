import cv2
import io
import logging
import operator
import os
import numpy as np
from PIL import Image
import requests
import time

from settings import EMOTIONS_API_KEY

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.WARN,
                    filename=os.path.join(BASE_DIR, 'bot.log')
                    )
logger = logging.getLogger(__name__)

EMOTIONS_URL = 'https://westus.api.cognitive.microsoft.com/emotion/v1.0/recognize'
MAX_NUM_RETRIES = 10


def processRequest(data, headers, json=None, params=None):
    """
    Helper function to process the request to Project Oxford

    Parameters:
    data: Used when processing image read from disk
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:
        response = requests.post(EMOTIONS_URL, json=json, data=data, headers=headers, params=params)

        if response.status_code == 429:

            logger.warn("Message: %s" % (response.json()['error']['message']))

            if retries <= MAX_NUM_RETRIES:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):

                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            logger.warn("Error code: %d" % (response.status_code))
            logger.warn("Message: %s" % (response.json()['error']['message']))

        break

    return result


def renderResultOnImage(result, img):
    """Display the obtained results onto the input image"""
    emotion_rus = {
        "anger": "Гнев",
        "contempt": "Сомнение",
        "disgust": "Отвращение",
        "fear": "Страх",
        "happiness": "Радость",
        "neutral": "Нейтрально",
        "sadness": "Грусть",
        "surprise": "Удивление"
    }

    for currFace in result:
        faceRectangle = currFace['faceRectangle']
        cv2.rectangle(
            img,
            (faceRectangle['left'], faceRectangle['top']),
            (faceRectangle['left'] + faceRectangle['width'], faceRectangle['top'] + faceRectangle['height']),
            color=(0, 0, 255),
            thickness=5
        )

    for currFace in result:
        faceRectangle = currFace['faceRectangle']
        currEmotion = emotion_rus[max(currFace['scores'].items(), key=operator.itemgetter(1))[0]]

        textToWrite = "%s" % (currEmotion)
        cv2.putText(
            img,
            textToWrite,
            (faceRectangle['left'], faceRectangle['top'] - 10),
            cv2.FONT_HERSHEY_COMPLEX,
            1,
            (0, 0, 255),
            1
        )


def process_file(file, saveto=None):
    im = Image.open(file)
    im.thumbnail((800, 800))
    b = io.BytesIO()
    im.save(b, 'JPEG')
    data = b.getvalue()

    headers = dict()
    headers['Ocp-Apim-Subscription-Key'] = EMOTIONS_API_KEY
    headers['Content-Type'] = 'application/octet-stream'

    result = processRequest(data, headers)

    if result is not None:
        data8uint = np.fromstring(data, np.uint8)  # Convert string to an unsigned int array
        img = cv2.imdecode(data8uint, cv2.IMREAD_UNCHANGED)

        renderResultOnImage(result, img)

        if saveto:
            cv2.imwrite(saveto, img)
            return None
        else:
            return img


if __name__ == "__main__":
    process_file('2017-04-29 12.27.26.jpg', saveto='newpic.jpg')
