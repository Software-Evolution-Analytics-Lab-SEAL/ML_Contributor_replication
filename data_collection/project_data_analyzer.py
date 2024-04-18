"""
IMPORTANT: If you only want to reproduce the experiment results, you don't need to run this file as 
we have provided our dataset in under /data directory. This file is only for recreating the dataset.

This file clone the github repository of the six subject projects to current directory/git_repos.

Modify the line 720: add github authentication tokens, e.g., Github("ghp_1x1x1x1x1x2w2w2w3E3E3E3E4R4R4R4R") 
to collect the contributors' number of Github follower and check the user type (user/bot/organization account) from github.

Modify the basedir in line 723 to the directory (i.e., replication/data) of project data collected from Github with github_crawler.py 
"""
import datetime
import os
import csv
import sys
import pandas as pd
import github
import requests
from github import Github
import numpy as np
from statistics import mode
import re
import time
import pydriller
import git

# Handle string to datetime object
def date_handler(date_str):
    return datetime.datetime.fromisoformat(date_str.split()[0])
def date_time_handler(date_time_str):
    return datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')


def get_bots(dir,developers, known_bots):
    """
    Check the github account type with a github login, it can be either: user, bot, or organization account
    The results are stored in "users.txt", "bots.txt", and "organizations.txt" in the given directory

    param dir -> string: the directory to store the resulting files
    param developers -> list<string>: a list of github logins
    param known_bots -> list<string>: a list of github logins who already are known as bots from manual investigation
    """
    print(f'Using Github to check {dir.split("/")[-1]} user account type: ')
    users,bots,organizations = [],[],[]
    gi_counter = 0  # github instance counter
    counter, num_developers = 0,len(developers)
    try:
        gi = github_instances[gi_counter]
        gi_counter += 1  # Point to next available github account for current repo
    except github.UnknownObjectException:  # 404 error, repo not found
        print(f"404 {repo_name} not found")

    except github.RateLimitExceededException:  # need to change github account
        if gi_counter < len(github_instances)-1:
            gi = github_instances[gi_counter+1]
            gi_counter += 2  # Point to next available github account for current repo, because gi_counter+1 is used now
        else:
            gi_counter = 0
            while(True):
                #result[repo_name] = "Not Finished"
                #print(f"{repo_name} not finished")
                #continue
                try:
                    gi = github_instances[gi_counter+1]
                    gi_counter += 1  # Point to next available github account for current repo
                    break
                except TimeoutError:
                    print(f"Time Out Error sleep for {delay} seconds")
                    time.sleep(delay)
                except github.GithubException:
                    print(f"Github error, delay {delay} seconds")
                    time.sleep(delay)
                except github.RateLimitExceededException:  # github instance still not available
                    print(f"{repo_name} crawler sleeps {delay} seconds, wait for available github instance")
                    time.sleep(delay)
                except requests.exceptions.ReadTimeout:  # HTTP read time out
                    print(f"Http Time Out delay {delay} seconds")
                    time.sleep(delay)
                except requests.exceptions.ConnectionError:
                    print(f"Connect Error delay {delay} seconds")
                    time.sleep(delay)
    
    while counter < num_developers:
        try:
            d = developers[counter]
            user = gi.get_user(d)
            if d in known_bots:
                bots.append(d)
            elif user.type == "Bot":
                bots.append(d)
            elif user.type == "Organization":
                organizations.append(d)
            elif user.type == "User":
                users.append(f"{d} {user.followers}")
            else:
                print(d,user.type)
            counter += 1
        except github.UnknownObjectException:
            print("Unknown", d)
            counter += 1
        except github.RateLimitExceededException:  # change Github account
            if gi_counter < len(github_instances):
                gi = github_instances[gi_counter]
                gi_counter += 1
            else:  # all Github accounts are used
                gi_counter = 0
                while (True):
                    try:
                        gi = github_instances[gi_counter]
                        gi_counter += 1
                        break
                    except TimeoutError:
                        print(f"Time Out Error sleep for {delay} seconds")
                        time.sleep(delay)
                    except github.GithubException:
                        print(f"Github error, delay {delay} seconds")
                        time.sleep(delay)
                    except github.RateLimitExceededException:  # github instance still not available
                        print(f"{repo_name} crawler sleeps {delay} seconds, wait for available github instance")
                        time.sleep(delay)
                    except requests.exceptions.ReadTimeout:  # HTTP read time out
                        print(f"Http Time Out delay {delay} seconds")
                        time.sleep(delay)
                    except requests.exceptions.ConnectionError:
                        print(f"Connect Error delay {delay} seconds")
                        time.sleep(delay)
        sys.stdout.write('\r' + f"{counter}/{num_developers}")
        
        path = os.path.join(dir,f"users.txt")
        with open(path,"w") as f:
            f.write('\n'.join(users))
        f.close()
        path = os.path.join(dir,f"bots.txt")
        with open(path,"w") as f:
            f.write('\n'.join(bots))
        f.close()    
        path = os.path.join(dir,f"organizations.txt")
        with open(path,"w") as f:
            f.write('\n'.join(organizations))
        f.close()


def read_txt_lines(fildir):
    lines = []
    with open(fildir,"r") as f:
        for line in f:
            line = line.strip()
            lines.append(line)
    f.close()
    return lines

def get_developers(dir,commit_data):
    user_logins_file = os.path.join(dir,'users.txt')
    if not os.path.exists(user_logins_file):
        developers = []

        for idx in commit_data:
            developers.append(commit_data[idx]["Author"])
            
        developers = list(set(developers))
        get_bots(dir,developers,known_bots)
        
    developers = read_txt_lines(user_logins_file)
    developerDB = {}
    for item in developers:
        d,followers = item.split()
        initialize_developer_profile(developerDB,d)
        developerDB[d]["Followers"] = int(followers)
    print(f"Number of developers: {len(developerDB.keys())}")
    return list(developerDB.keys()),developerDB


def initialize_developer_profile(developerDB,d):
    developerDB[d] = {}
    developerDB[d]["Join Date"] = None
    developerDB[d]["Last Active"] = None
    developerDB[d]["Duration"] = 0
    developerDB[d]["First Activity"] = ""
    developerDB[d]["Last Activity"] = ""
    developerDB[d]["Total Commits"] = 0
    developerDB[d]["Authored files"] = 0
    developerDB[d]["Total Issues"] = 0
    developerDB[d]["Total Pull Requests"] = 0
    developerDB[d]["Buggy Commits"] = 0
    developerDB[d]["Code Commits"] = 0
    developerDB[d]["Other Commits"] = 0
    developerDB[d]["Deletions"] = 0
    developerDB[d]["Additions"] = 0
    developerDB[d]["Followers"] = 0
    developerDB[d]["Collaborations"] = []
    #### New Params ###
    #developerDB[d]["Commit Comments"] = 0
    #developerDB[d]["Issue Comments"] = 0
    #developerDB[d]["Issue Events"] = 0
    #developerDB[d]["Issue Assigned"] = 0
    developerDB[d]["Issue Participated"] = 0
    developerDB[d]["Issue Solved"] = 0
    #developerDB[d]["PR Comments"] = 0
    #developerDB[d]["PR Events"] = 0
    developerDB[d]["PR Merged"] = 0
    developerDB[d]["PR Merged unknown pytorch"] = 0 # this is just used for pytorch to remove noise in pytorch pr data
    #developerDB[d]["PR Assigned"] = 0
    developerDB[d]["PR Reviewed"] = 0
    developerDB[d]["Issue Participated"] = 0
    developerDB[d]["PR Participated"] = 0
    developerDB[d]["PR Durations"] = []
    developerDB[d]["Worktimes"] = []
    developerDB[d]["Timezones"] = []
    developerDB[d]["Languages"] = []
    developerDB[d]["Changed Files"] = []
    developerDB[d]["File Types"] = {}


def update_join_date(developerDB, developer, date, message, start, end):
    # Make sure the date is in our studied period
    if date > end or date < start:
        return developerDB
    if developerDB[developer]["Join Date"] == None:
        developerDB[developer]["Join Date"] = date
        developerDB[developer]["First Activity"] = message
    elif developerDB[developer]["Join Date"] >= date:
        developerDB[developer]["Join Date"] = date
        developerDB[developer]["First Activity"] = message
    return developerDB

def update_leave_date(developerDB, developer, date, message, start, end):
    # Make sure the date is in our studied period
    if date > end or date < start:
        return developerDB
    if developerDB[developer]["Last Active"] == None:
        developerDB[developer]["Last Active"] = date
        developerDB[developer]["Last Activity"] = message
    elif developerDB[developer]["Last Active"] <= date:
        developerDB[developer]["Last Active"] = date
        developerDB[developer]["Last Activity"] = message
    return developerDB


def commit_analyzer(commit_data, developerDB, start, end): # only one time interval
    source_code_exts = ["c","cc" ,"cgi", "pl", "class", "java", "cpp", "cs", "h", "php", "py", "sh", "swift", "vb"]
    for idx in commit_data:
        commit = commit_data[idx]
        if idx == "Commit#":
            continue
        elif commit["Time"] >= end:
            continue
        elif commit["Time"] < start:
            continue
        else:
            committer = commit["Author"]
            if not isinstance(committer,str) or not committer in developerDB:
                continue
            developerDB = update_join_date(developerDB, committer, commit["Time"], f"Commit {idx}", start, end)
            developerDB = update_leave_date(developerDB, committer, commit["Time"], f"Commit {idx}", start, end)
            developerDB[committer]["Total Commits"] += 1
            developerDB[committer]["Additions"] += commit["Additions"]
            developerDB[committer]["Deletions"] += commit["Deletions"]
            developerDB[committer]["Changed Files"].extend(commit["Changed Files"])
            developerDB[committer]["Timezones"].append(commit["Timezone"])

            # convert UTC time to the commit author's local time
            time = commit_data[idx]['Time'].hour + commit_data[idx]['Timezone']
            if time >= 24:
                time -= 24
            elif time < 0:
                time += 24
            developerDB[committer]["Worktimes"].append(time) 

            code_commit = False
            for file in commit["Changed Files"]:
                ext = file.split('.')[-1] if '.' in file else file.split('/')[-1]
                if ext in developerDB[committer]["File Types"]:
                    developerDB[committer]["File Types"][ext] += 1
                else:
                    developerDB[committer]["File Types"][ext] = 1
                if ext in source_code_exts:
                    code_commit = True
                    developerDB[committer]["Languages"].append(ext)
                    
            if code_commit:
                developerDB[committer]["Code Commits"] += 1
            else:
                developerDB[committer]["Other Commits"] += 1
            


def issue_analyzer(issue_data, developerDB, start, end):
    for idx in issue_data:
        issue = issue_data[idx]
        if idx == "Issue#":
            continue
        elif issue["Opened time"] >= end:
            continue
        elif issue["Opened time"] < start:
            continue
        else:
            owner, open_time= issue["Owner"], issue["Opened time"]
            if not isinstance(owner,str):
                continue
            if owner in developerDB:
                developerDB[owner]["Total Issues"] += 1
                developerDB = update_join_date(developerDB, owner, open_time, f"Raise Issue {idx}", start, end)
                developerDB = update_leave_date(developerDB, owner, open_time, f"Raise Issue {idx}", start, end)
        for participant in issue["Participants"]:
            if participant in developerDB:
                developerDB[participant]['Issue Participated'] += 1
                if owner in developerDB and not owner==participant:
                    developerDB[owner]["Collaborations"].append(participant)


def pull_request_analyzer(pr_data, developerDB, start, end):
    for idx in pr_data:
        pr = pr_data[idx]
        if idx == "Issue#":
            continue
        elif pr["Opened time"] < start:
            continue
        elif pr["Opened time"] >= end:
            continue
        else:
            owner, open_time = pr["Owner"], pr["Opened time"]
            if not isinstance(owner,str):
                continue
            if owner in developerDB:
                developerDB[owner]["Total Pull Requests"] += 1
                developerDB = update_join_date(developerDB, owner, open_time, f"Raise PR {idx}", start, end)
                developerDB = update_leave_date(developerDB, owner, open_time, f"Raise PR {idx}", start, end)
                if pr["Merged"] == True:
                    developerDB[owner]["PR Merged"] += 1
                elif pr["Merged"] == None: # for pytorch pr (unknown merged or not)
                    developerDB[owner]["PR Merged unknown pytorch"] += 1

            for reviewer in pr["Reviewers"]:
                if reviewer in developerDB:
                    developerDB[reviewer]["PR Reviewed"] += 1
                    developerDB = update_join_date(developerDB, reviewer, open_time, f"Reviewed PR {idx}", start, end)
                    developerDB = update_leave_date(developerDB, reviewer, open_time, f"Reviewed PR {idx}", start, end)
                    #developerDB[reviewer]["Worktimes"].append(closed_time.hour)
            for participant in pr["Participants"]:
                if participant in developerDB:
                    developerDB[participant]['PR Participated'] += 1
                    if owner in developerDB and not owner==participant:
                        developerDB[owner]["Collaborations"].append(participant)

def comment_analyzer(pr_comment, issue_comment, developerDB, start, end):
    for d in developerDB:
        if d in pr_comment:
            d_prc = list(filter(lambda x:x>start and x <=end,sorted(pr_comment[d])))
            if len(d_prc) > 0:
                developerDB = update_join_date(developerDB, d, d_prc[0], f"pr comment", start, end)
                developerDB = update_leave_date(developerDB, d, d_prc[-1], f"pr comment", start, end)
        if d in issue_comment:
            d_ic = list(filter(lambda x:x>start and x <=end,sorted(issue_comment[d])))
            if len(d_ic) > 0:
                developerDB = update_join_date(developerDB, d, d_ic[0], f"issue comment", start, end)
                developerDB = update_leave_date(developerDB, d, d_ic[-1], f"issue comment", start, end)

def read_commit_data(dir, start, end):
    commit_data = {}
    mainfileDir = os.path.join(dir, "commit_main3.csv")
    commit_main = pd.read_csv(mainfileDir)
    for idx, commit in commit_main.iterrows():
        if commit['Commit#'] == "Commit#":
            continue
        new_commit = {"Author": commit["Author"],
                            "Message": commit["Message"],
                            "Time": date_time_handler(commit["Time"]),
                            "Timezone" : commit["Timezone"],
                            "Additions" : commit["Additions"],
                            "Deletions" : commit["Deletions"],
                            "Changed Files": commit["Changed Files"].split() if isinstance(commit["Changed Files"],str) else []
                           }
        if new_commit['Time'] <= end and new_commit['Time'] >= start:
            id = commit['Commit#']
            commit_data[id] = new_commit
    return commit_data

def read_pr_data(dir, start, end):
    mainfileDir = os.path.join(dir, "pull_request_main.csv")
    pr_main = pd.read_csv(mainfileDir, index_col=0)
    pr_data = {}
    for idx,pr in pr_main.iterrows():
        if idx == "Issue#":
            continue
        date = date_time_handler(pr["Opened time"])
        if date > end or date < start:
            continue
        pr_data[idx] = {"Owner": pr["Owner"],
                        "Opened time": date,
                        "Closed time": date_time_handler(pr["Closed time"]),
                        "Title":pr["Title"],
                        "Description":pr["Description"],
                        "Commits": pr["Commits"].split() if isinstance(pr["Commits"],str) else [],
                        "Participants": pr["Participants"].split(),
                        "Merged": pr["Merged"],
                        "Comments":pr["Number of Comments"],
                        "Reviewers": pr["Reviewers"].split() if isinstance(pr["Reviewers"],str) else [],
                        "Changed Files":pr["Changed Files"].split() if isinstance(pr["Changed Files"],str) else [],
                        "Events": pr["Events"].split(',') if isinstance(pr["Events"],str) else [],
                        "Labels": pr["Labels"].split() if isinstance(pr["Labels"],str) else [],
                        "Comments": pr["Number of Comments"],
                        "First": False}
    return pr_data

def read_pytorch_pr_data(dir, start, end):
    mainfileDir = os.path.join(dir, "pull_request_main.csv")
    pr_main = pd.read_csv(mainfileDir, index_col=0)
    pr_data = {}
    for idx,pr in pr_main.iterrows():
        if idx == "Issue#":
            continue
        date = date_time_handler(pr["Opened time"])
        if date > end or date < start:
            continue
        
        pr_data[idx] = {"Owner": pr["Owner"],
                        "Opened time": date,
                        "Closed time": date_time_handler(pr["Closed time"]),
                        "Title":pr["Title"],
                        "Description":pr["Description"],
                        "Commits": pr["Commits"].split() if isinstance(pr["Commits"],str) else [],
                        "Participants": pr["Participants"].split(),
                        "Merged": pr["Merged"],
                        "Comments":pr["Number of Comments"],
                        "Reviewers": pr["Reviewers"].split() if isinstance(pr["Reviewers"],str) else [],
                        "Changed Files":pr["Changed Files"].split() if isinstance(pr["Changed Files"],str) else [],
                        "Events": pr["Events"].split(',') if isinstance(pr["Events"],str) else [],
                        "Labels": pr["Labels"].split() if isinstance(pr["Labels"],str) else [],
                        "Comments": pr["Number of Comments"],
                        "First": False}
        
        if isinstance(pr["Labels"],str) and "Merged" in pr["Labels"]:
            pr_data[idx]["Merged"] = True
        if date >= datetime.datetime(2018,7,1) and date < datetime.datetime(2019,5,1):
            pr_data[idx]["Merged"] = None
    return pr_data

def read_issue_data(dir, start, end):
    mainfileDir = os.path.join(dir, "issue_main.csv")
    issue_main = pd.read_csv(mainfileDir, index_col=0)
    issue_data = {}
    for idx,issue in issue_main.iterrows():
        if idx == "Issue#":
            continue
        date = date_time_handler(issue["Opened time"])
        if date > end or date < start:
            continue
        issue_data[idx] = {"Owner": issue["Owner"],
                           "Title":issue["Title"],
                            "Description":issue["Description"],
                           "Opened time": date,
                           "Closed time": date_time_handler(issue["Closed time"]),
                           "Assignee": issue["Assignees"].split() if isinstance(issue["Assignees"],str) else [],
                           "Events": issue["Events"].split(',') if isinstance(issue["Events"],str) else [],
                           "Labels" : issue["Labels"],
                           "Participants": issue["Participants"].split(),
                          "Comments": issue["Number of Comments"]}
    return issue_data


def read_tensorflow_pr_comment(tensorflow_dir):
    tensorflow_pr_comments_df = pd.read_csv(os.path.join(tensorflow_dir, "pull_request_comments.csv"),index_col = False, sep='delimiter', header=None)
    tensorflow_pr_comments = ' '.join(tensorflow_pr_comments_df.loc[~tensorflow_pr_comments_df[0].isna()][0].values)
    pattern = r'([A-Za-z\d](?:[A-Za-z\d]|-(?=[A-Za-z\d])){0,38})\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\):'
    tensorflow_pr_comment_matches = re.findall(pattern, tensorflow_pr_comments)
    tensorflow_pr_comments = {}
    for match in tensorflow_pr_comment_matches:
        if not match[0] in tensorflow_pr_comments:
            tensorflow_pr_comments[match[0]] = []
        tensorflow_pr_comments[match[0]].append(date_handler(match[1]))
    return tensorflow_pr_comments

def read_pr_comment(dir):
    pattern = r'([A-Za-z\d](?:[A-Za-z\d]|-(?=[A-Za-z\d])){0,38})\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\):'
    with open(os.path.join(dir, "pull_request_comments.txt"), 'r') as file:
        file_contents = file.read()
    pr_comments = str(file_contents)
    
    matches = re.findall(pattern, pr_comments)
    
    pr_comment_dict = {}
    for match in matches:
        if not match[0] in pr_comment_dict:
            pr_comment_dict[match[0]] = []
        pr_comment_dict[match[0]].append(date_handler(match[1]))
    return pr_comment_dict

def read_tensorflow_issue_comment(tensorflow_dir, tensorflow_issue_data):
    tensorflow_issue_comments_df = pd.read_csv(os.path.join(tensorflow_dir, "issue_comments.csv"), 
                                               header=None, sep=',', names=[i for i in range(550)], 
                                               on_bad_lines='warn', index_col=0)
    
    tensorflow_issue_comments_df = tensorflow_issue_comments_df.loc[tensorflow_issue_comments_df.index.isin(tensorflow_issue_data.keys())]
    non_nan_values = [str(value) for value in tensorflow_issue_comments_df.values.flatten() if not pd.isna(value)]
    resulting_string = ' '.join(non_nan_values)
    pattern = r'([A-Za-z\d](?:[A-Za-z\d]|-(?=[A-Za-z\d])){0,38})\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\):'
    tensorflow_comment_matches = re.findall(pattern, resulting_string)
    tensorflow_issue_comments = {}
    for match in tensorflow_comment_matches:
        if not match[0] in tensorflow_issue_comments:
            tensorflow_issue_comments[match[0]] = []
        tensorflow_issue_comments[match[0]].append(date_handler(match[1]))
    return tensorflow_issue_comments


def extract_content_between_issues(text):
    pattern = r"Issue#\s(\d+)"
    matches = list(re.finditer(pattern, text))
    contents = {}

    for i in range(len(matches)):
        # Convert issue number to integer
        issue_number = int(matches[i].group(1))
        start = matches[i].end()  # End of the current match

        # End of content: start of the next match or end of text
        end = matches[i + 1].start() if i < len(matches) - 1 else len(text)
        contents[issue_number] = text[start:end].strip()

    return contents

def read_issue_comment(dir, issue_data):
    pattern = r'([A-Za-z\d](?:[A-Za-z\d]|-(?=[A-Za-z\d])){0,38})\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\):'
    with open(os.path.join(dir, "issue_comments.txt"), 'r') as file:
        file_contents = file.read()
    issue_comments = str(file_contents)
    issue_comments = extract_content_between_issues(issue_comments)
    issue_comments = {key: value for key, value in issue_comments.items() if key in issue_data.keys()}
    issue_comments = ' '.join(str(value) for value in issue_comments.values())
    matches = re.findall(pattern, issue_comments)
    
    issue_comment_dict = {}
    for match in matches:
        if not match[0] in issue_comment_dict:
            issue_comment_dict[match[0]] = []
        issue_comment_dict[match[0]].append(date_handler(match[1]))
    return issue_comment_dict

            
# Input:  dict commit_date = {"commit_id_1":{"Author":"xxx", "Time":datetime, "Message":"commit message", "Changed Files":["file1", "file2", ...]}, "commit_id_2":{...},...}
#         dict issue_data = {issue_id_1(int):{"Owner":"xxx", "Opened time": datetime, ...}, issue_id_2(int):{...}, ...}
#
# Output: dict issue_commit_mapping = {issue_id_1(int): ["bug_fixing_commit_id_1","bug_fixing_commit_id_2",... ], issue_id_2(int):[...], ... }

def issue_fixing_commit_mapping(proj_name, commit_data, issue_data, pr_data,startdate, enddate):
    issue_fixed = 0
    excludes = []
    issue_commit_mapping = {}
    if proj_name == "tensorflow/tensorflow":
        excludes = [128,256, 404,512,1024]
    bug_fix_commits = []
    keywords = ["issue","fix","resolve", "solve", "address","settle", "close"]
    for idx in commit_data:
        if idx == "Commit#":
            continue
        if commit_data[idx]["Time"] >= enddate or commit_data[idx]["Time"] < startdate:
            continue
        for keyword in keywords:
            if keyword in commit_data[idx]["Message"].lower():
                bug_fix_commits.append(idx)
                break
    bug_fix_commits = list(set(bug_fix_commits))
    
    issue_date_mapping = {}
    for idx in issue_data:
        if issue_data[idx]["Opened time"] >= enddate or issue_data[idx]["Opened time"] < startdate:
            continue
        issue_date_mapping[idx] = [issue_data[idx]["Opened time"],issue_data[idx]["Closed time"]]
    
        
    for commit_id in bug_fix_commits:
        msg = commit_data[commit_id]["Message"]
        try:
            message_lines = msg.split('\n')
        except:
            continue
        for line in message_lines:
            if "PiperOrigin-RevId" in line:
                continue
            if "github.com" in line:
                if not re.search(rf'({proj_name}\/issues\/)(\d+)', line):
                    continue
            line = line = re.sub(r'(\d+[a-z]+)|([a-z]+\d+)|([a-z]+fix)',"",line.lower())
            if re.search(r'(pr|pull request|line)(\s)*(#|\s)*(\d+)',line):
                continue
            if "fix" in line or "resolve" in line or "address" in line or "solve" in line or "close" in line:
                ids = [int(item) for item in re.findall('[0-9]+', line) if int(item) > 100]
                for _id in ids:
                    if _id in excludes:
                        continue
                    if _id in pr_data:
                        #print(commit_id, _id, line)
                        continue
                    #if _id in pr_data and commit_id in pr_data[_id]["Commits"]:
                    #    continue
                    if _id in issue_date_mapping and commit_data[commit_id]["Time"] > issue_date_mapping[_id][0]:
                        if not _id in issue_commit_mapping:
                            issue_commit_mapping[_id] = [commit_id]
                            issue_fixed += 1
                        elif not commit_id in issue_commit_mapping[_id]:
                            issue_commit_mapping[_id].append(commit_id)
                            issue_fixed += 1
    for idx in pr_data:
        pr = pr_data[idx]
        if pr["Opened time"] >= enddate or pr["Opened time"] < startdate:
            continue
        try:
            message_lines = [pr["title"]]
            message_lines.extends(pr["Description"].split('\n'))
        except:
            message_lines = [pr["Title"]]
        for line in message_lines:
            if not isinstance(line,str):
                continue
            if "github.com" in line:
                if not re.search(rf'({proj_name}\/issues\/)(\d+)', line):
                    continue
            line = line = re.sub(r'(\d+[a-z]+)|([a-z]+\d+)|([a-z]+fix)',"",line.lower())
            if re.search(r'(pr|pull request|line)(\s)*(#|\s)*(\d+)',line):
                continue
            if "fix" in line or "resolve" in line or "address" in line or "solve" in line or "close" in line:
                ids = [int(item) for item in re.findall('[0-9]+', line) if int(item) > 100]
                for _id in ids:
                    if _id in excludes:
                        continue
                    if _id in issue_date_mapping and pr["Opened time"] > issue_date_mapping[_id][0]:
                        if not _id in issue_commit_mapping:
                            issue_commit_mapping[_id] = [commit_id for commit_id in pr["Commits"] if commit_id in commit_data]
                            issue_fixed += 1
                            #print(_id,pr["Commits"])
                            #print(line)
                        else:
                            for commit_id in pr["Commits"]:
                                if not commit_id in issue_commit_mapping[_id] and commit_id in commit_data:
                                    issue_commit_mapping[_id].append(commit_id)
                                    issue_fixed += 1
                                    #print(_id, commit_id,line)
        
    return issue_commit_mapping


def update_commit_timezone(git_repo_dir, dir):
    mainfileDir = os.path.join(dir, "commit_main.csv")
    commit_main = pd.read_csv(mainfileDir, index_col=0)
    gr = pydriller.Git(git_repo_dir)
    timezones = []
    for idx, commit in commit_main.iterrows():
        timezones.append(int(gr.get_commit(idx).author_timezone/3600)*(-1))
    commit_main["Timezone"] = timezones
    commit_main.to_csv(os.path.join(dir, "commit_main3.csv"))

def developer_profile_analyzer(developerDB, commit_data, issue_fixing_commits, start, end):
    for commit_id in issue_fixing_commits:
        if commit_id in commit_data and commit_data[commit_id]["Author"] in developerDB:
            if isinstance(commit_data[commit_id]["Author"],str) and commit_data[commit_id]["Time"] >= start and commit_data[commit_id]["Time"] < end:
                developerDB[commit_data[commit_id]["Author"]]['Issue Solved'] += 1

    for d in developerDB:
        developerDB[d]["Duration"] = (developerDB[d]["Last Active"] - developerDB[d]["Join Date"]).days +1 if developerDB[d]["Last Active"] and developerDB[d]["Join Date"] else 1
        developerDB[d]["Authored files"] = len(set(developerDB[d]["Changed Files"]))
        developerDB[d]["Commit Rate"] =  developerDB[d]["Total Commits"]/developerDB[d]["Duration"]
        developerDB[d]["Code Commit Rate"] =  developerDB[d]["Code Commits"]/developerDB[d]["Duration"]
        developerDB[d]["Other Commit Rate"] =  developerDB[d]["Other Commits"]/developerDB[d]["Duration"]
        #developerDB[d]["Buggy Commit Density"] =  developerDB[d]["Buggy Commits"]/developerDB[d]["Duration"]
        developerDB[d]["Worktime"] = mode(developerDB[d]["Worktimes"])
        developerDB[d]["Timezone"] = mode(developerDB[d]["Timezones"])
        developerDB[d]["Code Contribution"] = developerDB[d]["Additions"] + developerDB[d]["Deletions"]
        developerDB[d]["Code Contribution Rate"] = developerDB[d]["Code Contribution"]/developerDB[d]["Duration"]
        developerDB[d]["Code Contribution Density"] = developerDB[d]["Code Contribution"]/developerDB[d]["Total Commits"]
        developerDB[d]["Issue Contribution"] = developerDB[d]["Total Issues"] + developerDB[d]["Issue Solved"]
        developerDB[d]["Issue Contribution Rate"] = developerDB[d]["Issue Contribution"]/developerDB[d]["Duration"]

        developerDB[d]["Issue Solving Ratio"] = developerDB[d]["Issue Solved"]/developerDB[d]["Issue Participated"] if developerDB[d]["Issue Participated"] > 0 else 0
        developerDB[d]["Issue Solving Density"] = developerDB[d]["Issue Solving Ratio"]/developerDB[d]["Duration"]
        developerDB[d]["PR Contribution"] = developerDB[d]["Total Pull Requests"] + developerDB[d]["PR Reviewed"]
        developerDB[d]["PR Contribution Rate"] = developerDB[d]["PR Contribution"]/developerDB[d]["Duration"]
        developerDB[d]["PR Approval Ratio"] = developerDB[d]["PR Merged"]/developerDB[d]["Total Pull Requests"] if developerDB[d]["Total Pull Requests"] > 0 else 0
        if developerDB[d]["PR Merged unknown pytorch"] > 0:
            if developerDB[d]["Total Pull Requests"] - developerDB[d]["PR Merged unknown pytorch"] <= 0:
                developerDB[d]["PR Approval Ratio"] = 0
            else:
                developerDB[d]["PR Approval Ratio"] = developerDB[d]["PR Merged"]/(developerDB[d]["Total Pull Requests"] - developerDB[d]["PR Merged unknown pytorch"])

        developerDB[d]["PR Approval Density"] = developerDB[d]["PR Approval Ratio"]/developerDB[d]["Duration"]
        # developerDB[d]["Buggy Commit Ratio"] = developerDB[d]["Buggy Commits"]/developerDB[d]["Code Commits"] if developerDB[d]["Code Commits"] > 0 else 0
        # developerDB[d]["Buggy Commit Density"] =  developerDB[d]["Buggy Commit Ratio"]/developerDB[d]["Duration"]
        developerDB[d]["Languages"] = len(set(developerDB[d]["Languages"]))
        developerDB[d]["Collaborations"] = len(set(developerDB[d]["Collaborations"]))


def write_developerDB_temp(dir, filename, developerDB, sorted_developers):
    headers = ["Name", "Join Date","First Activity", "Last Active","Last Activity", "Duration", "Timezone", "Worktime", 
               "Total Commits", "Authored files","Commit Rate", "Code Commits", "Code Commit Rate","Other Commits","Other Commit Rate",  
               "Code Contribution", "Code Contribution Rate", "Code Contribution Density",
               "Total Issues", "Issue Participated","Issue Solved", "Issue Contribution", "Issue Contribution Rate","Issue Solving Ratio", "Issue Solving Density", 
               "Total Pull Requests","PR Merged", "PR Reviewed","PR Participated", "PR Contribution","PR Contribution Rate", "PR Approval Ratio", "PR Approval Density","Followers",
               "Collaborations","Languages","File Types"]
    csv_main = open(os.path.join(dir, filename), "w", encoding="utf-8")
    main_writer = csv.writer(csv_main)
    main_writer.writerow(headers)
    for d in sorted_developers:
        file_types = dict(sorted(developerDB[d]["File Types"].items(), key=lambda x: x[1],reverse=True))
        file_types = [f"{item}_{file_types[item]}" for item in file_types]
        file_types = " ".join(file_types)
        main_writer.writerow([d,developerDB[d]["Join Date"], developerDB[d]["First Activity"],developerDB[d]["Last Active"],developerDB[d]["Last Activity"],developerDB[d]["Duration"],developerDB[d]["Timezone"], developerDB[d]["Worktime"],
                              developerDB[d]["Total Commits"],developerDB[d]["Authored files"],developerDB[d]["Commit Rate"],developerDB[d]["Code Commits"],developerDB[d]["Code Commit Rate"],
                              developerDB[d]["Other Commits"], developerDB[d]["Other Commit Rate"], 
                              developerDB[d]["Code Contribution"], developerDB[d]["Code Contribution Rate"],developerDB[d]["Code Contribution Density"],
                              developerDB[d]["Total Issues"], developerDB[d]["Issue Participated"], developerDB[d]["Issue Solved"], developerDB[d]["Issue Contribution"], developerDB[d]["Issue Contribution Rate"],
                              developerDB[d]["Issue Solving Ratio"], developerDB[d]["Issue Solving Density"], 
                              developerDB[d]["Total Pull Requests"], developerDB[d]["PR Merged"],developerDB[d]["PR Reviewed"], developerDB[d]["PR Participated"],
                              developerDB[d]["PR Contribution"],developerDB[d]["PR Contribution Rate"],developerDB[d]["PR Approval Ratio"],developerDB[d]["PR Approval Density"],
                              developerDB[d]["Followers"],developerDB[d]["Collaborations"],developerDB[d]["Languages"],file_types])
    csv_main.close()




# Modify this place, add github authentication tokens, e.g., Github("ghp_1x1x1x1x1x2w2w2w3E3E3E3E4R4R4R4R")
github_instances = []

# Modify this directory to where the collected project data (from github_crawler.py) is stored
basedir = os.path.join(os.path.dirname(__file__),'..','data')

# Bots identified from manual investigation
known_bots = ['tensorflower-gardener','tensorflow-jenkins','onnxbot','facebook-github-bot','pytorchmergebot',
              'docusaurus-bot','theano-bot','deadsnakes-issues-bot','mxnet-label-bot']

start = datetime.datetime(2008,1,1)
end = datetime.datetime(2022,4,30)

repo_names = ["tensorflow/tensorflow", "pytorch/pytorch", "keras-team/keras", "Theano/Theano", "onnx/onnx", "apache/mxnet"]

# clone the github repository of the subject projects
git_repo_dir = os.path.join(os.path.dirname(__file__), '..',"git_repos")
if not os.path.exists(git_repo_dir):
    os.makedirs(git_repo_dir)
if not os.path.exists(os.path.join(git_repo_dir,'tensorflow')):
    git.Git(git_repo_dir).clone("https://github.com/tensorflow/tensorflow")
if not os.path.exists(os.path.join(git_repo_dir,'pytorch')):
    git.Git(git_repo_dir).clone("https://github.com/pytorch/pytorch")
if not os.path.exists(os.path.join(git_repo_dir,'keras')):
    git.Git(git_repo_dir).clone("https://github.com/keras-team/keras")
if not os.path.exists(os.path.join(git_repo_dir,'mxnet')):
    git.Git(git_repo_dir).clone("https://github.com/apache/mxnet")
if not os.path.exists(os.path.join(git_repo_dir,'Theano')):
    git.Git(git_repo_dir).clone("https://github.com/Theano/Theano")
if not os.path.exists(os.path.join(git_repo_dir,'onnx')):
    git.Git(git_repo_dir).clone("https://github.com/onnx/onnx")



for repo_name in repo_names:
    dir = os.path.join(basedir, repo_name.replace('/', '_'))
    git_repo_dir = os.path.join("..","git_repos",repo_name.split('/')[-1])

    # use pydriller to get commit author timezone
    if not os.path.exists(os.path.join(dir, "commit_main3.csv")):
        update_commit_timezone(git_repo_dir, dir)
        
    commit_data = read_commit_data(dir, start, end)
    issue_data = read_issue_data(dir, start, end)
    if 'pytorch' in repo_name:
        pr_data = read_pytorch_pr_data(dir, start, end)
    else:
        pr_data = read_pr_data(dir, start, end)
    
    # In the project data collected with Github API, the issues contain both issue reports and the pull requests.
    # This line of code remove the pull requests from the issue file.
    issue_data = dict(filter(lambda x:not x[0] in pr_data, issue_data.items()))

    if 'tensorflow' in repo_name:
        issue_comment = read_tensorflow_issue_comment(dir, issue_data)
        pr_comment = read_tensorflow_pr_comment(dir)
    else:
        issue_comment = read_issue_comment(dir, issue_data)
        pr_comment = read_pr_comment(dir)

    # The mapping of issue ids and the commit ids which fix the issue
    issue_commit_mapping = issue_fixing_commit_mapping(repo_name,commit_data, issue_data, pr_data, start, end)

    # get a list of issue_fixing_commit_ids
    issue_fixing_commits = []
    for x in list(issue_commit_mapping.values()):
        issue_fixing_commits.extend(x)
    issue_fixing_commits = list(set(issue_fixing_commits))

    developers, developerDB = get_developers(dir,commit_data)

    commit_analyzer(commit_data, developerDB, start, end)
    issue_analyzer(issue_data, developerDB, start, end)
    pull_request_analyzer(pr_data, developerDB, start, end)
    comment_analyzer(pr_comment, issue_comment, developerDB, start, end)

    # Keep only the contributors who have make commits
    developerDB = dict(filter(lambda d:d[1]["Total Commits"]>0, developerDB.items()))

    sorted_developers =  list(sorted(developerDB.keys(), key=lambda x: developerDB[x]['Total Commits'],reverse=True))

    developer_profile_analyzer(developerDB, commit_data, issue_fixing_commits, start, end)

    write_developerDB_temp(dir, "contributor_features.csv", developerDB,sorted_developers)

# write merged contributor feature files for all projects to data directory
developer_data = []
for repo_name in repo_names:
    dir = os.path.join(basedir, repo_name.replace('/', '_'))
    proj_profile = pd.read_csv(os.path.join(dir, "contributor_features.csv"))
    proj_profile['Project'] = repo_name.split('/')[-1].lower()
    developer_data.append(proj_profile)
developer_data =  pd.concat(developer_data,ignore_index=True)
developer_data = developer_data[['Project']+developer_data.columns.to_list()[:-1]]
developer_data = developer_data.drop(['First Activity','Last Activity'],axis=1)
developer_data.to_csv(os.path.join(basedir,'contributor_features.csv'))