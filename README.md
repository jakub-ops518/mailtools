# MailTools

A collection of command-line utilities for inspecting and troubleshooting email messages.

Currently included:

- parse_eml.py — Parse `.eml` files and extract routing, authentication and message metadata.

---

## Features

- Envelope From / Return-Path
- Header From
- Recipients (To, Cc, Bcc)
- Subject
- Date
- Message-ID
- Mail path (Received headers)
- SPF / DKIM / DMARC summary
- DNS reverse lookup (PTR)
- Delivery timeline
- URL extraction
- Raw header view
- JSON output
- Automatically opens the newest `.eml` file from `~/Downloads`

---

## Requirements

- Python 3.10 or newer

Check your Python version:

```bash
python3 --version
```

No third-party dependencies are required.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/jakub-ops518/mailtools.git
cd mailtools
```

Make the script executable (optional):

```bash
chmod +x tools/parse_eml.py
```

---

## Usage

Parse the newest `.eml` file from your Downloads folder:

```bash
python3 tools/parse_eml.py
```

Parse a specific file:

```bash
python3 tools/parse_eml.py message.eml
```

<<<<<<< HEAD
- DNS lookup is performed only for public IP addresses.
- Authentication results are read from email headers; DKIM is not cryptographically verified.
=======
Display help:

```bash
python3 tools/parse_eml.py --help
```

---

## Examples

Daily summary:

```bash
python3 tools/parse_eml.py --brief
```

Verbose output:

```bash
python3 tools/parse_eml.py --verbose
```

Show the delivery timeline:

```bash
python3 tools/parse_eml.py --timeline
```

Perform DNS lookups:

```bash
python3 tools/parse_eml.py --lookup
```

Extract URLs from the message body:

```bash
python3 tools/parse_eml.py --urls
```

Display raw mail headers:

```bash
python3 tools/parse_eml.py --raw
```

Export parsed information as JSON:

```bash
python3 tools/parse_eml.py --json
```

---

## Sample Output

```text
FILE
----------------------------------------------------------------
File: example.eml

MESSAGE
----------------------------------------------------------------
Subject:          Test message
Date UTC:         2026-06-25 07:15:19 UTC

AUTHENTICATION
----------------------------------------------------------------
SPF:              PASS
DKIM:             PASS
DMARC:            PASS

MAIL PATH
----------------------------------------------------------------
sender.example.com
        |
        v
mx.receiver.net
```

---

## Project Structure

```text
mailtools/
├── docs/
├── samples/
├── tools/
│   ├── parse_eml.py
│   └── mailtools/
│       ├── __init__.py
│       ├── auth.py
│       ├── hops.py
│       ├── lookup.py
│       ├── output.py
│       ├── parser.py
│       ├── urls.py
│       └── utils.py
├── .gitignore
├── LICENSE
└── README.md
```

---

## Roadmap

Planned improvements:

- Attachment inspection
- IOC extraction (IP addresses, domains and URLs)
- HTML body parsing
- Security score
- Attachment hash calculation
- ASN lookup
- WHOIS lookup
- Improved bounce message detection

---

## License

Released under the MIT License.
>>>>>>> c5d8025 (Improve README)
