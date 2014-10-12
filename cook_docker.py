#!/usr/bin/python3

import os
import sys
import pystache
import shutil
import json
import subprocess


def transform_file(template='', outfile='', data=''):
    mst_file = open(template, 'r')
    mst_content = mst_file.read()
    mst_file.close()
    rendered = pystache.render(mst_content, data)
    output_file = open(outfile, 'w')
    output_file.write(rendered)
    output_file.close()


def read_config(working_dir=None):
    config_file_path = working_dir + '/' + 'make.json'
    config_file = open(config_file_path, 'r')
    config_content = config_file.read()
    config_file.close()
    output = json.loads(config_content)
    return output


def build(kitchen_home, working_dir):
    target_dir = working_dir + '/' + 'target'

    print("Kitchen home: " + kitchen_home)
    print("Working dir: " + working_dir)
    print("Target dir: " + target_dir)

    data = read_config(working_dir)

    dockerfile_mst = kitchen_home + '/' + 'Dockerfile.mst'
    entry_mst = kitchen_home + '/' + 'entry.sh.mst'
    script_mst = working_dir + '/' + 'script.sh.mst'
    start_mst = kitchen_home + '/' + 'start.py.mst'
    ssh_mst = kitchen_home + '/' + 'access_ssh.sh.mst'

    dockerfile_output = target_dir + '/' + 'Dockerfile'
    entry_output = target_dir + '/' + 'entry.sh'
    script_output = target_dir + '/' + 'script.sh'
    start_output = target_dir + '/' + 'start_' + data['image_name'] + '.py'
    ssh_output = target_dir + '/' + 'ssh_' + data['image_name'] + '.sh'

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    os.mkdir(target_dir)

    transform_file(dockerfile_mst, dockerfile_output, data)
    transform_file(entry_mst, entry_output, data)
    transform_file(script_mst, script_output, data)
    transform_file(start_mst, start_output, data)
    transform_file(ssh_mst, ssh_output, data)

    subprocess.call(['chmod', '755', start_output])
    subprocess.call(['chmod', '755', ssh_output])

    subprocess.call(['cp', data['ssh_public_key'], target_dir + '/' + 'key.pub'])

    for f in data['files']:
        subprocess.call(['cp', f, target_dir + '/' + f])

    subprocess.call(['docker', 'build', '-t', data['image_name'], target_dir])


def pack(kitchen_home, working_dir):
    config = read_config(working_dir)
    return


def main():
    if len(sys.argv) < 2:
        print("Usage: cook_docker.py action")
        return

    action = sys.argv[1]

    kitchen_home = os.environ.get('DOCKER_KITCHEN_HOME')
    if kitchen_home is None:
        print('Please define DOCKER_KITCHEN_HOME variable')
        exit(1)

    working_dir = os.getcwd()

    if action == 'build':
        build(kitchen_home, working_dir)
    elif action == 'pack':
        pack(kitchen_home, working_dir)


if __name__ == '__main__':
    main()



