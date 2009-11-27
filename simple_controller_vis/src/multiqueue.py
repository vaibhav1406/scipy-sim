from sets import Set
import thread
from threading import Thread


class Lockable:
    def __init__(self):
        self.mutex = thread.allocate_lock()

def locked(method):
    def _locked(self, *args, **kwargs):
        self.mutex.acquire()
        try:
            result = method(self, *args, **kwargs)
        finally:
            self.mutex.release()
        return result
    return _locked


class TaggedSignal:
    def __init__(self, names):
        self.names = names
        self.lock = thread.allocate_lock()
        self.lock.acquire()
        self.tag = None

    def set(self, tag):
        self.tag = tag
        self.lock.release()

    def wait(self):
        self.lock.acquire()
        self.lock.release()
        return self.tag


class MultiQueue(Lockable):
    def __init__(self, maxsize):
        self.maxsize = maxsize
        self.queues = {}
        self.writeLocks = {}
        self.waitingLists = {}
        Lockable.__init__(self)

    def put(self, name, value):
        writeLock = self.getWriteLock(name)
        must_release = True
        writeLock.acquire()
        try:
            must_release = self._put(name, value, writeLock)
        finally:
            if must_release:
                writeLock.release()

    def _put(self, name, value, writeLock):
        if self.waitingLists.has_key(name):
            self.notify_signal(name, value)
            return True
        else:
            queue = self.getQueue(name)
            queue.append(value)
            return len(queue) < self.maxsize
    _put = locked(_put)

    def notify_signal(self, name, value):
        signal = self.waitingLists[name][0]
        signal.set((name, value))
        for name in signal.names:
            waitingList = self.waitingLists[name]
            waitingList.remove(signal)
            if len(waitingList) == 0:
                del self.waitingLists[name]

    def get(self, *names):
        must_wait, result = self._get(names)
        if must_wait:
            return result.wait()
        else:
            return result

    def _get(self, names):
        populatedQueues = Set(self.queues.keys()).intersection(names)
        if len(populatedQueues) == 0:
            return True, self.createSignal(names)
        else:
            return False, self.getValue(populatedQueues.pop())
    _get = locked(_get)

    def getValue(self, queueName):
        queue = self.queues[queueName]
        was_full = len(queue) == self.maxsize
        value = queue.pop(0)
        if len(queue) == 0:
            del self.queues[queueName]
            del self.writeLocks[queueName]
        else:
            if was_full:
                self.writeLocks[queueName].release()
        return queueName, value

    def createSignal(self, names):
        signal = TaggedSignal(names)
        for name in names:
            try:
                waitingList = self.waitingLists[name]
            except KeyError:
                waitingList = self.waitingLists[name] = []
            waitingList.append(signal)
        return signal

    def getWriteLock(self, name):
        try:
            writeLock = self.writeLocks[name]
        except KeyError:
            writeLock = self.writeLocks[name] = thread.allocate_lock()
        return writeLock
    getWriteLock = locked(getWriteLock)

    def getQueue(self, name):
        try:
            queue = self.queues[name]
        except KeyError:
            queue = self.queues[name] = []
        return queue


# Testing the code

class TestPutter(Thread):
    def __init__(self, mq, name, value):
        super(TestPutter, self).__init__()
        self.mq = mq
        self.name = name
        self.value = value

    def run(self):
        print "Putting value %s into queue %s" % (str(self.value), str(self.name))
        self.mq.put(self.name, self.value)
        print "--Put value %s into queue %s" % (str(self.value), str(self.name))

class TestGetter(Thread):
    def __init__(self, mq, names):
        super(TestGetter, self).__init__()
        self.mq = mq
        self.names = names # Names of queues to receive from..?

    def run(self):

        while True:
            print ("Getting a value from the multiqueue")
            name, value = self.mq.get(*self.names)
            print "--Got value %s from queue %s" % (str(value), str(name))

class TestMultiQueue:
    def __init__(self, maxsize):

        self.mq = MultiQueue(maxsize)
        self.names = ['A', 'B', 3]
        self.testSetter = TestPutter(self.mq, 'A', 1.5)
        self.testSetter2 = TestPutter(self.mq, 'B', "I'm a string")
        self.testGetter = TestGetter(self.mq, self.names)
        print "Putting value 1 into queue A"
        self.mq.put('A', 1)
        self.testSetter.start()
        self.testSetter2.start()
        self.testGetter.start()

    def run(self):
        print "Trying to block..."
        print "Getting value from queue(s) %s" % (str(self.names))
        name, value = self.mq.get(*self.names)
        print "--Got value %s from queue %s while waiting for queues(s) %s" % (str(value), str(name), str(self.names))


testMultiQueue = TestMultiQueue(4)
testMultiQueue.run()

"""
By running this test I see that the multiqueue is not preserving the order between queues... this may not be important.
Also it doesn't actually use the Python Queue class... so it won't play nice with the rest of the blocks using the current
connection scheme...

Actually... a Python Queue IS a multiqueue....
"""

