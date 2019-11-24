import wave
from pydub import AudioSegment
from pydub.silence import split_on_silence
from ffmpeg import *
import os
import speech_recognition as sr

class Audio():
    def  __init__(self, audiopath):
        if str(audiopath).lower().endswith('.wav'):
            self.setText(audiopath, ".wav")
        elif str(audiopath).lower().endswith('.mp3'):
            self.converttowav(audiopath)
            audiopath = os.getcwd() + "\CAudio.wav"
            self.setText(audiopath, ".mp3")

    def converttowav(self, audiopath):
        os.environ["PATH"] += os.pathsep + 'ffmpeg/bin/'
        audiotowav = AudioSegment.from_mp3(audiopath)
        audiotowav.export(os.getcwd() + "\CAudio.wav", format="wav")

    def setText(self, audiopath, ext):
        r = sr.Recognizer()
        hellow = sr.AudioFile(audiopath)

        with hellow as source:
            audioX = r.record(source)

        try:
            self.text = r.recognize_google(audioX)
            print(self.text)
        except Exception as e:
            print(str(e))

        # if ext == '.mp3':
            #  os.remove(audiopath)


c = Audio("C:/Users/Asad/Desktop/AAAA.wav")
#c = Audio("CAudio.wav")
print("Hello")
print(c.text)
#c.CreateWordCloud(c.text)

