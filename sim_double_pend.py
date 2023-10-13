import time
import array
from math import sin, cos, pi, tau

START_TIME_NS = time.perf_counter_ns()
tick = 0
amplitude = 0.9
num_samples = 1

r1 = 0.5
r2 = 0.5
m1 = 0.05
m2 = 0.02
a1 = tau/6
a2 = tau/8
a1_v = 0
a2_v = 0
g = 0.0002

def update(FPS, SAMPLE_RATE):
    global tick
    global num_samples
    global a1_v
    global a2_v
    global a1
    global a2
    buffer = array.array('f')

    d_time = (time.perf_counter_ns() - START_TIME_NS + 1000) // 1000000000
    tot_samples = d_time * SAMPLE_RATE
    for i in range(min(int(SAMPLE_RATE/FPS*2), max(1, tot_samples-num_samples+1)**2)):
        tick += 1

        num1 = -g * (2 * m1 + m2) * sin(a1)
        num2 = -m2 * g * sin(a1 - 2 * a2)
        num3 = -2 * sin(a1 - a2) * m2
        num4 = a2_v * a2_v * r2 + a1_v * a1_v * r1 * cos(a1 - a2)
        den = r1 * (2 * m1 + m2 - m2 * cos(2 * a1 - 2 * a2))
        a1_a = (num1 + num2 + num3 * num4) / den
        num1 = 2 * sin(a1 - a2)
        num2 = (a1_v * a1_v * r1 * (m1 + m2))
        num3 = g * (m1 + m2) * cos(a1)
        num4 = a2_v * a2_v * r2 * m2 * cos(a1 - a2)
        den = r2 * (2 * m1 + m2 - m2 * cos(2 * a1 - 2 * a2))
        a2_a = (num1 * (num2 + num3 + num4)) / den

        a1_v += a1_a
        a2_v += a2_a
        a1 += a1_v
        a2 += a2_v

        x1 = r1 * sin(a1)
        y1 = r1 * cos(a1)
        x2 = x1 + r2 * sin(a2)
        y2 = y1 + r2 * cos(a2)

        sample = amplitude * y2
        buffer.append(sample)
    num_samples += len(buffer)
    return buffer

def handle_input(pygame, event_queue):
    global m2
    for event in event_queue:
        if event.type == pygame.KEYDOWN:
            print("yes")
            if event.key == pygame.K_UP:
                m2 *= 1.05945165945
            elif event.key == pygame.K_DOWN:
                m2 /= 1.05945165945

def updateGUI(pygame, event_queue, WIN_SIZE, scr, font, buffer):
    handle_input(pygame, event_queue)
    scr.fill((0, 0, 0))
    for x, s in enumerate(buffer):
        pygame.draw.circle(scr, (0, 0, 255), (WIN_SIZE[0]/len(buffer)*x, WIN_SIZE[1] / 2 + s * WIN_SIZE[1] / 2), 5)

    x1 = r1 * sin(a1)
    y1 = r1 * cos(a1)
    x2 = x1 + r2 * sin(a2)
    y2 = y1 + r2 * cos(a2)

    pygame.draw.line(scr, (255, 255, 255), (WIN_SIZE[0] / 2 + 0 * WIN_SIZE[1] / 2, WIN_SIZE[0] / 2 + 0 * WIN_SIZE[1] / 2), (WIN_SIZE[0] / 2 + x1 * WIN_SIZE[1] / 2, WIN_SIZE[0] / 2 + y1 * WIN_SIZE[1] / 2), 5)
    pygame.draw.line(scr, (255, 255, 255), (WIN_SIZE[0] / 2 + x1 * WIN_SIZE[1] / 2, WIN_SIZE[0] / 2 + y1 * WIN_SIZE[1] / 2), (WIN_SIZE[0] / 2 + x2 * WIN_SIZE[1] / 2, WIN_SIZE[0] / 2 + y2 * WIN_SIZE[1] / 2), 5)
    pygame.draw.circle(scr, (255, 0, 0), (WIN_SIZE[0] / 2 + x1 * WIN_SIZE[1] / 2, WIN_SIZE[0] / 2 + y1 * WIN_SIZE[1] / 2), 5)
    pygame.draw.circle(scr, (255, 0, 0), (WIN_SIZE[0] / 2 + x2 * WIN_SIZE[1] / 2, WIN_SIZE[0] / 2 + y2 * WIN_SIZE[1] / 2), 5)

    scr.blit(font.render("tick: " + str(tick), True, (255, 255, 255)), (20, 50))
    scr.blit(font.render("M2: " + str(m2), True, (255, 255, 255)), (20, 70))
    pygame.display.flip()
