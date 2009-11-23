
class Source(object):
    '''
    This is just an abstract interface for a signal source.
    '''

    def __init__(self):
        raise NotImplementedError("This base class is supposed to be derived from")
    
if __name__ == "__main__":
    src = Source()
    