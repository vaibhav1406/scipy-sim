'''
This module tests the core component of scipysim that locates and parses
model and actor files (as python code).

The path wrangling is to get around the fact we are testing importing both
relative and absolute paths. This test can be run from the parent directory 
of scipysim. For example in windows the command::
    C:\Python26\python.exe -m scipysim.core.test_codefile -v
will pass all the tests but::
    C:\Python26\python.exe ./scipysim/core/test_codefile -v
will not work (right now half the tests fail). This is the same as being 
in the core directory and running `python test_codefile.py`.

Created on Feb 5, 2010

@author: brianthorne
'''
from os import path
import sys
from codefile import CodeFile
import unittest

PATH_TO_SRC_DIR = path.abspath(path.join( path.dirname( __file__ ), path.pardir, path.pardir ))

sys.path.insert(0, PATH_TO_SRC_DIR)


class Test_Code_File_Path( unittest.TestCase ):

    def test_file_is_class_name( self ):
        '''Test that a class with the same name as the filename makes valid CodeFile'''
        c = CodeFile( path.join( PATH_TO_SRC_DIR, 'scipysim', 'actors', 'math', 'trig', 'sin.py' ) )
        self.assertEquals(c.name, "Sin")

    def test_file_when_given_class_name( self ):
        filepath = path.join( PATH_TO_SRC_DIR, 'scipysim', 'actors', 'strings', 'intparser.py' )
        c = CodeFile( filepath, "IntParser" )
        self.assertEquals(c.name, "IntParser")

    def test_fail_on_invalid_name( self ):
        '''Test that an exception is raised when loading a non-existant class from a file.'''
        filepath = path.join( PATH_TO_SRC_DIR, 'scipysim', 'actors', 'strings', 'intparser.py' )
        self.assertRaises(NameError, CodeFile,  filepath, "Parser" )  # Parser is not defined in intparser.py
        

    def test_file_isnt_class_name( self ):
        '''Test that a class in a trickily named file is still parsed as a valid CodeFile'''
        c = CodeFile( path.join( PATH_TO_SRC_DIR, 'scipysim', 'actors', 'strings', 'intparser.py' ) )
        self.assertEquals(c.name, "IntParser")

class Test_Code_File_Num_Input_Output_Parsing( unittest.TestCase ):

    def test_siso_code_file( self ):
        '''Test by loading a siso actor from a hardcoded path'''
        filepath = path.abspath(path.join(PATH_TO_SRC_DIR, 'scipysim', 'actors', 'math', 'trig', 'sin.py'))
        c = CodeFile( filepath )
        self.assertNotEqual(None, c)
        self.assertEqual( c.num_inputs, 1 )
        self.assertEqual( c.num_outputs, 1 )

    def test_display_actor( self ):
        '''Test that a plotter has one channel input'''
        filepath = path.abspath(path.join(PATH_TO_SRC_DIR, 'scipysim','actors','display','stemmer.py'))
        c = CodeFile( filepath  )
        self.assertEqual( c.num_inputs, 1 )
        self.assertEqual( c.num_outputs, 0 )

    def test_dynamic_actor( self ):
        '''Test that a block that can have multiple inputs (summer)'''
        filepath = path.abspath(path.join(PATH_TO_SRC_DIR, 'scipysim','actors', 'math', 'summer.py'))
        c = CodeFile( filepath )
        self.assertEqual( c.num_outputs, 1 )
        self.assertEqual( c.num_inputs, None )

    def test_composite_model( self ):
        '''Test a composite_actor for num of inputs and output channels'''
        filepath = path.abspath(path.join(PATH_TO_SRC_DIR, 'scipysim','actors','math','trig','DTSinGenerator.py'))
        c = CodeFile( filepath )
        self.assertEqual( c.num_outputs, 1 )
        self.assertEqual( c.num_inputs, 0 )

class Test_Code_File_Input_Output_Domain_Parsing( unittest.TestCase ):

    def test_dynamic_actor( self ):
        '''Test the a block that can have multiple inputs (summer)'''
        filepath = path.abspath(path.join(PATH_TO_SRC_DIR, 'scipysim','actors', 'math', 'summer.py'))
        c = CodeFile( filepath )
        self.assertTrue ( all( ( domain == None for domain in c.output_domains ) ) )

    def test_composite_model( self ):
        '''Test a composite_actor for num of inputs and output channels'''
        filepath = path.abspath(path.join(PATH_TO_SRC_DIR, 'scipysim','actors','math','trig','DTSinGenerator.py'))
        c = CodeFile( filepath )
        self.assertTrue( all( ( domain == "DT" for domain in c.output_domains ) ) )

class Test_Code_File_Parameters( unittest.TestCase ):

    def test_actor_parameter_names( self ):
        '''Check the parameters dictionary contains the correct names'''
        filepath = path.abspath(path.join(PATH_TO_SRC_DIR, 'scipysim','actors','math','trig','DTSinGenerator.py'))
        c = CodeFile( filepath )
        # arguments should contain this:
        # self, out, amplitude=1.0, freq=0.01, phi=0.0, simulation_length=100
        params = c.get_default_parameters()
        for name in ['out', 'amplitude', 'freq', 'phi', 'simulation_length']:
            self.assertTrue(name in params)

    def test_actor_parameter_defaults(self):
        '''Check the parameters dictionary contains the correct default arguments'''
        filepath = path.abspath(path.join(PATH_TO_SRC_DIR, 'scipysim','actors','math','trig','DTSinGenerator.py'))
        c = CodeFile( filepath )
        # arguments should contain this:
        # self, out, amplitude=1.0, freq=0.01, phi=0.0, simulation_length=100
        params = c.get_default_parameters()
        for name, value in [('out', None), ('amplitude',1.0), ('freq',0.01), ('phi',0.0), ('simulation_length',100)]:
            self.assertEquals(params[name], value)

if __name__ == "__main__":
    unittest.main()
