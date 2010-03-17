from scipysim.actors import Siso

class Compare(Siso):
    '''This abstract base class is for any actor which carries out a comparison.
    
    @requires: Compare function to take a event (dictionary) object and return true/false.
    '''
    def __init__(self, input_channel, output_channel, threshold, boolean_output=False):
        '''Constructor for a Compare actor.
        
        @param threshold: Since most comparisons occur against something, this simply stores 
        the threshold value in self.threshold
        
        @param boolean_output: If this is set to true, instead of passing on 
        the value, the value is replaced with the boolean 'True' value.
        '''
        super(Compare, self).__init__(input_channel=input_channel,
                                      output_channel=output_channel,
                                      child_handles_output=True)
        self.bool_out = boolean_output
        self.threshold = threshold

    def compare(self, obj):
        '''This method must be overridden. If it returns True
        the value is put onto the output channel, else discarded.
        Or if boolean_output is true, a boolean is substituted for the 'value'
        
        @return Boolean value
        '''
        raise NotImplementedError

    def siso_process(self, obj):
        '''Carry out the comparison using the compare method.'''
        if self.compare(obj):
            if self.bool_out:
                obj['value'] = True
            self.output_channel.put(obj)
        elif self.bool_out:
            obj['value'] = False
            self.output_channel.put(obj)

