try:
    import Tkinter as tk
except ImportError:
    import tkinter
from rushygraphics import *
from random import *
import graphics
from math import pi, cos, log
import colorsys

def main():
    root = tk.Tk()
    root.title('Mandelbrot Explorer')
    root.resizable(width=False, height=False)
    window = App(root)               #for class App below
    root.mainloop()
    
class App:
    def __init__(self, master):
        #frames
        self.master = master
        self.frame = tk.Frame(self.master)
        self.buttonframe = tk.Frame(self.master)

        #graphwin
        self.g = GraphWin(self.frame, 600, 600, False)

        #creating the widgets
        self.drawbutton = tk.Button(self.buttonframe, text = 'Draw Mandelbrot', font = ("Courier New", 14), command = lambda: self.iterate(-2, -2, 2, 2, self.g))
        self.zoombutton = tk.Button(self.buttonframe, text = 'Zoom In', font = ("Courier New", 14), command = self.zoom)
        self.clearbutton = tk.Button(self.buttonframe, text = 'Clear Window', font = ("Courier New", 14), command = self.clear)
        self.juliabutton = tk.Button(self.buttonframe, text = 'Generate Julia Set', font = ("Courier New", 14), command = lambda: self.Julia(-2, -2, 2, 2))
        self.inversebutton = tk.Button(self.buttonframe, text = 'Inverse Julia', font = ("Courier New", 14), command = lambda: self.inverse(-2, -2, 2, 2))
        self.helpbutton = tk.Button(self.buttonframe, text = 'Help', font = ("Courier New", 14), command = lambda: self.help())
        self.master.protocol('WM_DELETE_WINDOW', self.master.quit)

        #gridding stuff
        self.frame.grid(row=1, column=1, sticky=tk.N)
        self.buttonframe.grid(row=1, column=2, sticky=tk.N)
        self.zoombutton.grid(row=20, column=1, sticky=tk.N)
        self.drawbutton.grid(row=10, column=1, sticky=tk.N)
        self.clearbutton.grid(row=40, column=1, sticky=tk.N)
        self.juliabutton.grid(row=30, column=1, sticky=tk.N)
        self.inversebutton.grid(row=35, column=1, sticky=tk.N)
        self.helpbutton.grid(row=45, column=1, sticky=tk.N)
        #gridding graphwin
        self.g.grid(row=1, column=1, sticky=tk.N)
    #####################################################################
    '''Mandelbrot Explorer Functions begin here'''
    #####################################################################
    hue_offset = random()
    print hue_offset
    def color(self, n):
        '''generic function to determine color of a point based off its escape
        iterations. Runs with HSV color system and converts it to color_rgb'''
        hsvcolor =  colorsys.hsv_to_rgb(n/40.0 + self.hue_offset, 1, min(n/10.0, 1))  #hue_offset will make different color scheme each time.
        return color_rgb(int(255*hsvcolor[0]), int(255*hsvcolor[1]), int(255*hsvcolor[2]))
        
    def colorsmoothing(self, n, last_iter):
        '''This is a function for smoothing colors together.
        the number of iterations it takes to escape is passed in as n
        and last_iter is the next iteration of the point AFTER it has already escaped
        the graphwin window. in the iterate() function, last_iter is passed in explicitly
        as result**2 + clonepoint'''
        return n + 1 - log(log(abs(last_iter)))/log(2)
        
    def iterate(self, xmin, ymin, xmax, ymax, g, max_iter=50):      #draws the mandelbrot set
        self.clear()
        g.setCoords(xmin, ymin, xmax, ymax)
        start = Point(xmin, ymax)                                   #start at top left
        while start.getX() <= xmax:
            while start.getY() >= ymin:                             #go down the column
                
                result = complex(0,0)                               #start orbit with 0,0
                clonepoint = complex(start.getX(), start.getY())
               
                start.move(0, -1*abs(ymax-ymin)/600.0)
                
                '''this block of conditionals checks for main cardioid and bulb to the left of it'''
                test_var = (1-4.0*clonepoint)**0.5
                if abs(1 - test_var) <= 1 or abs(1 + test_var) <= 1:
                    continue
                elif abs(clonepoint - complex(-1, 0)) <= 0.25:
                    continue

                iterations = 0
                while iterations < max_iter:
                    result = result**2 + clonepoint    
                    iterations += 1            

                    if abs(result) > 2:  #cut off iterations if orbit exceeds window
                        break
                     
                if abs(result) > 2:
                    '''if the orbit exceeds the graphwin window, plot it. Some color coding going on also,
                    based on how many iterations it takes to escape. So white means in the Mandelbrot set'''
                    g.plot(clonepoint.real, clonepoint.imag, self.color(self.colorsmoothing(iterations, result**2 + clonepoint)))
                    '''you run the generic color function on the output of 
                    the colorsmoothing function to achieve a color smoothness'''
                    
                #start.move(0, -1*abs(ymax-ymin)/600.0)              #going down the column
                   
            start = Point(start.getX(), ymax)                         #start at the top of the next column.
            start.move(abs(xmax-xmin)/600.0, 0)

    def zoom(self):
        lowerleft = self.g.getMouse()
        upperright = self.g.getMouse()
        '''The next lines parse the zoom points to ensure that we maintain a square window as we zoom in'''
        '''Upperright and lowerleft denote only the first and 2nd clicks, you can select the corners
        of the box in any order'''
        vdist, hdist = abs(upperright.getY() - lowerleft.getY()), abs(upperright.getX()-lowerleft.getX())
        self.clear()
        if upperright.getY() > lowerleft.getY() and upperright.getX() > lowerleft.getX():
            if hdist > vdist: upperright.move(0, hdist-vdist) #move upper right vertex to preserve aspect ratio
            else: upperright.move(vdist-hdist, 0)
            itercount = ((abs(2*(abs(1-(2.0*(360000.0/vdist**2))**0.5))**0.5))*77.5)**0.5
            self.iterate(lowerleft.getX(), lowerleft.getY(), upperright.getX(), upperright.getY(), self.g, itercount)
            
        elif upperright.getY() < lowerleft.getY() and upperright.getX() < lowerleft.getX():
            upperright.move(hdist-vdist, 0)
            itercount = ((abs(2*(abs(1-(2.0*(360000.0/vdist**2))**0.5))**0.5))*77.5)**0.5
            self.iterate(upperright.getX(), upperright.getY(), lowerleft.getX(), lowerleft.getY(), self.g, itercount)
            
        elif upperright.getX() > lowerleft.getX() and upperright.getY() < lowerleft.getY():
            if vdist < hdist: upperright.move(vdist-hdist, 0) 
            else: upperright.move(vdist-hdist, 0)
            itercount = ((abs(2*(abs(1-(2.0*(360000.0/vdist**2))**0.5))**0.5))*77.5)**0.5
            self.iterate(lowerleft.getX(), upperright.getY(), upperright.getX(), lowerleft.getY(), self.g, itercount)
            
        elif upperright.getX() < lowerleft.getX() and upperright.getY() > lowerleft.getY():
            if vdist > hdist: upperright.move(0, hdist-vdist)
            else: upperright.move(hdist-vdist, 0)
            itercount = ((abs(2*(abs(1-(2.0*(360000.0/vdist**2))**0.5))**0.5))*77.5)**0.5
            self.iterate(upperright.getX(), lowerleft.getY(), lowerleft.getX(), upperright.getY(), self.g, itercount)

        #itercount is giant complicated formula to determine how many iterations we need at a certain zoom level
        print 'iterations = ', itercount
        print 'done', App.hue_offset

    def clear(self):
        self.g.delete("all")
    
    def help(self):
        helper = tk.Toplevel()
        helper.resizable(width=False, height=False)
        helper.title('Instructions')
        instructions = '1. Click \'Draw Mandelbrot\'\n\n 2. To zoom, first click \'Zoom In\'\n\n then click on any two opposite vertices of a rectangle you wish to zoom in on\n\n The program will automatically maintain a square aspect ratio\n\n 3. Click \'Generate Julia Set\', wait for the button to become unhighlighted\n (back to white), then click a point on the screen to generate its Julia Set.\n You can also use the Inverse option in the same way.\n\n 4. \'Clear Window\' erases the window.\n To regenerate the Mandelbrot Set, click \'Draw Mandelbrot\' again'
        msg = tk.Message(helper, text=instructions, font = ("Times New Roman", 14))
        msg.grid(row=1, column=1, sticky=tk.N)
        
    #function that produces corresponding Julia set for Point you click on Mandelbrot    
    def Julia(self, xmin, ymin, xmax, ymax):
        ### creating graphwin Window ###
        c = self.g.getMouse()
        c = complex(c.getX(), c.getY())
        Juliawin = graphics.GraphWin('Corresponding Julia Set', 600, 600, autoflush = False)
        Juliawin.setCoords(xmin, ymin, xmax, ymax)
                
        ### iteration algorithm (Brute Force) ###
        start = Point(xmin, ymax)                                   #start at top left
        while start.getX() <= xmax:
            while start.getY() >= ymin:                             #go down the column
                
                result = complex(start.getX(), start.getY())        #setting the imaginary number to iterate
                clonepoint = complex(start.getX(), start.getY())
                iterations = 0
                while iterations < 150:                             #iterating the complex function
                    result = result**2 + c
                    iterations += 1
                    if abs(result.real) > abs(xmax) or abs(result.imag) > abs(ymax):  #if orbit exceeds range of window, spare the extra iterations.
                        break
                           
                if abs(result.real) > abs(xmax) or abs(result.imag) > abs(ymax):
                    '''if the orbit exceeds the graphwin window, plot it.'''
                    Juliawin.plot(clonepoint.real, clonepoint.imag, self.color(self.colorsmoothing(iterations, result**2 + c)))
                    
                start.move(0, -1*abs(ymax-ymin)/600.0)
                
            start = Point(start.getX(), ymax)
            start.move(abs(xmax-xmin)/600.0, 0)
            
        ### Text to display on Julia Set Window ###
        text = graphics.Text(graphics.Point(1.5, -1.5), 'Click to Close')
        text.setTextColor('white')
        text.setSize(10)
        text.draw(Juliawin)
        
        text = graphics.Text(graphics.Point(1.5, 1.5), 'Julia Set For: %0.4f' % (c.real) + ', %0.4f' % (c.imag) + 'j')
        text.setTextColor('white')
        text.setSize(10)
        text.draw(Juliawin)
        Juliawin.getMouse()
        Juliawin.close()
            
    def inverse(self, xmin, ymin, xmax, ymax):
        c = self.g.getMouse()
        c = complex(c.getX(), c.getY())
        Juliawin = graphics.GraphWin('Corresponding Julia Set', 600, 600, autoflush = False)
        Juliawin.setCoords(xmin, ymin, xmax, ymax)
        startpoint = complex(2, -1.5)  #randomly choose z0
        
        root_1 = abs((startpoint-c)**0.5 - c)**2
        root_2 = abs(complex((-(startpoint-c)**0.5).real, ((startpoint-c)**0.5).imag- c))**2
        
        '''transient iterations'''
        for i in xrange(9000):
            newpoint = (startpoint-c)**0.5
            startpoint = newpoint
    
        '''plotting after iterating a lot'''
        for i in xrange(75000):
            if root_2/(root_2 + root_1) >= random(): 
                startpoint = (startpoint - c)**0.5 
            else: 
                startpoint = -(startpoint-c)**0.5
            Juliawin.plot(startpoint.real, startpoint.imag, 'blue')
            root_1 = abs(((startpoint-c)**0.5 - c)**2)
            root_2 = abs((-(startpoint-c)**0.5 - c)**2)
            
        startpoint = complex(2, -1.5)
        root_1 = abs((startpoint-c)**0.5 - c)**2
        #root_2 = abs(complex((-(startpoint-c)**0.5).real, ((startpoint-c)**0.5).imag- c))**2
    
        for i in xrange(90000):
            newpoint = (startpoint-c)**0.5
            if root_2/(root_2 + root_1) >= random():
                startpoint = newpoint
            else:
                startpoint = -(startpoint-c)**0.5
            Juliawin.plot(startpoint.real, startpoint.imag, 'blue')
            root_1 = abs((startpoint-c)**0.5 - c)**2
            root_2 = abs(complex((-(startpoint-c)**0.5).real, (startpoint-c)**0.5).imag- c)**2
            
        text = graphics.Text(graphics.Point(1.5, -1.5), 'Click to Close')
        text.setSize(10)
        text.draw(Juliawin)
        Juliawin.getMouse()
        Juliawin.close()

if __name__ == '__main__':
    main()