#!/usr/bin/env python
'''
Created on 20/11/2009

@author: Brian Thorne
'''


from Tkinter import *
import commands
import os

pathtoscript = os.path.dirname(os.path.realpath(__file__))

def load_example(name):
    """Load a actor file."""
    examplesDir = os.path.join(os.path.split(pathtoscript)[0],'src','actors')
    text = "".join(open(os.path.join(examplesDir,name),'r').readlines())
    return text

class ExamplesGroup:
    """A group of similar actors examples to be displayed in a block."""
    def __init__(self, name, frame, code, set_text_callback):
        self.name = name
        self.frame = frame
        self.code = code
        self.set_text = set_text_callback
        self.draw_list()
        
        
    def get_list(self):
        keys = self.code.keys()
        return keys

    def get_example(self,key):
        return self.code[key]
    
    def get_selection(self, x):
        index = self.listbox.curselection()[0]
        seltext = self.listbox.get(index)
        self.set_text(self.code[seltext])
    
    def draw_list(self):
        label = Label(self.frame, text=self.name)
        label.pack()
        self.listbox = Listbox(self.frame,selectmode=SINGLE)
        self.listbox.pack(fill=BOTH, expand=1)
        for i in self.get_list():
            self.listbox.insert(END, i)
           
        # left mouse click on a list item to display selection
        self.listbox.bind('<ButtonRelease-1>', self.get_selection)

        
class App:
    def __init__(self, frame):
      
        # The frame for all the file management on the left.
        file_frame = Frame(frame)
        file_frame.pack(side=LEFT,fill=BOTH, expand=1)

        math_code = {
            "addition": 
"""a = 10
b = 5
c = (a + b)
('a + b = ' + c).print()
            """,
            "multiplication": """a = 103
b = 578
c = a * b
('a * b = ' + c).print()
            """,
            "factorials": """self.fact = method(x){
if(x == 1){return (x )}
    return (x * self.fact(x-1))
}
a = 5
('!' + a + ' = ' + self.fact(a)).print()
""",
        }        
        
        program_code = {
"if":
"""# If statements do something after evaluating an expression
a = 5
if(a < 100)
{
    'a was less than 100'.print()
}

# If statements can be combined with elseif and else statements
if(a < 5)
{
    'a is less than 10'.print()
} elseif( a < 10 ){
    'a was less than 10'.print()
} else {
    'a was greater than 10'.print()
}

if( a==5)
{
    'a was 5!'.print()
}
""",

"for loop":
"""# Use a for loop to iterate over a range of numbers.
for(i=0,i<10,i = i + 1)
{
    i.print()
}
""",
'arrays':
"""# Any object in vorpal can be treated as an array
x = new()
x[0] = 1
x[1] = 200
x[2] = 4

x[1].print()

# Arrays can be used with dynamic slots
a = new()
a[500] = 'abc'
a[10000] = 'hello'
a[1.1 * 18] = 5
a['greeting'] = 'hi'
a.greeting.print()  # Note the slot access syntax
a[1.1 * 18].print()

""",
'booleans':
"""# true false and none
a = true
b = false
c = none
# Booleans can be used in logical expressions
if(a && !b || c){
    a.print()
    b.print()
    c.print()
}
""",
'methods':"""
# A method has to be added to an object
# This method takes 2 numbers and doesn't specify a return value
.multiply = method(x,y)
{
    (x*y).print()
}

# Calling the method
ans = .multiply(5,2)

ans.print()    # every method in vorpal returns it parent unless changed.
(ans == self).print()
ans.multiply(1,2)

# This is a method with a return value
.square = method(x)
{
    return (x*x)
}
.square(5).print()
""",
'Euler Project - 1':"""#http://projecteuler.net
total = 0
for(i=0,i<1000,i=i+1)
{
    if((i%3==0) || (i % 5==0))
    {
        total = total + i
    }
}
total.print()""",
'File IO':"""# Specify the path to a file with a string
path = 'fileIOtest.text'

# a file can be opened in either read or write mode
file_a = path.open('write')

# Strings can be written to the file
# Each string will be put on a new line
file_a.write('this is some text')
file_a.write('here is some more')
file_a.close()

file_b = path.open('read')

# The contents of a file can also be read by reading each line
'Reading file:'.print()
file_b.read().print()
file_b.read().print()

# 'EOF' is returned when the end of the file has been reached
file_b.read().print()
file_b.close()
"""
        }
        
        # These three next examples are loaded from the examples directory.
        example_code = {
            'All': load_example('Actor.py'), 
            #'stack': load_example('stack.vorpal'),
            #'increment': load_example('increment-decrement.vorpal'),
            }
        
        
        math_group = ExamplesGroup("Math",file_frame, math_code, self.write_to_win)
        program_group = ExamplesGroup("Programing", file_frame, program_code, self.write_to_win)
        misc = ExamplesGroup("Misc Examples", file_frame, example_code, self.write_to_win)
        # The frame for the main window
        main_frame = Frame(frame)
        main_frame.pack(side=LEFT)
        
        # Text Editor
        self.textEdit = Text(main_frame, width=80)
        self.textEdit.pack(side=TOP,fill=X)
        self.textEdit.insert(END,"self.hello = 'Hello World (Change me!)'\nself.hello.print()\n")
        
        # Frame to hold all the main buttons
        controls_frame = Frame(main_frame)
        controls_frame.pack(fill=X)
        
        self.console = Text(main_frame, width=80)
        self.console.pack(fill=X)
        self.console.insert(END, "Vorpal Output Console\n \n")
        

               
        run_button = Button(controls_frame, text="Run", fg="green", command=self.run)
        run_button.pack(side=LEFT)
        
        stop_button = Button(controls_frame, text="Stop", fg="red", command=self.stop)
        stop_button.pack(side=LEFT)
        
        save_button = Button(controls_frame, text="Save", command=self.save)
        save_button.pack(side=LEFT)
        
        help_button = Button(controls_frame, text="Help", command=self.help)
        help_button.pack(side=LEFT)
        
        quit_button = Button(controls_frame, text="QUIT", fg="white", command=frame.quit)
        quit_button.pack(side=LEFT)

    def save(self):
        from tkFileDialog import asksaveasfilename
        f = asksaveasfilename(parent=root, defaultextension=".txt")
        if not f:
            raise Cancel
        try:
            text = self.textEdit.get(1.0, END)
            writeFile(f,text)
        except IOError:
            from tkMessageBox import showwarning
            showwarning("Save As", "Cannot save the file.")
            raise Cancel

        
    def stop(self):
        pass
      
    def run(self):
        """Get the text from the window, save a temp file, run the tempfile with vorpal"""
        text = self.textEdit.get(1.0, END)
        temp = os.path.join(os.path.split(pathtoscript)[0],'local','temp.vorpal') 
        writeFile(temp,text)
        vr = VorpalRunner()
        output = vr.runFile(temp)
        self.write_to_console(output)
    
    def write_to_console(self,text):
        self.console.insert(END, "\n" + text  + "\n")
        self.console.see(END)    # Scroll the console
    
    def write_to_win(self,text):
        self.textEdit.delete(1.0, END)
        self.textEdit.insert('end', text)
        
    def help(self):
        self.write_to_console("""Help for Vorpal IDE""")


class VorpalRunner:
    
    def __init__(self):
        """
        In the future could set up the vorpal VM here.
        """

        self.vorpalPath = os.path.join(os.path.split(pathtoscript)[0],"bin","vorpal")
        self.vorpalOptions = "--record-info "
        if not os.path.exists(self.vorpalPath):
            raise Exception("Could not find vorpal at: " + self.vorpalPath)
        
    
    def runFile(self,file):
        cmd = self.vorpalPath + " " + self.vorpalOptions + '"' + file + '"'
        ( status, outtext) = commands.getstatusoutput(cmd)    
        # TODO redirect the stdin to the bottom pane...
        # TODO do in seperate thread, so we can stop a long running file...
        if status:
            print status, "Error in running vorpal file."
        return outtext
 
def writeFile(filepath,content):
    try:
        if os.path.exists(os.path.split(filepath)[0]):
            f = open(filepath,'w')
            f.seek(0)
            f.write(content)
            f.close()
    except Exception, e:
        print("File write error occured...", e)   
      
if __name__ == "__main__":
    root = Tk()
    root.title("Vorpal Gui")
    
    app = App(root)
    
    root.mainloop()
