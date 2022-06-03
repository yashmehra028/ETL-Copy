from turtle import color
import matplotlib.pyplot as plt
import math
import copy

import numpy as np
import pandas as pd

from partition import *


colors = {
    3: 'cyan',
    6: 'magenta',
    7: 'yellow',
    11: 'orange',
    12: 'blue',
    14: 'green'
}


class three_vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.r = np.sqrt(x**2+y**2)
        self.theta = np.arctan2(self.r, z)
        self.eta = -np.log(np.tan(self.theta/2))
        self.phi = np.arctan2(y, x)

    @classmethod
    def fromEtaPhi(cls, eta, phi, z):
        cls.eta = eta
        cls.phi = phi
        cls.z = z
        cls.theta = 2*np.arctan(np.exp(cls.eta*(-1)))
        cls.r = z*np.tan(cls.theta)
        cls.x = cls.r*np.cos(cls.phi)
        cls.y = cls.r*np.sin(cls.phi)

        return cls


class Pixel:
    def __init__(self, x, y, height, width):
        self.x = x
        self.y = y
        self.height = height
        self.width = width

    def setOutline(self):
        self.x1 = self.x - self.height/2
        self.x2 = self.x + self.height/2
        self.y1 = self.y - self.width/2
        self.y2 = self.y + self.width/2
        self.outline = [
            (self.x1, self.y2),
            (self.x2, self.y2),
            (self.x2, self.y1),
            (self.x1, self.y1)
        ]

    def getPolygon(self):
        return plt.Polygon(self.outline, color='blue', closed=True, edgecolor='black', alpha=0.6)


class Sensor2(object):
    def __init__(self, height, width, x=0, y=0, deadspace1=0.3, deadspace2=0.5, color='orange'):
        '''
        Create a sensor object with height (in x) and width (in y). x and y define the position of the center
        '''
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.color = color
        self.deadspace1 = deadspace1
        self.deadspace2 = deadspace2

        self.setOutline()

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

    def setActiveArea(self):
        self.ax1 = self.x - self.height/2. + self.deadspace1
        self.ax2 = self.x + self.height/2. - self.deadspace1
        self.ay1 = self.y - self.width/2. + self.deadspace2
        self.ay2 = self.y + self.width/2. - self.deadspace1

        self.activeArea = [
            [self.ax1, self.ay2],
            [self.ax2, self.ay2],
            [self.ax2, self.ay1],
            [self.ax1, self.ay1]
        ]

    def get_pixel_centers(self, m, n, gap):

        self.n_pixels = m*n
        self.x_pixel_size = (abs(self.ax2-self.ax1)-(m-1)*gap)/m
        self.y_pixel_size = (abs(self.ay2-self.ay1)-(n-1)*gap)/n
        self.x0 = self.ax1
        self.y0 = self.ay2
        self.centers_new_system = []
        self.centers_pixels = []

        initial_y = -1*(self.y_pixel_size/2)

        for _ in range(n):
            initial_x = 1*(self.x_pixel_size/2)
            for _ in range(m):
                coor_new = [initial_x, initial_y]
                coor_needed = [initial_x+self.x0, initial_y+self.y0]
                self.centers_pixels.append(coor_needed)
                self.centers_new_system.append(coor_new)
                initial_x += (gap + self.x_pixel_size)

            initial_y -= (gap + self.y_pixel_size)

    def getPixelsOutline(self):
        self.pixels = []
        for center in self.centers_pixels:
            pixel = Pixel(
                x=center[0], y=center[1], height=self.x_pixel_size, width=self.y_pixel_size)
            pixel.setOutline()
            self.pixels.append(pixel)

    def getActiveArea(self):
        return abs((self.ax2-self.ax1)*(self.ay2-self.ay1))

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.setOutline()
        self.setActiveArea()

    def move_by(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.setOutline()
        self.setActiveArea()

    def getPolygon(self, active=False):
        '''
        Returns a polygon that can be drawn with matplotlib
        '''
        return plt.Polygon(self.outline if not active else self.activeArea, closed=True, edgecolor='black', facecolor=self.color if not active else 'gray', alpha=0.5)


class Sensor(object):
    def __init__(self, height, width, x=0, y=0, deadspace=0.5, color='orange'):
        '''
        Create a sensor object with height (in x) and width (in y). x and y define the position of the center
        '''
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.color = color
        self.deadspace = deadspace

        self.setOutline()

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

    def setActiveArea(self):
        self.ax1 = self.x - self.height/2. + self.deadspace
        self.ax2 = self.x + self.height/2. - self.deadspace
        self.ay1 = self.y - self.width/2. + self.deadspace
        self.ay2 = self.y + self.width/2. - self.deadspace

        self.activeArea = [
            [self.ax1, self.ay2],
            [self.ax2, self.ay2],
            [self.ax2, self.ay1],
            [self.ax1, self.ay1]
        ]

    def get_pixel_centers(self, m, n, gap):

        self.n_pixels = m*n
        self.x_pixel_size = (abs(self.ax2-self.ax1)-(m-1)*gap)/m
        self.y_pixel_size = (abs(self.ay2-self.ay1)-(n-1)*gap)/n
        self.x0 = self.x2
        self.y0 = self.y1
        self.centers_new_system = []
        self.centers_pixels = []

        initial_x = -1*(self.deadspace + self.x_pixel_size/2)

        for _ in range(m):
            initial_y = 1*(self.deadspace + self.y_pixel_size/2)
            for _ in range(n):
                coor_new = [initial_x, initial_y]
                coor_needed = [initial_x+self.x0, initial_y+self.y0]
                self.centers_pixels.append(coor_needed)
                self.centers_new_system.append(coor_new)
                initial_y += (gap + self.y_pixel_size)

            initial_x -= (gap + self.x_pixel_size)

    def getPixelsOutline(self):
        self.pixels = []
        for center in self.centers_pixels:
            pixel = Pixel(
                x=center[0], y=center[1], height=self.x_pixel_size, width=self.y_pixel_size)
            pixel.setOutline()
            self.pixels.append(pixel)

    def getActiveArea(self):
        return abs((self.ax2-self.ax1)*(self.ay2-self.ay1))

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.setOutline()
        self.setActiveArea()

    def move_by(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.setOutline()
        self.setActiveArea()

    def getPolygon(self, active=False):
        '''
        Returns a polygon that can be drawn with matplotlib
        '''
        return plt.Polygon(self.outline if not active else self.activeArea, closed=True, edgecolor='black', facecolor=self.color if not active else 'gray', alpha=0.5)


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
        self.deadspace = 0

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
        self.deadspace = 0

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

        self.getActiveCorners()

    def getPolygon(self):
        '''
        Returns a polygon that can be drawn with matplotlib
        '''
        return plt.Polygon(self.outline, fill=None, closed=True, edgecolor='black', linewidth=2)

    def populate(self, sensor):
        for ix in range(self.n_sensor_x):
            for iy in range(self.n_sensor_y):
                s_temp = copy.deepcopy(sensor)
                s_temp.move_to((2*ix-1)*self.sensor_distance_x/2 +
                               self.x, (2*iy-1)*self.sensor_distance_y/2 + self.y)
                self.sensors.append(s_temp)

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.setOutline()
        for s in self.sensors:
            s.move_to(s.x+x, s.y+y)

    def move_by(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.setOutline()
        for s in self.sensors:
            s.move_by(x, y)

    def getActiveArea(self):
        return sum([s.getActiveArea() for s in self.sensors])

    def getActiveCorners(self):
        '''
        this gets numpy arrays of the corners.
        in the end, we can check if a particle with (x,y) intersects with the active area of a sensor by doing
        ((m.vax1 < x) & (x < m.vax2) & (m.vay1 < y) & (y < m.vay2)).any()
        '''
        self.vax1 = [s.ax1 for s in self.sensors]
        self.vax2 = [s.ax2 for s in self.sensors]
        self.vay1 = [s.ay1 for s in self.sensors]
        self.vay2 = [s.ay2 for s in self.sensors]


class SuperModule(object):
    def __init__(self, module, powerboard, readoutboard, x=0, y=0, n_modules=3, module_gap=0.5, orientation='above', color='b'):
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
        self.color = color

        self.setOutline()

        # make copies of the components
        self.PB = copy.deepcopy(powerboard)
        self.RB = copy.deepcopy(readoutboard)
        # also keep the originals
        self._PB = copy.deepcopy(powerboard)
        self._RB = copy.deepcopy(readoutboard)
        # not really used, but can be useful
        self._module = copy.deepcopy(module)

        # place the modules
        self.modules = []
        for im in range(n_modules):
            m_temp = copy.deepcopy(module)
            m_temp.move_by((-(n_modules-1)/2 + im)*(module.height+module_gap),
                           (-1)*self.PB.width/2 if orientation == 'above' else self.PB.width/2)
            self.modules.append(m_temp)

        # update the dimensions of the RB and PB
        self.PB.height = self.height
        self.PB.setOutline()
        self.RB.height = self.height
        self.RB.setOutline()

        # move the components in place
        self.PB.move_by(0, self.RB.width/2 if orientation ==
                        'above' else (-1)*self.RB.width/2)
        self.RB.move_by(0, (-1)*self.PB.width/2 if orientation ==
                        'above' else self.PB.width/2)

    @classmethod
    def fromSuperModule(cls, supermodule, x=0, y=0, n_modules=3, module_gap=0.5, orientation='above', color='b'):

        return cls(supermodule._module, supermodule._PB, supermodule._RB, x=x, y=y, n_modules=n_modules, module_gap=module_gap, orientation=orientation, color=color)

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
        self.RB.move_by(x, y)
        self.PB.move_by(x, y)
        for s in self.modules:
            s.move_by(x, y)

    def getPolygon(self):
        '''
        Returns a polygon that can be drawn with matplotlib
        '''
        return plt.Polygon(self.outline, closed=True, linewidth=3, edgecolor='black', facecolor=self.color, alpha=0.5)

    def getActiveArea(self):
        '''
        This will be important
        '''
        return sum([sum([s.getActiveArea() for s in m.sensors]) for m in self.modules])

    def centerModule(self):
        '''
        Move the whole thing so that the modules are centered around y
        '''
        self.move_by(-self.x1, self.width/2-self.RB.width/2 if self.orientation ==
                     'above' else self.width/2-self.PB.width-self.RB.width/2)

    def centerPB(self):
        '''
        Move the whole thing so that the modules are centered around y
        '''
        self.move_by(-self.x1, -self.width/2+self.PB.width /
                     2 if self.orientation == 'above' else self.width/2-self.PB.width/2)


class Dee(object):
    def __init__(self, r_inner, r_outer, z=0, color='red'):
        self.r_inner = r_inner
        self.r_outer = r_outer
        self.area = (r_outer**2 - r_inner**2)*np.pi/2
        self.z = z
        self.color = color
        self.supermodules = []

    def populate(self, supermodule, edge_x=6, shift_x=0, shift_y=0, flavors=[3, 6, 7], center_RB=False, center_PB=False):
        '''
        takes a supermodule, puts them wherever there's space.
        shift_y = 0 will make the _modules_ symmetric around the y-axis.
        shift_y = module.width/2 would then be the second Dee, for example.
        '''
        smallest = SuperModule.fromSuperModule(
            supermodule, n_modules=1, module_gap=supermodule.module_gap, orientation=supermodule.orientation)
        if center_RB:
            smallest.centerModule()
        if center_PB:
            smallest.centerPB()
        smallest.move_by(edge_x, 0)

        self.n_rows = int(2*self.r_outer/smallest.width)+2
        self.n_columns = int(
            self.r_outer/(smallest.height+smallest.module_gap))+2

        #self.slot_matrix = np.zeros((self.n_rows,self.n_columns))
        self.slot_matrix = [
            [0 for x in range(self.n_columns)] for y in range(self.n_rows)]

        self.slots = [[] for y in range(self.n_rows)]

        for row in range(self.n_rows):
            for column in range(self.n_columns):
                # SuperModule.fromSuperModule(smallest, x=smallest.x, y=smallest.y, n_modules=1, module_gap=smallest.module_gap, orientation=smallest.orientation)
                tmp = copy.deepcopy(smallest)
                tmp.move_by(column*(smallest.height+smallest.module_gap),
                            (math.floor(self.n_rows/2)-row)*smallest.width)
                if (tmp.x1**2 + tmp.y1**2) > self.r_inner**2 and \
                   (tmp.x2**2 + tmp.y2**2) > self.r_inner**2 and \
                   (tmp.x1**2 + tmp.y2**2) > self.r_inner**2 and \
                   (tmp.x2**2 + tmp.y1**2) > self.r_inner**2 and \
                   (tmp.x1**2 + tmp.y1**2) < self.r_outer**2 and \
                   (tmp.x2**2 + tmp.y2**2) < self.r_outer**2 and \
                   (tmp.x1**2 + tmp.y2**2) < self.r_outer**2 and \
                   (tmp.x2**2 + tmp.y1**2) < self.r_outer**2:

                    # NOW apply the shift, otherwise we mess up the "on-disk" requirement. This can cause weirdness in the plots.
                    tmp.move_by(shift_x, shift_y)

                    self.slots[self.n_rows-row-1].append(tmp)

                    self.slot_matrix[self.n_rows-row-1][column] = 1
                else:
                    self.slot_matrix[self.n_rows-row-1][column] = 0

        # now let's go through the matrix again and see which slots we can actually populate
        self.module_matrix = []
        self.slots_flat = []
        for i, row in enumerate(self.slot_matrix):
            # maximum length
            length = sum(row)

            # use the partition function to get the composition of RB flavors
            partition = getPartition(length, flavors=flavors)
            covered = sum(partition)

            x_shift = 0
            for k, n_mod in enumerate(partition):
                tmp = copy.deepcopy(SuperModule.fromSuperModule(
                    supermodule, n_modules=n_mod, module_gap=supermodule.module_gap, orientation=supermodule.orientation, color=colors[n_mod]))
                tmp.move_by(self.slots[i][0].x1-tmp.x1 +
                            x_shift, self.slots[i][0].y1-tmp.y1)
                x_shift += tmp.height + tmp.module_gap
                self.supermodules.append(tmp)
                # break
                # self.slots[i][0].x1

            for j in range(length):
                self.slots[i][j].covered = True if j < covered else False

            self.slots_flat += self.slots[i] if length > 0 else []

            if length == covered:
                self.module_matrix.append(row)
            else:
                self.module_matrix.append(
                    [1]*covered + [-1]*(length-covered) + [0]*(len(row)-length))

        self.getAllCorners()

        return

    def fromCenters(self, centers, sensor):
        '''
        this is useful for old layouts / tilings

        '''
        # loop over centers
        self.sensors = []
        for x, y in centers:
            tmp = copy.deepcopy(sensor)
            tmp.move_to(x, y)
            self.sensors.append(tmp)

        # manually get the corners
        self.vax1 = []
        self.vax2 = []
        self.vay1 = []
        self.vay2 = []

        for sen in self.sensors:

            self.vax1 += [sen.ax1]
            self.vax2 += [sen.ax2]
            self.vay1 += [sen.ay1]
            self.vay2 += [sen.ay2]

        self.vax1 = np.array(self.vax1)
        self.vax2 = np.array(self.vax2)
        self.vay1 = np.array(self.vay1)
        self.vay2 = np.array(self.vay2)

    def fromCenters2(self, centers, sensor, m_sens, n_sens, gap_pixel):
        '''
        this is useful for old layouts / tilings

        '''
        # loop over centers
        self.m_sens = m_sens
        self.n_sens = n_sens
        self.gap_pixel = gap_pixel
        self.sensors = []
        for x, y in centers:
            tmp = copy.deepcopy(sensor)
            tmp.move_to(x, y)
            self.sensors.append(tmp)

        # manually get the corners
        self.vax1 = []
        self.vax2 = []
        self.vay1 = []
        self.vay2 = []

        for sen in self.sensors:
            sen.get_pixel_centers(
                m=self.m_sens, n=self.n_sens, gap=self.gap_pixel)
            sen.getPixelsOutline()
            for pixel in sen.pixels:
                self.vax1 += [pixel.x1]
                self.vax2 += [pixel.x2]
                self.vay1 += [pixel.y1]
                self.vay2 += [pixel.y2]

        self.vax1 = np.array(self.vax1)
        self.vax2 = np.array(self.vax2)
        self.vay1 = np.array(self.vay1)
        self.vay2 = np.array(self.vay2)

    def getAllCorners(self):
        self.vax1 = []
        self.vax2 = []
        self.vay1 = []
        self.vay2 = []

        for slot in self.slots_flat:
            if slot.covered:
                for mod in slot.modules:
                    for sen in mod.sensors:
                        self.vax1 += [sen.ax1]
                        self.vax2 += [sen.ax2]
                        self.vay1 += [sen.ay1]
                        self.vay2 += [sen.ay2]

        self.vax1 = np.array(self.vax1)
        self.vax2 = np.array(self.vax2)
        self.vay1 = np.array(self.vay1)
        self.vay2 = np.array(self.vay2)

    def intersect(self, x, y):
        '''
        ((m.vax1 < x) & (x < m.vax2) & (m.vay1 < y) & (y < m.vay2)).any()
        '''
        return ((self.vax1 < x) & (x < self.vax2) & (self.vay1 < y) & (y < self.vay2)).any()


if __name__ == "__main__":

    # run an example
    # current TAMALES
    s = Sensor(42.5, 22)
    m = Module(43.10, 56.50, n_sensor_x=1, n_sensor_y=2,
               sensor_distance_y=22.5, sensor_distance_x=42.5+0.1)

    # the other possibility
    #sensor_x = (42.5/2 + 0.5)
    #s = Sensor(sensor_x, 22)
    #m = Module(44.20, 56.50, n_sensor_x=2, n_sensor_y=2, sensor_distance_y=22.5, sensor_distance_x=sensor_x+0.1)

    m.populate(s)

    rb = ReadoutBoard(10, 56.5, color='green')
    pb = ReadoutBoard(10, 29.5, color='red')

    SM = SuperModule(m, pb, rb, n_modules=3, orientation='above')

    D = Dee(315, 1185)
    D.populate(SM, flavors=[3, 6, 7], center_RB=True,
               edge_x=6, shift_x=2, shift_y=2)

    # for row in D.slot_matrix:
    #    print ((' '.join([ str(x) for x in row])).replace('1','X').replace('0', '.'))

    for row in D.module_matrix:
        print((' '.join([str(x) for x in row])).replace(
            '-1', 'O').replace('0', '.').replace('1', 'X'))

    covered_area = sum([slot.getActiveArea() for slot in D.slots_flat])
    available_slots = sum([sum(row) for row in D.slot_matrix])
    filled_slots = sum([sum([x for x in row if x == 1])
                       for row in D.module_matrix])

    print("Number of available slots:", available_slots)
    print("Number of used slots (= number of modules):", filled_slots)
    print("The maximum fill factor is:", round(covered_area/D.area, 3))

    print("Testing if a particle at 10,10 intersects any of the sensors (it shouldn't):",
          D.intersect(10, 10))
    print("Testing if a particle at 10,500 intersects any of the sensors:",
          D.intersect(10, 500))
