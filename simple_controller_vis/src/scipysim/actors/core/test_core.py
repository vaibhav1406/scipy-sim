import unittest
from actor import Actor
class TestActor( unittest.TestCase ):

    def setUp( self ):
        self.block = Actor()

    def test_actor_is_abstract( self ):
        self.assertRaises( NotImplementedError, self.block.run )

    def test_input_queue_made( self ):
        self.block.input_queue.put( "Something" )
        self.assertEquals( "Something", self.block.input_queue.get() )

    def test_actor_has_defualt_port_nums( self ):
        '''Test by loading a siso actor from a hardcoded path'''
        my_actor = Actor()
        self.assertEqual( my_actor.num_inputs, None )
        self.assertEqual( my_actor.num_outputs, None )

if __name__ == "__main__":
    unittest.main()
