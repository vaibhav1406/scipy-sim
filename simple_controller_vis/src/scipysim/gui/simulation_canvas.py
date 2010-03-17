'''
Created on Feb 10, 2010

@author: brianthorne
'''
from Tkconstants import RIDGE, TOP
from Tkinter import Canvas
import logging
import itertools

class CanvasBlock ( object ):
    '''An instance of an Actor drawn on a Simulation Canvas'''

    # To create a unique ID number for every block.
    # functools to map to str
    counter = itertools.count()

    # Settings for all blocks.
    font = ( "Helvetica", 10 )
    BLOCK_SIZE = ( BLOCK_WIDTH, BLOCK_HEIGHT ) = ( 70, 50 )


    def __init__( self, canvas, codefile, x, y, colour ):
        self.canvas = canvas
        self.codefile = codefile
        self.x, self.y = x, y
        self.colour = colour
        self.id = str( self.counter.next() )

        preview_tags = [
                        # Anything moveable will have the "DRAG" tag
                        "DRAG",
                        # Every blocks name will tagged so we can group bits together
                        "name:" + codefile.name,
                        "id:%s" % self.id,
                        # type: block/text
                        "preview"
                        ]


        self.canvas.create_rectangle( *( x, y ) + self.BLOCK_SIZE,
                                     fill=colour,
                                     tags=preview_tags + ["type:block"]
                                     )

        self.canvas.create_text ( x + ( self.BLOCK_WIDTH / 4 ), y + ( self.BLOCK_HEIGHT / 2 ),
                                 font=self.font, text=codefile.name,
                                 tags=preview_tags + ["type:text"]
                                 )
        num_inputs, num_outputs = codefile.num_inputs, codefile.num_outputs
        x_, y_ = x, y
        logging.debug( "Block has %d inputs, and %d outputs." % ( num_inputs, num_outputs ) )
        # Draw on input and output ports
        gap = 5
        if num_inputs is None:
            # Will default to drawing one connector, and when it is used we will draw another
            num_inputs = 1
        elif num_inputs == 0:
            pass
        else:
            for input in xrange( num_inputs ):
                self.canvas.create_polygon( x, y_ + gap , x - gap, y_ + gap * 3 / 2 , x , y_ + 2 * gap,
                                            tags=preview_tags + ["type:input-%d" % input],
                                            fill="#000000" )
                y_ = y_ + gap
        x_, y_ = x + 50 + gap, y
        if num_outputs is None:
            num_outputs = 1
        elif num_outputs == 0:
            pass
        else:
            for output in xrange( num_outputs ):
                self.canvas.create_polygon( x_, y_ + gap , x_ + gap, y_ + gap * 3 / 2 , x_ , y_ + 2 * gap,
                                            tags=preview_tags + ["type:output-%d" % input],
                                            fill="#000000" )


    def move_to( self, x, y ):
        '''Move this block to blah'''
        pass

    def set_colour( self, colour ):
        '''Set the main colour of this block to "colour" but keep
        the text and outline etc black.
        '''
        # TODO filter out all but the block
        self.canvas.itemconfigure( "id:%s" % self.id, fill=colour )

class SimulationCanvas( object ):
    """A canvas where blocks can be dragged around and connected up"""
    # The class attribute colours will hold all the colour info 
    # Randomly chosen from (visibone.com colour-lab)
    colours = {
         "background": "#CCFFCC", # Pale weak green. A weak yellow is FFFFCC
         "block": "#00FF66", # a lime green
         "preview": "#0099FF", # a blue
         "selected": "#FF6600" # orangne - red
         }

    size = ( width, height ) = ( 550, 250 )

    def __init__( self, frame ):
        # Create the canvas
        self.canvas = Canvas( frame,
                             width=self.width, height=self.height,
                             relief=RIDGE,
                             background=self.colours["background"],
                             borderwidth=1 )
        # Add event handlers for dragable items
        self.canvas.tag_bind ( "DRAG", "<ButtonPress-1>", self.mouse_down )
        #self.canvas.tag_bind ("DRAG", "<ButtonRelease-1>", self.mouse_release)
        self.canvas.tag_bind ( "DRAG", "<Enter>", self.enter )
        self.canvas.tag_bind ( "DRAG", "<Leave>", self.leave )
        self.canvas.pack( side=TOP )

        # Some default locations
        self.PREVIEW_WIDTH = 80
        self.PREVIEW_LOCATION = ( self.PREVIEW_X, self.PREVIEW_Y ) = ( 15, 30 )


        # Draw a "preview" area
        self.canvas.create_line( self.PREVIEW_WIDTH, 0, self.PREVIEW_WIDTH, 250, dash=True )

        # A dict indexed by unique ID of elements in the canvas.
        self.blocks = {}

    def preview_actor( self, codefile ):
        """
        Display a preview of an actor or compisite actor in the canvas,
        it will be dragable into desired position
        """
        logging.debug( "Creating a preview of %(name)s on simulation canvas." % {'name':codefile.name} )

        logging.debug( "Deleting any existing items still tagged 'preview'" )
        self.canvas.delete( "preview" )

        block = CanvasBlock( self.canvas, codefile, *self.PREVIEW_LOCATION, colour=self.colours["preview"] )
        self.blocks[block.id] = block



    def mouse_down( self, event ):
        self.select_location = ( event.x, event.y )
        logging.debug( "The mouse was pressed at (%d, %d)" % ( event.x, event.y ) )
        logging.debug( "The mouse went down on a block. Binding mouse release..." )
        selected = self.canvas.gettags( "current" )
        logging.debug( "Currently selected items tags are %s" % selected.__repr__() )
        self.selected_name = [a for a in selected if a.startswith( "name:" ) ][0]
        self.selected_id = [tag for tag in selected if tag.startswith( "id:" ) ][0]
        logging.debug( "Block selected was %s with %s" % ( self.selected_name, self.selected_id ) )
        block_id = self.selected_id[3:]

        self.canvas.addtag( 'Selected', 'withtag', self.selected_id )
        logging.debug( "Current blocks are: %s" % self.blocks )
        self.blocks[block_id].set_colour( self.colours['selected'] )

        self.canvas.bind( "<ButtonRelease-1>", self.block_move_mouse_release )

    def block_move_mouse_release( self, event ):
        logging.debug( "The mouse was released at (%d, %d)" % ( event.x, event.y ) )
        if event.x >= 0 and event.x <= self.canvas.winfo_width() \
            and event.y >= 0 and event.y <= self.canvas.winfo_height():
                logging.debug( "Valid move inside canvas. Relocating block." )
                self.canvas.move( "Selected", event.x - self.select_location[0], event.y - self.select_location[1] )
                if event.x >= self.PREVIEW_WIDTH:
                    if "preview" in self.canvas.gettags( "Selected" ):
                        logging.info( "Moved out of preview zone, adding now component to model" )
                        self.canvas.dtag( "preview" )
                        #TODO HERE - add to model compiler or what ever...
                    event.widget.itemconfigure( "Selected", fill=self.colours["block"] )
                    event.widget.itemconfigure( "type:text", fill="#000000" )
                else:
                    event.widget.itemconfigure( "Selected", fill=self.colours["preview"] )
                    self.canvas.addtag_withtag( "preview", "Selected" )

                #block = self.canvas.gettags("Selected")
                #logging.debug("Block moved was made up of these components: %s" % block.__repr__())
                self.canvas.dtag( "Selected", "Selected" )

        else:
            logging.info( "Invalid move." )


    def enter( self, event ):
        logging.debug( "Enter" )

    def leave( self, event ):
        logging.debug( "Leaving" )
