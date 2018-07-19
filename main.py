'''
'''

import global_vars as gv
import party
from utils import listFiles, printJson

def createMember():
    raw_input("What is your Hero's Name? ")

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
            elif selection == 1:
                p_name = raw_input("Select a Party name: ")
                try:
                    assert p_name + "_party.json" not in listFiles('.')

                    obj_party = party.Party(p_name)
                    
                    while True:
                        print("Let's create our Party Members now.")
                        try:
                            m_cnt = raw_input("How many Heroes would you like to add? ")
                            m_cnt = int(m_cnt)
                            for cnt in range(1, m_cnt+1):
                                print(cnt)
                        except Exception as err:
                            print("[Exception] :: %s" % err)
                            pass
                        break
                    printJson(obj_party)
                except AssertionError:
                    print("That Party Name already exists!!! Start again...")
                    pass
                
        else:
            print('Invalid selection')


gv.init() # call only once
createParty()
