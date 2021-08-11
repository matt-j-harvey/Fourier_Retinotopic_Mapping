import numpy as np
import matplotlib.pyplot as plt
import sys
import h5py
import os
import tables
from scipy import signal, ndimage, stats
from sklearn.neighbors import KernelDensity
import cv2
from matplotlib import gridspec, cm



def create_image_from_data(data, image_height, image_width, indicies):
    template = np.zeros([image_height, image_width])
    data = np.nan_to_num(data)
    np.put(template, indicies, data)
    image = np.ndarray.reshape(template, (image_height, image_width))
    image = ndimage.gaussian_filter(image, 2)

    return image


def load_mask(home_directory):

    mask = np.load(home_directory + "/mask.npy")
    mask = np.where(mask>0.1, 1, 0)
    mask = mask.astype(int)
    image_height = np.shape(mask)[0]
    image_width = np.shape(mask)[1]
    flat_mask = np.ndarray.flatten(mask)
    indicies = np.argwhere(flat_mask)
    indicies = np.ndarray.astype(indicies, int)
    indicies = np.ndarray.flatten(indicies)

    print("maks height", image_height)
    print("mask width", image_width)

    return indicies, image_height, image_width


def get_colour(input_value, colour_map, scale_factor):

    input_value = input_value * scale_factor
    cmap = cm.get_cmap(colour_map)
    colour = cmap(input_value)

    return colour


def combine_images_into_video(image_folder, video_name):

    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images.sort()
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'DIVX'), frameSize=(width, height), fps=15)  # 0, 12

    count = 0
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))
        count += 1

    cv2.destroyAllWindows()
    video.release()
    print("Finished - Video Is: " ,video_name)




def create_activity_video(home_directory, stimulus_name):


    stimuli_evoked_responses_directory = home_directory + "/Stimuli_Evoked_Responses"
    data_folder_1 = stimuli_evoked_responses_directory + "/" + stimulus_name

    # Check Output Folder Exists
    output_folder = stimuli_evoked_responses_directory + "/" + stimulus_name
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)


    # Load Mask
    indicies, image_height, image_width = load_mask(home_directory)

    # Load Activity Matrix
    activity_matrix = data_folder_1 + "/" + stimulus_name + "_Activity_Matrix_Average.npy"
    activity_matrix = np.load(activity_matrix, allow_pickle=True)

    # Get Window Dimensions
    number_of_frames     = np.shape(activity_matrix)[0]

    print("activity matrix", np.shape(activity_matrix))

    # Get X Values
    colourmap = cm.get_cmap("jet")

    activity_matrix = np.nan_to_num(activity_matrix)

    image_max = np.percentile(activity_matrix, 99)
    image_min = np.percentile(activity_matrix, 1)

    print(np.shape(activity_matrix))
    print("number of frames", number_of_frames)

    print("max", image_max)
    print("min", image_min)


    # Draw Activity
    for frame in range(number_of_frames):

        # Create Figure
        figure_1 = plt.figure(dpi=200, constrained_layout=True)
        image_axis = figure_1.add_subplot()
        image_axis.set_axis_off()

        # Plot Brain Activity
        image = create_image_from_data(activity_matrix[frame], image_height, image_width, indicies)

        #Get RGBA Colours from Colourmap
        image_axis.imshow(image, vmin=image_min, vmax=image_max, cmap='inferno')

        plt.savefig(output_folder + "/" + str(frame).zfill(6) + ".png", box_inches='tight', pad_inches=0)
        plt.close()


    combine_images_into_video(output_folder, stimuli_evoked_responses_directory + "/" + stimulus_name + ".avi")



