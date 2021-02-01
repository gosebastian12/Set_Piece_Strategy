# Visualizations Directory
This directory contains all of the visualizations created during this project. The purposes of these images range from exploring the behavior and predictions of the clustering models trained in this project to creating supplemental visuals for the presentation found in the `reports/` directory.

# Directory Contents and Organization
*(Use drop-down menus to see more information about each directory)*
<details>
<summary>1. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/visualizations/cluster_scatter">cluster_scatter</a>: Directory that contains all of the scatter plots that were used to first see how well the clustering model was able to segment between the different identified clusters in the feature space.</summary>
  <ol>
      <ol>
      	<li><code>cluster_scatter/</code>: </li>
      		<ol>
      			<li><code>events_kmeans_scaled.png</code>: This image shows the clustering results in the feature space of a K-Means model trained on a scaled version of the event-by-event training data set.</li>
      			<li><code>seq_kmeans_scaled.png</code>: This image shows the clustering results in the feature space of a K-Means model trained on a scaled version of the sequence aggregated training data set.</li>
      			<li><code>seq_kmeans_unscaled.png</code>: This image shows the clustering results in the feature space of K-Means model trained on an unscaled version of the sequence aggregated training data set..</li>
      			<li><code>seq_mean_shift_scaled.png</code>: This image shows the clustering results in the feature space of a Mean-Shift model trained on a scaled version of the sequence aggregated training data set.</li>
      		</ol>
      </ol>
  </ol>
</details>

<details>
<summary>2. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/visualizations/clusters_investigation">cluster_scatter</a>: Directory that contains all of the visualizations that help with the in-depth cluster exploration performed after training the clustering models.</summary>
  <ol>
      <ol>
            <li><code>k_means</code>: Sub-directory that contains all of the various figures that help summarize the key characteristics of each identified cluster.</li>
                  <ol>
                        <li><code>Spatial_Dist_0.png</code>: This image shows how the positions of the events in the sequences that belong to cluster 0 are distributed in the 2-dimensional space of the field.</li>
                        <li><code>Spatial_Dist_1.png</code>: This image shows how the positions of the events in the sequences that belong to cluster 1 are distributed in the 2-dimensional space of the field.</li>
                        <li><code>Spatial_Dist_2.png</code>: This image shows how the positions of the events in the sequences that belong to cluster 2 are distributed in the 2-dimensional space of the field.</li>
                        <li><code>Spatial_Dist_3.png</code>: This image shows how the positions of the events in the sequences that belong to cluster 3 are distributed in the 2-dimensional space of the field.</li>
                        <li><code>Spatial_Dist_4.png</code>: This image shows how the positions of the events in the sequences that belong to cluster 4 are distributed in the 2-dimensional space of the field.</li>
                        <li><code>Spatial_Dist_5.png</code>: This image shows how the positions of the events in the sequences that belong to cluster 5 are distributed in the 2-dimensional space of the field.</li>
                        <li><code>event_types_hist_0.png</code>: This image shows the distribution of event types for the events in the sequences that belong to cluster 0.</li>
                        <li><code>event_types_hist_1.png</code>: This image shows the distribution of event types for the events in the sequences that belong to cluster 1.</li>
                        <li><code>event_types_hist_2.png</code>: This image shows the distribution of event types for the events in the sequences that belong to cluster 2.</li>
                        <li><code>event_types_hist_3.png</code>: This image shows the distribution of event types for the events in the sequences that belong to cluster 3.</li>
                        <li><code>event_types_hist_4.png</code>: This image shows the distribution of event types for the events in the sequences that belong to cluster 4.</li>
                        <li><code>event_types_hist_5.png</code>: This image shows the distribution of event types for the events in the sequences that belong to cluster 5.</li>
                        <li><code>event_types_rel_hist_0.png</code>: This image shows the distribution relative to the average count across clusters of event types for the events in the sequences that belong to cluster 0.</li>
                        <li><code>event_types_rel_hist_1.png</code>: This image shows the distribution relative to the average count across clusters of event types for the events in the sequences that belong to cluster 1.</li>
                        <li><code>event_types_rel_hist_2.png</code>: This image shows the distribution relative to the average count across clusters of event types for the events in the sequences that belong to cluster 2.</li>
                        <li><code>event_types_rel_hist_3.png</code>: This image shows the distribution relative to the average count across clusters of event types for the events in the sequences that belong to cluster 3.</li>
                        <li><code>event_types_rel_hist_4.png</code>: This image shows the distribution relative to the average count across clusters of event types for the events in the sequences that belong to cluster 4.</li>
                        <li><code>event_types_rel_hist_5.png</code>: This image shows the distribution relative to the average count across clusters of event types for the events in the sequences that belong to cluster 5.</li>
                        <li><code>subevent_types_hist_0.png</code>: This image shows the distribution of sub-event types for the events in the sequences that belong to cluster 0.</li>
                        <li><code>subevent_types_hist_1.png</code>: This image shows the distribution of sub-event types for the events in the sequences that belong to cluster 1.</li>
                        <li><code>subevent_types_hist_2.png</code>: This image shows the distribution of sub-event types for the events in the sequences that belong to cluster 2.</li>
                        <li><code>subevent_types_hist_3.png</code>: This image shows the distribution of sub-event types for the events in the sequences that belong to cluster 3.</li>
                        <li><code>subevent_types_hist_4.png</code>: This image shows the distribution of sub-event types for the events in the sequences that belong to cluster 4.</li>
                        <li><code>subevent_types_hist_5.png</code>: This image shows the distribution of sub-event types for the events in the sequences that belong to cluster 5.</li>
                        <li><code>subevent_types_rel_hist_0.png</code>: This image shows the distribution relative to the average count across clusters of sub-event types for the events in the sequences that belong to cluster 0.</li>
                        <li><code>subevent_types_rel_hist_1.png</code>: This image shows the distribution relative to the average count across clusters of sub-event types for the events in the sequences that belong to cluster 1.</li>
                        <li><code>subevent_types_rel_hist_2.png</code>: This image shows the distribution relative to the average count across clusters of sub-event types for the events in the sequences that belong to cluster 2.</li>
                        <li><code>subevent_types_rel_hist_3.png</code>: This image shows the distribution relative to the average count across clusters of sub-event types for the events in the sequences that belong to cluster 3.</li>
                        <li><code>subevent_types_rel_hist_4.png</code>: This image shows the distribution relative to the average count across clusters of sub-event types for the events in the sequences that belong to cluster 4.</li>
                        <li><code>subevent_types_rel_hist_5.png</code>: This image shows the distribution relative to the average count across clusters of sub-event types for the events in the sequences that belong to cluster 5.</li>
                  </ol>
      </ol>
  </ol>
</details>


<details>
<summary>3. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/Data_Preprocessing_Pipeline.png">Data_Preprocessing_Pipeline.png</a>: Image that visually displays the sequence of steps that were taken to prepare the raw event-tracking data for clustering modeling.</summary>
</details>

<details>
<summary>4. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/example_sps_1.gif">example_sps_1.png</a>: GIF that shows the first example of a set piece (displayed in root README).</summary>
</details>

<details>
<summary>5. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/example_sps_2.gif">example_sps_2.png</a>: GIF that shows the second example of a set piece (displayed in root README).</summary>
</details>

<details>
<summary>6. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/match_2500097_boxscore.png">match_2500097_boxscore.png</a>: GIF that shows the second example of a set piece (displayed in root README).</summary>
</details>

<details>
<summary>7. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/match_2500097_spp_1.gif">match_2500097_spp_1.gif</a>: GIF of an example set piece sequence that was identified extracted by the source code that compiles all of the set piece sequences in our data set.</summary>
</details>

<details>
<summary>8. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/match_2500097_sps_1.png">match_2500097_spp_1.png</a>: GIF of an example set piece sequence that was identified extracted by the source code that compiles all of the set piece sequences in our data set.</summary>
</details>

<details>
<summary>9. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/match_2500097_spp_2.gif">match_2500097_spp_2.gif</a>: GIF of an example set piece sequence that was identified extracted by the source code that compiles all of the set piece sequences in our data set.</summary>
</details>

<details>
<summary>10. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/match_2500097_sps_2.png">match_2500097_spp_2.png</a>: GIF of an example set piece sequence that was identified extracted by the source code that compiles all of the set piece sequences in our data set.</summary>
</details>
