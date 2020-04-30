# Designed for new hires to complete their first PR.
# Writes to 'employee_registry.txt' by calling `python new_hire.py <alias>`

from datetime import date
import os
import sys
import click
from utility import ROOT_DIR

def register_alias(alias):
    """
    Appends text to 'employee_registry.txt'
    """
    with open(os.path.join(ROOT_DIR, 'employee_registry.txt'), 'a') as f:
        f.write('{} was here!\t\t{}\n'.format(alias, date.today()))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        click.secho("`new_hire.py` takes one string as an argument. "
                    "Please provide your alias surrounded in strings, "
                    "i.e. \"elbosc\".", err=True)
    else:
        register_alias(sys.argv[1])
