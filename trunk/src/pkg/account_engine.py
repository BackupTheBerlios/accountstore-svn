# -*- coding: utf-8 -*-
import re
import sys  # for debugging
        
class Account:
    '''
    This class is defines an account
    '''
    def __init__(self, name, uname, pword):
        self.name  = name   # name is "key" i.e. uniqueness required & sustained
        self.uname = uname
        self.pword = pword
        
    def __str__(self):
        '''
        This "to string" method makes a comma separated line of an account
        '''
        return self.name + ', ' + self.uname + ', ' + self.pword

class AccountManager:
    '''
    This class stores a list of accounts and has various CRUD methods for an
    account in relation to this list. It of course depends on the preceding 
    Account class
    '''
    def __init__(self):
        self.accounts = []
    
    def add(self, act):
        '''
        This method adds an account to the accounts list. And it does it by 1) 
        preserving uniqueness of the names of the accounts (i.e. two accounts
        having the same name can not be found in the accounts list). 2) The 
        accounts list is sorted after each insert implying thats it's always 
        sorted (the delete operation can't destroy a valid order)
        '''
        try:
            self.uniqueness_violation(act.name)
        except self.UniquenessException as ue:
            print str(ue)
        else:    
            self.accounts.append(act)
            self.sort()
    
    def uniqueness_violation(self, name):
        ''' 
        Helper method for add()
        '''
        for act in self.accounts:
            if act.name == name:
                raise self.UniquenessException(name)
    
    def delete(self, name):
        ''' 
        A check for if name *is* in the list of accounts. The check is not 
        really nessessary - the filter-command alone is enough. But it demos 
        map() and filter() which might impress the teachers. Joke aside: One
        could rethrow KeyError so a warning could pop up. But then again: it 
        *can* never happen in this app because the gui will select a 
        line/account which exists
        '''
        try:
            names = map(lambda act: act.name, self.accounts)
            if name not in names:
                raise KeyError('There is no such account name (%s)!' %name)
        except KeyError as ke:
            print str(ke)
        else:   # Well 'name' was there... . filter() *preserves* the elements 
                # that comply to the criteria in the function. Here we want the
                # names that not equal to 'name'
            self.accounts = filter(lambda act: act.name != name, self.accounts)
    
    def update(self, name):
        '''
        Not implemented yet.
        '''
        pass
    
    def load(self):
        '''
        Load the accounts from file
        '''
        self.accounts = []  # Be sure nothing is in accounts
        f = None
        try:
            f = open(File.ACCOUNT_FILE, 'r')
            act_fields = []
            for line in f:  # a line is a field
                line = line.strip()  # strip(): remove trailing newline
                act_fields.append(line)
                # When 3 lines are read make an account and add it
                if len(act_fields) == File.LINES_PER_ACCOUNT:
                    act = Account(act_fields[0], act_fields[1], act_fields[2])
                    self.accounts.append(act)
                    act_fields = []  # reset before reading the next account
        except IOError as io:
            print str(io)
        finally:
            if f:
                f.close()  # We don't forget this one do we?
           
    def persist(self):
        ''' 
        Save the accounts to file
        '''
        f = None
        try:
            f = open(File.ACCOUNT_FILE, 'w')
            for act in self.accounts:
                act_fields = self.csv2list(str(act))  # 'x, y, z' --> ['x', 'y', 'z']
                act_fields = map(lambda s: s + '\n', act_fields) # ['x', 'y', 'z'] --> ['x\n', 'y\n', 'z\n']
                map(f.write, act_fields)  # Who needs 'for' when you have 'map'?
        except IOError as io:
            print str(io)
        finally:
            if f:
                f.close()  # We don't forget this one do we?
    
    def sort(self):
        '''
        In-place sorting of the account using the "key'ed-sorting" stolen from
        http://wiki.python.org/moin/HowTo/Sorting/ search 'Key Functions'
        Noticeable client is self.add()
        '''
        self.accounts.sort(key=lambda act: act.name)
    
    def csv2list(self, str):
        ''' Minute helper - also used in account_store.py '''
        return re.split(', ', str)  # 'x, y, z' --> ['x', 'y', 'z']
    
    def __str__(self):
        s = ''  # TODO Consider using reduce()
        for act in self.accounts:
            s += str(act) + '\n'
        return s
            
    class UniquenessException(Exception):
        def __init__(self, name):
            self.message = "The account name '%s' is not unique among existing account names" %name
        def __str__(self):
            return self.message

class File:
    '''
    This class contains various file handling constants and also attributes/ 
    methods assisting the file encryption
    '''
    # The AccountManager class knows where to persist it's accounts
    ACCOUNT_FILE = '/usr/lib/gedit-2/plugins/account_store.txt'
    LINES_PER_ACCOUNT = 3
    
if __name__ == "__main__":
    my_acts = AccountManager()
    my_acts.load()
    print str(my_acts)  # ok
    
    my_acts.delete('KNord')
    print str(my_acts)  # ok
    
    act = Account('American Pizza', '60760024', 'n/a')
    my_acts.add(act)
    print str(my_acts)  # ok
    
    # Persist, load and confirm correct
    my_acts.persist()
    print 'Efter persist()'
    my_acts.load()
    print 'Efter load()'
    
    print str(my_acts)
    print 'Forventer: American Pizza, Danske Netbank, Dropbox, Super Brugsen'
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    