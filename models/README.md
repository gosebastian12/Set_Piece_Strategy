# Models Directory
This directory contains all of the saved trained model files. These files are created in the `2_Clustering_Investigation` notebook and are used throughout for more efficient computation since the models only have to be trained once each.

# Directory Contents and Organization
*(Use drop-down menus to see more information about each directory)*
<details>
<summary>1. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/models/event_by_event">event_by_event</a>: Directory where the models trained on non-sequence aggregated data are stored.</summary>
  <ol>
      <ol>
        <li><code>best_k_means_scaled.sav</code>: Model file that saves the K-Means clustering model trained on a scaled version of the event-by-event engineered set piece sequence data set.</li>
      </ol>
  </ol>
</details>

<details>
<summary>2. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/models/sequence_aggregation">sequence_aggregation</a>: Directory where the models trained on sequence aggregated data are stored.</summary>
  <ol>
    <ol>
      <li><code>best_k_means_agg_scaled.sav</code>: Model file that saves the K-Means cluster model trained on a scaled version of the sequence-aggregated engineered set piece sequence data set.</li>
      <li><code>best_k_means_agg_unscaled.sav</code>: Model file that saves the K-Means cluster model trained on an unscaled version of the sequence-aggregated engineered set piece sequence data set.</li>
      <li><code>mean_shift_agg_scaled.sav</code>: Model file that saves the Mean-Shift cluster model trained on a scaled version of the sequence-aggregated engineered set piece sequence data set.</li>
    </ol>
  </ol>
</details>