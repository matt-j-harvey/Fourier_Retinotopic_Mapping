import numpy as np
import matplotlib.pyplot as plt
import h5py
from scipy import signal, ndimage, stats
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph
import sys
from skimage import measure

pyqtgraph.setConfigOptions(imageAxisOrder='row-major')



class session_matching_window(QWidget):

    def __init__(self, parent=None):
        super(session_matching_window, self).__init__(parent)

        # Setup Window
        self.setWindowTitle("Session Registration")
        #self.setGeometry(0, 0, 1000, 500)

        # Create Variable Holders
        self.template_directory = None
        self.template_name = None
        self.template_max_projection = None

        self.matching_directory = None
        self.matching_name = None
        self.matching_max_projection = None

        self.variable_dictionary = self.create_variable_dictionary()

        display_widget_min_width = 400
        display_widget_min_height = 400

        # Add Session Buttons
        self.select_template_session_button = QPushButton("Select Template Session")
        self.select_matching_session_button = QPushButton("Select Matching Session")

        self.select_template_session_button.clicked.connect(self.select_template_session)
        self.select_matching_session_button.clicked.connect(self.select_matching_session)

        self.template_label = QLabel("Template Session: ")
        self.matching_label = QLabel("Matching Session: ")



        # Create Skeleton Figures
        self.display_view_widget = QWidget()
        self.display_view_widget_layout = QGridLayout()
        self.display_view = pyqtgraph.ImageView()
        self.display_view.ui.histogram.hide()
        self.display_view.ui.roiBtn.hide()
        self.display_view.ui.menuBtn.hide()
        self.display_view_widget_layout.addWidget(self.display_view, 0, 0)
        self.display_view_widget.setLayout(self.display_view_widget_layout)
        self.display_view_widget.setMinimumWidth(display_widget_min_width)
        self.display_view_widget.setMinimumHeight(display_widget_min_height)


        # Create Buttons
        self.left_button = QPushButton("Left")
        self.left_button.clicked.connect(self.move_left)

        self.right_button = QPushButton("Right")
        self.right_button.clicked.connect(self.move_right)

        self.up_button = QPushButton("Up")
        self.up_button.clicked.connect(self.move_up)

        self.down_button = QPushButton("Down")
        self.down_button.clicked.connect(self.move_down)

        self.rotate_clockwise_button = QPushButton("Rotate Clockwise")
        self.rotate_clockwise_button.clicked.connect(self.rotate_clockwise)

        self.rotate_counterclockwise_button = QPushButton("Rotate Counterclockwise")
        self.rotate_counterclockwise_button.clicked.connect(self.rotate_counterclockwise)

        self.map_button = QPushButton("Set Alignment")
        self.map_button.clicked.connect(self.set_alignment)

        # Add Labels
        self.x_label = QLabel("X: ")
        self.y_label = QLabel("Y: ")
        self.angle_label = QLabel("Rotation: ")

        # Create Layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Add Loading Widgets
        self.layout.addWidget(self.template_label,                  0, 0, 1, 1)
        self.layout.addWidget(self.matching_label,                  1, 0, 1, 1)
        self.layout.addWidget(self.select_template_session_button,  2, 0, 1, 1)
        self.layout.addWidget(self.select_matching_session_button,  3, 0, 1, 1)

        # Add Transformation Widgets
        self.layout.addWidget(self.left_button,                     4,  0,  1,  1)
        self.layout.addWidget(self.right_button,                    5,  0,  1,  1)
        self.layout.addWidget(self.up_button,                       6,  0,  1,  1)
        self.layout.addWidget(self.down_button,                     7,  0,  1,  1)
        self.layout.addWidget(self.rotate_clockwise_button,         8,  0,  1,  1)
        self.layout.addWidget(self.rotate_counterclockwise_button,  9,  0,  1,  1)
        self.layout.addWidget(self.x_label,                         10, 0,  1,  1)
        self.layout.addWidget(self.y_label,                         11, 0,  1,  1)
        self.layout.addWidget(self.angle_label,                     12, 0,  1,  1)
        self.layout.addWidget(self.map_button,                      13, 0,  1,  1)

        # Add Display Widgets
        self.layout.addWidget(self.display_view_widget,             0,  1,  14, 1)


        self.show()


    def create_variable_dictionary(self):

        # Transformation Attributes
        x_shift = 0
        y_shift = 0
        rotation = 0

        # Array Details
        background_size = 800
        bounding_size = 400
        background_array = np.zeros((background_size, background_size, 3))
        bounding_array = np.zeros((bounding_size, bounding_size))

        # Template Details
        template_x_start = 100
        template_y_start = 100
        template_width = 608
        template_height = 600

        # Create Dictionary
        variable_dictionary = {

            # Affine Atributes
            'x_shift': x_shift,
            'y_shift': y_shift,
            'rotation': rotation,

            # Template Deets
            'template_x_start': template_x_start,
            'template_y_start': template_y_start,
            'template_width': template_width,
            'template_height': template_height,

            # Arrays
            'background_array': background_array,
            'bounding_array': bounding_array
        }

        return variable_dictionary


    def select_template_session(self):
        new_session_filepath = QFileDialog.getOpenFileName(self, "Select Template Max Projection")[0]
        print(new_session_filepath)

        # Load Max Projection
        max_projection = np.load(new_session_filepath)
        self.template_max_projection = max_projection

        # Get New Directory + Session Name
        new_session_directory_split = new_session_filepath.split("/")
        new_session_name = new_session_directory_split[-3] + "_" + new_session_directory_split[-2]
        new_session_directory = new_session_filepath.replace("max_projection.npy", "")
        print("Template Directory", new_session_directory)

        # Add These To The Lists
        self.template_name = new_session_name
        self.template_directory = new_session_directory
        self.template_label.setText("Template Session: " + self.template_name)


    def select_matching_session(self):

        new_session_filepath = QFileDialog.getOpenFileName(self, "Select Matching Max Projection")[0]
        print(new_session_filepath)

        # Load Max Projection
        max_projection = np.load(new_session_filepath)
        self.matching_max_projection = max_projection

        # Get New Directory + Session Name
        new_session_directory_split = new_session_filepath.split("/")
        new_session_name = new_session_directory_split[-3] + "_" + new_session_directory_split[-2]
        new_session_directory = new_session_filepath.replace("max_projection.npy", "")
        print("Matching Directory", new_session_directory)

        # Add These To The Lists
        self.matching_name = new_session_name
        self.matching_directory = new_session_directory
        self.matching_label.setText("Matching Session: " + self.matching_name)


    def move_left(self):
        self.variable_dictionary['x_shift'] = self.variable_dictionary['x_shift'] + 2
        self.x_label.setText("x: " + str(self.variable_dictionary['x_shift']))
        self.draw_images(self.variable_dictionary)

    def move_right(self):
        self.variable_dictionary['x_shift'] = self.variable_dictionary['x_shift'] - 2
        self.x_label.setText("x: " + str(self.variable_dictionary['x_shift']))
        self.draw_images(self.variable_dictionary)

    def move_up(self):
        self.variable_dictionary['y_shift'] = self.variable_dictionary['y_shift'] - 2
        self.y_label.setText("y: " + str(self.variable_dictionary['y_shift']))
        self.draw_images(self.variable_dictionary)

    def move_down(self):
        self.variable_dictionary['y_shift'] = self.variable_dictionary['y_shift'] + 2
        self.y_label.setText("y: " + str(self.variable_dictionary['y_shift']))
        self.draw_images(self.variable_dictionary)

    def rotate_clockwise(self):
        self.variable_dictionary['rotation'] = self.variable_dictionary['rotation'] - 1
        self.angle_label.setText("Angle: " + str(self.variable_dictionary['rotation']))
        self.draw_images(self.variable_dictionary)

    def rotate_counterclockwise(self):
        self.variable_dictionary['rotation'] = self.variable_dictionary['rotation'] + 1
        self.angle_label.setText("Angle: " + str(self.variable_dictionary['rotation']))
        self.draw_images(self.variable_dictionary)


    def draw_images(self, variable_dictionary):

        # Load Data
        template_x_start = variable_dictionary['template_x_start']
        template_y_start = variable_dictionary['template_y_start']
        template_width = variable_dictionary['template_width']
        template_height = variable_dictionary['template_height']
        x_shift = variable_dictionary['x_shift']
        y_shift = variable_dictionary['y_shift']
        background_array = np.copy(variable_dictionary["background_array"])

        # Load Images
        template_image = self.template_max_projection
        matching_image = self.matching_max_projection

        # Rotate
        angle = variable_dictionary['rotation']
        matching_image = ndimage.rotate(matching_image, angle, reshape=False)

        # Translate
        matching_image = np.roll(a=matching_image, axis=0, shift=y_shift)
        matching_image = np.roll(a=matching_image, axis=1, shift=x_shift)

        # Insert Back In
        image_height = np.shape(matching_image)[0]
        image_width  = np.shape(matching_image)[1]

        template_image = np.divide(template_image.astype(float), np.percentile(template_image, 99))
        matching_image = np.divide(matching_image.astype(float), np.percentile(matching_image, 99))

        background_array[template_y_start:template_y_start + template_height, template_x_start:template_x_start + template_width, 2] = template_image
        background_array[template_y_start:template_y_start + image_height,    template_x_start:template_x_start + image_width,    0] = matching_image

        background_array[template_y_start:template_y_start + template_height, template_x_start:template_x_start + template_width, 1] += 0.5 * template_image
        background_array[template_y_start:template_y_start + image_height,    template_x_start:template_x_start + image_width,    1] += 0.5 * matching_image

        self.display_view.setImage(background_array)


    def change_session(self):
        template_index = self.template_combobox.currentIndex()
        matching_index = self.matching_combobox.currentIndex()

        print(template_index)
        print(matching_index)
        self.variable_dictionary["template_image"] = self.matrix_list[template_index]
        self.variable_dictionary["matching_image"] = self.matrix_list[matching_index]
        self.draw_images(self.variable_dictionary)


    def set_alignment(self):

        # Get Save Location
        save_directory = self.matching_directory + "/Transformation_Dictionary.npy"
        print("Save Directory", save_directory)

        # Create Transformation Array
        transformation_dictionary = {}
        transformation_dictionary["template"] = self.template_directory
        transformation_dictionary["rotation"] = self.variable_dictionary["rotation"]
        transformation_dictionary["y_shift"] = self.variable_dictionary["y_shift"]
        transformation_dictionary["x_shift"] = self.variable_dictionary["x_shift"]

        np.save(save_directory, transformation_dictionary)

        self.create_bilateral_retinotopic_map()

    def create_bilateral_retinotopic_map(self):

        # Assume Template Is Always Left

        # Load Template Max Projection and Sign
        template_max_projection = self.template_max_projection
        template_max_projection = np.divide(template_max_projection, np.max(template_max_projection))
        template_sign_map = np.load(self.template_directory + "/_Sign_Map_Array.npy")

        # Load Matching Session Sign Map
        matching_sign_map = np.load(self.matching_directory + "/_Sign_Map_Array.npy")

        # Transform Sign Map
        angle = self.variable_dictionary['rotation']
        y_shift = self.variable_dictionary["y_shift"]
        x_shift = self.variable_dictionary["x_shift"]

        matching_sign_map = ndimage.rotate(matching_sign_map, angle, reshape=False)
        matching_sign_map = np.roll(a=matching_sign_map, axis=0, shift=y_shift)
        matching_sign_map = np.roll(a=matching_sign_map, axis=1, shift=x_shift)

        # Get Image Midline
        image_height = np.shape(template_sign_map)[0]
        image_width = np.shape(template_sign_map)[1]
        image_midpoint = int(image_width/2)

        # Create Template To Place Sign Maps On
        template_array = np.zeros((image_height, image_width, 3))
        template_array[:, :, 0] = template_max_projection
        template_array[:, :, 1] = template_max_projection
        template_array[:, :, 2] = template_max_projection

        contour_array = np.zeros((image_height, image_width))

        # Fill In Left Side
        for y in range(image_height):
            for x in range(image_midpoint, image_width):
                visual_sign = template_sign_map[y, x]
                if visual_sign > 0.8:
                    template_array[y, x, 0] = 1
                    contour_array[y, x] = 1
                elif visual_sign < -0.8:
                    template_array[y, x, 2] = 1
                    contour_array[y, x] = 2

        # Fill In Right Side
        for y in range(image_height):
            for x in range(0, image_midpoint):
                visual_sign = matching_sign_map[y, x]
                if visual_sign > 0.8:
                    template_array[y, x, 0] = 1
                    contour_array[y, x] = 1
                elif visual_sign < -0.8:
                    template_array[y, x, 2] = 1
                    contour_array[y, x] = 2

        # Detect Contours
        contours = measure.find_contours(contour_array, level=0.8)

        contour_array = np.zeros((image_height, image_width))
        for contour in contours:
            for point in contour:
                print(point)
                contour_array[int(point[0]), int(point[1])] = 1

        # Save Arrays
        np.save(self.template_directory + "/Combined_Sign_Array.npy", template_array)
        np.save(self.template_directory + "/Combined_Contour_Array.npy", contour_array)

        plt.imshow(template_array)
        plt.savefig(self.template_directory + "/Combined_Sign_Map.png")
        plt.close()

if __name__ == '__main__':

    app = QApplication(sys.argv)


    window = session_matching_window()
    window.show()
    app.exec_()


