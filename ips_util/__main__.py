from ips_util import Patch
import argparse
import sys

def cmd_apply(args):
    patch = Patch.load(args.ips_file)

    in_file = None
    with open(args.in_file, 'rb') as f:
        in_file = f.read()

    out_file = patch.apply(in_file)

    if 'out_file' in args:
        with open(args.out_file, 'w+b') as f:
            f.write(out_file)
    else:
        sys.stdout.buffer.write(out_file)

def main():
    parser = argparse.ArgumentParser()
    parser.prog = 'ips_util'
    parser.description = 'Utilities for working with IPS (International Patching System) patch files.'

    subparsers = parser.add_subparsers(help='Specify a command.')

    # Workaround for https://bugs.python.org/issue9253
    subparsers.required = True
    subparsers.dest = 'command'

    apply_parser = subparsers.add_parser('apply', help='Apply a patch to a file.')

    apply_parser.add_argument('ips_file', help='The IPS file containing the patch to be applied.')
    apply_parser.add_argument('in_file', help='The file to apply the patch to.')
    apply_parser.add_argument('--output', '-o', dest='out_file', help='The file to write the patched data to. If not specified, the patched data will be sent to stdout.')
    apply_parser.set_defaults(func=cmd_apply)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()