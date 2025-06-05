"""
IMPORTANT: If you only want to reproduce the experiment results, you don't need to run this file as 
we have provided our dataset in under /data directory. This file is only for recreating the dataset.

 Crawl Commits/Issues/Pull Requests with Github API

 1. Modify line 729 and 731 before running this script.
 2. A main directory named 'Projects' will be created to store all collected project data.
 3. A directory will be created for each repo, and Commits/Issues/Pull Requests data will be stored into main.csv and comments.csv. (e.g., commit_main.csv and commit_comments.csv)
    pull_request_main.csv: "Title", "Description", "Owner", "Labels", "Reviewers", "Assignees", "Opened time", "Closed time", "Changed Files", "Events", "Participants"
    Multiple items in a csv cell are separated by space(e.g. assignees), except for events are separated by comma
    comments.csv only contain comments with format: "issue_id, user:comment_body, user:comment_body,... " in each line
 4. Results stored in a dictionary->result, and result.txt will be exported under the same directory
 5. This script will take more than 3 days to execute. Make sure provide at least 10 github authentication token in line 729. 

"""
import datetime
import time
import os
import github
import requests
from github import Github
import csv
import sys


def pull_request_crawler(repo_name,until_time):
    print(f"Crawling Pull Requests from {repo_name}...")
    dir = os.path.join(basedir, repo_name.replace('/', '_'))
    if not os.path.exists(dir):  # create a folder for each repo
        os.makedirs(dir)
    csv_main = open(os.path.join(dir, "pull_request_main.csv"), "w", encoding="utf-8")
    comments_file = open(os.path.join(dir, "pull_request_comments.txt"), "w", encoding="utf-8")
    repo_log = open(os.path.join(dir, "pull_request_log.txt"), "w", encoding="utf-8")
    # Info stored into main file and comment file separately
    # Main file has all most of the info and comment file only has comments
    main_writer = csv.writer(csv_main,escapechar='\\')
    # Main file format below, multiple items in a cell are seperated by space, expect for events separated by comma
    main_writer.writerow(["Issue#","Title", "Owner", "Description", "Labels", "Reviewers", "Assignees", "Opened time",
                          "Closed time", "Changed Files", "Commits", "Events", "Participants","Number of Comments", "Merged"])
    pr_counter, gi_counter = 0, 0  # pull request counter, github instance counter
    while True:
        try:
            repo = github_instances[gi_counter].get_repo(repo_name)
            pull_requests = repo.get_pulls(state='closed', sort='created')
            gi_counter += 1  # Point to next available github account for current repo
            num_PR = pull_requests.totalCount
            break
        except github.UnknownObjectException:  # 404 error, repo not found
            result[repo_name] = "Repo Not Found"
            print(f"404 {repo_name} not found")
            repo_log.write("Repo Not Found\n")
            csv_main.close()
            comments_file.close()
            repo_log.close()
            return
        except github.RateLimitExceededException:  # need to change github account
            if gi_counter < len(github_instances)-1:
                repo = github_instances[gi_counter+1].get_repo(repo_name)
                pull_requests = repo.get_pulls(state='closed', sort='created')
                num_PR = pull_requests.totalCount
                gi_counter += 2  # Point to next available github account for current repo, because gi_counter+1 is used now
                break
            else:
                gi_counter = 0
        except TimeoutError:
            repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
            print(f"Time Out Error sleep for {delay} seconds")
            time.sleep(delay)
        except github.GithubException.GithubException:
            repo_log.write(f"503 Service Unavailable, delay {delay} seconds\n")
            print(f"Http Time Out delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ReadTimeout:  # HTTP read time out
            repo_log.write(f"Http Time Out delay {delay} seconds\n")
            print(f"Http Time Out delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ConnectionError:
            repo_log.write(f"Connect Error delay {delay} seconds\n")
            print(f"Connect Error delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions:
            repo_log.write(f"Connect Error delay {delay} seconds\n")
            print(f"Connect Error delay {delay} seconds")
            time.sleep(delay)

    while pr_counter < num_PR:
        try:
            pr = pull_requests[pr_counter]  # current pull request
            participants = [pr.user.login]

            # Labels assignees, reviewers are separated by space
            labels = " ".join([label.name for label in pr.labels]) if pr.labels else None
            assignees = " ".join([assignee.login for assignee in pr.assignees]) if pr.assignees else None

            reviewers = []
            for review in pr.get_reviews():
                if review.user:
                    reviewers.append(review.user.login)
                    participants.append(review.user.login)
            reviewers = list(set(reviewers))  # Remove if PR owner is in the list
            if pr.user.login in reviewers:
                reviewers.remove(pr.user.login)
            reviewers = " ".join(reviewers) if len(reviewers) > 0 else None

            num_comments = 0
            for comment in pr.get_issue_comments():  # comments
                if comment.user:
                    comments_file.write(f"{comment.user.login}({comment.created_at}):{comment.body}\n")
                    participants.append(comment.user.login)
                    num_comments += 1
            for comment in pr.get_comments():  # comments under reviewed
                if comment.user:
                    comments_file.write(f"{comment.user.login}({comment.created_at}):{comment.body}\n")
                    participants.append(comment.user.login)
                    num_comments += 1

            changed_files = []
            for commit in pr.get_commits():
                changed_files.extend(list(map(lambda x: x.filename, commit.files)))
            changed_files = " ".join(list(set(changed_files))) if len(changed_files) > 0 else None

            commits = []
            for commit in pr.get_commits():
                commits.append(commit.sha)
            commits = " ".join(list(set(commits))) if len(commits) > 0 else None

            events = []  # For events, only user, event and time created are stored
                         # e.g. "cgruber mentioned 2014-11-02 17:55:22"
            for event in pr.get_issue_events():
                if event.actor:
                    events.append(f"{event.actor.login} {event.event} {event.created_at}")
                    participants.append(event.actor.login)
            events = ",".join(events) if len(events) > 0 else None

            participants = " ".join(list(set(participants)))

            output_main = [pr.number, pr.title, pr.user.login, pr.body, labels, reviewers, assignees,
                           pr.created_at, pr.closed_at, changed_files, commits, events, participants, num_comments,
                           pr.merged]

            main_writer.writerow(output_main)
            pr_counter += 1
            sys.stdout.write("\r"+f"Issue {pr.number}, {pr_counter} / {num_PR} done!")
            repo_log.write(f"Issue {pr.number} done!")
        except github.RateLimitExceededException:  # change Github account
            if gi_counter < len(github_instances):
                repo = github_instances[gi_counter].get_repo(repo_name)
                pull_requests = repo.get_pulls(state='closed', sort='created')
                gi_counter += 1
                #print("Github account changed!")
            else:  # all Github accounts are used
                gi_counter = 0

                while (True):
                    # result[repo_name] = "Not Finished"
                    # print(f"{repo_name} not finished")
                    # continue
                    try:
                        repo = github_instances[gi_counter].get_repo(repo_name)
                        pull_requests = repo.get_pulls(state='closed', sort='created')
                        gi_counter += 1  # Point to next available github account for current repo
                        break
                    except TimeoutError:
                        repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
                        print(f"Time Out Error sleep for {delay} seconds")
                        time.sleep(delay)
                    except github.GithubException:
                        repo_log.write(f"503 Service Unavailable, delay {delay} seconds\n")
                        print(f"Http Time Out delay {delay} seconds")
                        time.sleep(delay)
                    except github.RateLimitExceededException:  # github instance still not available
                        repo_log.write(
                            f"{repo_name} crawler sleeps {delay} seconds, wait for available github instance\n")
                        print(f"{repo_name} crawler sleeps {delay} seconds, wait for available github instance")
                        time.sleep(delay)
                    except requests.exceptions.ReadTimeout:  # HTTP read time out
                        repo_log.write(f"Http Time Out delay {delay} seconds\n")
                        print(f"Http Time Out delay {delay} seconds")
                        time.sleep(delay)
                    except requests.exceptions.ConnectionError:
                        repo_log.write(f"Connect Error delay {delay} seconds\n")
                        print(f"Connect Error delay {delay} seconds")
                        time.sleep(delay)
                    except requests.exceptions:
                        repo_log.write(f"Connect Error delay {delay} seconds\n")
                        print(f"Connect Error delay {delay} seconds")
                        time.sleep(delay)
        except TimeoutError:
            repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
            print(f"Time Out Error sleep for {delay} seconds")
            time.sleep(delay)
        except github.GithubException:
            repo_log.write(f"503 Service Unavailable, delay {delay} seconds\n")
            print(f"Http Time Out delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ReadTimeout:  # HTTP read time out
            repo_log.write(f"Http Time Out delay {delay} seconds\n")
            print(f"Http Time Out delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ConnectionError:
            repo_log.write(f"Connect Error delay {delay} seconds\n")
            print(f"Connect Error delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions:
            repo_log.write(f"Connect Error delay {delay} seconds\n")
            print(f"Connect Error delay {delay} seconds")
            time.sleep(delay)

    csv_main.close()
    repo_log.close()
    result[repo_name] = "Done"
    print(f"{repo_name} All Done!")

def commit_crawler(repo_name, until_time):
    print(f"Crawling commits from {repo_name}...")
    dir = os.path.join(basedir, repo_name.replace('/', '_'))
    if not os.path.exists(dir):  # create a folder for each repo
        os.makedirs(dir)
    csv_main = open(os.path.join(dir, "commit_main.csv"), "w", encoding="utf-8")
    #comments_file = open(os.path.join(dir, "commit_comments.txt"), "w", encoding="utf-8")
    repo_log = open(os.path.join(dir, "commit_log.txt"), "w", encoding="utf-8")
    # Info stored into main file and comment file separately
    # Main file has all most of the info and comment file only has comments
    main_writer = csv.writer(csv_main, escapechar='\\')
    # Main file format below, multiple items in a cell are seperated by space, expect for events separated by comma
    main_writer.writerow(["Commit#", "Author", "Message", "Time", "Changed Files", "Additions", "Deletions", "Parents", "Number of Comments"])
    num_commits, commit_counter, gi_counter = 0, 0 ,0 # number of total commit in project, commit counter, github instance counter
    while True:
        try:
            repo = github_instances[gi_counter].get_repo(repo_name)
            commits = repo.get_commits(until=until_time)
            num_commits = commits.totalCount
            gi_counter += 1  # Point to next available github account for current repo
            break
        except github.UnknownObjectException:  # 404 error, repo not found
            result[repo_name] = "Repo Not Found"
            print(f"404 {repo_name} not found")
            repo_log.write("Repo Not Found\n")
            csv_main.close()
            #comments_file.close()
            repo_log.close()
            return
        except github.RateLimitExceededException:  # need to change github account
            if gi_counter < len(github_instances)-1:
                repo = github_instances[gi_counter+1].get_repo(repo_name)
                commits = repo.get_commits(until=until_time)
                num_commits = commits.totalCount
                print(f"Try to change github account {gi_counter+1}")
                gi_counter += 2  # Point to next available github account for current repo, because gi_counter+1 is used now
                break
            else:
                gi_counter = 0
        except TimeoutError:
            repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
            print(f"Time Out Error sleep for {delay} seconds")
            time.sleep(delay)
        except github.GithubException:
            repo_log.write(f"Github error, delay {delay} seconds\n")
            print(f"Github error, delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ReadTimeout:  # HTTP read time out
            repo_log.write(f"Http Time Out delay {delay} seconds\n")
            print(f"Http Time Out delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ConnectionError:
            repo_log.write(f"Connect Error delay {delay} seconds\n")
            print(f"Connect Error delay {delay} seconds")
            time.sleep(delay)

    while commit_counter < num_commits:
        try:
            commit = commits[commit_counter]  # current commits
            commit_id = commit.sha
            if commit.author == None:
                commit_counter+= 1
                continue
            else:
                author = commit.author.login
            changed_files = []
            for file in commit.files:
                changed_files.append(file.filename)
            changed_files = " ".join(list(set(changed_files))) if len(changed_files) > 0 else None

            parents = []
            for parent in commit.parents:
                parents.append(parent.sha)
            parents = " ".join(list(set(parents))) if len(parents) > 0 else None


            output_main = [commit_id, author, commit.commit.message, commit.commit.author.date, changed_files,
                           commit.stats.additions, commit.stats.deletions, parents, commit.get_comments().totalCount]
            main_writer.writerow(output_main)
            commit_counter += 1
            msg = f"Current commit {commit_id}, {commit_counter}/{num_commits} done!"
            sys.stdout.write('\r'+msg)
        except github.RateLimitExceededException:  # change Github account
            if gi_counter < len(github_instances):
                repo = github_instances[gi_counter].get_repo(repo_name)
                commits = repo.get_commits(until=until_time)
                gi_counter += 1
                #print("Github account changed!")
                print(f"Try to change github account {gi_counter}")
            else:  # all Github accounts are used
                gi_counter = 0
                while (True):
                    # result[repo_name] = "Not Finished"
                    # print(f"{repo_name} not finished")
                    # continue
                    try:
                        repo = github_instances[gi_counter].get_repo(repo_name)
                        commits = repo.get_commits(until=until_time)
                        gi_counter += 1  # Point to next available github account for current repo
                        print(f"Try to change github account {gi_counter}")
                        break
                    except TimeoutError:
                        repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
                        print(f"Time Out Error sleep for {delay} seconds")
                        time.sleep(delay)
                    except github.GithubException as githuberror:
                        if "Returned object contains no URL" in str(githuberror):
                            repo_log.write(f"skip commit {commit_id}\n")
                            print(f"skip commit {commit_id}\n")
                            commit_counter += 1
                        else:
                            print(f"{str(githuberror)}, delay {delay} seconds for commit {commit_id}")
                            repo_log.write(f"Github error, delay {delay} seconds\n")
                            time.sleep(delay)
                    except github.RateLimitExceededException:  # github instance still not available
                        repo_log.write(
                            f"{repo_name} crawler sleeps {delay} seconds, wait for available github instance\n")
                        print(f"{repo_name} crawler sleeps {delay} seconds, wait for available github instance")
                        time.sleep(delay)
                    except requests.exceptions.ReadTimeout:  # HTTP read time out
                        repo_log.write(f"Http Time Out delay {delay} seconds\n")
                        print(f"Http Time Out delay {delay} seconds")
                        time.sleep(delay)
                    except requests.exceptions.ConnectionError:
                        repo_log.write(f"Connect Error delay {delay} seconds\n")
                        print(f"Connect Error delay {delay} seconds")
                        time.sleep(delay)
        except TimeoutError:
            repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
            print(f"Time Out Error sleep for {delay} seconds")
            time.sleep(delay)
        except github.GithubException as githuberror:
            if "Returned object contains no URL" in str(githuberror):
                repo_log.write(f"skip commit {commit_id}\n")
                print(f"skip commit {commit_id}\n")
                commit_counter += 1
            else:
                print(f"{str(githuberror)}, delay {delay} seconds for commit {commit_id}")
                repo_log.write(f"Github error, delay {delay} seconds\n")
                time.sleep(delay)
        except requests.exceptions.ReadTimeout:  # HTTP read time out
            repo_log.write(f"Http Time Out delay {delay} seconds\n")
            print(f"Http Time Out delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ConnectionError:
            repo_log.write(f"Connect Error delay {delay} seconds\n")
            print(f"Connect Error delay {delay} seconds")
            time.sleep(delay)
    csv_main.close()
    repo_log.close()
    result[repo_name] = "Done"
    print(f"{repo_name} All Done!")

def commit_crawler_continue(repo_name, commit_id, until_time):
    print(f"Crawling commits from {repo_name}...")
    dir = os.path.join(basedir, repo_name.replace('/', '_'))
    if not os.path.exists(dir):  # create a folder for each repo
        os.makedirs(dir)
    csv_main = open(os.path.join(dir, "commit_main.csv"), "a", encoding="utf-8")
    #comments_file = open(os.path.join(dir, "commit_comments.txt"), "w", encoding="utf-8")
    repo_log = open(os.path.join(dir, "commit_log.txt"), "a", encoding="utf-8")
    # Info stored into main file and comment file separately
    # Main file has all most of the info and comment file only has comments
    main_writer = csv.writer(csv_main, escapechar='\\')
    # Main file format below, multiple items in a cell are seperated by space, expect for events separated by comma
    #main_writer.writerow(["Commit#", "Author", "Message", "Time", "Changed Files", "Additions", "Deletions", "Parents", "Number of Comments"])
    num_commits, commit_counter, gi_counter = 0, 0 ,0 # number of total commit in project, commit counter, github instance counter
    while True:
        try:
            repo = github_instances[gi_counter].get_repo(repo_name)
            commits = repo.get_commits(until=until_time)
            num_commits = commits.totalCount
            gi_counter += 1  # Point to next available github account for current repo
            for c in commits:
                commit_counter += 1
                if c.sha == commit_id:
                    break
            break
        except github.UnknownObjectException:  # 404 error, repo not found
            result[repo_name] = "Repo Not Found"
            print(f"404 {repo_name} not found")
            repo_log.write("Repo Not Found\n")
            csv_main.close()
            #comments_file.close()
            repo_log.close()
            return
        except github.RateLimitExceededException:  # need to change github account
            if gi_counter < len(github_instances)-1:
                repo = github_instances[gi_counter+1].get_repo(repo_name)
                commits = repo.get_commits(until=until_time)
                num_commits = commits.totalCount
                for c in commits:
                    commit_counter += 1
                    if c.sha == commit_id:
                        break
                print(f"Try to change github account {gi_counter+1}")
                gi_counter += 2  # Point to next available github account for current repo, because gi_counter+1 is used now
                break
            else:
                gi_counter = 0
        except TimeoutError:
            repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
            print(f"Time Out Error sleep for {delay} seconds")
            time.sleep(delay)
        except github.GithubException as githuberror:
            repo_log.write(f"Github error, delay {delay} seconds\n")
            print(f"github error, delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ReadTimeout:  # HTTP read time out
            repo_log.write(f"Http Time Out delay {delay} seconds\n")
            print(f"Http Time Out delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ConnectionError:
            repo_log.write(f"Connect Error delay {delay} seconds\n")
            print(f"Connect Error delay {delay} seconds")
            time.sleep(delay)

    while commit_counter < num_commits:
        try:
            commit = commits[commit_counter]  # current commits
            commit_id = commit.sha
            if commit.author == None:
                commit_counter+= 1
                continue
            else:
                author = commit.author.login
            changed_files = []
            for file in commit.files:
                changed_files.append(file.filename)
            changed_files = " ".join(list(set(changed_files))) if len(changed_files) > 0 else None

            parents = []
            for parent in commit.parents:
                parents.append(parent.sha)
            parents = " ".join(list(set(parents))) if len(parents) > 0 else None


            output_main = [commit_id, author, commit.commit.message, commit.commit.author.date, changed_files,
                           commit.stats.additions, commit.stats.deletions, parents, commit.get_comments().totalCount]
            main_writer.writerow(output_main)
            commit_counter += 1
            msg = f"Current commit {commit_id}, {commit_counter}/{num_commits} done!"
            sys.stdout.write('\r'+msg)
        except github.RateLimitExceededException:  # change Github account
            if gi_counter < len(github_instances):
                repo = github_instances[gi_counter].get_repo(repo_name)
                commits = repo.get_commits(until=until_time)
                gi_counter += 1
                #print("Github account changed!")
                print(f"Try to change github account {gi_counter}")
            else:  # all Github accounts are used
                gi_counter = 0
                while (True):
                    # result[repo_name] = "Not Finished"
                    # print(f"{repo_name} not finished")
                    # continue
                    try:
                        repo = github_instances[gi_counter].get_repo(repo_name)
                        commits = repo.get_commits(until=until_time)
                        gi_counter += 1  # Point to next available github account for current repo
                        print(f"Try to change github account {gi_counter}")
                        break
                    except TimeoutError:
                        repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
                        print(f"Time Out Error sleep for {delay} seconds")
                        time.sleep(delay)
                    except github.GithubException as githuberror:
                        if "Returned object contains no URL" in str(githuberror):
                            repo_log.write(f"skip commit {commit_id}\n")
                            print(f"skip commit {commit_id}\n")
                            commit_counter += 1
                        else:
                            print(f"{str(githuberror)}, delay {delay} seconds for commit {commit_id}")
                            repo_log.write(f"Github error, delay {delay} seconds\n")
                            time.sleep(delay)
                    except github.RateLimitExceededException:  # github instance still not available
                        repo_log.write(
                            f"{repo_name} crawler sleeps {delay} seconds, wait for available github instance\n")
                        print(f"{repo_name} crawler sleeps {delay} seconds, wait for available github instance")
                        time.sleep(delay)
                    except requests.exceptions.ReadTimeout:  # HTTP read time out
                        repo_log.write(f"Http Time Out delay {delay} seconds\n")
                        print(f"Http Time Out delay {delay} seconds")
                        time.sleep(delay)
                    except requests.exceptions.ConnectionError:
                        repo_log.write(f"Connect Error delay {delay} seconds\n")
                        print(f"Connect Error delay {delay} seconds")
                        time.sleep(delay)
        except TimeoutError:
            repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
            print(f"Time Out Error sleep for {delay} seconds")
            time.sleep(delay)
        except github.GithubException as githuberror:
            if "Returned object contains no URL" in str(githuberror):
                repo_log.write(f"skip commit {commit_id}\n")
                print(f"skip commit {commit_id}\n")
                commit_counter += 1
            else:
                print(f"{str(githuberror)}, delay {delay} seconds for commit {commit_id}")
                repo_log.write(f"Github error, delay {delay} seconds\n")
                time.sleep(delay)
        except requests.exceptions.ReadTimeout:  # HTTP read time out
            repo_log.write(f"Http Time Out delay {delay} seconds\n")
            print(f"Http Time Out delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ConnectionError:
            repo_log.write(f"Connect Error delay {delay} seconds\n")
            print(f"Connect Error delay {delay} seconds")
            time.sleep(delay)
    csv_main.close()
    repo_log.close()
    result[repo_name] = "Done"
    print(f"{repo_name} All Done!")


def issue_crawler(repo_name,until_time):
    print(f"Crawling issue reports from {repo_name}...")
    dir = os.path.join(basedir, repo_name.replace('/', '_'))
    if not os.path.exists(dir):  # create a folder for each repo
        os.makedirs(dir)
    csv_main = open(os.path.join(dir, "issue_main.csv"), "w", encoding="utf-8")
    comments_file = open(os.path.join(dir, "issue_comments.txt"), "w", encoding="utf-8")
    repo_log = open(os.path.join(dir, "issue_log.txt"),"w",encoding="utf-8")

    # Info stored into main file and comment file separately
    # Main file has all most of the info and comment file only has comments
    main_writer = csv.writer(csv_main,escapechar='\\')
    # Main file format below, multiple items in a cell are seperated by space, expect for events separated by comma
    main_writer.writerow(["Issue#","Title", "Owner", "Description", "Labels", "Assignees", "Opened time",
                          "Closed time", "Events", "Participants", "Number of Comments"])
    issue_counter, gi_counter = 0, 0  # issue counter, github instance counter
    while True:
        try:
            repo = github_instances[gi_counter].get_repo(repo_name)
            issues = repo.get_issues(state='closed', sort='created')
            gi_counter += 1  # Point to next available github account for current repo
            num_issues = issues.totalCount
            break
        except github.UnknownObjectException:  # 404 error, repo not found
            result[repo_name] = "Repo Not Found"
            print(f"404 {repo_name} not found")
            repo_log.write("Repo Not Found\n")
            repo_log.close()
            csv_main.close()
            comments_file.close()
            return
        except github.RateLimitExceededException:  # need to change github account
            if gi_counter < len(github_instances)-1:
                repo = github_instances[gi_counter+1].get_repo(repo_name)
                issues = repo.get_issues(state='closed', sort='created')
                num_issues = issues.totalCount
                gi_counter += 2  # Point to next available github account for current repo, because gi_counter+1 is used now
                print(f"Github account changed to {gi_counter-1}!")
                repo_log.write("Github account changed!\n")
                break
            else:
                gi_counter = 0
        except TimeoutError:
            repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
            print(f"Time Out Error sleep for {delay} seconds")
            time.sleep(delay)
        except github.GithubException.GithubException:
            repo_log.write(f"503 Service Unavailable, delay {delay} seconds\n")
            print(f"503 Service Unavailable, delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ReadTimeout:  # HTTP read time out
            repo_log.write(f"Http Time Out delay {delay} seconds\n")
            print(f"Http Time Out delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ConnectionError:
            repo_log.write(f"Connect Error delay {delay} seconds\n")
            print(f"Connect Error delay {delay} seconds")
            time.sleep(delay)

    while issue_counter < num_issues:
        try:
            issue = issues[issue_counter]  # current issue
            participants = [issue.user.login]

            # Labels assignees, reviewers are separated by space
            labels = " ".join([label.name for label in issue.labels]) if issue.labels else None
            assignees = " ".join([assignee.login for assignee in issue.assignees]) if issue.assignees else None
            num_comments = 0
            comments_file.write(f"Issue# {issue.number}")
            for comment in issue.get_comments():  # comments under reviewed
                if comment.user:
                    comments_file.write(f"{comment.user.login}({comment.created_at}):{comment.body}\n")
                    num_comments += 1
                    participants.append(comment.user.login)
            events = []  # For events, only user, event and time created are stored
                         # e.g. "cgruber mentioned 2014-11-02 17:55:22"
            for event in issue.get_events():
                if event.actor:
                    events.append(f"{event.actor.login} {event.event} {event.created_at}")
                    participants.append(event.actor.login)
            events = ",".join(events) if len(events) > 0 else None

            participants = " ".join(list(set(participants)))

            output_main = [issue.number, issue.title, issue.user.login, issue.body, labels, assignees,
                           issue.created_at, issue.closed_at, events, participants, num_comments]
            main_writer.writerow(output_main)
            issue_counter += 1
            msg = f"Issue {issue.number}, {round(issue_counter*100/num_issues,2)}% done!"
            sys.stdout.write('\r' + msg)
            repo_log.write(f"Issue {issue.number} done!\n")
        except github.RateLimitExceededException:  # change Github account
            if gi_counter < len(github_instances):
                repo = github_instances[gi_counter].get_repo(repo_name)
                issues = repo.get_issues(state='closed', sort='created')
                gi_counter += 1
                print("Github account changed!")
                repo_log.write("Github account changed!\n")
            else:  # all Github accounts are used
                gi_counter = 0
                while (True):
                    # result[repo_name] = "Not Finished"
                    # print(f"{repo_name} not finished")
                    # continue
                    try:
                        repo = github_instances[gi_counter].get_repo(repo_name)
                        issues = repo.get_issues(state='closed', sort='created')
                        gi_counter += 1  # Point to next available github account for current repo
                        break
                    except TimeoutError:
                        repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
                        print(f"Time Out Error sleep for {delay} seconds")
                        time.sleep(delay)
                    except github.GithubException.GithubException:
                        repo_log.write(f"503 Service Unavailable, delay {delay} seconds\n")
                        print(f"503 Service Unavailable, delay {delay} seconds")
                        time.sleep(delay)
                    except github.RateLimitExceededException:  # github instance still not available
                        repo_log.write(
                            f"{repo_name} crawler sleeps {delay} seconds, wait for available github instance\n")
                        print(f"{repo_name} crawler sleeps {delay} seconds, wait for available github instance")
                        time.sleep(delay)
                    except requests.exceptions.ReadTimeout:  # HTTP read time out
                        repo_log.write(f"Http Time Out delay {delay} seconds\n")
                        print(f"Http Time Out delay {delay} seconds")
                        time.sleep(delay)
                    except requests.exceptions.ConnectionError:
                        repo_log.write(f"Connect Error delay {delay} seconds\n")
                        print(f"Connect Error delay {delay} seconds")
                        time.sleep(delay)
        except TimeoutError:
            repo_log.write(f"Time Out Error sleep for {delay} seconds\n")
            print(f"Time Out Error sleep for {delay} seconds")
            time.sleep(delay)
        except github.GithubException:
            repo_log.write(f"503 Service Unavailable, delay {delay} seconds\n")
            print(f"503 Service Unavailable, delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ReadTimeout:  # HTTP read time out
            repo_log.write(f"Http Time Out delay {delay} seconds\n")
            print(f"Http Time Out delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions.ConnectionError:
            repo_log.write(f"Connect Error delay {delay} seconds\n")
            print(f"Connect Error delay {delay} seconds")
            time.sleep(delay)
        except requests.exceptions:
            repo_log.write(f"Connect Error delay {delay} seconds\n")
            print(f"Connect Error delay {delay} seconds")
            time.sleep(delay)

    csv_main.close()
    comments_file.close()
    result[repo_name] = "Done"
    print(f"{repo_name} All Done!\n")

def repo_info_crawler(repo_names):
    csv_main = open(os.path.join(basedir, "repo_info.csv"), "w", encoding="utf-8")
    main_writer= csv.writer(csv_main,escapechar='\\')
    # Main file format below, multiple items in a cell are seperated by space, expect for events separated by comma
    main_writer.writerow(["Repo Name", "Created at","Developers", "Total PRs", "Total IRs", "Total Commits"])
    gi_counter = 0  # github instance counter
    for repo_name in repo_names:
        try:
            repo = github_instances[gi_counter].get_repo(repo_name)
            developers = repo.get_contributors()
            developers = list(map(lambda x: x.login, developers))
            developers = " ".join(developers) if len(developers) > 0 else None
            main_writer.writerow([repo_name, repo.created_at,developers,repo.get_pulls(state='closed', sort='created').totalCount,
                                  repo.get_issues(state='closed', sort='created').totalCount,repo.get_commits().totalCount])
        except github.RateLimitExceededException:  # change Github account
                while (True):
                    try:
                        gi_counter = gi_counter + 1 if gi_counter < len(github_instances)-1 else 0
                        repo = github_instances[gi_counter+1].get_repo(repo_name)
                        developers = repo.get_contributors()
                        developers = list(map(lambda x: x.login, developers))
                        developers = " ".join(developers) if len(developers) > 0 else None
                        main_writer.writerow([repo_name, repo.created_at, developers, repo.get_pulls(state='closed', sort='created').totalCount,
                                              repo.get_issues(state='closed', sort='created').totalCount, repo.get_commits().totalCount])
                        break
                    except TimeoutError:
                        print(f"Time Out Error sleep for {delay} seconds")
                        time.sleep(delay)
                    except github.GithubException.GithubException:
                        print(f"Http Time Out delay {delay} seconds")
                        time.sleep(delay)
                    except github.RateLimitExceededException:  # github instance still not available
                        print(f"{repo_name} crawler sleeps {delay} seconds, wait for available github instance")
                        time.sleep(delay)
                    except requests.exceptions.ReadTimeout:  # HTTP read time out
                        print(f"Http Time Out delay {delay} seconds")
                        time.sleep(delay)
    csv_main.close()



# Modify these two lines: 
# 1. Add the github authencation tokens. e.g, Github("ghp_1x1x1x1x1x2w2w2w3E3E3E3E4R4R4R4R") 
github_instances = []
# 2. Change the directory of where to save the collected data. Default is the data folder.
basedir = os.path.join(os.path.dirname(__file__),'..','data')

delay = 1
start = time.time()

if not os.path.exists(basedir):  # Create a directory to store all the collected project data 
    os.makedirs(basedir)

repos = ["tensorflow/tensorflow", "pytorch/ptrorch", "apache/mxnet","keras-team/keras","Theano/Theano", "onnx/onnx", "aesara-devs/aesara", "deeplearning4j/deeplearning4j", "scikit-learn/scikit-learn"]
# global variables
for repo_name in repos:
    dir = os.path.join(basedir, repo_name.replace('/', '_'))
    if not os.path.exists(dir):  # create a folder for each repo
        os.makedirs(dir)
    result = dict.fromkeys(repo_name, None)

    gi_counter = 0
    gi_change_counter = 0

    issue_crawler(repo_name,datetime.datetime(2022,5,30))
    pull_request_crawler(repo_name,datetime.datetime(2022,5,30))
    commit_crawler(repo_name,datetime.datetime(2022,5,30))


end = time.time()
print("File stored to "+basedir)
print(f"Total time used: {end-start} s")
