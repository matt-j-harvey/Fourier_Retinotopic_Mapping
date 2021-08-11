import numpy as np
import matplotlib.pyplot as plt
import h5py
import tables
import os


def load_arrays(video_file):
    print("Extracting Camera Data")
    table = tables.open_file(video_file, mode='r')
    blue_array = table.root.blue
    violet_array = table.root.violet

    return blue_array, violet_array, table


def check_led_colours(blue_array, violet_array):
    figure_1 = plt.figure()
    axes_1 = figure_1.subplots(1, 2)

    axes_1[0].set_title("Blue?")
    axes_1[0].imshow(blue_array[0])

    axes_1[1].set_title("Violet?")
    axes_1[1].imshow(violet_array[0])
    plt.show()


def get_chunk_structure(chunk_size, array_size):
    number_of_chunks = int(np.ceil(array_size / chunk_size))
    remainder = array_size % chunk_size

    # Get Chunk Sizes
    chunk_sizes = []
    if remainder == 0:
        for x in range(number_of_chunks):
            chunk_sizes.append(chunk_size)

    else:
        for x in range(number_of_chunks - 1):
            chunk_sizes.append(chunk_size)
        chunk_sizes.append(remainder)

    # Get Chunk Starts
    chunk_starts = []
    chunk_start = 0
    for chunk_index in range(number_of_chunks):
        chunk_starts.append(chunk_size * chunk_index)

    # Get Chunk Stops
    chunk_stops = []
    chunk_stop = 0
    for chunk_index in range(number_of_chunks):
        chunk_stop += chunk_sizes[chunk_index]
        chunk_stops.append(chunk_stop)

    return number_of_chunks, chunk_sizes, chunk_starts, chunk_stops


def restructure_data(array, output_directory):
    print("Restructuring data")

    number_of_images = np.shape(array)[0]  # Calculate The Number of Images In The Raw Video File
    number_of_pixels = np.shape(array)[1] * np.shape(array)[2]  # Calculate The Number of Pixels In The Raw Video File

    preferred_chunk_size = 5000
    number_of_chunks, chunk_sizes, chunk_starts, chunk_stops = get_chunk_structure(preferred_chunk_size,
                                                                                   number_of_images)

    with h5py.File(output_directory, "w") as f:
        dataset = f.create_dataset("Data", (number_of_pixels, number_of_images), dtype=np.uint16, chunks=True, compression="gzip")

        for chunk_index in range(number_of_chunks):
            chunk_size = chunk_sizes[chunk_index]
            chunk_start = chunk_starts[chunk_index]
            chunk_stop = chunk_stops[chunk_index]

            data = array[chunk_start:chunk_stop]
            data = np.moveaxis(data, [0, 1, 2], [2, 0, 1])

            reshaped_data = np.ndarray.reshape(data, (number_of_pixels, chunk_size))
            dataset[:, chunk_start:chunk_stop] = reshaped_data


def compress_files(filename):

    base_directory, file_id = get_base_directory(filename)

    file_location = filename
    blue_file = base_directory + "\\" + file_id + "Blue_Data.hdf5"
    violet_file = base_directory + "\\" + file_id + "Violet_Data.hdf5"

    # Extract Array Data
    blue_array, violet_array, table = load_arrays(file_location)

    # Check LED Colours
    #check_led_colours(blue_array, violet_array)

    # Restructure Data
    restructure_data(blue_array, blue_file)
    restructure_data(violet_array, violet_file)



def load_compressed_data(file_location):
    processed_data_file = h5py.File(file_location, 'r')
    processed_data = processed_data_file["Data"]

    return processed_data

def compare_data(raw_data, compressed_data, preffered_chunk_size=5000):

    number_of_frames = np.shape(raw_data)[0]
    number_of_pixels = np.shape(compressed_data)[0]

    number_of_chunks, chunk_sizes, chunk_starts, chunk_stops = get_chunk_structure(preffered_chunk_size, number_of_frames)

    equivalent = True
    for chunk_index in range(number_of_chunks):

        chunk_size = chunk_sizes[chunk_index]
        chunk_start = chunk_starts[chunk_index]
        chunk_stop  = chunk_stops[chunk_index]

        raw_chunk   = raw_data[chunk_start:chunk_stop]
        compressed_chunk = compressed_data[:, chunk_start:chunk_stop]

        raw_chunk = np.ndarray.reshape(raw_chunk, (chunk_size, number_of_pixels))
        raw_chunk = np.swapaxes(raw_chunk, axis1=0, axis2=1)

        comparison = raw_chunk == compressed_chunk
        are_equal = comparison.all()

        if are_equal != True:
            equivalent = False


    return equivalent



def run_file_checking(filename):

    base_directory, file_id = get_base_directory(filename)

    raw_file = filename
    blue_file = base_directory + "\\" + file_id + "Blue_Data.hdf5"
    violet_file = base_directory + "\\" + file_id + "Violet_Data.hdf5"

    #Load Data
    raw_blue_data, raw_violet_data, table = load_arrays(raw_file)
    compressed_blue_data = load_compressed_data(blue_file)
    compressed_violet_data = load_compressed_data(violet_file)

    #Compare Files
    blue_check   = compare_data(raw_blue_data,   compressed_blue_data)
    violet_check = compare_data(raw_violet_data, compressed_violet_data)

    if blue_check == True and violet_check == True:
        print("The file contents are exactly the same :)")

    else:
        print("Not the same :(")


def get_base_directory(full_filepath):

    split_string = full_filepath.split("/")
    base_directory = split_string[0]

    for x in range(1, len(split_string)-1):
        base_directory = base_directory + "/" + split_string[x]

    file_id = split_string[-1]
    file_id = file_id.strip("widefield.h5")

    return base_directory, file_id



def check_all_data(directory_list):

    for directory in directory_list:
        print(directory)
        compress_files(directory)
        print("Files Compressed")
        run_file_checking(directory)



