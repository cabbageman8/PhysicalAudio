# Program Imports
import time
import pyaudio
import sim_double_pend
import sim_wire
import cProfile
import timeit

GUI = 1
WIN_SIZE = 1000, 1000
FPS = 60
SAMPLE_RATE = 16000

quit = False

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE, output=True)

# If GUI is True (We initialize the pygame gui)
if GUI:
    import pygame
    fontsize = 20
    pygame.init()
    pygame.font.init()
    scr = pygame.display.set_mode(WIN_SIZE)
    silombol = pygame.font.Font("SilomBol.ttf", fontsize)

event_queue = []
def handle_input():
    global quit
    global event_queue
    event_queue = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit = True
            else:
                event_queue.append(event)

while not quit:
    before = time.perf_counter()
    #cProfile.run('buffer = sim_wire.update(FPS, SAMPLE_RATE)', sort=2)
    buffer = sim_wire.update(FPS, SAMPLE_RATE)
    print("update time = ", int((time.perf_counter() - before)*1000), "ms")
    byt = buffer.tobytes()
    stream.write(byt, len(buffer))
    if GUI:
        handle_input()
        sim_wire.updateGUI(pygame, event_queue, WIN_SIZE, scr, silombol, buffer)
    time.sleep(1/FPS)

if GUI:
    pygame.quit()
stream.stop_stream()
stream.close()
p.terminate()
