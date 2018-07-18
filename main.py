'''
'''

import global_vars as gv
import party

def createParty():
    while True:
        print('What would you like to do?')
        print('  1 - Create a new Party')
        print('  2 - Edit or Update an existing Party')
        print('  3 - Quit')
        ret = raw_input('>: ')

        try:
            selection = int(ret)
        except Exception as err:
            print('[createParty :: Exception] %s' % (err))
            pass

        if selection in [1,2,3]:
            if selection == 3:
                break
            elif selection == 2:
                p_name = raw_input("What is the Party's name: ")
                try:
                    party.loadHeroData(dataFile=p_name+'_party.json')
                except Exception as err:
                    print("[Load Existing Party Exception] :: %s" % (err))
        else:
            print('Invalid selection')


gv.init() # call only once
createParty()
