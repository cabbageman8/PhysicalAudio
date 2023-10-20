import random
import time
import array
import numpy as np

START_TIME_NS = time.perf_counter_ns()
tick = 0
amplitude = 50
num_samples = 1

n_points = 16
n_strings = 5
full_position = np.zeros((n_strings, n_points+2))
position = full_position[:, 1:-1]
momentum = np.zeros((n_strings, n_points))
base_jerk = 0.08
base_mass = 100
mass = np.full((n_strings, n_points), base_mass)
base_damp = 0.999
damper = np.full((n_strings, n_points), base_damp)
base_k = 5
k = np.full((n_strings, n_points), base_k)
dt = 0.01
cd = 0.05
OCT = -6
FFT_buffer = array.array('f')
def update(FPS, SAMPLE_RATE):
    global tick
    global num_samples
    global momentum
    global full_position
    global position
    global FFT_buffer
    buffer = array.array('f')

    d_time = (time.perf_counter_ns() - START_TIME_NS + 1000) // 1000000000
    tot_samples = d_time * SAMPLE_RATE
    #print("tot_samples-num_samples = ", tot_samples-num_samples)
    batch_size = min(int(SAMPLE_RATE/FPS*2), max(1, tot_samples-num_samples+1))

    for i in range(batch_size):
        tick += 1
        full_position[:,1] = 0
        full_position[:,-2] = 0

        force = (k * (full_position[:, 1:-1] - full_position[:,:-2] + full_position[:, 1:-1] - full_position[:,2:])) + ((momentum / mass) * cd)
        momentum = momentum*damper - force*dt
        full_position[:, 1:-1] = full_position[:, 1:-1] + momentum / mass

        sample = amplitude * np.sum((force * momentum / mass)[:,:])
        buffer.append(sample)

    num_samples += len(buffer)
    return buffer

def handle_input(pygame, event_queue):
    global k
    global mass
    number_keys = (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0)
    row1_keys = (pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t, pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p)
    row2_keys = (pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l)
    row3_keys = (pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v, pygame.K_b, pygame.K_n, pygame.K_m)
    row4_keys = (pygame.K_SPACE,)
    key_rows = (number_keys, row1_keys, row2_keys, row3_keys, row4_keys)
    all_keys = number_keys + row1_keys + row2_keys + row3_keys + row4_keys
    #if random.random() < 1/60:
    #    event_queue.append(pygame.event.Event(pygame.KEYDOWN, key=random.choice(all_keys)))
    for event in event_queue:
        if event.type == pygame.KEYDOWN:
            if event.key in all_keys:
                for i, key_row in enumerate(key_rows):
                    if event.key in key_row:
                        row = i
                        key_list = key_row
                damper[row, :] = np.full((1, n_points), 1)
                k[row,:] = np.full((1, n_points), base_k*(1.05945165945**(key_list.index(event.key)-(8*(OCT+row)))))
                new_mass = base_mass*(1.05945165945**(-key_list.index(event.key)+(8*(OCT+row))))
                mass[row,:] = np.full((1, n_points), new_mass)
                #momentum[row, :] = 0.01
                position[row, :] = 0.01
        if event.type == pygame.KEYUP:
            if event.key in all_keys:
                for i, key_row in enumerate(key_rows):
                    if event.key in key_row:
                        row = i
                damper[row,:] = np.full((1, n_points), base_damp)

def updateGUI(pygame, event_queue, WIN_SIZE, scr, font, buffer):
    global FFT_buffer
    handle_input(pygame, event_queue)
    scr.fill((0, 0, 0))
    for x in range(n_points-1):
        for y in range(n_strings):
            pygame.draw.line(scr, (255*(y%2), 255*(y//2%2), 255*((y-1)//3%2)),
                             (WIN_SIZE[0]/(n_points-1)* x   , (y+1) * WIN_SIZE[1] / (n_strings+1) + position[y,  x  ] * WIN_SIZE[1] / 2),
                             (WIN_SIZE[0]/(n_points-1)*(x+1), (y+1) * WIN_SIZE[1] / (n_strings+1) + position[y,  x+1] * WIN_SIZE[1] / 2), int(40*mass[y,  x  ]/base_mass))
    X = np.fft.fftshift(np.fft.rfft(np.asarray(buffer)))
    for x, f in enumerate(X):
        pygame.draw.line(scr, (255, 255, 255), (WIN_SIZE[0] / len(X) * x, WIN_SIZE[1] - (f.real**2+f.imag**2)**0.5/60 * WIN_SIZE[1]), (WIN_SIZE[0] / len(X) * x, WIN_SIZE[1]), 3)
    for x, s in enumerate(buffer):
        pygame.draw.circle(scr, (100, 100, 100), (WIN_SIZE[0] / len(buffer) * x, WIN_SIZE[1] / 2 + s * WIN_SIZE[1]), 5)

    scr.blit(font.render("tick: " + str(tick), True, (255, 255, 255)), (20, 50))
    pygame.display.flip()
