'''

A graph like API for building scipysim models.

In essense a graph contains the "blocks" (instances of Actors), along with a mapping
between them and default parameters and/or parameter ranges and types.

A graph can be changed in every way, actors need not be connected up while the
graph is being created. Channels are created for each block's outputs which may
be connected to other block's inputs. When connecting channels, the domain of the
output port is used for the channel and must match the domain of the input port.


A complete graph will have all input connections correctly "wired up" - outputs
that are not connected are ignored.

Implementation detail - Nodes are CodeFile instances - wrappers around the actual Actor blocks.
'''


from event import Event
from siso import Siso
from actor import Actor, Source
from channel import Channel, MakeChans
import sys
import os
from codefile import CodeFile
import logging

class Node(object):
    '''
    Abstraction of an *Actor* or *Model* that can be used in a program *Graph*.
    Wraps a *CodeFile* with capabilities to handle parameters and keeps track of
    *Channel*s. Can be thought of as a not-yet-created but individual instance of
    an *Actor* with individual parameters and connections.
    '''
    def __init__(self, codefile, parameters=None):
        '''
        params
        ======

        codefile
            A *CodeFile* instance to base this Node on.
        
        parameters
            a dictionary containing the arguments passed to the *Actor*'s
            constructor when the simulation runs. Can be changed later,
            might have defaults, if not defined the default dict will be used.

            The default dictionary containing the default parameters can be obtained
            for a *CodeFile* by calling an instances *get_default_parameters* method.

            If the key is "input", "inputs", "input_channel", "input_channels" it
            will instead be added to the node's *input_channels* list. Likewise
            for 'output', 'out', 'output_channel', 'outputs', 'outs', and
            'output_channels'.
        '''
        self.input_channels = []
        self.output_channels = []

        # Export some of codefile's attributes
        for attrib in [ 'name',
                        'num_outputs',
                        'num_inputs',
                        'output_domains',
                        'input_domains',
                        'get_default_parameters']:
            setattr(self, attrib, getattr(codefile, attrib))
        # Export the codefile itself
        self.codefile = codefile
        
        # Save the node's parameters
        if parameters is None:
            parameters = self.codefile.get_default_parameters()

        # Create own changable copy of the parameters dictionary
        self.params = parameters.copy()

        # Move input and output channels from parameters to own lists
        for key in parameters:
            if key in ["input", "input_channel", "inputs", "input_channels"]:
                if type(self.params[key]) in [list, tuple]:
                    self.input_channels.extend(self.params.pop(key))
                else:
                    self.input_channels.append(self.params.pop(key))
            if key in ['output', 'out', 'output_channel', 'outputs', 'outs', 'output_channels']:
                if type(self.params[key]) in [list, tuple]:
                    self.output_channels.extend(self.params.pop(key))
                else:
                    self.output_channels.append(self.params.pop(key))

        # Create output channels
        for _ in range(self.output_channels.count(None)):
            index = self.output_channels.index(None)
            self.output_channels[index] = Channel(domain=self.output_domains[index])

    def ready(self):
        connected = all(chan is not None for chan in self.input_channels)
        specified = all(self.params[key] is not None for key in self.params)
        return connected and specified
        
    def set_parameter(name, value):
        self.params[name] = value

class Graph(object):

    def __init__(self, name='Generic Model'):
        self.nodes = []
        self.codefiles = set()
        self.name = name

    def __repr__(self):
        out = ''
        for node in self.nodes:
            out += str(node)
        return node

    def __contains__(self, node):
        return node in self.nodes

    def add(self, node):
        '''
        Add an Actor to this graph.

        params
        ======

        node
            a Node instance for the Actor to be added to this graph.
        '''
        self.nodes.append(node)
        self.codefiles.add(node.codefile)

    def remove(self, node):
        # TODO: It might be required to disconnect the channels first
        for output_chan in node.output_channels:
            del output_chan
        self.nodes.remove(node)

    def connect(self, channel, node, input_name='input_channel'):
        '''
        Connect channel to node as an input.

        params
        ======

        channel
            The channel to be used as input, it should already be connected as an
            output to another node. Its domain must match the input domain for
            the node.

        node
            The *Node* within this graph to connect *channel* to.
            
        input_name
            Optionally include the input_name if there are multiple inputs or
            different parameter names in the Actor's initialiser. If the name is
            anything except "input", "input_channel", "inputs", "input_channels"
            this must be given
            (TODO?)
        '''
        assert node in self.nodes
        
        if None not in node.input_domains:   # None means any domain is allowed
            assert channel.domain in node.input_domains
        else:
            logging.warning('Could probably improve Actor:%s by specifying input domains' % node.name)
        
        if input_name in ["input", "input_channel"]:
            node.input_channels.pop(0)   # TODO: this is why channels need names
            node.input_channels.append(channel)
        else:
            node.set_parameter(input_name, channel)

    def ready(self):
        '''
        Verify the model.

        Check that every input channel and every parameter is not None.
        '''
        return all(block.ready() for block in self.nodes)

    def run(self):
        '''
        Create a program from the graph and run it.
        '''
        # Create a python program in a temporary file
        from tempfile import NamedTemporaryFile
        tempfile = NamedTemporaryFile()
        filename = tempfile.name
        self.write_to_py_file(filename)

        # preview the output:
        h = '\n' + '#' * 80 + '\n\n'
        print h + ''.join(line for line in tempfile) + h

        # Execute the python program
        from scipysim.core.util import run_python_file
        
        output = run_python_file( filename )
        print output
        return output

    def write_to_py_file(self, filename):
        '''
        Create a python file containing an exectuable version of this model
        '''
        domains = []
        
        code = """#!/bin/env python
import scipysim
from scipysim.actors import Model, MakeChans, Event
%(imports)s

print '%(header)s

class %(class_name)s(Model):
    '''
    A model of ...
    '''

    def __init__(self):

        wires = MakeChans(%(number_chans)d, %(domains)s)

        self.components = [
            #DTSinGenerator(wires[1], amplitude = 0.1, freq = 0.45, simulation_length=200),
            %(components)s
        ]


if __name__ == '__main__':
    %(class_name)s().run()

""" %   {
            'imports': '\n'.join(codefile.get_import() for codefile in self.codefiles),
            'header': 'Scipysim Automatically Generated Program',
            'class_name': self.name.replace(' ', '_'),
            'number_chans': len(domains),
            'domains': str(domains),
            'components': '\n            '.join(node.write_to_py() for node in self.nodes)
        }

        f = open(filename, 'w')
        f.write(code)
        
        f.close()

import unittest
get_source = lambda *args: os.path.abspath(os.path.join( os.path.dirname( __file__ ), os.path.pardir, os.path.pardir, *args ))

class TestNode(unittest.TestCase):
    def test_create_node(self):
        '''test creation of a blank node'''
        n = Node(CodeFile( get_source( 'scipysim', 'actors', 'math', 'trig', 'sin.py' ) ))

    def test_multiple_instances(self):
        '''Ensure parameter changing is node specific.'''
        c = CodeFile( get_source( 'scipysim', 'actors', 'math', 'trig', 'sin.py' ) )
        n1 = Node(c)
        n2 = Node(c)
        self.assertEquals(n1.params, n2.params)
        n1.params['freq'] = 9999
        self.assertNotEquals(n1.params, n2.params)

    def test_node_has_channels(self):
        '''A node should have a list of both input and output channels
        (possibly empty)'''
        
        n = Node(CodeFile( get_source( 'scipysim', 'actors', 'math', 'trig', 'sin.py' ) ))
        self.assertTrue(isinstance( n.output_channels, list))
        self.assertEquals(len(n.input_channels), 0)

    def test_node_makes_output_chans(self):
        '''Nodes should create output channels'''
        n = Node(CodeFile( get_source( 'scipysim', 'actors', 'math', 'trig', 'DTSinGenerator.py' ), 'DTSinGenerator' ))
        self.assertTrue(isinstance( n.output_channels, list))
        self.assertEquals(len(n.output_channels), 1)
        self.assertTrue(isinstance(n.output_channels[0], Channel))
        self.assertEquals(n.output_channels[0].domain, 'DT')


class TestGraph(unittest.TestCase ):

    def test_empty_graph( self ):
        '''Test creation of a blank graph.'''
        g = Graph()

    def test_add_node( self ):
        '''Add a node to a graph'''
        g = Graph()
        cf = CodeFile( get_source( 'scipysim', 'actors', 'math', 'trig', 'sin.py' ) )
        self.assertEquals(cf.name, 'Sin')
        node = Node(cf)
        g.add(node)
        self.assertTrue(node in g)
        

    def test_remove_node( self ):
        '''Add then remove a node to a graph'''
        g = Graph()
        node = Node(CodeFile( get_source( 'scipysim', 'actors', 'math', 'trig', 'sin.py' ) ))
        g.add(node)
        g.remove(node)
        self.assertFalse(node in g)

    def test_connect_nodes(self):
        '''Connect nodes together'''
        g = Graph()
        source_node = Node(CodeFile( get_source( 'scipysim', 'actors', 'math', 'trig', 'DTSinGenerator.py' ), 'DTSinGenerator' ))
        gain = Node(CodeFile( get_source( 'scipysim', 'actors', 'math', 'proportional.py'), 'Proportional'))

        g.add(source_node)
        g.add(gain)

        chan = source_node.output_channels[0]
        g.connect(chan, gain)
        
    def test_verify(self):
        '''Verify that all inputs are connected'''
        g = Graph()
        source_node = Node(CodeFile( get_source( 'scipysim', 'actors', 'math', 'trig', 'DTSinGenerator.py' ), 'DTSinGenerator' ))
        gain = Node(CodeFile( get_source( 'scipysim', 'actors', 'math', 'proportional.py'), 'Proportional'))

        g.add(source_node)
        g.add(gain)
        
        gain.params['gain'] = 10

        chan = source_node.output_channels[0]
        g.connect(chan, gain)
        self.assertTrue(g.ready())

    def test_verify_fails(self):
        '''Create a model with an unfilled input channel'''
        g = Graph()
        
        gain = Node(CodeFile( get_source( 'scipysim', 'actors', 'math', 'proportional.py'), 'Proportional'))
        g.add(gain)
        gain.params['gain'] = 10

        self.assertFalse(g.ready())        

    def test_run(self):
        '''Test execution'''
        g = Graph()
        source_node = Node(CodeFile( get_source( 'scipysim', 'actors', 'math', 'trig', 'DTSinGenerator.py' ), 'DTSinGenerator' ))
        gain = Node(CodeFile( get_source( 'scipysim', 'actors', 'math', 'proportional.py'), 'Proportional'))
        
        g.add(source_node)
        g.add(gain)

        # could connect this up to a file writer to unittest the output (io.TextWriter)
        
        g.connect(source_node.output_channels[0], gain)
        self.assertTrue(g.ready())
        g.run()
        
        
if __name__ == "__main__":
    unittest.main()
