import Check_Photodiode_Trace
import File_Compression
import Template_Masking
import Heamocorrection_Continous_retinotopy
import Extract_Trial_Aligned_Activity_Continous_Retinotopy
import Create_Sweep_Aligned_Movie
import Continous_Retinotopy_Fourier_Analysis

base_directory = r"/media/matthew/Seagate Expansion Drive2/Widefield_Imaging/Transition_Analysis/NXAK14.1A/NXAK14.1A_Cont_Retinotopy_Left/Continous_Retinotopic_Mapping/"
#base_directory = r"/media/matthew/Seagate Expansion Drive2/Widefield_Imaging/Transition_Analysis/NXAK14.1A/NXAK14.1a_Cont_Retinotopy_Right/Continous_Retinotopic_Mapping_Right/"

# Compress Files
#File_Compression.check_all_data([base_directory])

# Perform Template Masking
#Template_Masking.perform_template_masking(base_directory)

# Get Stimuli Onsets
Check_Photodiode_Trace.check_photodiode_times(base_directory)

# Perform Heamocorrection
#Heamocorrection_Continous_retinotopy.perform_heamocorrection(base_directory)

# Extract Trial Aligned Activity
Extract_Trial_Aligned_Activity_Continous_Retinotopy.extract_trial_aligned_activity(base_directory)

# Create Trial Averaged Movie
Create_Sweep_Aligned_Movie.create_activity_video(base_directory, "Horizontal_Sweep")
Create_Sweep_Aligned_Movie.create_activity_video(base_directory, "Vertical_Sweep")

# Perform Fourrier Analysis
Continous_Retinotopy_Fourier_Analysis.perform_fourier_analysis(base_directory)