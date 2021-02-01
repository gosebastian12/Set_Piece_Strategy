# Notebooks Directory
This directory 

# Directory Contents and Organization
*(Use drop-down menus to see more information about each directory)*
<details>
<summary>1. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/notebooks/1_Obtaining_Set_Piece_Data.ipynb">1_Obtaining_Set_Piece_Data.ipynb</a>: The intended use of this notebook is to provide a space where the user can run all of the code written in the `common_tasks`, `data_loader`, `set_piece_extractor`, and `feature_engineering` scripts that are found in the `src.data` sub-module. The end result should be a collection of, what we call in this project, set piece sequences which are a collection of all of the events that corresponding to the attacking effort started by a particular set piece event. This collection of events is saved in the `compiled_sequences` sub-directory found in the `data/interim` directory.</summary>
</details>

<details>
<summary>2. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/notebooks/2_Clustering_Investigation.ipynb">2_Clustering_Investigation.ipynb</a>: The intended use of this notebook is to provide a space where the user can run all of the initial clustering model efforts with the set piece sequence data. The goal of this modeling effort is to arrive at a set of clustering predictions that can differentiate between different set piece strategies that teams employ throughout matches. The decision of which strategy to use can be dependent on game situation (i.e., score, time, etc...), player personnel, and league characteristics, opposition, and coaching philosophy to name a few possible factors. The final goal is to arrive a set of explanation for what each cluster is characterized by to inspire future exploration.</summary>
</details>
