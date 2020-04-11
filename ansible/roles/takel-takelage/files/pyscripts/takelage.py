#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
import re
import subprocess


class Status(object):
    _RED = '125'
    _GREEN = '46'
    _BLUE = '38'

    def __init__(self):
        self.args = self._parse_args_()
        self._takelage_status = self._get_status_takelage_()
        self._tau_status = self._get_status_tau_()
        self._gpg_status = self._get_status_gpg_()
        self._ssh_status = self._get_status_ssh_()
        self._gopass_status = self._get_status_gopass_()
        self._git_status = self._get_status_git_()

    def print_header(self):
        header_ver = []
        header_ok = []
        header_error = []

        # takelage version
        if self._takelage_status['returncode'] == 0:
            header_ver.append(
                self._get_header_success_('takelage',
                                          self._takelage_status['version']))
        else:
            header_error.append(
                self._get_header_error_('takelage version: '))

        # tau version
        if self._tau_status['returncode'] == 0:
            header_ver.append(
                self._get_header_success_('tau',
                                          self._tau_status['version']))
        else:
            header_error.append(
                self._get_header_error_('tau version:      '))

        # git config
        if self._git_status['returncode'] == 0:
            header_ok.append(
                self._get_header_success_('git', 'ok'))
        else:
            header_error.append(
                self._get_header_error_('git config status:'))

        # gopass config
        if self._gopass_status['returncode'] == 0:
            header_ok.append(
                self._get_header_success_('gopass', 'ok'))
        else:
            header_error.append(
                self._get_header_error_('gopass status:    '))

        # gpg agent
        if self._gpg_status['returncode'] == 0:
            header_ok.append(
                self._get_header_success_('gpg', 'ok'))
        else:
            header_error.append(
                self._get_header_error_('gpg agent status: '))

        # ssh agent
        if self._ssh_status['returncode'] == 0:
            header_ok.append(
                self._get_header_success_('ssh', 'ok'))
        else:
            header_error.append(
                self._get_header_error_('ssh agent status: '))

        if len(header_ok) > 0:
            header_ok.append(
                self._get_header_success_('for details run', 'takelage'))

        if len(header_ver + header_ok) > 0:
            print(' | '.join(header_ver + header_ok))

        if len(header_error) > 0:
            print("\n".join(header_error).strip())

    def print_status_git(self):
        if self._git_status['returncode'] == 0:
            print('git config status: \t' +
                  self._display_colored_text_(
                      self._GREEN, 'available'))
            if not self.args.short:
                print('git config:')
                print('\tname: \t\t' +
                      self._display_colored_text_(
                          self._BLUE, self._git_status['name']))
                print('\te-mail: \t' +
                      self._display_colored_text_(
                          self._BLUE, self._git_status['mail']))
                print('\tgpg signingkey: ' +
                      self._display_colored_text_(
                          self._BLUE, self._git_status['gpg-key']))

    def print_status_gopass(self):
        used_gpg_keys = []
        for key in self._gopass_status['keys']:
            for own_key in self._gpg_status['keys']:
                if key in own_key and own_key not in used_gpg_keys:
                    used_gpg_keys.append(own_key)
        if self._gopass_status['returncode'] == 0 and len(used_gpg_keys) > 0:
            print('gopass cfg status: \t' +
                  self._display_colored_text_(
                      self._GREEN, 'available'))
            if not self.args.short:
                print('used gpg-keys:')
                for key in used_gpg_keys:
                    print('\t\t\t' + self._display_colored_text_(
                        self._BLUE, key))

    def print_status_gpg(self):
        if self._gpg_status['returncode'] == 0:
            print('gpg agent status: \t' +
                  self._display_colored_text_(
                      self._GREEN, 'available'))
            if not self.args.short:
                print('available gpg keys:')
                for key in self._gpg_status['keys']:
                    print('\t\t\t' + self._display_colored_text_(
                        self._BLUE, key))

    def print_status_ssh(self):
        if self._ssh_status['returncode'] == 0:
            print('ssh agent status: \t' +
                  self._display_colored_text_(
                      self._GREEN, 'available'))
            if not self.args.short:
                print('available ssh keys:')
                for key in self._ssh_status['keys']:
                    print('\t\t\t' + self._display_colored_text_(
                        self._BLUE, key))

    def _display_colored_text_(self, color, text):
        colored_text = f'\033[38;5;{color}m{text}\033[00m'
        return colored_text

    def _get_header_error_(self, section):
        header_error = section + '\t'
        header_error += self._display_colored_text_(
            self._RED, 'not available')
        return header_error

    def _get_header_success_(self, section, result):
        header_success = section + ': '
        header_success += self._display_colored_text_(
            self._GREEN, result)
        return header_success

    def _get_status_git_(self):
        _git_status = {
            'returncode': -1,
            'name': None,
            'mail': None,
            'gpg-key': None}
        command = ['git', 'config', '--list']
        git_result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        if git_result.returncode == 0:
            result = git_result.stdout.decode('UTF-8')
            git_name_search = re.search(r'user\.name=(.*)', result)
            git_mail_search = re.search(r'user\.email=(.*)', result)
            git_gpg_search = re.search(r'user\.signingkey=(.*)', result)
            if git_mail_search is not None and \
                    git_mail_search.group(1) is not None:
                _git_status['mail'] = git_mail_search.group(1)
            if git_name_search is not None and \
                    git_name_search.group(1) is not None:
                _git_status['name'] = git_name_search.group(1)
            if git_gpg_search is not None and \
                    git_gpg_search.group(1) is not None:
                gpg_fingerprint = git_gpg_search.group(1)
                for key in self._gpg_status['keys']:
                    if gpg_fingerprint in key:
                        _git_status['gpg-key'] = key
            if _git_status['name'] is not None and \
                    _git_status['mail'] is not None:
                _git_status['returncode'] = 0
            return _git_status

    def _get_status_gopass_(self):
        _gopass_status = {'returncode': None,
                          'keys': []}

        command = ['gopass', 'recipients']
        gopass_add_result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        _gopass_status['returncode'] = gopass_add_result.returncode

        if gopass_add_result.returncode == 0:
            gopass_keys_string = gopass_add_result.stdout.decode('utf-8')
            keys = re.findall(r'0x(.*?) -', gopass_keys_string)
            _gopass_status['keys'] = keys
        else:
            print('stderr:')
            print(gopass_add_result.stderr)

        return _gopass_status

    def _get_status_gpg_(self):
        gpg_status = {
            'returncode': None,
            'keys': []}

        command = ['gpg', '--list-secret-keys']
        gpg_list_result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        gpg_returncode = gpg_list_result.returncode

        if gpg_returncode == 0:
            gpg_keys_string = gpg_list_result.stdout.decode('utf-8')

            keys = re.findall(r'sec(.*)\n(.*)\nuid(.*)', gpg_keys_string)
            for key in keys:
                key_info = ''.join(
                    key[0].strip() + ': ' +
                    key[1].strip() + ' - ' + key[2].strip())
                gpg_status['keys'].append(key_info)

            if keys:
                key_id = keys[0][1].strip()
                command = [
                    'bash -c "set -o pipefail && echo "test" | ' +
                    'gpg --sign --local-user ' +
                    key_id + '"']
                gpg_encrypt_result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True)
                gpg_status['returncode'] = gpg_encrypt_result.returncode
            else:
                gpg_status['returncode'] = 1

        return gpg_status

    def _get_status_ssh_(self):
        _ssh_status = {'returncode': None,
                       'keys': []}

        command = 'SSH_AUTH_SOCK=~/.gnupg/S.gpg-agent.ssh ssh-add -l'
        ssh_add_result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        _ssh_status['returncode'] = ssh_add_result.returncode
        if ssh_add_result.returncode == 0:
            ssh_keys_string = ssh_add_result.stdout.decode('utf-8').strip('\n')
            ssh_keys_list = ssh_keys_string.split('\n')
            _ssh_status['keys'] = ssh_keys_list

        return _ssh_status

    def _get_status_takelage_(self):
        _takelage_status = {'returncode': 0,
                            'version': 'none'}

        try:
            takelage_version_file = Path('/etc/takelage_version')
            _takelage_status['version'] = \
                takelage_version_file.read_text().strip()
        except OSError:
            import sys
            print(sys.exc_info()[0])
            _takelage_status['returncode'] = 1

        return _takelage_status

    def _get_status_tau_(self):
        _tau_status = {'returncode': 0,
                       'version': 'none'}

        try:
            command = ['/usr/local/rvm/wrappers/default/tau', 'version']
            tau_version_result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            _tau_status['version'] = \
                tau_version_result.stdout.decode('utf-8').strip()
        except OSError:
            _tau_status['returncode'] = 1

        return _tau_status

    def _parse_args_(self):
        parser = ArgumentParser()
        parser.add_argument(
            "--short",
            dest="short",
            action="store_true",
            default=False,
            help="Display only the status.")
        return parser.parse_args()


def main():
    status = Status()
    status.print_header()
    if not status.args.short:
        status.print_status_git()
        status.print_status_gopass()
        status.print_status_gpg()
        status.print_status_ssh()


if __name__ == "__main__":
    main()