'''
Created on Feb 10, 2010

@author: brianthorne
'''
from Tkconstants import RIDGE, TOP
from Tkinter import Canvas
import logging


class SimulationCanvas( object ):
    """A canvas where blocks can be dragged around and connected up"""
    # The class attribute colours will hold all the colour info 
    # Randomly chosen from (visibone.com colour-lab)
    colours = {
         "background": "#CCFFCC", # Pale weak green. A weak yellow is FFFFCC
         "block": "#00FF66", # a lime green
         "preview": "#0099FF", # a blue
         "selected": "#FFCCCC" # pale weak red
         }

    size = ( width, height ) = ( 550, 250 )

    font = ( "Helvetica", 10 )


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
        self.BLOCK_SIZE = ( self.BLOCK_WIDTH, self.BLOCK_HEIGHT ) = ( 70, 50 )

        # Draw a "preview" area
        self.canvas.create_line( self.PREVIEW_WIDTH, 0, self.PREVIEW_WIDTH, 250, dash=True )

    def preview_actor( self, codefile ):
        """
        Display a preview of an actor or compisite actor in the canvas,
        it will be dragable into desired position
        """
        logging.debug( "Creating a preview of %(name)s on simulation canvas." % {'name':codefile.name} )

        logging.debug( "Delecting any existing items still tagged 'preview'" )
        self.canvas.delete( "preview" )


        self.canvas.create_rectangle( *self.PREVIEW_LOCATION + self.BLOCK_SIZE,
                                     fill=self.colours["preview"],
                                     tags=["DRAG", # Anything moveable will have the "DRAG" tag
                                            "name:" + codefile.name, # Every blocks name will tagged so we can group bits together
                                            "type:block", # type: block/text
                                            "preview"
                                            ]
                                     )
        self.canvas.create_text ( self.PREVIEW_X + ( self.BLOCK_WIDTH / 2 ), self.PREVIEW_Y + 25,
                                 font=self.font, text=codefile.name,
                                 tags=["DRAG",
                                        "name:" + codefile.name,
                                        "type:text",
                                        "preview"
                                        ]
                                 )

    def mouse_down( self, event ):
        logging.debug( "The mouse was pressed at (%d, %d)" % ( event.x, event.y ) )
        logging.debug( "The mouse went down on a block. Binding mouse release..." )
        selected = self.canvas.gettags( "current" )
        logging.debug( "Currently selected items tags are %s" % selected.__repr__() )
        self.selected_name = [a for a in selected if a.startswith( "name:" ) ][0]
        logging.debug( "Block selected was %s" % self.selected_name )
        self.select_location = ( event.x, event.y )
        self.canvas.addtag( 'Selected', 'withtag', self.selected_name )
        event.widget.itemconfigure( "Selected", fill=self.colours["selected"] )
        self.canvas.bind( "<ButtonRelease-1>", self.mouse_release )

    def mouse_release( self, event ):
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
