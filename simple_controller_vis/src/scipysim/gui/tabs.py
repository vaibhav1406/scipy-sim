# A simple Notebook-like Tkinter widget.
"""
TODO: A notebook should have minimise symbol in the top right corner when
expanded, and an expand symbol when minimised.
A quick work around is to have an empty frame as a tab.

TODO replace this with tile or pyttk or one of the thousands of prebuilt widget sets...
"""

from Tkinter import TOP, LEFT, BOTTOM, Frame, Tk, Radiobutton, IntVar, RIDGE, BOTH

class Notebook:

    # initialisation. receives the master widget
    # reference and the Notebook orientation
    def __init__( self, master, side=LEFT ):

        self.active_fr = None
        self.count = 0
        self.choice = IntVar( 0 )

        # allows the TOP and BOTTOM
        # radiobuttons' positioning.
        if side in ( TOP, BOTTOM ):
            self.side = LEFT
        else:
            self.side = TOP

        # creates notebook's frames structure
        self.rb_fr = Frame( master, borderwidth=2, relief=RIDGE )
        self.rb_fr.pack( side=side, fill=BOTH )
        self.screen_fr = Frame( master, borderwidth=2, relief=RIDGE )
        self.screen_fr.pack( fill=BOTH )


    # return a master frame reference for the external frames (screens)
    def __call__( self ):
        return self.screen_fr


    # add a new frame (screen) to the (bottom/left of the) Notebook
    def add_screen( self, fr, title ):

        b = Radiobutton( self.rb_fr, text=title, indicatoron=0, \
            variable=self.choice, value=self.count, \
            command=lambda: self.display( fr ), padx=10, pady=5 )
        b.pack( fill=BOTH, side=self.side )

        # ensures the first frame will be
        # the first selected/enabled
        if not self.active_fr:
            fr.pack( fill=BOTH, expand=1 )
            self.active_fr = fr

        self.count += 1

        # returns a reference to the newly created
        # radiobutton (allowing its configuration/destruction)         
        return b


    # hides the former active frame and shows 
    # another one, keeping its reference
    def display( self, fr ):

        self.active_fr.forget()
        fr.pack( fill=BOTH, expand=1 )
        self.active_fr = fr

# END


###-------------------------------
# simple demonstration of the Tkinter Notebook
from Tkinter import Button, Entry
def test_tabs():
    a = Tk()
    n = Notebook( a, TOP )

    # uses the Notebook's frame
    f1 = Frame( n() )
    b1 = Button( f1, text="Ignore me" )
    e1 = Entry( f1 )
    # pack your widgets before adding the frame 
    # to the Notebook (but not the frame itself)!
    b1.pack( fill=BOTH, expand=1 )
    e1.pack( fill=BOTH, expand=1 )

    # keeps the reference to the radiobutton (optional)
    x1 = n.add_screen( f1, "Tab 1" )

    f2 = Frame( n() )
    # this button destroys the 1st screen radiobutton
    b2 = Button( f2, text='Remove Tab 1', command=lambda:x1.destroy() )
    b3 = Button( f2, text='Beep...', command=lambda:Tk.bell( a ) )
    b2.pack( fill=BOTH, expand=1 )
    b3.pack( fill=BOTH, expand=1 )

    f3 = Frame( n() )


    n.add_screen( f2, "Tab 2" )
    n.add_screen( f3, "Minimize" )
    a.mainloop()

if __name__ == "__main__":
    test_tabs()

