#!/usr/bin/env python3

'''
Parse docker-compose.yml and start telepresence for the specified service
'''

import itertools
import subprocess
import sys
from argparse import ArgumentParser

import prompter
import yaml


def main(args):
    with open(args.composefile) as file:
        compose_file = yaml.load(file)
    if not args.service in compose_file['services']:
        sys.exit('Service {} not found in {}'.format(args.service, compose_file['services'].keys()))
    image = compose_file['services'][args.service]['image']
    volumes = compose_file['services'][args.service]['volumes']
    volume_list = itertools.chain.from_iterable(zip(itertools.repeat('-v', len(volumes)), volumes))
    # create command to run
    cmd = ['telepresence']
    if args.swap:
        cmd.extend(['--swap-deployment', args.service])
    cmd.extend(['--expose', '80'])
    cmd.extend(['--mount', 'false'])
    if len(compose_file['services'][args.service]['env_file']):
        cmd.extend(['--env-file', compose_file['services'][args.service]['env_file'][0]])
    # now all the rest is docker config
    cmd.extend(['--docker-run', '--rm', '-it'])
    cmd.extend(volume_list)
    cmd.append(image)
    # finally we run it
    print('Your service will be locally accessible at http://telepresence-local.docker/{}/'.format(args.service))
    if prompter.yesno('Run {} in telepresence?'.format(args.service)):
        subprocess.run(cmd)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--service', help='Service name to start', required=True)
    parser.add_argument('-S', '--swap', help='Should we replace the service?', default=False, action='store_true')
    parser.add_argument('composefile', help='Path to docker-compose.yml')
    args = parser.parse_args()
    main(args)
