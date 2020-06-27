print('Example of the use of odfdo in a script : odfdo-show.py. This command '
      'line tool dumps text from an OpenDocument file to the standard '
      'output, optionally styles and meta.\n\n'
      'odfdo-show.py is available in the script directory of the odfdo-python'
      ' package.\n')

from subprocess import call
from pathlib import PurePath
p = PurePath('../scripts/odfdo-show.py')
call('python %s --help' % p, shell=True)
