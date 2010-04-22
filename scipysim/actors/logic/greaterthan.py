'''
Created on Feb 2, 2010

@author: Brian Thorne
'''
from scipysim.actors.logic import Compare

class GreaterThan(Compare):
    '''
    This actor takes a source and passes on the value if it is equal or over 
    a specified threshold. Or boolean output is available (@see Compare).
    '''
    def compare(self, obj):
        '''Return true if value is above preset threshold'''
        return obj['value'] >= self.threshold
