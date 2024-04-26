# Understanding Contributor Profiles in Popular Machine Learning Libraries

## Abstract
With the increasing popularity of machine learning (ML), a growing number of developers have been attracted to developing and adopting ML approaches for many domains, such as natural language processing, computer vision, and recommendation systems. To ensure the success of ML software development and maintenance processes, it is crucial to establish a comprehensive understanding of ML contributors who could potentially affect the success of a project. Without such knowledge, there is a risk of inefficient resource allocation and hindered collaboration within the open-source environment. Existing research efforts to study ML contributors focus on the understanding of difficulties and challenges perceived by ML contributors using user surveys. There is a lack of understanding of the characteristics of open-source ML contributors based on their activities observed from the software repositories (e.g., their code changes, raised issues, or participated discussions). In this paper, we aim to understand the characteristics of contributors' activities by identifying contributor profiles in ML libraries. We further study the OSS engagement of ML contributors from three aspects: workload composition, work preferences, and technical importance. By investigating 7,640 contributors from 6 popular ML libraries (i.e., Tensorflow, PyTorch, Keras, MXNet, Theano and ONNX), we identify four ML contributor profiles, namely - Core-Afterhour, Core-Workhour, Peripheral-Afterhour, and Peripheral-Workhour contributors. We find that 1) project experience, code contribution diversity, collaborations, and geological location are significant features of all profiles; 2) contributors in the Core profiles exhibit significantly different OSS engagement compared to Peripheral profiles; 3) the distribution of contributors’ work preferences and workload compositions significantly affect the increase of project popularity; and 4) long-term contributors evolve towards making fewer, constant, balanced and less technical contributions.

## Usage
### Dataset
We have provided our dataset under **/data**. The collected repository data for our subject projects are in separate directories (e.g., data/tensorflow_tensorflow). 

**data/contributor_features.csv** contains the extracted contributor features.

**data/contributor_period_activity.csv** and **data/contributor_activity_sequence.csv** contain the extracted OSS engagement features.

### Data Collection
We have provided our dataset under **/data**. The code under **/data_collection** directory is only for recreating our dataset.

Execute ```pip install -r data_collection/requirements.txt``` to install the required dependencies to execute the data collection scripts. Make sure to execute the data collection scripts following the order below. Modifications are needed to execute each script and more instructions are included in the head comments inside each script.

**data_collection/github_crawler.py** collects the commits/pull requests/issues of our subject projects from GitHub.

**data_collection/project_data_analyzer.py** collects contributor commit time and timezone, and extracts contributor features.

**data_collection/collect_fork_history.py** collects the timestamps of forks from Github.

**data_collection/collect_fork_history.py** collects the timestamps of star ratings from Github.

### Approach
Executing code under **/approach** directory requires a conda environment. Unzip the zipped files under tensorflow_tensorflow and pytorch_pytorch before executing the code in this directory.

Execute ```pip install -r approach/requirements.txt``` to install the required dependencies to execute the approach scripts. Open the following ipynb files in an IDE and click "Run ALL" to execute the scripts.

**approach/profile_clustering.ipynb** reproducing our profile identification. The result is in data/contributor_features.csv column 'profile'.

**approach/workload_composition_work_preference_technical_importance.ipynb** reproducing the workload composition pattern identification, work preference feature extraction, and technical importance calculation. The results are in data/contributor_period_activity.csv and data/contributor_activity_sequence.csv.

### Experiment
The code under **/experiments** directory reproduces our experiments and results for each RQ. Executing code under this directory requires a conda environment. 

Execute ```pip install -r experiment/requirements.txt``` to install the required dependencies to execute the RE experiment scripts. Open the following ipynb files in an IDE and click "Run ALL" to execute the scripts.

### RQ1 Result
The code is in **experiments/rq1.ipynb**.
### RQ2 Result
The code is in **experiments/rq2.ipynb**.
### RQ3 Result
The code is in **experiments/rq3.ipynb**.
### RQ4 Result
The code is in **experiments/rq4.ipynb**.
