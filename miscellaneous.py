

class three_vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.r     = np.sqrt(x**2+y**2)
        self.theta = np.arctan2(self.r, z)
        self.eta   = -np.log(np.tan(self.theta/2))
        self.phi   = np.arctan2(y, x)
        
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

def get_sign(n1):

    return n1/(np.sqrt(n1*n1))

def fill(layers):
    global disk_new
    for disk, side in layers:
        disk_new[disk][side].sort(key=lambda x:x[1], reverse=True)

        y_s = {}

        for i in disk_new[disk][side]:
            if i[1] in y_s:
                y_s[i[1]].append(i[0])
            else:
                y_s[i[1]] = [i[0]]
            
            y_s[i[1]].sort()


        new_sensors = []

        for y in y_s:
            x_s = y_s[y]
            for i in range(len(x_s)-1):
                if get_sign(x_s[i]) == get_sign(x_s[i+1]):
                    if x_s[i+1]-x_s[i] - 43.6 > 1:
                        n_sensors = int((x_s[i+1]-x_s[i]-43.6)/43.6)
                        s = 43.6
                        for j in range(n_sensors):
                            new_sensors.append((x_s[i]+s,y))
                            s += 43.6
                

        disk_new[disk][side] += new_sensors

print('hello')