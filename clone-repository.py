#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-
import traceback
import os
import shutil
import tempfile
from datetime import datetime as dt
import sys
import git
from git import Repo
import time
from github import Github
import datetime

os.environ["GIT_PYTHON_REFRESH"] = "quiet"


def scan_repo(github, repo_name):
    project_path = tempfile.mkdtemp()
    project_name = "chuphalashit19/" + repo_name
    df = "%Y-%m-%d %H:%M:%S"

    try:
        # repo = clone_repository(repo_url, repo_path, bare=True)  # Clones a bare repository
        Repo.clone_from(github + repo_name + '.git', project_path)

    except git.exc.GitCommandError as exception:
        print(exception)

    already_searched_pair_of_hashes, latest_hash_per_branch = set(), {}
    repo = Repo(project_path)
    owner_name, repo_name = project_name.split("/")
    print('Ownername: {}   RepoName: {}'.format(owner_name, repo_name))

    remote_branches = None
    try:
        remote_branches = repo.remotes.origin.fetch()
        print('Remote Branches:', remote_branches)
    except git.exc.GitCommandError as exception:
        print(exception)
        return

    if not remote_branches:
        return

    for remote_branch in remote_branches:
        try:
            remote_branch_name = remote_branch.name.split("/")[1].replace(".", "_")
        except:
            print("Skipping Branch : {} Due to name splitting exception.".format(remote_branch.name))
            continue

        prev_commit, commits = None, None
        try:
            custom_commit_range = repo.iter_commits(rev=remote_branch.name, max_count=1)
        except git.exc.GitCommandNotFound:
            print("git.exc.GitCommandNotFound " + project_name)
            continue
        next_commit = next(custom_commit_range)
        if not next_commit:
            continue
        last_hash = next_commit.hexsha
        commit_range = last_hash
        commits = repo.iter_commits(rev=commit_range)

        try:
            commits = repo.iter_commits(rev=remote_branch.name, max_count=10000)

        except git.exc.GitCommandNotFound as exception:
                print(exception + project_name)
                continue
        try:
            for curr_commit in commits:
                if not prev_commit:
                    pass
                else:
                    latest_hash_per_branch[remote_branch_name] = curr_commit.hexsha
                    hashes = str(prev_commit) + str(curr_commit)
                    if hashes in already_searched_pair_of_hashes:
                        prev_commit = curr_commit
                        continue
                    already_searched_pair_of_hashes.add(hashes)
                    try:
                        diff = prev_commit.diff(curr_commit, create_patch=True)
                    except (ValueError, MemoryError, git.exc.GitCommandError):
                        print('Exception to find the difference between commits')

                prev_commit = curr_commit

        except Exception as exception:
            print(exception)
    
    date_scanned = dt.utcnow().strftime(df)
    print('Date Scanned:', date_scanned)


def scan():
    repos_scanned = []

    username = "chuphalashit19"
    g = Github()
    user = g.get_user(username)
    for repo in user.get_repos():
        start = datetime.datetime.now()
        repo_name = repo.name
        repos_scanned.append(repo_name)
        scan_repo("https://github.com/chuphalashit19/", repo_name)
        print('Time taken to scan repo:', datetime.datetime.now()-start)
        print()

    print("Scanned Repos: ", repos_scanned)


if __name__ == '__main__':
    try:
        print('Starting Execution')
        scan()
        time.sleep(5)
        print('Completed')
        print('Ending Execution')
    except:
        print('Error in Scanning: ' + str(sys.exc_info()))
        print(traceback.format_exc())
