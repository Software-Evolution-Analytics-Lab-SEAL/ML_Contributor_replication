"""
IMPORTANT: If you only want to reproduce the experiment results, you don't need to run this file as 
we have provided our dataset in under /data directory. This file is only for recreating the dataset.

This file collect the star rating history of the subject project repository.

Modify line 18 and line 43 before executing this script.
"""

import requests
import os
import pandas as pd
import sys

url = "https://api.github.com/graphql"

# Modify this variable to your github authentication token. This is an example token.
github_token = 'ghp_1x1x1x1x1x2w2w2w3E3E3E3E4R4R4R4R'

headers = {
    "Authorization": f"Bearer {github_token}",
}

template_query = """
query ($endCursor: String) {
  repository(name: "project_name", owner: "project_owner") {
    stargazers(first: 100, after: $endCursor) {
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        starredAt
        node {
          login
        }
      }
    }
  }
}
"""
# Modify this directory to where you want to store the collected data
basedir = os.path.join(os.path.dirname(__file__),'..','data')

repos = ["tensorflow/tensorflow", "pytorch/ptrorch", "apache/mxnet","keras-team/keras","Theano/Theano", "onnx/onnx", "aesara-devs/aesara", "deeplearning4j/deeplearning4j", "scikit-learn/scikit-learn"]

for repo_name in repos:
    dir = os.path.join(basedir, repo_name.replace('/', '_'))
    if not os.path.exists(dir):
        os.mkdir(dir)
    owner, name = repo_name.split('/')
    print(f'Collecting star rating dates for {repo_name} ...')
    repo_query = template_query.replace('project_name',name).replace('project_owner',owner)

    end_cursor = None
    all_stargazers = []
    counter = 0
    while True:
        response = requests.post(
            url,
            json={"query": repo_query, "variables": {"endCursor": end_cursor}},
            headers=headers,
        )

        if response.status_code == 200:
            data = response.json()
            stargazers_page = data["data"]["repository"]["stargazers"]
            edges = stargazers_page["edges"]
            all_stargazers.extend(edges)

            if stargazers_page["pageInfo"]["hasNextPage"]:
                end_cursor = stargazers_page["pageInfo"]["endCursor"]
                counter += 100
                sys.stdout.write('\r'+f'{counter}/{end_cursor}')
            else:
                break
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break

    all_stargazers = [{'Name':edge["node"]["login"], "starredAt":edge["starredAt"]} for edge in all_stargazers if 'starredAt' in edge]
    stargazer_df = pd.DataFrame.from_dict(all_stargazers, orient='columns')
    stargazer_df.to_csv(os.path.join(dir, 'star_history.csv'))
    print(f'{repo_name} Done!')
