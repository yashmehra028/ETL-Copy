import matplotlib.pyplot as plt
import math
import copy

import numpy as np
import pandas as pd

class Sensor(object):
    def __init__(self, height, width, x=0, y=0, color='orange'):
        '''
        Create a sensor object with height (in x) and width (in y). x and y define the position of the center
        '''
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.color = color

        self.setOutline()

    def setOutline(self):
        self.outline = [
            [self.x - self.height/2., self.y + self.width/2.],
            [self.x + self.height/2., self.y + self.width/2.],
            [self.x + self.height/2., self.y - self.width/2.],
            [self.x - self.height/2., self.y - self.width/2.]
        ]

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.setOutline()

    def move_by(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.setOutline()

    def getPolygon(self):
        '''
        Returns a polygon that can be drawn with matplotlib
        '''
        return plt.Polygon(self.outline, closed=True, edgecolor='black', facecolor=self.color, alpha=0.5 )

class ReadoutBoard(Sensor):
    def __init__(self, height, width, x=0, y=0, color='green'):
        '''
        Create a readout board object with height (in x) and width (in y). x and y define the position of the center
        This inherits from Sensor - it's just a rectangle after all
        '''
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.color = color

        self.setOutline()

class PowerBoard(Sensor):
    def __init__(self, height, width, x=0, y=0, color='red'):
        '''
        Create a power board object with height (in x) and width (in y). x and y define the position of the center.
        This inherits from Sensor - it's just a rectangle after all
        '''
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.color = color

        self.setOutline()

class Module(object):
    def __init__(self, height, width, x=0, y=0, n_sensor_x=1, n_sensor_y=2, sensor_distance_y=22.5, sensor_distance_x=42.6):
        '''
        nSensor can be an even number (or 1).
        Sensor_distance is a measure from center of sensors.
        Symmetry is assumed.
        '''

        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.n_sensor_x = n_sensor_x
        self.n_sensor_y = n_sensor_y
        self.sensor_distance_x = 0 if n_sensor_x == 1 else sensor_distance_x 
        self.sensor_distance_y = 0 if n_sensor_y == 1 else sensor_distance_y
        self.sensors = []

        self.setOutline()

    def setOutline(self):
        self.outline = [
            [self.x - self.height/2., self.y + self.width/2.],
            [self.x + self.height/2., self.y + self.width/2.],
            [self.x + self.height/2., self.y - self.width/2.],
            [self.x - self.height/2., self.y - self.width/2.]
        ]

    def getPolygon(self):
        '''
        Returns a polygon that can be drawn with matplotlib
        '''
        return plt.Polygon(self.outline, fill=None, closed=True, edgecolor='black', linewidth=2)

    def populate(self, sensor):
        for ix in range(self.n_sensor_x):
            for iy in range(self.n_sensor_y):
                s_temp = copy.deepcopy(sensor)
                s_temp.move_to( (2*ix-1)*self.sensor_distance_x/2 + self.x, (2*iy-1)*self.sensor_distance_y/2 + self.y )
                self.sensors.append(s_temp)

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.setOutline()
        for s in self.sensors:
            s.move_to(s.x+x,s.y+y)

    def move_by(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.setOutline()
        for s in self.sensors:
            s.move_by(x, y)

class SuperModule(object):
    def __init__(self, module, powerboard, readoutboard, x=0, y=0, n_modules=3, module_gap=0.5, orientation='above'):
        '''
        This consists of N modules together with a readout board and a power board.
        '''

        self.height = module.height * n_modules + module_gap * (n_modules-1)
        self.width = module.width+powerboard.width
        self.x = x
        self.y = y
        self.orientation = orientation
        self.module_gap = module_gap
        self.n_modules = n_modules

        self.setOutline()

        # make copies of the components
        self.PB = copy.deepcopy(powerboard)
        self.RB = copy.deepcopy(readoutboard)
        # also keep the originals
        self._PB = copy.deepcopy(powerboard)
        self._RB = copy.deepcopy(readoutboard)
        self._module = copy.deepcopy(module) # not really used, but can be useful

        # place the modules
        self.modules = []
        for im in range(n_modules):
            m_temp = copy.deepcopy(module)
            m_temp.move_by( ( -(n_modules-1)/2 + im )*(module.height+module_gap),  (-1)*self.PB.width/2 if orientation=='above' else self.PB.width/2 )
            self.modules.append(m_temp)

        # update the dimensions of the RB and PB
        self.PB.height = self.height
        self.PB.setOutline()
        self.RB.height = self.height
        self.RB.setOutline()

        # move the components in place
        self.PB.move_by(0, self.RB.width/2 if orientation=='above' else (-1)*self.RB.width/2)
        self.RB.move_by(0, (-1)*self.PB.width/2 if orientation=='above' else self.PB.width/2)
    
    @classmethod
    def fromSuperModule(cls, supermodule, x=0, y=0, n_modules=3, module_gap=0.5, orientation='above'):
        
        return cls(supermodule._module, supermodule._PB, supermodule._RB, x=x, y=y, n_modules=n_modules, module_gap=module_gap, orientation=orientation)

    def setOutline(self):
        '''
        set the outline for the polygon, but also the coordinates of the corners in an easily accessible way.
        x1 < x2,
        y1 < y2
        so (x1, y1) is the lower left corner.
        '''
        self.x1 = self.x - self.height/2.
        self.x2 = self.x + self.height/2.
        self.y1 = self.y - self.width/2.
        self.y2 = self.y + self.width/2.

        self.outline = [
            [self.x1, self.y2],
            [self.x2, self.y2],
            [self.x2, self.y1],
            [self.x1, self.y1]
        ]

    def move_by(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.setOutline()
        self.RB.move_by(x,y)
        self.PB.move_by(x,y)
        for s in self.modules:
            s.move_by(x, y)
        

    def getPolygon(self):
        '''
        Returns a polygon that can be drawn with matplotlib
        '''
        return plt.Polygon(self.outline, fill=None, closed=True, edgecolor='blue', linewidth=3)

    def getActiveAreas(self):
        '''
        This will be important
        '''
        return

    def centerModule(self):
        '''
        Move the whole thing so that the modules are centered around y
        '''
        self.move_by(-self.x1, self.width/2-self.RB.width/2 if self.orientation=='above' else self.width/2-self.PB.width-self.RB.width/2)

class Dee(object):
    def __init__(self, r_inner, r_outer, z=0, color='red'):
        self.r_inner = r_inner
        self.r_outer = r_outer
        self.z       = z
        self.color   = color

    def populate(self, supermodule, shift_y=0, edge_x=6):
        '''
        takes a supermodule, puts them wherever there's space.
        shift_y = 0 will make the _modules_ symmetric around the y-axis.
        shift_y = module.width/2 would then be the second Dee, for example.
        '''
        smallest = SuperModule.fromSuperModule(supermodule, n_modules=1, module_gap=supermodule.module_gap, orientation=supermodule.orientation)
        smallest.centerModule()
        smallest.move_by(edge_x,0)

        self.n_rows    = int(2*self.r_outer/smallest.width)+2
        self.n_columns = int(self.r_outer/(smallest.height+smallest.module_gap))+2

        #self.slot_matrix = np.zeros((self.n_rows,self.n_columns))
        self.slot_matrix = [['O' for x in range(self.n_columns)] for y in range(self.n_rows)] 

        self.slots = []
        
        for row in range(self.n_rows):
            for column in range(self.n_columns):
                tmp = copy.deepcopy(smallest) #SuperModule.fromSuperModule(smallest, x=smallest.x, y=smallest.y, n_modules=1, module_gap=smallest.module_gap, orientation=smallest.orientation)
                tmp.move_by(column*(smallest.height+smallest.module_gap), (math.floor(self.n_rows/2)-row)*smallest.width )
                if (tmp.x1**2 + tmp.y1**2)>self.r_inner**2 and \
                   (tmp.x2**2 + tmp.y2**2)>self.r_inner**2 and \
                   (tmp.x1**2 + tmp.y2**2)>self.r_inner**2 and \
                   (tmp.x2**2 + tmp.y1**2)>self.r_inner**2 and \
                   (tmp.x1**2 + tmp.y1**2)<self.r_outer**2 and \
                   (tmp.x2**2 + tmp.y2**2)<self.r_outer**2 and \
                   (tmp.x1**2 + tmp.y2**2)<self.r_outer**2 and \
                   (tmp.x2**2 + tmp.y1**2)<self.r_outer**2:

                    self.slots.append(tmp)
                    self.slot_matrix[self.n_rows-row-1][column] = 'X'
                else:
                    self.slot_matrix[self.n_rows-row-1][column] = '.'        

        return


def getFactors(length, y):
    '''
    This is an old function. Should get updated
    '''
    tmp = length
    nSeven = 0
    nSix = 0
    nThree = 0
    length = length - nThree*3 # new
    nSevenMax = int(length/7)
    for i in reversed(range(nSevenMax+1)):
        if (length-i*7)%3==0 and (length-i*7>=0 or length==7):
            length = length-i*7
            nSeven = i
            break
    nSix = int(length/6) # new
    if length%6>0:
        nThree += 1
    if length == 11: 
        nSeven+=1
        nSix-=1 # that's after subtraction
    column = [7]*nSeven + [6]*nSix + [3]*nThree
    if not sum(column) == tmp: print ("Something went wrong")
    return column

if __name__ == "__main__":

    # run an example
    s = Sensor(42.5, 22)
    m = Module(43.10, 56.50, n_sensor_x=1, n_sensor_y=2, sensor_distance_y=22.5, sensor_distance_x=42.5+0.1)
    m.populate(s)
    
    rb = ReadoutBoard(10,56.5, color='green')
    pb = ReadoutBoard(10,29.5, color='red')
    
    SM = SuperModule(m, pb, rb, n_modules=3, orientation='above')
    
    SM.centerModule()


    D = Dee(315, 1185)
    D.populate(SM)


    for row in D.slot_matrix:
        print (' '.join(row))
