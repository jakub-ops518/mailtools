# mailtools

Small command-line utilities for inspecting and troubleshooting email.

## Tool: parse_eml.py

`parse_eml.py` parses `.eml` files and extracts message metadata, senders, recipients, mail path, SPF/DKIM/DMARC results, optional DNS lookups, URLs, raw headers, and a delivery timeline.

## Usage

```bash
python3 tools/parse_eml.py
python3 tools/parse_eml.py message.eml
python3 tools/parse_eml.py --brief
python3 tools/parse_eml.py --verbose
python3 tools/parse_eml.py --timeline
python3 tools/parse_eml.py --lookup
python3 tools/parse_eml.py --urls
python3 tools/parse_eml.py --raw
python3 tools/parse_eml.py --json --urls --lookup
python3 tools/parse_eml.py --version
```

If no `.eml` path is supplied, the newest `.eml` file from `~/Downloads` is used.

## Notes

- DNS lookup is performed only for public IP addresses.
- Authentication results are read from email headers; DKIM is not cryptographically verified.
