'''
'''

import json
import random

from os import listdir
from os.path import isfile, join

def listFiles(mypath):
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]

def printJson(jsonData):
    print(json.dumps(jsonData.getJson(), indent=4, sort_keys=True))

def pickRandom(listChoices):
    # to make it really random use the cryptographically safe
    # random initialization each time
    secure_random = random.SystemRandom()
    return secure_random.choice(listChoices)
