#!/usr/bin/env python3
#
#   Copyright 2026 The Pixel Minimal Watch Face contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""Validates watch face XML files against the Watch Face Format XSD (XSD 1.1, needs `pip install xmlschema`).

The XSD files come from https://github.com/google/watchface (third_party/wff/specification/documents).

Usage: python3 validate_watchface.py <xsd documents dir> <format version> <watchface.xml>...
"""
import sys

import xmlschema


def main():
    xsd_dir, version, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    schema = xmlschema.XMLSchema11("%s/%s/watchface.xsd" % (xsd_dir, version))
    valid = True
    for path in files:
        errors = list(schema.iter_errors(path))
        print("%s: %d error(s)" % (path, len(errors)))
        for error in errors[:15]:
            print("  -", error.path, ":", (error.reason or str(error))[:300])
        valid = valid and not errors
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
