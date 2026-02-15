#!/usr/bin/env python3
"""PartsBox Files API operations.

Subcommands: url, download
Files are accessed via GET to https://partsbox.com/files/{file_id}
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import api_download, output_success, output_error, output_json

FILES_BASE_URL = "https://partsbox.com/files"


def cmd_url(args):
    """Get download URL for a file without downloading it."""
    url = f"{FILES_BASE_URL}/{args.file_id}"
    output_success({"file_id": args.file_id, "url": url})


def cmd_download(args):
    """Download a file to the local filesystem."""
    url = f"{FILES_BASE_URL}/{args.file_id}"
    response = api_download(url)

    content_type = response.headers.get("Content-Type", "")

    # Determine filename
    filename = args.output
    if not filename:
        # Try to extract from Content-Disposition header
        cd = response.headers.get("Content-Disposition", "")
        if "filename=" in cd:
            parts = cd.split("filename=")
            if len(parts) > 1:
                filename = parts[1].strip("'\"")

        if not filename:
            # Generate from file_id and content type
            ext = content_type.split("/")[-1].split(";")[0] if content_type else "bin"
            filename = f"{args.file_id}.{ext}"

    with open(filename, "wb") as f:
        f.write(response.content)

    output_success(
        {
            "file_id": args.file_id,
            "path": os.path.abspath(filename),
            "size_bytes": len(response.content),
            "content_type": content_type,
        }
    )


def main():
    parser = argparse.ArgumentParser(description="PartsBox Files API")
    sub = parser.add_subparsers(dest="command", required=True)

    # url
    p = sub.add_parser("url", help="Get download URL for a file")
    p.add_argument("--file-id", dest="file_id", required=True, help="File ID from part data")

    # download
    p = sub.add_parser("download", help="Download a file to disk")
    p.add_argument("--file-id", dest="file_id", required=True, help="File ID from part data")
    p.add_argument("--output", "-o", help="Output file path (auto-detected if omitted)")

    args = parser.parse_args()
    commands = {"url": cmd_url, "download": cmd_download}
    commands[args.command](args)


if __name__ == "__main__":
    main()
