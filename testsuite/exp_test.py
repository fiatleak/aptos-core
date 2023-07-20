import unittest
from test_framework.shell import SpyShell, FakeCommand, RunResult

import os
import imp

from test_framework.git import Git

exp = imp.load_source("exp", os.path.join(os.path.dirname(__file__), "exp"))


class TestExp(unittest.TestCase):
    def test_try_push_new_branch_branch_does_not_exist(self):
        spy_shell = SpyShell(
            [
                FakeCommand(
                    "git rev-parse --verify exp/banana",  # the branch does not exist
                    RunResult(1, b""),
                ),
                FakeCommand(
                    "git checkout -b exp/banana",  # push the branch
                    RunResult(0, b""),
                ),
                FakeCommand(
                    "git push -f origin exp/banana",  # push the branch
                    RunResult(0, b""),
                ),
                FakeCommand(
                    "git checkout banana",
                    RunResult(0, b""),
                ),
            ]
        )
        git = Git(spy_shell)
        exp.try_push_new_branch(git, "banana", "exp/banana")
        spy_shell.assert_commands(self)

    def test_try_push_new_branch_branch_exists(self):
        spy_shell = SpyShell(
            [
                FakeCommand(
                    "git rev-parse --verify exp/banana",  # the branch exists already
                    RunResult(0, b""),
                ),
                FakeCommand(
                    "git branch -D exp/banana",  # the branch exists already
                    RunResult(0, b""),
                ),
                FakeCommand(
                    "git checkout -b exp/banana",  # push the branch
                    RunResult(0, b""),
                ),
                FakeCommand(
                    "git push -f origin exp/banana",  # push the branch
                    RunResult(0, b""),
                ),
                FakeCommand(
                    "git checkout banana",
                    RunResult(0, b""),
                ),
            ]
        )
        git = Git(spy_shell)
        exp.try_push_new_branch(git, "banana", "exp/banana")
        spy_shell.assert_commands(self)

    def test_workflow_dispatch_docker_build(self):
        branch = "banana_branch"
        git_sha = "banana_sha"
        features = "banana_feature1,banana_feature2"
        profile = "banana_performance"
        dry_run = False
        wait = False
        shell = SpyShell([
                FakeCommand(
                    f"gh workflow run {exp.DOCKER_RUST_BUILD_WORKFLOW_NAME} --ref {branch} --field GIT_SHA={git_sha} --field FEATURES={features} --field PROFILE={profile} --field BUILD_ADDL_TESTING_IMAGES=true",  # the branch exists already
                    RunResult(0, b""),
                ),
        ])
        exp.workflow_dispatch_docker_build(
            shell, branch, git_sha, features, profile, dry_run, wait
        )
        shell.assert_commands(self)