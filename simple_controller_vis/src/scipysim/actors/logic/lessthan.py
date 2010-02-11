'''
Created on Feb 2, 2010

@author: brianthorne
'''
from scipysim.actors.logic import Compare
class LessThan(Compare):
    def compare(self, obj):
        return obj['value'] < self.threshold