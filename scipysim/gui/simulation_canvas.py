'''
Created on Feb 10, 2010

@author: brianthorne
'''
from Tkconstants import RIDGE, TOP
from Tkinter import Canvas
import logging
import itertools


# The colour palette
# Randomly chosen from (visibone.com colour-lab)
# TODO: make configurable
colours = {
     "background": "#CCFFCC", # Pale weak green. A weak yellow is FFFFCC
     "block": "#00FF66", # a lime green
     "preview": "#0099FF", # a blue
     "selected": "#FF6600" # orange - red
     }

class CanvasBlock ( object ):
    '''An instance of an Actor drawn on a Simulation Canvas'''

    # To create a unique ID number for every block.
    # functools to map to str
    counter = itertools.count()

    # Settings for all blocks.
    font = ( "Helvetica", 10 )
    BLOCK_SIZE = ( BLOCK_WIDTH, BLOCK_HEIGHT ) = ( 70, 50 )


    def __init__( self, canvas, codefile, x, y):
        self.canvas = canvas
        self.codefile = codefile
        self.x, self.y = x, y
        self.colour = colours["preview"]
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


        self.canvas.create_rectangle( *( x, y )
                                      + (x + self.BLOCK_WIDTH, y + self.BLOCK_HEIGHT),
                                     fill=self.colour,
                                     tags=preview_tags + ["type:block"]
                                     )

        self.canvas.create_text ( x + ( self.BLOCK_WIDTH / 2 ), y + ( self.BLOCK_HEIGHT / 2 ),
                                 font=self.font, text=codefile.name,
                                 tags=preview_tags + ["type:text"]
                                 )

        num_inputs, num_outputs = codefile.num_inputs, codefile.num_outputs

        # Draw on input and output ports
        port_size = 5

        logging.debug( "Block has %d inputs, and %d outputs." % ( num_inputs, num_outputs ) )

        if num_inputs is None:
            # Will default to drawing one connector, and when it is used we will draw another
            num_inputs = 1
        elif num_inputs == 0:
            pass
        else:
            input_gap = 0
            if num_inputs > 1:
                input_gap = (self.BLOCK_HEIGHT - 2*port_size) / (num_inputs - 1)
            x_, y_ = x, ((y + self.BLOCK_HEIGHT / 2) - ((num_inputs - 1) * input_gap)/2)

            for input in xrange( num_inputs ):
                self.canvas.create_polygon( x - port_size, y_ - port_size, x, y_, x - port_size , y_ + port_size,
                                            tags=preview_tags + ["type:input-%d" % input],
                                            fill="#000000" )
                y_ = y_ + input_gap

        if num_outputs is None:
            num_outputs = 1
        elif num_outputs == 0:
            pass
        else:
            output_gap = 0
            if num_outputs > 1:
                output_gap = (self.BLOCK_HEIGHT - 2*port_size) / (num_outputs - 1)
            x_, y_ = x + self.BLOCK_WIDTH + 1, ((y + self.BLOCK_HEIGHT / 2) - ((num_outputs - 1) * output_gap)/2)

            for output in xrange( num_outputs ):
                self.canvas.create_polygon( x_, y_ - port_size , x_ + port_size, y_, x_, y_ + port_size,
                                            tags=preview_tags + ["type:output-%d" % output],
                                            fill="#000000" )
                y_ = y_ + output_gap


    def move_to( self, x, y ):
        '''Move this block to the specified location'''
        self.x, self.y = x - self.selected_x, y - self.selected_y
        self.canvas.move( "id:%s" % self.id, self.x, self.y )


    def select(self, selected_x, selected_y):
        """Select the block."""
        self.canvas.addtag( 'Selected', "withtag" , "id:%s" % self.id )
        self.canvas.dtag( "id:%s" % self.id, "preview" )
        self.set_colour(colours["selected"])
        self.selected_x, self.selected_y = selected_x, selected_y

    def unselect(self):
        """Unselect the block."""
        self.canvas.dtag( "id:%s" % self.id, 'Selected' )
        self.set_colour(colours["block"])

    def preview(self):
        """Preview the block."""
        self.canvas.addtag( 'preview', "withtag" , "id:%s" % self.id )
        self.canvas.dtag( "id:%s" % self.id, "Selected" )
        self.set_colour(colours["preview"])

    def is_preview(self):
        return self.canvas.find_withtag("preview && id:%s" % self.id)

    def set_colour( self, colour ):
        '''Set the main colour of this block to "colour" but keep
        the text and outline etc black.
        '''
        # TODO filter out all but the block
        self.canvas.itemconfigure("id:%s && type:block" % self.id, fill=colour )

    def select_port(self, port):
        """Select a port."""
        self.canvas.addtag( "Selected", "withtag", "id:%s && type:%s" % (self.id, port) )
        self.canvas.itemconfigure("id:%s && type:%s" % (self.id, port), fill=colours["selected"] )



class SimulationCanvas( object ):
    """A canvas where blocks can be dragged around and connected up"""

    size = ( width, height ) = ( 550, 300 )

    def __init__( self, frame ):
        # Create the canvas
        self.canvas = Canvas( frame,
                             width=self.width, height=self.height,
                             relief=RIDGE,
                             background=colours["background"],
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
        self.canvas.create_line( self.PREVIEW_WIDTH, 0, self.PREVIEW_WIDTH, self.height, dash=True )

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

        block = CanvasBlock( self.canvas, codefile, *self.PREVIEW_LOCATION )
        self.blocks[block.id] = block



    def mouse_down( self, event ):
        logging.debug( "The mouse was pressed at (%d, %d)" % ( event.x, event.y ) )
        logging.debug( "The mouse went down on a block. Binding mouse release..." )
        selected = self.canvas.gettags( "current" )
        logging.debug( "Currently selected items tags are %s" % selected.__repr__() )
        self.selected_name = [tag for tag in selected if tag.startswith( "name:" ) ][0][5:]
        self.selected_id = [tag for tag in selected if tag.startswith( "id:" ) ][0][3:]
        self.selected_type = [tag for tag in selected if tag.startswith( "type:" ) ][0][5:]
        logging.debug( "Block selected was %s with id:%s" % ( self.selected_name, self.selected_id ) )

        #self.canvas.addtag( 'Selected', 'withtag', self.selected_id )
        logging.debug( "Current blocks are: %s" % self.blocks )
        #self.blocks[block_id].set_colour( colours['selected'] )

        if self.selected_type == "block" or self.selected_type == "text":
            self.blocks[self.selected_id].select(event.x, event.y)
            self.canvas.bind( "<ButtonRelease-1>", self.block_move_mouse_release )
        elif self.selected_type.startswith("input") or self.selected_type.startswith("output"):
            self.blocks[self.selected_id].select_port(self.selected_type)
            self.canvas.bind( "<ButtonRelease-1>", self.port_connect_mouse_release )
        else:
            logging.info("Tried to select %s" % self.selected_type)

    
    def block_move_mouse_release( self, event ):
        logging.debug( "The mouse was released at (%d, %d)" % ( event.x, event.y ) )
        self.canvas.bind( "<ButtonRelease-1>", lambda e: None )
        if event.x >= 0 and event.x <= self.canvas.winfo_width() \
            and event.y >= 0 and event.y <= self.canvas.winfo_height():
                logging.debug( "Valid move inside canvas. Relocating block." )
                self.blocks[self.selected_id].move_to(event.x, event.y)
                if event.x >= self.PREVIEW_WIDTH:
                    if self.blocks[self.selected_id].is_preview():
                        logging.info( "Moved out of preview zone, adding new component to model" )
                        #TODO HERE - add to model compiler or what ever...
                    self.blocks[self.selected_id].unselect()
                else:
                    self.blocks[self.selected_id].preview()
        else:
            logging.info( "Invalid move." )

    def port_connect_mouse_release( self, event ):
        logging.debug( "The mouse was released at (%d, %d)" % ( event.x, event.y ) )
        self.canvas.bind( "<ButtonRelease-1>", lambda e: None )
        if event.x >= 0 and event.x <= self.canvas.winfo_width() \
            and event.y >= 0 and event.y <= self.canvas.winfo_height():
                logging.debug( "Valid location inside canvas." )

                event.widget.itemconfigure( "Selected", fill="#000000" )
                event.widget.itemconfigure( "type:text", fill="#000000" )

                #block = self.canvas.gettags("Selected")
                #logging.debug("Block moved was made up of these components: %s" % block.__repr__())
                self.canvas.dtag( "Selected", "Selected" )

        else:
            logging.info( "Invalid wiring." )

    def enter( self, event ):
        logging.debug( "Enter" )

    def leave( self, event ):
        logging.debug( "Leaving" )
