# Understanding Contributor Profiles in Popular Machine Learning Libraries

## Abstract
With the increasing popularity of machine learning (ML), a growing number of developers have been attracted to developing and adopting ML approaches for many domains, such as natural language processing, computer vision, and recommendation systems. To ensure the success of ML software development and maintenance processes, it is crucial to establish a comprehensive understanding of ML contributors who could potentially affect the success of a project. Without such knowledge, there is a risk of inefficient resource allocation and hindered collaboration within the open-source environment. Existing research efforts to study ML contributors focus on the understanding of difficulties and challenges perceived by ML contributors using user surveys. There is a lack of understanding of the characteristics of open-source ML contributors based on their activities observed from the software repositories (e.g., their code changes, raised issues, or participated discussions). In this paper, we aim to understand the characteristics of contributors' activities by identifying contributor profiles in ML libraries. We further study the OSS engagement of ML contributors from three aspects: workload composition, work preferences, and technical importance. By investigating 7,640 contributors from 6 popular ML libraries (i.e., Tensorflow, PyTorch, Keras, MXNet, Theano and ONNX), we identify four ML contributor profiles, namely - Core-Afterhour, Core-Workhour, Peripheral-Afterhour, and Peripheral-Workhour contributors. We find that 1) project experience, code contribution diversity, collaborations, and geological location are significant features of all profiles; 2) contributors in the Core profiles exhibit significantly different OSS engagement compared to Peripheral profiles; 3) the distribution of contributors’ work preferences and workload compositions significantly affect the increase of project popularity; and 4) long-term contributors evolve towards making fewer, constant, balanced and less technical contributions.

## Setup
## Usage
### Data Collection
We have provided the collected data under /data. The code under /data_collect directory is only for recreating our dataset.
data_collect/github_crawler.py collects the commits/pull requests/issues subject projects from GitHub
data_collect/project_data_analyzer.py collects contributor timezone and commit, and extracts contributor features.
data_collect/collect_fork_history.py collects the timestamps of forks from Github.
data_collect/collect_fork_history.py collects the timestamps of star ratings from Github.

### Approach
Executing code under /approach directory requires a conda environment. Make sure to unzip the zipped data under tensorflow_tensorflow and pytorch_pytorch before executing the code in this directory.
approach/profile_clustering.ipynb reproducing our profile identification. The result is in data/contributor_features.csv column 'profile.
approach/workload_composition_work_preference_technical_importance.ipynb reproducing the workload composition pattern identification, work preference feature extraction, and technical importance calculation. The results are in data/contributor_period_activity.csv and data/contributor_activity_sequence.csv.

### Experiment
The code under /experiments directory reproduces our experiments and results for each RQ. Executing code under this directory requires a conda environment. 
### RQ1 Result
The code is in experiments/rq1.ipynb.
### RQ2 Result
The code is in experiments/rq2.ipynb.
### RQ3 Result
The code is in experiments/rq3.ipynb.
### RQ4 Result
The code is in experiments/rq4.ipynb.
