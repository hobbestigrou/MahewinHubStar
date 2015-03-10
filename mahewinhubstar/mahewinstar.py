import argparse
import ConfigParser
import os
import sys

from colorama import init
from termcolor import colored
from github3 import login


class MahewinStar(object):
    def __init__(self):
        args = self._argument()
        config = self._get_config()
        user = config.get('credentials', 'user')
        password = config.get('credentials', 'password')
        self.username = args.username
        self.project = args.project
        self.star = args.star
        self.follow_user = args.follow
        self.all_project = args.all_project
        self._github = login(user, password)

        init()

    @staticmethod
    def _argument():
        parser = argparse.ArgumentParser(
            description='To follow, star or watch.')

        parser.add_argument(
            'username', metavar='username', type=str,
            help='The username of github')
        parser.add_argument(
            'project', nargs='?', metavar='project', type=str,
            help='The name of the github project')

        parser.add_argument(
            '-f', '--follow', dest='follow', default=None,
            help='To follow the user', action='store_true')
        parser.add_argument(
            '-u', '--unfollow', dest='follow',
            help='To unfollow the user', action='store_false')

        parser.add_argument(
            '-s', '--star', dest='star', default=None,
            help='To star a project', action='store_true')
        parser.add_argument(
            '-n', '--unstar', dest='star',
            help='To unstar a project', action='store_false')
        parser.add_argument(
            '-a', '--all', dest='all_project',
            help='To star or watch all project of user', action='store_true')

        return parser.parse_args()

    @staticmethod
    def _get_config():
        config_file = os.path.expanduser('~/.mhwhstarrc')

        if not os.path.isfile(config_file):
            print 'Need a configuration .mhwhstarrc file in your home'
            sys.exit(1)

        config = ConfigParser.ConfigParser()
        config.read(config_file)

        return config

    def _star_project(self, repository_name):
        if self.star:
            self._github.star(self.username, repository_name)
        else:
            self._github.unstar(self.username, repository_name)

    def run(self):
        if not self._github.user(login=self.username):
            print 'The user {username} not found on github'.format(
                username=self.username)
            sys.exit(1)

        if self.project:
            repository = self._github.repository(self.username, self.project)

            if not repository:
                print 'The project {project} not found on github'.format(
                    project=self.project)
                sys.exit(1)

        if self.follow_user is not None:
            self.follow()

        if self.star is not None:
            self.starred()

    def follow(self, is_follow=True):
        user = self._github.user(login=self.username)

        if not user:
            print 'The user {username} not found on github'.format(
                username=self.username)
            sys.exit(1)

        if self.follow_user:
            self._github.follow(self.username)
        else:
            self._github.unfollow(self.username)

        for follow in self._github.user().iter_following():
            if follow.name == self.username:
                print colored(follow, color='grey', on_color='on_yellow')
            else:
                print follow

    def starred(self):
        all_project = []

        if self.all_project:
            for repository in self._github.iter_user_repos(
                    self.username, type='owner'):
                if not repository.fork:
                    self._star_project(repository.name)
                    all_project.append(repository.name)
        else:
            self._star_project(self.project)
            all_project.append(self.project)

        for star_project in self._github.iter_starred():
            if star_project.name in all_project:
                print colored(star_project, color='grey', on_color='on_yellow')
            else:
                print star_project
