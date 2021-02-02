# Set Piece Strategy Analysis w/Data Science
At the end of the day, any sport-related Data Science project should be focused on (either directly or in-directly) the bottom line of competition: to maximize your chances of **winning**. This project strives to do this in the context of soccer by focusing its scope on *set piece sequences*, the set of plays that immediately follow and are directly related to a set piece. 

Set pieces are the events in soccer that resume play after there has been a stoppage because of, i.e., the ball going out of bounds, a foul occurring, etc. They are crucial to winning because it is easy for teams to execute pre-planned strategies since player movement and repositioning is allowed at the teams are getting ready to restart play. Since the team that has possession and is executing the set piece knows what they are about to do while the other team is more in a reactive defensive mindset, many goals are scored off of set pieces that occur near the goal. In fact, 50% of the goals scored in the Men's 2018 World Cup were off of set pieces. That figure was at 25% for the Men's 2014 World Cup (the competition occurs every 4 years). Thus, if one can gain a deeper understanding of set piece strategy using Machine Learning, they could direct their teams towards more successful strategies to score more goals and to defend against those strategies when the other team is executing a set piece to prevent them from scoring goals. The end result would be your team having a better chance of having more goals than your opposition and thus a better chance of winning the match.

![alt-text](https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/example_sps_1.gif)
![alt-text](https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/example_sps_2.gif)


Of course, being that this is a Data Science project, we need a data set to be able to solve this *business problem* of increasing a team's chances of winning by scoring more goals after gaining insight on set pieces. Luckily, there is a free and publicly-available data set that is (almost; more on that later) perfect for this task. This is the ["spatio-temporal" event tracking data set](https://www.nature.com/articles/s41597-019-0247-7#Tab2) that is collected and provided by [Wyscout](https://wyscout.com) (download-able files of this data can be found [here](https://figshare.com/collections/Soccer_match_event_dataset/4415000)). Data is collected on a event-by-event basis for all matches in the 2017 and 2018 seasons of [La Liga](https://en.wikipedia.org/wiki/La_Liga), the [Premiere League](https://en.wikipedia.org/wiki/Premier_League), the [Bundesliga](https://en.wikipedia.org/wiki/Bundesliga), [Seria A](https://en.wikipedia.org/wiki/Serie_A), [Ligue 1](https://en.wikipedia.org/wiki/Ligue_1), [Champions League](https://en.wikipedia.org/wiki/UEFA_Champions_League), and [World Cup](https://en.wikipedia.org/wiki/FIFA_World_Cup) (events can simply be thought of as occurrences in a soccer match such as passes, shots, fouls, etc.) For each event, you are given key information such as the coordinates of the ball on the field at the beginning and at the end of the event, the player that initiated the event (i.e., who made the pass), the team that that player is on, what kind of event it was (i.e., pass, duel, etc...) and when in the match the event occurred, among other descriptive pieces of information.

# TL;DR Conclusion

# Results
This [link](https://docs.google.com/presentation/d/1jqUp0S9pugfP3oyMhbzdbBDgweddCKFhVNKmHKDLbqM/edit#slide=id.gb88cbc0d2a_0_33) takes one to a shared Google Slides file that was used to present this project.

### Data Preprocessing and Feature Engineering
The following image displays all of the steps taken to take the raw event-tracking Wyscout data and prepare it for cluster model training.
![Data Pre-Pipeline](https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/Data_Preprocessing_Pipeline.png)

By computing "cumulative scores", it is meant that code was executed to determine the score of the match at the point at which each event takes place. This was done because Wyscout only tracks the number of goals scored (slightly different than the score because of "own goals") by each team at the end of the two halves and during penalties (if there was a penalty shootout) and because the score differential provides a lot of game context for each event (information that we use later on).  Luckily, this computation simply requires the raw event-tracking data since the "101" and "102" tag values indicate when a goal and an own-goal have been scored. We are very confident in these cumulative score calculations because they are verified along the way with the aforementioned end-of-half scores.

Perhaps the most important part of this project is the next step in the data pre-processing pipeline. The raw data set gives us information on all of the tracked events of a match. However, we are only interested in set pieces and the related events that are part of the sequence of attacking plays immediately following it. This what we refer to as set piece sequences. The set of events that make up these sequences is the data set that we ultimately after to use in model training. To extract these special event sequences took advantage of the fact that the attack following a set piece is over after any of the following things occur:

1. The team playing defense during the set piece has comfortably taken back possession and is now dictating the flow of the match (that is, they have made several passes without the other team touching the ball).
2. The team that initiated the set piece decides to completely reset whatever attack it started with that set piece. This could be seen by them passing the ball all the back to their side of the field (either to their defenders or to their goalie) and repositioning the rest of their players.
3. The defending goalie saves any on-target shot attempt that was made forcing the original attacking team to retreat in preparation for the opposition to begin their possession of the ball.
4. The attacking team is successful in their set piece attack and scores a goal. Thus, possession will now be turned over.
5. The defending team commits a hard foul meaning that a new set piece sequence is about to start.s
6. A player on the attacking team is called offsides meaning that possession will change hands.
7. The attacking team accidentally kicks the ball out of bounds.
8. The half is said to be over by the referees which results in a stop of any play.
9. The defending team is able to make an effective clearance that either results in the defending team regaining possession or the attacking team having to reset its attack.
10. Another set piece sequence begins for some reason.

We also have the benefit of the fact that an event ID of "3" indicates that that specific event is a set piece. Thus, code was written to analyze a large chunk of plays (about 50) that immediately follow of the set pieces in our data set to determine when and how the corresponding set piece sequences ended. Below you will find two examples of set piece sequences that were extracted out from the May 13, 2018 match between Leicester City and Tottenham:
![sps 1 table](https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/match_2500097_sps_1.png)
![sps 1 GIF](https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/match_2500097_sps_1.gif)
![sps 2 table](https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/match_2500097_sps_2.png)
![sps 2 GIF](https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/match_2500097_sps_2.gif)

Evidently, we can visually see each event identified as part of the sequence as well as how the score of the match in the last columns of the displayed tables get updated as the score off the sequence is scored.

With all of the set piece sequences extracted out from the data set, the next steps involve feature engineering both at the event-by-event level as well as the sequence-by-sequence level. For the former, the positional, player, time, and score information is all taken to compute features such as the distance between where the event starts and end, a set of indicator variables that tells which position the initiating player players (goalie, defender, midfield, or forward), and the proportion through which the game has been played (i.e., 0.5 would be halftime and 1 would 90 minutes), to name a few. After doing this, we arrive a set of sequence-wide features by aggregating the information of all of the information into one set of feature vectors. For most features, this is simply done by taking the mean of all of its event values. For others, we take the maximum value or the first value across the event features. Now that we have sequence-wide features, the only remaining step is to ensure that the scale of all of the different features is comparable. We do this by implementing a z-score transformation to the features with a wide scale.

### Clustering and Cluster Characteristics 
Once the raw tracking has undergone all of the steps in the data pre-processing pipeline, it is ready to be used a training set for a clustering model. The two such models that we implemented were K-Means and Mean-Shift. Both methods yielded similar results and so we will focus our discussion on the results of the method that is the most computationally efficient and scalable, K-Means. The below image provides a snapshot of the cluster performance as viewed in the feature space:
![feature space clustering](https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/cluster_scatter/seq_kmeans_scaled.png)

We see an encouraging level of clean segmentation across the clusters in this space. We can further determine how different the identified clusters are from each other by identifying the data instances that are closest to the centroids of each cluster. Doing so yields the following:
![closest-centroid data instances](https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/cluster_scatter/K_Means_Closest_Data_Points.png)

After validating that the model was able to identify clusters that were different from each other, the next step involved determining what each cluster meant since that was key to relating it back to the topic at hand, *winning games in soccer*. We did this generating the following plots for each cluster. Notice above that the optimal number of clusters we identified for the K-Means model was 6. The following is a breakdown of each:

<details>
<summary>1. "Completely Down and Out"</summary>
  <ol>
    <ol>
      <li>Initiating team is losing.</li>
      <li>Closest data point to cluster shows no goalie involvement.</li>
      <li>The initiating team struggles a bit to hold on to possession.</li>
      <li>The attack makes little progress towards the goal.</li>
      <li>The event types is dominated by simple passes.</li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/event_types_rel_hist_0.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/subevent_types_rel_hist_0.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/Spatial_Dist_0.png"></li>
    </ol>
  </ol>
</details>

<details>
<summary>2. "2nd Half Out the Gates"</summary>
  <ol>
    <ol>
      <li>Closest data shows the match is tied.</li>
      <li>Time in match seems to favor being right after half-time.</li>
      <li>Cluster with highest rate of shot attempts.</li>
      <li>Cluster with highest rate of ball going out of bounds.</li>
      <li>High distribution in attacking half.</li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/event_types_rel_hist_1.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/subevent_types_rel_hist_1.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/Spatial_Dist_1.png"></li>
    </ol>
  </ol>
</details>

<details>
<summary>3. "Lethargic Beginning"</summary>
  <ol>
    <ol>
      <li>Closest data point shows that we are early on in the match.</li>
      <li>The match is tied.</li>
      <li>High rate of goalie kicks</li>
      <li>High rate of long passes.</li>
      <li>Despite, long passes not much advancement towards goal. Perhaps goal kicks are not successful in lead towards effective attacks.</li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/event_types_rel_hist_2.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/subevent_types_rel_hist_2.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/Spatial_Dist_2.png"></li>
    </ol>
  </ol>
</details>

<details>
<summary>4. "1st Half Out the Gates"</summary>
  <ol>
    <ol>
      <li>Closest data point shows that we are early on in the match.</li>
      <li>The match is tied.</li>
      <li>Cluster with most involvement of forwards.</li>
      <li>Cluster with best advancement towards goal.</li>
      <li>Main difference with the second cluster is that these events occur early on in the match. </li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/event_types_rel_hist_3.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/subevent_types_rel_hist_3.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/Spatial_Dist_3.png"></li>
    </ol>
  </ol>
</details>

<details>
<summary>5. "Passive and Dominating"</summary>
  <ol>
    <ol>
      <li>Closest data point shows that the initiating team has a big lead.</li>
      <li>Events occur late in the match</li>
      <li>Closest data point to cluster shows no goalie involvement.</li>
      <li>Cluster with Highest Possession Rate.</li>
      <li>Most events occur in own half of field.</li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/event_types_rel_hist_4.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/subevent_types_rel_hist_4.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/Spatial_Dist_4.png"></li>
    </ol>
  </ol>
</details>

<details>
<summary>6. "Coasting Towards Half Time"</summary>
  <ol>
    <ol>
      <li>The match is tied.</li>
      <li>Closest data point shows that we are about to reach halftime for the match.</li>
      <li>We mainly see passes and duels.</li>
      <li>Cluster in which play is very fluid.</li>
      <li>Minimal advancement towards the goal.</li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/event_types_rel_hist_5.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/subevent_types_rel_hist_5.png"></li>
      <li><img src="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/clusters_investigation/kmeans/Spatial_Dist_5.png"></li>
    </ol>
  </ol>
</details>

### Tying it All Back to the Business Problem
Recall that the goal of this project was to gain a deeper understanding of set pieces in order to help a team either maximize their chances of scoring more goals off of set pieces or minimize the chances of the other team scoring set piece goals since that will help a team's chance of winning. The results that we have for this project so far help in making significant progress towards that goal. As presently constructed, one can use the trained models of this project to analyze a specific team's set piece sequences by seeing how their classified clusters are distributed. They can see if they have executed many sequences that are in the "Passive and Dominating" cluster, for example, which of course would be very encouraging. Conversely, one analyze the set piece sequences of an upcoming opponent to quickly see how well they are at scoring off of set pieces; with that information, the coaches of that team can make an informed decision on how much they think they should prepare for such attacks in their team's preparation for match against that opponent.

At the very least, we have Minimally Viable Product (MVP) with this project that shows that it is possible to obtain information about set piece strategy with position tracking data regarding the ball and descriptive event data.

# Repository Contents and Organization
*(Use drop-down menus to see more information about each directory)*
<details>
<summary>1. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/data">data</a>: Stores all of the data that is used during the project.</summary>
  <ol>
      <ol>
        <li><code>raw/</code>: Directory where the data was downloaded from Wyscout (see link above) is stored.</li>
        <li><code>interim/</code>: Directory where the data obtained after pre-processing is stored.</li>
        <li><code>final/</code>: Directory where the data obtained after feature engineering is stored. This data is used to train the clustering models of this project.</li>
      </ol>
  </ol>
</details>

<details>
<summary>2. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/models">models</a>: Stores all of the saved models trained for this project.</summary>
  <ol>
      <ol>
        <li><code>event_by_event/</code>: Directory where the models trained on non-sequence aggregated data are stored.</li>
        <li><code>sequence_aggregation/</code>: Directory where the models trained on sequence aggregated data are stored.</li>
      </ol>
  </ol>
</details>

<details>
<summary>3. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/notebooks">notebooks</a>: Stores all of the Jupyter notebooks that run the code written during this project.</summary>
  <ol>
      <ol>
        <li><code>1_Obtaining_Set_Piece_Data.ipynb</code>: Jupyter notebook that runs all of the source code that puts together the set of piece sequences.</li>
        <li><code>2_Clustering_Investigation.ipynb</code>: Jupyter notebook that takes the set piece sequences and performs feature engineering, sequence aggregation, model training, and model evaluation.</li>
      </ol>
  </ol>
</details>

<details>
<summary>4. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/reports">reports</a>: Stores all of the files created to summarize the findings and conclusions of this project.</summary>
  <ol>
      <ol>
        <li><code>Set_Piece_Sequence_Investigation_Slides.pdf</code>: PDF document that contains all of the slides of a Google Slides document used to present this project.</li>
      </ol>
  </ol>
</details>

<details>
<summary>5. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/src">src</a>: Stores all of the the code written during this project that performs all of the necessary tasks for data loading, data pre-processing, model training, and model evaluation.</summary>
  <ol>
      <ol>
        <li><code>data/</code>: Directory that contains all of the source code dedicated to loading in and manipulating data.</li>
        <li><code>models/</code>: Directory that contains all of the source code dedicated to training and saving clustering models.</li>
        <li><code>test/</code>: Directory that contains all of the source code dedicated to validating function input data.</li>
        <li><code>visualizations/</code>: Directory that contains all of the source code dedicated to creating the visualizations that help perform model evaluation.</li>
      </ol>
  </ol>
</details>

<details>
<summary>6. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/visualizations">visualizations</a>: Stores all of the images that were saved while exploring that predictions of trained models.</summary>
  <ol>
      <ol>
        <li><code>cluster_scatter/</code>: Directory that contains all of the scatter plots that were used to first see how well the clustering model was able to segment between the different identified clusters in the feature space.</li>
        <li><code>clusters_investigation/</code>: Directory that contains all of the visualizations that help with the in-depth cluster exploration performed after training the clustering models.</li>
        <li><code>Data_Preprocessing_Pipeline.png</code>: Image that visually displays the sequence of steps that were taken to prepare the raw event-tracking data for clustering modeling.</li>
        <li><code>example_sps_1.gif</code>: GIF that shows the first example of a set piece (displayed above).</li>
        <li><code>example_sps_2.gif</code>: GIF that shows the second example of a set piece (displayed above).</li>
        <li><code>match_2500097_boxscore.png</code>: Image that displays the box score of the match for which we are displaying set piece sequence examples.</li>
        <li><code>match_2500097_spp_1.gif</code>: GIF of an example set piece sequence that was identified extracted by the source code that compiles all of the set piece sequences in our data set.</li>
        <li><code>example_sps_1.png</code>: Image that displays the extracted out sequences of events that comprise the set piece sequence displayed in the corresponding GIF.</li>
        <li><code>match_2500097_spp_2.gif</code>: Another GIF of an example set piece sequence that was identified extracted by the source code that compiles all of the set piece sequences in our data set.</li>
        <li><code>match_2500097_spp_2.png</code>: Image that displays the extracted out sequences of events that comprise the set piece sequence displayed in the corresponding GIF.</li>
      </ol>
  </ol>
</details>

<details>
<summary>7. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/.gitignore">.gitignore</a>: Text file that specifies all of the files and directories that were not written to this repository for reasons such as security and memory/size limitations.</summary>
</details>

<details>
<summary>8. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/README.md">README.md</a>: Markdown file that contains all of the information used to generate this summary view.</summary>
</details>

<details>
<summary>9. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/requirements.txt">README.md</a>: Text file that contains all of the Python packages and their versions that are need to successfully run the code in this project.</summary>
</details>

<details>
<summary>10. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/setup.py">setup.py</a>: Python script that allows the user to create a new local module that is comprised of all of the code found in `src/` directory.</summary>
</details>

# Future Improvements