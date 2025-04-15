import numpy as np
from typing import Tuple
import sys
import time

class ProgressBar:
    def __init__(self, num_iterations, fill_char='-', width=50):
        self.num_iterations = num_iterations
        self.fill_char = fill_char
        self.empty_char = ' '
        self.width = width
        self.prog_bar = self.progress_bar_str(0) # This will show the progress bar as empty
        self.time_after_last_iter = time.time()
        self.time_for_last_iter = None
        self.update(0)
        
    def progress_bar_str(self, iteration):
        if iteration > self.num_iterations:
            raise ValueError('iteration is larger than num_iterations')
        return "[" + self.fill_char * int(self.width * iteration / self.num_iterations)  + self.empty_char * int(self.width * (self.num_iterations - iteration) / self.num_iterations) + "]"
        
    def update(self, iteration):
        self.prog_bar = self.progress_bar_str(iteration).ljust(self.width)
        if iteration > 0:
            current_time = time.time()
            self.time_for_last_iter = round(current_time - self.time_after_last_iter, 3)
            self.time_after_last_iter = time.time()
        sys.stdout.write('\r{0} {1}% {2}'.format(self.prog_bar, int(100 * iteration / self.num_iterations), "Last iter: " + str(self.time_for_last_iter) + "s" if iteration > 0 else ""))
        sys.stdout.flush()