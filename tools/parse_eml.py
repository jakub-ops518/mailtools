#!/usr/bin/env python3
import sys
import json
import argparse
from pathlib import Path
from mailtools import __version__
from mailtools.parser import parse_eml
from mailtools.output import print_default, print_brief, print_verbose, print_timeline, print_lookup, print_urls, print_raw


def newest_eml_from_downloads():
    downloads = Path.home() / 'Downloads'
    files = list(downloads.glob('*.eml'))
    if not files:
        raise FileNotFoundError(f'No .eml file found in {downloads}')
    return max(files, key=lambda p: p.stat().st_mtime)


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description='Parse an EML file and extract sender, recipients, mail path, SPF/DKIM/DMARC, DNS lookup data, URLs, timeline and message status.',
        epilog=(
            'Examples:\n'
            '  parse_eml.py\n'
            '  parse_eml.py message.eml\n'
            '  parse_eml.py --brief\n'
            '  parse_eml.py --verbose\n'
            '  parse_eml.py --timeline\n'
            '  parse_eml.py --lookup\n'
            '  parse_eml.py --urls\n'
            '  parse_eml.py --raw\n'
            '  parse_eml.py --json --urls --lookup'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('eml', nargs='?', help='Path to an .eml file. If omitted, the newest .eml file from ~/Downloads is used.')
    parser.add_argument('--brief', action='store_true', help='Show a short daily-use summary.')
    parser.add_argument('--verbose', action='store_true', help='Show detailed mail hop information.')
    parser.add_argument('--timeline', action='store_true', help='Show timestamps and delivery delay between mail hops.')
    parser.add_argument('--lookup', action='store_true', help='Run DNS lookups for public IP addresses in the mail path.')
    parser.add_argument('--urls', action='store_true', help='Extract and show URLs found in the email body.')
    parser.add_argument('--raw', action='store_true', help='Show raw Received and authentication headers.')
    parser.add_argument('--json', action='store_true', help='Output the result as JSON.')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    try:
        eml_path = Path(args.eml).expanduser() if args.eml else newest_eml_from_downloads()
        if not eml_path.exists():
            raise FileNotFoundError(f'File does not exist: {eml_path}')
        data = parse_eml(eml_path, include_urls=args.urls, include_lookup=args.lookup)
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return
        if args.brief:
            print_brief(data)
        elif args.verbose:
            print_verbose(data)
        else:
            print_default(data)
        if args.timeline:
            print_timeline(data)
        if args.lookup:
            print_lookup(data)
        if args.urls:
            print_urls(data)
        if args.raw:
            print_raw(data)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
