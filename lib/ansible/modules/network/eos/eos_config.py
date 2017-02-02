#!/usr/bin/python
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

ANSIBLE_METADATA = {
    'status': ['preview'],
    'supported_by': 'core',
    'version': '1.0'
}

DOCUMENTATION = """
---
module: eos_config
version_added: "2.1"
author: "Peter Sprygada (@privateip)"
short_description: Manage Arista EOS configuration sections
description:
  - Arista EOS configurations use a simple block indent file syntax
    for segmenting configuration into sections.  This module provides
    an implementation for working with eos configuration sections in
    a deterministic way.  This module works with either CLI or eAPI
    transports.
extends_documentation_fragment: eos_local
options:
  lines:
    description:
      - The ordered set of commands that should be configured in the
        section.  The commands must be the exact same commands as found
        in the device running-config.  Be sure to note the configuration
        command syntax as some commands are automatically modified by the
        device config parser.
    required: false
    default: null
  parents:
    description:
      - The ordered set of parents that uniquely identify the section
        the commands should be checked against.  If the parents argument
        is omitted, the commands are checked against the set of top
        level or global commands.
    required: false
    default: null
  src:
    description:
      - The I(src) argument provides a path to the configuration file
        to load into the remote system.  The path can either be a full
        system path to the configuration file if the value starts with /
        or relative to the root of the implemented role or playbook.
        This argument is mutually exclusive with the I(lines) and
        I(parents) arguments.
    required: false
    default: null
    version_added: "2.2"
  before:
    description:
      - The ordered set of commands to push on to the command stack if
        a change needs to be made.  This allows the playbook designer
        the opportunity to perform configuration commands prior to pushing
        any changes without affecting how the set of commands are matched
        against the system.
    required: false
    default: null
  after:
    description:
      - The ordered set of commands to append to the end of the command
        stack if a change needs to be made.  Just like with I(before) this
        allows the playbook designer to append a set of commands to be
        executed after the command set.
    required: false
    default: null
  match:
    description:
      - Instructs the module on the way to perform the matching of
        the set of commands against the current device config.  If
        match is set to I(line), commands are matched line by line.  If
        match is set to I(strict), command lines are matched with respect
        to position.  If match is set to I(exact), command lines
        must be an equal match.  Finally, if match is set to I(none), the
        module will not attempt to compare the source configuration with
        the running configuration on the remote device.
    required: false
    default: line
    choices: ['line', 'strict', 'exact', 'none']
  replace:
    description:
      - Instructs the module on the way to perform the configuration
        on the device.  If the replace argument is set to I(line) then
        the modified lines are pushed to the device in configuration
        mode.  If the replace argument is set to I(block) then the entire
        command block is pushed to the device in configuration mode if any
        line is not correct.
    required: false
    default: line
    choices: ['line', 'block', 'config']
  force:
    description:
      - The force argument instructs the module to not consider the
        current devices running-config.  When set to true, this will
        cause the module to push the contents of I(src) into the device
        without first checking if already configured.
      - Note this argument should be considered deprecated.  To achieve
        the equivalent, set the C(match=none) which is idempotent.  This argument
        will be removed in a future release.
    required: false
    default: false
    choices: ['yes', 'no']
  backup:
    description:
      - This argument will cause the module to create a full backup of
        the current C(running-config) from the remote device before any
        changes are made.  The backup file is written to the C(backup)
        folder in the playbook root directory.  If the directory does not
        exist, it is created.
    required: false
    default: no
    choices: ['yes', 'no']
    version_added: "2.2"
  config:
    description:
      - The module, by default, will connect to the remote device and
        retrieve the current running-config to use as a base for comparing
        against the contents of source.  There are times when it is not
        desirable to have the task get the current running-config for
        every task in a playbook.  The I(config) argument allows the
        implementer to pass in the configuration to use as the base
        config for comparison.
    required: false
    default: null
  defaults:
    description:
      - The I(defaults) argument will influence how the running-config
        is collected from the device.  When the value is set to true,
        the command used to collect the running-config is append with
        the all keyword.  When the value is set to false, the command
        is issued without the all keyword
    required: false
    default: false
    version_added: "2.2"
  save:
    description:
      - The C(save) argument instructs the module to save the
        running-config to startup-config.  This operation is performed
        after any changes are made to the current running config.  If
        no changes are made, the configuration is still saved to the
        startup config.  This option will always cause the module to
        return changed.
    required: false
    default: false
    version_added: "2.2"
"""

EXAMPLES = """
- eos_config:
    lines: hostname {{ inventory_hostname }}

- eos_config:
    lines:
      - 10 permit ip 1.1.1.1/32 any log
      - 20 permit ip 2.2.2.2/32 any log
      - 30 permit ip 3.3.3.3/32 any log
      - 40 permit ip 4.4.4.4/32 any log
      - 50 permit ip 5.5.5.5/32 any log
    parents: ip access-list test
    before: no ip access-list test
    match: exact

- eos_config:
    lines:
      - 10 permit ip 1.1.1.1/32 any log
      - 20 permit ip 2.2.2.2/32 any log
      - 30 permit ip 3.3.3.3/32 any log
      - 40 permit ip 4.4.4.4/32 any log
    parents: ip access-list test
    before: no ip access-list test
    replace: block

- name: load configuration from file
  eos_config:
    src: eos.cfg
"""

RETURN = """
commands:
  description: The set of commands that will be pushed to the remote device
  returned: Only when lines is specified.
  type: list
  sample: ['hostname switch01', 'interface Ethernet1', 'no shutdown']
backup_path:
  description: The full path to the backup file
  returned: when backup is yes
  type: path
  sample: /playbooks/ansible/backup/eos_config.2016-07-16@22:28:34
start:
  description: The time the job started
  returned: always
  type: str
  sample: "2016-11-16 10:38:15.126146"
end:
  description: The time the job ended
  returned: always
  type: str
  sample: "2016-11-16 10:38:25.595612"
delta:
  description: The time elapsed to perform all operations
  returned: always
  type: str
  sample: "0:00:10.469466"
"""
from functools import partial

from ansible.module_utils import eos
from ansible.module_utils import eos_local
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.local import LocalAnsibleModule
from ansible.module_utils.netcfg import NetworkConfig, dumps

SHARED_LIB = 'eos'

def get_ansible_module():
    if SHARED_LIB == 'eos':
        return LocalAnsibleModule
    return AnsibleModule

def invoke(name, *args, **kwargs):
    obj = globals().get(SHARED_LIB)
    func = getattr(obj, name)
    return func(*args, **kwargs)

run_commands = partial(invoke, 'run_commands')
get_config = partial(invoke, 'get_config')
load_config = partial(invoke, 'load_config')
supports_sessions = partial(invoke, 'supports_sessions')

def check_args(module, warnings):
    if SHARED_LIB == 'eos_local':
        eos_local.check_args(module)

    if module.params['force']:
        warnings.append('The force argument is deprecated, please use '
                        'match=none instead.  This argument will be '
                        'removed in the future')

    if not supports_sessions(module):
        warnings.append('The current version of EOS on the remote device does '
                        'not support configuration sessions.  The commit '
                        'argument will be ignored')

def get_candidate(module):
    candidate = NetworkConfig(indent=3)
    if module.params['src']:
        candidate.load(module.params['src'])
    elif module.params['lines']:
        parents = module.params['parents'] or list()
        candidate.add(module.params['lines'], parents=parents)
    return candidate

def run(module, result):
    match = module.params['match']
    replace = module.params['replace']

    candidate = get_candidate(module)

    if match != 'none' and replace != 'config':
        config_text = get_config(module)
        config = NetworkConfig(indent=3, contents=config_text)
        configobjs = candidate.difference(config, match=match, replace=replace)
    else:
        configobjs = candidate.items

    if configobjs:
        commands = dumps(configobjs, 'commands').split('\n')

        if module.params['lines']:
            if module.params['before']:
                commands[:0] = module.params['before']

            if module.params['after']:
                commands.extend(module.params['after'])

        result['commands'] = commands

        replace = module.params['replace'] == 'config'
        commit = not module.check_mode

        response = load_config(module, commands, replace=replace, commit=commit)
        if 'diff' in response:
            result['diff'] = {'prepared': response['diff']}
        if 'session' in response:
            result['session'] = response['session']

        result['changed'] = True

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        src=dict(type='path'),

        lines=dict(aliases=['commands'], type='list'),
        parents=dict(type='list'),

        before=dict(type='list'),
        after=dict(type='list'),

        match=dict(default='line', choices=['line', 'strict', 'exact', 'none']),
        replace=dict(default='line', choices=['line', 'block', 'config']),

        defaults=dict(type='bool', default=False),

        backup=dict(type='bool', default=False),
        save=dict(default=False, type='bool'),

        # deprecated arguments (Ansible 2.3)
        config=dict(),
        # this argument is deprecated in favor of setting match: none
        # it will be removed in a future version
        force=dict(default=False, type='bool'),
    )

    argument_spec.update(eos_local.eos_local_argument_spec)

    mutually_exclusive = [('lines', 'src')]

    required_if = [('match', 'strict', ['lines']),
                   ('match', 'exact', ['lines']),
                   ('replace', 'block', ['lines']),
                   ('replace', 'config', ['src'])]

    cls = get_ansible_module()

    module = cls(argument_spec=argument_spec,
                 mutually_exclusive=mutually_exclusive,
                 required_if=required_if,
                 supports_check_mode=True)

    if module.params['force'] is True:
        module.params['match'] = 'none'

    warnings = list()
    check_args(module, warnings)

    result = {'changed': False}
    if warnings:
        result['warnings'] = warnings

    if module.params['backup']:
        result['__backup__'] = get_config(module)

    if any((module.params['src'], module.params['lines'])):
        run(module, result)

    if module.params['save']:
        if not module.check_mode:
            run_commands(module, ['copy running-config startup-config'])
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    SHARED_LIB = 'eos_local'
    main()
