# Set Piece Strategy Analysis w/Data Science
At the end of the day, any sport-related Data Science project should be focused on (either directly or in-directly) the bottom line of competition: to maximize your chances of **winning**. This project strives to do this in the context of soccer by focusing its scope on *set piece sequences*, the set of plays that immediately follow and are directly related to a set piece. 

Set pieces are the events in soccer that resume play after there has been a stoppage because of, i.e., the ball going out of bounds, a foul occuring, etc. They are crucial to winning because it is easy for teams to execute pre-planned strategies since player movement and repositioning is allowed at the teams are getting ready to restart play. Since the team that has possession and is excuting the set piece knows what they are about to do while the other team is more in a reactive defensive mindset, many goals are scored off of set pieces that occur near the goal. In fact, 50% of the goals scored in the Men's 2018 World Cup were off of set pieces. That figure was at 25% for the Men's 2014 World Cup (the competition occurs every 4 years). Thus, if one can gain a deeper understanding of set piece strategy using Machine Learning, they could direct their teams towards more successful strategies to score more goals and to defend against those strategies when the other team is executing a set piece to prevent them from scoring goals. The end result would be your team having a better chance of having more goals than your opposition and thus a better chance of winning the match.

![alt-text](https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/example_sps_1.gif)
![alt-text](https://github.com/gosebastian12/Set_Piece_Strategy/blob/main/visualizations/example_sps_2.gif)


Of course, being that this is a Data Science project, we need a data set to be able to solve this *business problem* of increasing a team's chances of winning by scoring more goals after gaining insight on set pieces. Luckily, there is a free and publicly-available data set that is (almost; more on that later) perfect for this task. This is the ["spatio-temporal" event tracking data set](https://www.nature.com/articles/s41597-019-0247-7#Tab2) that is collected and provided by [Wyscout](https://wyscout.com) (downloadable files of this data can be found [here](https://figshare.com/collections/Soccer_match_event_dataset/4415000)). Data is collected on a event-by-event basis for all matches in the 2017 and 2018 seasons of [La Liga](https://en.wikipedia.org/wiki/La_Liga), the [Premiere League](https://en.wikipedia.org/wiki/Premier_League), the [Bundesliga](https://en.wikipedia.org/wiki/Bundesliga), [Seria A](https://en.wikipedia.org/wiki/Serie_A), [Ligue 1](https://en.wikipedia.org/wiki/Ligue_1), [Champions League](https://en.wikipedia.org/wiki/UEFA_Champions_League), and [World Cup](https://en.wikipedia.org/wiki/FIFA_World_Cup) (events can simply be thought of as occurances in a soccer match such as passes, shots, fouls, etc.) For each event, you are given key information such as the coordinates of the ball on the field at the beginning and at the end of the event, the player that initiated the event (i.e., who made the pass), the team that that player is on, what kind of event it was (i.e., pass, duel, etc...) and when in the match the event occured, among other descriptive pieces of information.

# TL;DR Conclusion

# Results
This [link](https://docs.google.com/presentation/d/1jqUp0S9pugfP3oyMhbzdbBDgweddCKFhVNKmHKDLbqM/edit#slide=id.gb88cbc0d2a_0_33) takes one to a shared Google Slides file that was used to present this project.

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
<summary>5. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/src">src</a>: Stores all of the the code written during this project that performs all of the neccessary tasks for data loading, data pre-processing, model training, and model evaluation.</summary>
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
        <li><code>match_2500097_boxscore.png: Image that displays the box score of the match for which we are displaying set piece sequence examples..</li>
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