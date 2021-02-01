# Data Directory
This directory stores all of the data that is used during the project. This ranges from data that was downloaded from third party sources as well as data that was created through various prep-processing and feature engineering tasks. Where along in this data pipeline the information in a file is is determined by the sub-directory it is stored in with the options being `raw`, `interim`, and `final`. See below for more information on each sub-directory and each of their contents.

# Directory Contents and Organization
*(Use drop-down menus to see more information about each directory)*
<details>
<summary>1. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/data/raw">raw</a>: Directory where the data was downloaded from Wyscout (see link in root README) is stored.</summary>
  <ol>
      <ol>
      	<li><code>events/</code>: Directory where the files that contain the raw event-tracking information is stored.</li>
      		<ol>
      			<li><code>events.zip</code>: A ZIP file that contains another directory that is home to a compressed version of all of the files listed below.</li>
      			<li><code>events_World_Cup.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the event-tracking data we have for matches from the 2018 Men's World Cup.</li>
      			<li><code>events_Spain.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the event-tracking data we have for matches from the 2017 and 2018 seasons of La Liga</li>
      			<li><code>events_Italy.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the event-tracking data we have for matches from the 2017 and 2018 seasons of Serie A.</li>
      			<li><code>events_Germany.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the event-tracking data we have for matches from the 2017 and 2018 seasons of the Bundesliga.</li>
      			<li><code>events_France.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the event-tracking data we have for matches from the 2017 and 2018 seasons of Ligue 1.</li>
      			<li><code>events_European_Championship.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the event-tracking data we have for matches from the 2017 and 2018 seasons of the Champions League.</li>
      			<li><code>events_England.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the event-tracking data we have for matches from the 2017 and 2018 seasons of the Premiere League.</li>
      		</ol>
        <li><code>matches/</code>: Directory where.</li>
        	<ol>
        		<li><code>matches.zip</code>: A ZIP file that contains another directory that is home to a compressed version of all of the files listed below.</li>
      			<li><code>matches_World_Cup.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the descriptive information we have for matches from the 2018 Men's World Cup.</li>
      			<li><code>matches_Spain.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the descriptive information we have for matches from the 2017 and 2018 seasons of La Liga</li>
      			<li><code>matches_Italy.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the descriptive information we have for matches from the 2017 and 2018 seasons of Serie A.</li>
      			<li><code>matches_Germany.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the descriptive information we have for matches from the 2017 and 2018 seasons of the Bundesliga.</li>
      			<li><code>matches_France.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the descriptive information we have for matches from the 2017 and 2018 seasons of Ligue 1.</li>
      			<li><code>matches_European_Championship.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the descriptive information we have for matches from the 2017 and 2018 seasons of the Champions League.</li>
      			<li><code>matches_England.json</code>: (**File not shown in repo. for memory concerns**) This JSON file contains the descriptive information we have for matches from the 2017 and 2018 seasons of the Premiere League.</li>
      		</ol>
      	<li><code>competitions.json</code>: This JSON file contains the descriptive information we have about all of the Leagues and Competitions we have data for, namely La Liga, Serie A, Ligue 1, Bundesliga, Premiere League, World Cup, and Champions League.</li>
      	<li><code>eventid2name.csv</code>: This CSV file serves as a map between the various Event and Sub-Event IDs given in the event-tracking data set and the event and sub-event types they correspond to. I.e., an event ID value of 8 means "Pass" and a sub-event ID value of 82 means "Head Pass".</li>
      	<li><code>players.json</code>: This JSON file contains the descriptive information we have about all of the players that participated in the matches that we have event-tracking data for.</li>
      	<li><code>tags2name.csv</code>: This CSV file serves as a map between the various tags given in the event-tracking data set and their text labels. I.e., a tag value of 101 corresponds to the label "Goal".</li>
      	<li><code>teams.json</code>: This JSON file contains the descriptive information we have about all of the teams that participated in the matches that we have event-tracking data for.</li>
      </ol>
  </ol>
</details>

<details>
<summary>2. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/data/interim">interim</a>: Directory where the data obtained after pre-processing is stored.</summary>
  <ol>
      <ol>
        <li><code>raw/</code>: Directory where the data was downloaded from Wyscout (see link above) is stored.</li>
      </ol>
  </ol>
</details>

<details>
<summary>1. <a href="https://github.com/gosebastian12/Set_Piece_Strategy/tree/main/data/final">final</a>: Directory where the data obtained after feature engineering is stored. This data is used to train the clustering models of this project.</summary>
  <ol>
      <ol>
        <li><code>raw/</code>: Directory where the data was downloaded from Wyscout (see link above) is stored.</li>
      </ol>
  </ol>
</details>