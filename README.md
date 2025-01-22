# Understanding Contributor Profiles in Popular Machine Learning Libraries

## Abstract
With the increasing popularity of machine learning (ML), many open source software (OSS) contributors are attracted to developing and adopting ML approaches. Comprehensive understanding of ML contributors is crucial for successful ML OSS development and maintenance. Without such knowledge, there is a risk of inefficient resource allocation and hindered collaboration in ML OSS projects. Existing research focuses on understanding the difficulties and challenges perceived by ML contributors through user surveys. There is a lack of understanding of ML contributors based on their activities recorded in the software repositories. In this paper, we aim to understand ML contributors by identifying contributor profiles in ML libraries. We further study contributors’ OSS engagement from four aspects: workload composition, work preferences, technical importance, and ML-specific vs SE contributions. By investigating 11,949 contributors from 8 popular ML libraries (i.e., TensorFlow, PyTorch, scikit-learn, Keras, MXNet, Theano/Aesara, ONNX, and deeplearning4j), we categorize them into four contributor profiles: Core-Afterhour, Core-Workhour, Peripheral-Afterhour, and Peripheral-Workhour. We find that: 1) project experience, authored files, collaborations, pull requests comments received and approval ratio, and geographical location are significant features of all profiles; 2) contributors in Core profiles exhibit significantly different OSS engagement compared to Peripheral profiles; 3) contributors’ work preferences and workload compositions significantly impact project popularity; and 4) long-term contributors evolve towards making fewer, constant, balanced and less technical contributions.

## Usage
### Dataset
We have provided our dataset under **/data**. The collected repository data for our subject projects are in separate directories (e.g., data/tensorflow_tensorflow). Files greater than 25Mb are zipped, make sure to unzip all the files before running any other scripts.
Run command: ```pip install -r data_collection/requirements.txt```
             ```python data_collection/unzip_all.py data```

**data/contributor_features.csv** contains the extracted contributor features.

**data/contributor_period_activity.csv** and **data/contributor_activity_sequence.csv** contain the extracted OSS engagement features.

### Data Collection
We have provided our dataset under **/data**. The code under **/data_collection** directory is only for recreating our dataset.

Run command ```pip install -r data_collection/requirements.txt``` to install the required dependencies to execute the data collection scripts. Make sure to execute the data collection scripts following the order below. Modifications are needed to execute each script and more instructions are included in the head comments inside each script.

**data_collection/github_crawler.py** collects the commits/pull requests/issues of our subject projects from GitHub.

**data_collection/project_data_analyzer.py** collects contributor commit time and timezone, and extracts contributor features.

**data_collection/collect_fork_history.py** collects the timestamps of forks from Github.

**data_collection/collect_fork_history.py** collects the timestamps of star ratings from Github.

### Approach
Executing code under **/approach** directory requires a conda environment. Unzip the zipped files under tensorflow_tensorflow and pytorch_pytorch before executing the code in this directory.

Run command ```pip install -r approach/requirements.txt``` to install the required dependencies to execute the approach scripts. Open the following ipynb files in an IDE and click "Run ALL" to execute the scripts.

**approach/profile_clustering.ipynb** reproducing our profile identification. The result is in data/contributor_features.csv column 'profile'.

**approach/workload_composition_work_preference_technical_importance.ipynb** reproducing the workload composition pattern identification, work preference feature extraction, and technical importance calculation. The results are in data/contributor_period_activity.csv and data/contributor_activity_sequence.csv.

### Experiment
The code under **/experiments** directory reproduces our experiments and results for each RQ. Executing code under this directory requires a conda environment. 

Run command ```pip install -r experiments/requirements.txt``` to install the required dependencies. Open the following ipynb files in an IDE and click "Run ALL" to execute the scripts.

### RQ1 Result
The code for reproducing RQ1 results is in **experiments/rq1.ipynb**.
### RQ2 Result
The code for reproducing RQ2 results is in **experiments/rq2.ipynb**.
### RQ3 Result
The code for reproducing RQ3 results is in **experiments/rq3.ipynb**.
### RQ4 Result
The code for reproducing RQ4 results is in **experiments/rq4.ipynb**.
