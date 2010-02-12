'''
Created on Feb 5, 2010

@author: brianthorne
'''
from os import path
import sys
from codefile import CodeFile
import unittest

PATH_TO_SRC_DIR = path.join( path.dirname( __file__ ), '..', '..' )

class Test_Code_File_Path( unittest.TestCase ):
    def test_file_is_class_name( self ):
        '''Test that a class with the same name as the filename makes valid CodeFile'''
        c = CodeFile( path.join( PATH_TO_SRC_DIR, 'scipysim', 'actors', 'math', 'trig', 'sin.py' ) )

    def test_file_isnt_class_name( self ):
        c = CodeFile( path.join( PATH_TO_SRC_DIR, 'scipysim', 'actors', 'strings', 'intparser.py' ) )

class Test_Code_File_Num_Input_Output_Parsing( unittest.TestCase ):
    src_dir = PATH_TO_SRC_DIR

    def test_siso_code_file( self ):
        '''Test by loading a siso actor from a hardcoded path'''
        c = CodeFile( self.src_dir + '/scipysim/actors/math/trig/sin.py' )
        self.assertEqual( c.num_inputs, 1 )
        self.assertEqual( c.num_outputs, 1 )

    def test_display_actor( self ):
        '''Test that a plotter has one channel input'''
        c = CodeFile( self.src_dir + '/scipysim/actors/display/stemmer.py' )
        self.assertEqual( c.num_inputs, 1 )
        self.assertEqual( c.num_outputs, 0 )

    def test_dynamic_actor( self ):
        '''Test the a block that can have multiple inputs (summer)'''
        c = CodeFile( self.src_dir + '/scipysim/actors/math/summer.py' )
        self.assertEqual( c.num_outputs, 1 )
        self.assertEqual( c.num_inputs, None )

    def test_composite_model( self ):
        '''Test a composite_actor for num of inputs and output channels'''
        c = CodeFile( self.src_dir + '/scipysim/actors/math/trig/DTSinGenerator.py' )
        self.assertEqual( c.num_outputs, 1 )
        self.assertEqual( c.num_inputs, 0 )

class Test_Code_File_Input_Output_Domain_Parsing( unittest.TestCase ):
    src_dir = PATH_TO_SRC_DIR


    def test_dynamic_actor( self ):
        '''Test the a block that can have multiple inputs (summer)'''
        c = CodeFile( self.src_dir + '/scipysim/actors/math/summer.py' )
        self.assertTrue ( all( ( domain == None for domain in c.output_domains ) ) )

    def test_composite_model( self ):
        '''Test a composite_actor for num of inputs and output channels'''
        c = CodeFile( self.src_dir + '/scipysim/actors/math/trig/DTSinGenerator.py' )
        self.assertTrue( all( ( domain == "DT" for domain in c.output_domains ) ) )


if __name__ == "__main__":
    unittest.main()
