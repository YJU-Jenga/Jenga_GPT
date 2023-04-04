import openai
import pyaudio
import pygame
import config
import multiprocessing
import time
import speech_recognition as sr
import subprocess
import pymysql
import re

from gtts import gTTS

# from playsound import playsound

# 동화 Database 생성
# subprocess.run(['python', 'crawling.py'])
db = pymysql.Connect(
    host='localhost',
    user='jenga',
    password=config.database_password,
    database='jenga',
    charset='utf8',
)
cursor = db.cursor()

sql = 'SELECT title, detail FROM jenga.book'
cursor.execute(sql)
datas = cursor.fetchall()
database_tuple = ()
for data in datas:
    database_tuple = database_tuple + data

print(database_tuple)

# GPT api key
openai.api_key = config.openai_api_key
# 인형 이름
name = "딸기"

# pygame init
pygame.mixer.init()

# pygame 음량조절
# pygame.mixer.music.set_volume(1.0) # 0.0 ~ 1.0

audio = pyaudio.PyAudio()
# 사용하는 마이크 출력
for index in range(audio.get_device_count()):
    desc = audio.get_device_info_by_index(index)
    print("DEVICE: {device}, INDEX: {index}, RATE: {rate} ".format(
        device=desc["name"], index=index, rate=int(desc["defaultSampleRate"])))

r = sr.Recognizer()


def mic_to_text(source):
    audio = r.listen(source)
    text = r.recognize_google(audio, language='ko-KR')
    print(text)

    return text


with sr.Microphone() as source:
    print("Speak:")
    while True:
        try:
            text = mic_to_text(source)
            if name in text:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                print("네")
                pygame.mixer.Sound("start.mp3").play()
                text = mic_to_text(source)
                print("You said: ", text)
                if '동화' in text:
                    tts = gTTS(text="어떤 동화를 읽어드릴까요?", lang="ko")
                    tts.save("gtts.mp3")
                    pygame.mixer.Sound("gtts.mp3").play()

                    text = mic_to_text(source)
                    text = re.sub(r"[^가-힣]", "", text)

                    if database_tuple in text:
                        try:
                            tts = gTTS(text=text+"동화를 들려드릴께요", lang="ko")
                            tts.save("gtts.mp3")
                            pygame.mixer.Sound("gtts.mp3").play()

                            sql = "SELECT detail from jenga.book WHERE title=%s"
                            cursor.execute(sql, text)
                            content = cursor.fetchall()
                            print(content)
                        except:
                            print("Database Error")

                else:
                    start = time.time()
                    response = openai.Completion.create(
                        model="text-davinci-003",
                        # 사용할 GPT-3 모델의 ID를 나타냅니다. 이 값은 OpenAI API에서 제공되는 모델 ID 중 하나여야 합니다. 위 코드에서는 text-davinci-003 모델을 사용하고 있습니다. 이 모델은 가장 성능이 뛰어난 모델 중 하나입니다.
                        prompt=text,
                        # 모델이 생성할 텍스트의 시작점이 되는 문장이나 단어를 나타냅니다. 이 값은 모델이 생성할 텍스트의 내용과 방향을 결정하는 데 중요한 역할을 합니다.
                        temperature=0.9,
                        # 모델이 생성한 단어의 다양성 정도를 나타내는 값입니다. 값이 낮을수록 더 일관성 있는 텍스트가 생성되고, 값이 높을수록 더 다양한
                        # 텍스트가 생성됩니다.
                        max_tokens=2048,  # 모델이 생성할 최대 단어 수를 나타냅니다. 이 값은 생성되는 텍스트의 길이를 제어하는 데 사용됩니다.
                        top_p=1,  # 다음 단어를 결정할 때 모델이 고려하는 가능성이 높은 상위 p%의 단어를 선택합니다. 값이 높을수록 더 다양한 텍스트가 생성됩니다.
                        frequency_penalty=0.0,
                        # 자주 등장하는 단어를 사용하지 않도록 하는 정도를 나타내는 값입니다. 값이 높을수록 자주 등장하는 단어를 사용하지 않도록 강제됩니다.
                        presence_penalty=0.6,
                        # 모델이 이전에 생성한 단어를 기억하고 다음 단어를 결정하는 정도를 나타내는 값입니다. 값이 높을수록 이전에 생성한 단어와 다르게 텍스트가 생성됩니다.
                        # stop=[" Human:", " AI:"]  # 생성된 텍스트의 끝나는 지점을 나타내는 문자열 리스트입니다. 이 값이 나타날 때까지 모델이 텍스트를 생성합니다.
                    )
                    end = time.time()
                    print(f"{end - start:.5f} sec")

                    message = response.choices[0].text.strip()
                    print('message: ', message)

                    tts = gTTS(text=message, lang="ko")
                    tts.save("gtts.mp3")

                    pygame.mixer.Sound("gtts.mp3").play()
        except:
            print("Could not recognize your voice")