import pyaudio
import math
import struct
import wave
import time
import os
from datetime import datetime

Threshold = 100

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2
PREBUFF = 16*5

TIMEOUT_LENGTH = 5

f_name_directory = '/home/ss/barks'

class Recorder:

    @staticmethod
    def rms(frame):
        count = len(frame) / swidth
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=chunk)

    def record(self, prev=[]):
        print('Noise detected, recording beginning')
        rec = [] + prev
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:

            data = self.stream.read(chunk)
            if self.rms(data) >= Threshold:
                end = time.time() + TIMEOUT_LENGTH

            current = time.time()
            rec.append(data)
        self.write(b''.join(rec))

    def write(self, recording):
        n_files = len(os.listdir(f_name_directory))

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(f_name_directory, '{}.wav'.format(now))

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        print('Written to file: {}'.format(filename))
        print('Returning to listening')



    def listen(self):
        print('Listening beginning')
        prev = []
        while True:
            prev = prev[-PREBUFF:]
            input = self.stream.read(chunk)
            prev.append(input)
            rms_val = self.rms(input)
            print(rms_val)
            if rms_val > Threshold:
                self.record(prev)

a = Recorder()

a.listen()
