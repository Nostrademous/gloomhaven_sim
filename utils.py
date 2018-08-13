'''
'''

import json
import random

from os import listdir
from os.path import isfile, join

def listFiles(mypath):
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]

def listFilesExtension(mypath, extension):
    files = list()
    for file in listdir(mypath):
        if file.endswith(extension):
            files.append(join(mypath, file))
    return files

def printJson(jsonData):
    if isinstance(jsonData, dict):
        print(json.dumps(jsonData, indent=4, sort_keys=True))
    else:
        print(json.dumps(jsonData.getJson(), indent=4, sort_keys=True))

def strJson(jsonData):
    if isinstance(jsonData, dict):
        return json.dumps(jsonData, indent=4, sort_keys=True)
    else:
        return json.dumps(jsonData.getJson(), indent=4, sort_keys=True)

def pickRandom(listChoices, num=1):
    if len(listChoices) == 0: return None

    # to make it really random use the cryptographically safe
    # random initialization each time
    secure_random = random.SystemRandom()
    
    if num == 1:
        if isinstance(listChoices, dict):
            return listChoices[secure_random.choice(list(listChoices))]
        return secure_random.choice(listChoices)
    else:
        return secure_random.sample(listChoices, num)

'''
    Compare Mixin, inheriting classes must define _cmpkey()
'''
class ComparableMixin(object):
    def _compare(self, other, method):
        try:
            return method(self._cmpkey(), other._cmpkey())
        except (AttributeError, TypeError):
            # _cmpkey not implemented, or return different type,
            # so I can't compare with "other".
            return NotImplemented

    def __lt__(self, other):
        return self._compare(other, lambda s, o: s < o)

    def __le__(self, other):
        return self._compare(other, lambda s, o: s <= o)

    def __eq__(self, other):
        return self._compare(other, lambda s, o: s == o)

    def __ge__(self, other):
        return self._compare(other, lambda s, o: s >= o)

    def __gt__(self, other):
        return self._compare(other, lambda s, o: s > o)

    def __ne__(self, other):
        return self._compare(other, lambda s, o: s != o)     