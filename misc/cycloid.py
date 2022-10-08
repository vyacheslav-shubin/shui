import math


class Epicycloid:
    Rb = 0
    Rs = 0
    F = 0
    def __init__(self, Rb, Rs, F, mode=False):
        self.Rb = Rb
        self.Rs = Rs
        self.F = F
        self.mode = mode
        if mode:
            self.__location = self.location_epi
            self.R = self.Rb - self.Rs + self.F
        else:
            self.__location = self.location_hypo
            self.R = self.Rb + self.Rs + self.F


    def location_hypo(self, fi):
        x = (self.Rb+self.Rs)*math.cos(fi) - self.F*math.cos((self.Rb+self.Rs)/self.Rs*fi)
        y = (self.Rb+self.Rs)*math.sin(fi) - self.F*math.sin((self.Rb+self.Rs)/self.Rs*fi)
        return x, y

    def location_epi(self, fi):
        x = (self.Rb-self.Rs)*math.cos(fi) + self.F*math.cos((self.Rb-self.Rs)/self.Rs*fi)
        y = (self.Rb-self.Rs)*math.sin(fi) - self.F*math.sin((self.Rb-self.Rs)/self.Rs*fi)
        return x, y

    def generate_layer(self, pr):
        lcm = math.lcm(self.Rb, self.Rs)
        ncycles = int(lcm/self.Rb)
        fx, fy = self.__location(0)
        px, py = fx, fy
        pr.move(px, py)
        steps_per_cycle = 720
        delta=(math.pi*2)/steps_per_cycle
        fi = 0
        for i in range(0, ncycles * steps_per_cycle):
            fi = fi + delta
            cx, cy = self.__location(fi)
            pr.line(px, py, cx, cy)
            px, py = cx, cy
        pr.line(px, py, fx, fy)


class GcodeGenerator:

    def __init__(self, centerX, centerY, layer_height, R=None):
        self.ed = (1.75*1.75*math.pi/4) / (0.4 * layer_height)
        self.centerX = centerX
        self.centerY = centerY
        self.scale = 1
        self.R = R
        pass

    def out(self, val):
        print(val)

    def move(self, x, y):
        self.out("G1X{0}Y{1}".format(x*self.scale + self.centerX, y*self.scale + self.centerY))

    def line(self, sx, sy, dx, dy):
        sx = sx*self.scale + self.centerX
        dx = dx*self.scale + self.centerX
        sy = sy*self.scale + self.centerY
        dy = dy*self.scale + self.centerY
        ed = math.sqrt((dx-sx)*(dx-sx)+(dy-sy)*(dy-sy))/self.ed
        self.out("G1X{0}Y{1}E{2}".format(dx, dy, ed))

    def generate(self, cycloid, rows):
        if self.R is not None:
            self.scale = self.R/cycloid.R
        self.out("G28")
        self.out("G1X20Y20Z10")
        self.out("M140S60")
        self.out("M104S150")
        self.out("M190S60")
        self.out("M109S200")
        self.out("G29")
        self.out("G1X20Y20Z10")

        self.out("G92 E0")
        self.out("G1 Z2.0 F3000")
        self.out("G1 X10.1 Y20 Z0.28 F5000.0")
        self.out("G1 X10.1 Y200.0 Z0.28 F1500.0 E15")
        self.out("G1 X10.4 Y200.0 Z0.28 F5000.0")
        self.out("G1 X10.4 Y20 Z0.28 F1500.0 E30")
        self.out("G92 E0")

        self.out("G90")
        self.out("M83")


        for i in range(1, rows+1):
            self.out("G1Z{0}".format(0.2 * i))
            cycloid.generate_layer(self)

        self.out("G1X20Y20")


class PngGen:

    def __init__(self, cycloid):
        from PIL import Image, ImageDraw
        self.scale = 500/cycloid.R
        self.cycloid = cycloid
        self.img = Image.new("RGB", (1000, 1000))
        self.draw = ImageDraw.Draw(self.img)

    def move(self, x, y):
        pass

    def line(self, sx, sy, dx, dy):

        shape = [(sx*self.scale + 500, sy*self.scale + 500), (dx*self.scale + 500, dy*self.scale + 500)]
        self.draw.line(shape, fill ="red", width = 0)
        pass

    def generate(self):
        self.cycloid.generate_layer(self)
        pass



#cycloid = Epicycloid(25, 13, 50, False)
cycloid = Epicycloid(25, 17, 6, True)
png_gen = PngGen(cycloid)
png_gen.generate()
png_gen.img.save("preview.png", "PNG")
png_gen.img.show()
gcode = GcodeGenerator(110, 110, 0.2, R=50)
gcode.generate(cycloid, 10)

#cycloid = Epicycloid(10, 10, 150, 150, 0.2)
#cycloid.generate(150, 150, 0.2)