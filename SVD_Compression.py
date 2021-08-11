from sklearn.decomposition import IncrementalPCA
import numpy as np
import h5py
import os
import joblib
import datetime



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





def perform_svd_compression(file, output_stem, save_directory, number_of_components=1000, chunk_size=5000):

    # Load Data
    data_container = h5py.File(file, 'r')
    data = data_container["Data"]

    # Get Data Structure
    number_of_pixels = np.shape(data)[0]
    number_of_timepoints = np.shape(data)[1]
    number_of_chunks, chunk_sizes, chunk_starts, chunk_stops = get_chunk_structure(chunk_size, number_of_timepoints)

    # Create Model
    model = IncrementalPCA(n_components=number_of_components)

    # Fit Model
    for chunk_index in range(1):
        print("Fitting Chunk ", str(chunk_index).zfill(2), " of ", number_of_chunks, "at ", datetime.datetime.now())
        chunk_start = chunk_starts[chunk_index]
        chunk_stop = chunk_stops[chunk_index]
        chunk_data = data[:, chunk_start:chunk_stop]
        chunk_data = np.ndarray.transpose(chunk_data)
        model.partial_fit(chunk_data)

    # Transform Data
    transformed_data = np.zeros((number_of_timepoints, number_of_components))
    for chunk_index in range(1):
        print("Transforming Chunk ", str(chunk_index).zfill(2), " of ", number_of_chunks, "at ", datetime.datetime.now())
        chunk_start = chunk_starts[chunk_index]
        chunk_stop = chunk_stops[chunk_index]
        chunk_data = data[:, chunk_start:chunk_stop]
        chunk_data = np.ndarray.transpose(chunk_data)
        transformed_chunk = model.transform(chunk_data)
        transformed_data[chunk_start:chunk_stop] = transformed_chunk

    # Save Outputs
    components = model.components_
    singular_values = model.singular_values_
    mean = model.mean_

    joblib.dump(model, output_stem + "SVD_Model")
    np.save(output_stem + "_SVD_Components.npy", components)
    np.save(output_stem + "_SVD_Singular_Values.npy", singular_values)
    np.save(output_stem + "_SVD_Transformed_Data.npy", transformed_data)
    np.save(output_stem + "_SVD_Means.npy", mean)


base_directory = r"/media/matthew/Seagate Expansion Drive/Transition_Analysis/NXAK7.1B/2021_03_31_Transition_Imaging/"
file = base_directory + "NXAK7.1B_20210331-144844_Blue_Data.hdf5"
output_stem = base_directory + "NXAK7.1B_20210331-144844_Blue_Data"
save_directory = "Blue_Data_SVD"
perform_svd_compression(file, output_stem, save_directory)