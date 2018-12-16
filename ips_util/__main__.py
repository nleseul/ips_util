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

def cmd_trace(args):
    patch = Patch.load(args.ips_file)
    patch.trace()

def cmd_create(args):
    source_file = None
    target_file = None
    with open(args.source_file, 'rb') as f:
        source_file = f.read()
    with open(args.target_file, 'rb') as f:
        target_file = f.read()

    patch = Patch.create(source_file, target_file)

    if args.out_file is not None:
        with open(args.out_file, 'w+b') as f:
            f.write(patch.encode())
    else:
        sys.stdout.buffer.write(patch.encode())

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

    trace_parser = subparsers.add_parser('trace', help='Trace the contents of a patch file.')
    trace_parser.add_argument('ips_file', help='The IPS file containing the patch to be traced.')
    trace_parser.set_defaults(func=cmd_trace)

    create_parser = subparsers.add_parser('create', help='Create a patch file based on differences between a source and target file.')
    create_parser.add_argument('source_file', help="The original, unpatched file.")
    create_parser.add_argument('target_file', help="The file containing differences from the original from which a patch should be created.")
    create_parser.add_argument('--output', '-o', dest='out_file', help='The file to which the patch should be written. If not specified, the patch will be sent to stdout.')
    create_parser.set_defaults(func=cmd_create)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()