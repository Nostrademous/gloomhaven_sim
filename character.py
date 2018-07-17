'''
'''

import json

class Character():
    def __init__(self, name):
        self.data = {}
        self.data['Name'] = name
        print("Created Character: '%s'" % name)

    def getName(self):
        return self.data['Name']

    def getJson(self):
        return self.data