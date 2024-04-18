"""
IMPORTANT: If you only want to reproduce the experiment results, you don't need to run this file as 
we have provided our dataset in under /data directory. This file is only for recreating the dataset.

This file collect the fork history of the subject project repository.

Modify line 18 and line 26 before executing this script.

"""

import github
from github import Github
import os
import pandas as pd
import sys

# Modify this place, add github authentication tokens, e.g., Github("ghp_1x1x1x1x1x2w2w2w3E3E3E3E4R4R4R4R")
github_instances = []

repo_names = ["tensorflow/tensorflow", "pytorch/pytorch", "keras-team/keras", "apache/mxnet", "Theano/Theano", "onnx/onnx"]

gi_counter = 0
gi = github_instances[0]

# Modify this directory to where you want to store the collected data
basedir = os.path.join(os.path.dirname(__file__),'..','data')

for repo_name in repo_names:
    dir = os.path.join(basedir, repo_name.replace('/', '_'))
    if not os.path.exists(dir):
        os.mkdir(dir)
    fork_history = []
    repo = gi.get_repo(repo_name)
    forks = repo.get_forks()
    total_page = forks.totalCount/30+1
    counter = 0
    page_num = 0
    error = 0
    print(f'Collecting fork dates for {repo_name} ...')
    while page_num < total_page:
        try:
            fk = forks.get_page(page_num)
        except github.RateLimitExceededException:
            if gi_counter < len(github_instances)-1:
                    gi_counter += 1
                    repo = github_instances[gi_counter].get_repo(repo_name)
                    forks = repo.get_forks()
                    print(f"Github account changed to {gi_counter}!")
            else:
                gi_counter = 0
                gi = github_instances[gi_counter]
                repo = github_instances[gi_counter].get_repo(repo_name)
                forks = repo.get_forks()
        except github.GithubException as e:
            print(e)
            if e.status == 502:
                print(page_num, "GitHub server Error: 502")
                error.append(page_num)
                page_num += 1
                continue
            else:
                print(e)
                break
                
        for i in range(len(fk)):
            try:
                fork_history.append({'repo':fk[i].full_name, 'time':fk[i].created_at})
            except github.RateLimitExceededException:
                if gi_counter < len(github_instances)-1:
                    gi_counter += 1
                    repo = github_instances[gi_counter].get_repo(repo_name)
                    forks = repo.get_forks()
                    fk = forks.get_page(page_num)
                    print(f"Github account changed to {gi_counter}!")
                else:
                    gi_counter = 0
                    gi = github_instances[gi_counter]
                    repo = github_instances[gi_counter].get_repo(repo_name)
                    forks = repo.get_forks() 
                    fk = forks.get_page(page_num)

        page_num += 1
        sys.stdout.write('\r'+f'{page_num}/{total_page}') 
    fork_df = pd.DataFrame.from_dict(fork_history, orient='columns')
    fork_df.to_csv(os.path.join(dir, 'fork_history.csv'))
    print(f'{repo_name} Done!')