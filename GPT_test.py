import openai
import pyaudio
import pygame
import time
import speech_recognition as sr
import subprocess
import pymysql
import re
import config

from gtts import gTTS
from config import db_config


# 동화 Database 생성
# subprocess.run(['python', 'crawling.py'])


# 동화 Database 연결
def connect_database(config):
    with pymysql.connect(**config) as db:
        with db.cursor() as cursor:
            sql = "SELECT title, detail FROM jenga.book"
            cursor.execute(sql)
            database_list = cursor.fetchall()
    return database_list


# 마이크와 스피커의 정보를 알려주는 함수
def print_audio_info():
    audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        print("Index: {0}, Name: {1}, Channels: {2}, Max Input Channels: {3}".format(i, info['name'],
                                                                                     info['maxInputChannels'],
                                                                                     info['maxOutputChannels']))
    audio.terminate()


# Speech To Text
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("음성 명령을 기다리는 중...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language='ko-KR')
        print("음성 명령: {}".format(text))
        return text
    except sr.UnknownValueError:
        print("음성을 인식할 수 없습니다.")
    except sr.RequestError as e:
        print("Google Speech Recognition 서비스에서 오류 발생; {0}".format(e))
    return ""


# Text To Speech
def text_to_speech(text):
    file_name = "gtts.mp3"
    tts = gTTS(text=text, lang='ko')
    tts.save(file_name)
    tts_sound = pygame.mixer.Sound(file_name)
    tts_sound.play()


# 받은 문자열에서 한글만 추출하고 공백과 특수문자를 제거하는 함
def get_cleaned_text(text):
    cleaned_text = re.sub(r"[^가-힣]", "", text)
    return cleaned_text


# 데이터베이스에 존재하는 동화를 읽어주는 함수
def play_fairy_tale(database_list):
    text_to_speech("어떤 동화를 들려줄까? 동화 제목만 말해줘.")
    time.sleep(3)
    try:
        text = speech_to_text()
        text = get_cleaned_text(text)
        for tale_title, tale_content in database_list:
            if tale_title == text:
                text_to_speech(text + "동화를 들려줄께.")
                text_to_speech(tale_content)
                break
        else:
            text_to_speech("그런 동화는 없어.")
    except sr.UnknownValueError:
        text_to_speech("미안해, 내가 듣지 못했어.")


def main():
    while True:
        try:
            text = speech_to_text()
            if dall_name in text:
                if pygame.mixer.get_busy():
                    pygame.mixer.stop()
                print("네")
                pygame.mixer.Sound("start.mp3").play()
                text = speech_to_text()
                if '동화' in text:
                    play_fairy_tale(database_list)
                else:
                    response = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=text,
                        temperature=0.9,
                        max_tokens=2048,
                        top_p=1,
                        frequency_penalty=0.0,
                        presence_penalty=0.6,
                    )
                    message = response.choices[0].text.strip()
                    print("message: ", message)

                    text_to_speech(message)
        except sr.UnknownValueError:
            print("음성을 인식할 수 없음")
        except sr.RequestError as e:
            print("Google 음성 인식 서비스에서 결과를 요청할 수 없음; {0}".format(e))
        except Exception as e:
            print("음성 명령을 처리하는 동안 오류가 발생; {0}".format(e))


if __name__ == "__main__":
    openai.api_key = config.openai_api_key
    dall_name = "딸기"

    print_audio_info()  # 마이크와 스피커의 정보를 알려주는 함수
    pygame.mixer.init()

    database_list = connect_database(db_config)

    main()