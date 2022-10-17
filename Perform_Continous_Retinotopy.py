import Check_Photodiode_Trace
import Extract_Trial_Aligned_Activity_Continous_Retinotopy
import Create_Sweep_Aligned_Movie
import Continous_Retinotopy_Fourier_Analysis

base_directory = r"/media/matthew/External_Harddrive_2/Widefield_Data_New_Pipeline/Retinotopy/NXAK22.1A/2021_09_01_Continuous_Retinotopic_Mapping_Left"

# Get Stimuli Onsets
Check_Photodiode_Trace.check_photodiode_times(base_directory)

# Extract Trial Aligned Activity
Extract_Trial_Aligned_Activity_Continous_Retinotopy.extract_trial_aligned_activity(base_directory)

# Create Trial Averaged Movie
Create_Sweep_Aligned_Movie.create_activity_video(base_directory, "Horizontal_Sweep")
Create_Sweep_Aligned_Movie.create_activity_video(base_directory, "Vertical_Sweep")

# Perform Fourrier Analysis
Continous_Retinotopy_Fourier_Analysis.perform_fourier_analysis(base_directory)