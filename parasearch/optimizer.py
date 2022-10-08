import numpy as np
import multiprocessing as mp

class Optimizer:
    def __init__(self, optimize_fn, mins, maxs, learning_rate, batch_size, epochs, logger=None, cpu_count=4):
        self.__fn = optimize_fn
        self.__learning_rate = learning_rate
        self.__batch_size = batch_size
        self.__mins = mins
        self.__maxs = maxs
        self.__epochs = epochs
        self.__logger = logger
        self.__cpu_count = cpu_count

    def run(self):
        v = np.random.uniform(self.__mins, self.__maxs)
        loc_min = False
        total_time = 0
        for _ in range(self.__epochs):
            mins = v - self.__learning_rate
            maxs = v + self.__learning_rate
            v_new_batch = np.random.uniform(mins, maxs, (self.__batch_size, len(v)))
            pool = mp.Pool()
            samples = pool.map(self.__fn, v_new_batch)
            # pool.close()
            
            loss=[i[0] for i in samples]
            time=[i[1] for i in samples]
            
            total_time += sum(time)
            
            loss_with_v = loss + [self.__fn(v)[0]]
            p = np.argmin(loss_with_v)
            min_loss = np.min(loss_with_v)

            if self.__logger is not None:
                # self.__logger.add_row([v_new_batch[p] if p < self.__batch_size else v, min_loss])
                for i in range(self.__batch_size):
                    self.__logger.add_row([v_new_batch[i], loss[i]])

            if min_loss == 0 or min_loss == float('inf'):
                break

            if p < self.__batch_size:
                v = v_new_batch[p]
                loc_min = False
            else:
                # # print('local minimum found')
                # if loc_min:
                #     break  # found local minimum twice
                # else:
                #     loc_min = True
                break
        return v, total_time
