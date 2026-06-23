import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os
import time

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 1

engine = pyttsx3.init()
newsapi = "<Your Key Here>"

pygame.mixer.init()

print(sr.Microphone.list_microphone_names())

def speak_old(text):
    engine.say(text)
    engine.runAndWait()

def speak(text):
    try:
        tts = gTTS(text=text, lang="en")
        tts.save("temp.mp3")

        pygame.mixer.music.load("temp.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()

        if os.path.exists("temp.mp3"):
            os.remove("temp.mp3")

    except Exception as e:
        print("Speech Error:", e)

def aiProcess(command):
    client = OpenAI(
        api_key="<Your Key Here>"
    )

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a virtual assistant named Jarvis skilled in general tasks like Alexa and Google Assistant. Give short responses."
            },
            {
                "role": "user",
                "content": command
            }
        ]
    )

    return completion.choices[0].message.content

def processCommand(c):
    c = c.lower()

    if "open google" in c:
        speak("Opening Google")
        webbrowser.open("https://google.com")

    elif "open facebook" in c:
        speak("Opening Facebook")
        webbrowser.open("https://facebook.com")

    elif "open youtube" in c:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")

    elif "open linkedin" in c:
        speak("Opening LinkedIn")
        webbrowser.open("https://linkedin.com")

    elif c.startswith("play"):
        try:
            song = c.split(" ")[1]
            link = musicLibrary.music[song]
            speak(f"Playing {song}")
            webbrowser.open(link)

        except Exception:
            speak("Song not found")

    elif "news" in c:
        try:
            r = requests.get(
                f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}"
            )

            if r.status_code == 200:
                data = r.json()
                articles = data.get("articles", [])

                for article in articles[:5]:
                    speak(article["title"])

            else:
                speak("Unable to fetch news")

        except Exception:
            speak("Internet connection error")

    else:
        try:
            output = aiProcess(c)
            print("Jarvis:", output)
            speak(output)

        except Exception as e:
            print(e)
            speak("Open AI error")

if __name__ == "__main__":
    speak("Initializing Jarvis")

    while True:
        try:
            with sr.Microphone(device_index=0) as source:
                print("Listening for wake word...")

                recognizer.adjust_for_ambient_noise(source, duration=2)

                audio = recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=5
                )

            word = recognizer.recognize_google(audio).lower()

            print("You said:", word)

            if "jarvis" in word:
                speak("Yes")

                with sr.Microphone(device_index=0) as source:
                    print("Jarvis Active...")

                    recognizer.adjust_for_ambient_noise(source, duration=1)

                    audio = recognizer.listen(
                        source,
                        timeout=10,
                        phrase_time_limit=7
                    )

                command = recognizer.recognize_google(audio)

                print("Command:", command)

                processCommand(command)

                time.sleep(1)

        except sr.WaitTimeoutError:
            print("Listening timeout")

        except sr.UnknownValueError:
            print("Could not understand audio")

        except sr.RequestError:
            print("Internet connection issue")

        except Exception as e:
            print("Error:", e)