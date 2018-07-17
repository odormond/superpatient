#! /usr/bin/env python3

from pathlib import Path
from string import Template
import sys

sys.path.insert(0, str(Path(__file__).absolute().parents[1]))

from superpatient.customization import SITE  # noqa


if __name__ == '__main__':
    if len(sys.argv) < 2 or '-h' in sys.argv or '--help' in sys.argv:
        print("Usage:", sys.argv[0], "script.sql.template [key=value ...]")
        raise SystemExit(0)
    with open(sys.argv[1]) as source:
        template = Template(source.read())
    mapping = {'SITE': SITE}
    mapping.update(m.split('=', 1) for m in sys.argv[2:])
    render = None
    while render is None:
        try:
            render = template.substitute(mapping)
        except KeyError as e:
            key, = e.args
            mapping[key] = input('Value to use for ${}: '.format(key))
    print(render)
