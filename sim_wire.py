import random
import time
import array
import numpy as np

START_TIME_NS = time.perf_counter_ns()
tick = 0
amplitude = 0.7
num_samples = 1

n_points = 16
n_strings = 5
full_position = np.zeros((n_strings, n_points+2))
position = full_position[:, 1:-1]
momentum = np.zeros((n_strings, n_points))
base_mass = 0.1
mass = np.full((n_strings, n_points), base_mass)
base_k = 0.03
k = np.full((n_strings, n_points), base_k)
dt = 0.02
dp = 0.9999
OCT = 0
def update(FPS, SAMPLE_RATE):
    global tick
    global num_samples
    global momentum
    global full_position
    global position
    buffer = array.array('f')

    d_time = (time.perf_counter_ns() - START_TIME_NS + 1000) // 1000000000
    tot_samples = d_time * SAMPLE_RATE
    #print("tot_samples-num_samples = ", tot_samples-num_samples)
    batch_size = min(int(SAMPLE_RATE/FPS*2), max(1, tot_samples-num_samples+1))
    for i in range(batch_size):
        tick += 1
        full_position[:,1] = 0
        full_position[:,-2] = 0

        force = (k * (full_position[:, 1:-1] - full_position[:,:-2] + full_position[:, 1:-1] - full_position[:,2:]))
        momentum = momentum*dp - force*dt
        full_position[:, 1:-1] = full_position[:, 1:-1] + momentum / mass

        sample = amplitude * np.sum(position[:,n_points//2])
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
    all_keys = number_keys + row1_keys + row2_keys + row3_keys
    if random.random() < 1/60:
        event_queue.append(pygame.event.Event(pygame.KEYDOWN, key=random.choice(all_keys)))
    for event in event_queue:
        if event.type == pygame.KEYDOWN:
            if event.key in all_keys:
                if event.key in number_keys:
                    k[0,:] = np.full((1, n_points), base_k*(1.05945165945**number_keys.index(event.key)))
                    mass[0,:] = np.full((1, n_points), base_mass*(1.05945165945**(8*(OCT+0))))
                    position[0, 3] = 0.5
                elif event.key in row1_keys:
                    k[1,:] = np.full((1, n_points), base_k*(1.05945165945**row1_keys.index(event.key)))
                    mass[1,:] = np.full((1, n_points), base_mass*(1.05945165945**(8*(OCT+2))))
                    position[1, 3] = 0.5
                elif event.key in row2_keys:
                    k[2,:] = np.full((1, n_points), base_k*(1.05945165945**row2_keys.index(event.key)))
                    mass[2,:] = np.full((1, n_points), base_mass*(1.05945165945**(8*(OCT+3))))
                    position[2, 3] = 0.5
                elif event.key in row3_keys:
                    k[3,:] = np.full((1, n_points), base_k*(1.05945165945**row3_keys.index(event.key)))
                    mass[3,:] = np.full((1, n_points), base_mass*(1.05945165945**(8*(OCT+4))))
                    position[3, 3] = 0.5
            elif event.key == pygame.K_SPACE:
                mass[4, :] = np.full((1, n_points), base_mass * (1.05945165945 ** (8 * (OCT + 5))))
                position[4, 3] = 0.5

def updateGUI(pygame, event_queue, WIN_SIZE, scr, font, buffer):
    handle_input(pygame, event_queue)
    scr.fill((0, 0, 0))
    for x, s in enumerate(buffer):
        pygame.draw.circle(scr, (255, 255, 255), (WIN_SIZE[0]/len(buffer)*x, WIN_SIZE[1] / 2 + s * WIN_SIZE[1]), 5)

    for x in range(n_points-1):
        for y in range(n_strings):
            pygame.draw.line(scr, (255*(y%2), 255*(y//2%2), 255*((y-1)//3%2)),
                             (WIN_SIZE[0]/(n_points-1)* x   , (y+1) * WIN_SIZE[1] / (n_strings+1) + position[y,  x  ] * WIN_SIZE[1] / 2),
                             (WIN_SIZE[0]/(n_points-1)*(x+1), (y+1) * WIN_SIZE[1] / (n_strings+1) + position[y,  x+1] * WIN_SIZE[1] / 2), 5)

    scr.blit(font.render("tick: " + str(tick), True, (255, 255, 255)), (20, 50))
    pygame.display.flip()
