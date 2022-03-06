import mss
import numpy as np
from PIL import Image

class SS(object):
    def __init__(self, x_start, x_end, y_start, y_end, x_increase, y_increase):
        with mss.mss() as sct:
            self.dimensions = (sct.monitors[1]['width'], sct.monitors[1]['height'])
            self.images = []
            self.color_map = [] # 0 -> gray -> (126, 124, 120) | 1 -> yellow -> (88, 180, 201) | 2 -> green -> (100, 170, 106)
            self.inital_starting_x = x_start
            self.inital_ending_x = x_end
            self.initial_starting_y = y_start
            self.inital_ending_y = y_end
            self.x_increase = x_increase
            self.y_increase = y_increase
            self.starting_point = [self.inital_starting_x, self.initial_starting_y]
            self.ending_point = [self.inital_ending_x, self.inital_ending_y]
            self.down_count = 0
    
    def reset_xaxis(self):
        self.starting_point[0] = self.inital_starting_x
        self.ending_point[0] = self.inital_ending_x

    def get_letters(self):
        letter_list = []
        color_list = []

        with mss.mss() as sct:
            for i in range(5):
                if i != 0:
                    self.starting_point[0] += self.x_increase
                    self.ending_point[0] += self.x_increase

                section = {'top': self.starting_point[1], 'left': self.starting_point[0], 
                            'width': self.ending_point[0] - self.starting_point[0], 
                            'height': self.ending_point[1] - self.starting_point[1]}

                letter_list.append(sct.grab(section))

            self.images.append(letter_list)

            for image in letter_list:
                matrix_representation = np.array(image)
                matrix_list = matrix_representation.tolist()

                for rows in matrix_list:
                    if [126, 124, 120, 255] in rows:
                        color_list.append(0)
                        break
                    elif [88, 180, 201, 255] in rows:
                        color_list.append(1)
                        break
                    elif [100, 170, 106, 255] in rows:
                        color_list.append(2)
                        break

            self.color_map.append(color_list)
            

        self.reset_xaxis()
            
    def show_images(self, index):
        if len(self.images) > 0:
             for sct_img in self.images[index]:
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                img.show()
    
    def go_down(self):
            self.starting_point[1] += self.y_increase
            self.ending_point[1] += self.y_increase
