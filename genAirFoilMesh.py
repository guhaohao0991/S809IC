#!/usr/bin/env python
"""
This script reads a coarse airfoil profile, refine the profile using spline function,
and outputs it as surfaceMesh.xyz. 
The coarse airfoil profile comes from NASA's experimental reports available at https://www.nrel.gov/docs/legosti/old/6918.pdf
Then it generate a 3D volume mesh with nSpan(number of grids in z direction) layers using pyHyp, available at https://github.com/mdolab/pyhyp
Note: the airfoil data should be seperated into PS and SS surfaces, they should start from the
LE and ends at TE. We use blunt TE so truncate the PS and SS data at about 99.8% of the chord.
"""

from pyhyp import pyHyp
import numpy
from pyspline import *

########## user input ################
# 2D
prefix = "./profiles/"
airfoilProfilePS = prefix + "lower.dat"
airfoilProfileSS = prefix + "upper.dat"
ZSpan = 0.01  # width in the z direction
nSpan = 2  # how many points in z
# PS parameters
dX1PS = 0.002  # first dx from the LE
Alpha1PS = 1.1  # clustering from the LE
dX2PS = 0.002  # first dx from the TE
Alpha2PS = 1.1  # clustering from the TE
dXMaxPS = 0.01  # max dx for PS
# SS parameters
dX1SS = 0.002  # first dx from the LE
Alpha1SS = 1.1  # clustering from the LE
dX2SS = 0.2e-3  # first dx from the TE
Alpha2SS = 1.1  # clustering from the TE
dXMaxSS = 0.005  # max dx for SS
# TE parameters
NpTE = 9  # number of points for blunt TE
# 3D
NpExtrude = 85  # how many points to extrude for the 3D volume mesh in y
yWall = 1e-5  # first layer mesh length
marchDist = 20.0  # march distance for extruding
########## user input ################

# read profiles
fPS = open(airfoilProfilePS, "r")
linesPS = fPS.readlines()
fPS.close()
xPS = []
yPS = []
zPS = []
for line in linesPS:
    cols = line.split()
    xPS.append(float(cols[0]))
    yPS.append(float(cols[1]))

for i in range(len(xPS)):
    zPS.append(0.0)

fSS = open(airfoilProfileSS, "r")
linesSS = fSS.readlines()
fSS.close()
xSS = []
ySS = []
zSS = []
for line in linesSS:
    cols = line.split()
    xSS.append(float(cols[0]))
    ySS.append(float(cols[1]))
for i in range(len(xSS)):
    zSS.append(0.0)

# ------------PS
# first compute how many stretching points do we need for both ends
tmp = dX1PS
for i in range(1000):
    if tmp > dXMaxPS:
        nStretch1PS = i
        break
    else:
        tmp = tmp * Alpha1PS
# print (nStretch1PS)
tmp = dX2PS
for i in range(1000):
    if tmp > dXMaxPS:
        nStretch2PS = i
        break
    else:
        tmp = tmp * Alpha2PS
# print (nStretch2PS)

# now compute how much length does these two stretching end and the constant portion have
xLPSConst = xPS[-1]
xLPS1 = 0
xLPS2 = 0
for i in range(nStretch1PS):
    xLPS1 += dX1PS * (Alpha1PS ** i)
    xLPSConst -= dX1PS * (Alpha1PS ** i)
for i in range(nStretch2PS):
    xLPS2 += dX2PS * (Alpha2PS ** i)
    xLPSConst -= dX2PS * (Alpha2PS ** i)
# print xLPS1,xLPS2,xLPSConst
# update dXMax, we just want to make sure these three portion add up
nXConstPS = int(xLPSConst / dXMaxPS)
dXMaxPS = xLPSConst / nXConstPS
# print(dXMaxPS)

# now we can add these three portions together
xInterpPS = [0]
tmp = dX1PS
for i in range(nStretch1PS):
    xInterpPS.append(xInterpPS[-1] + tmp)
    tmp = tmp * Alpha1PS
for i in range(nXConstPS):
    xInterpPS.append(xInterpPS[-1] + dXMaxPS)
tmp = dX2PS * (Alpha2PS ** (nStretch2PS - 1))
for i in range(nStretch2PS):
    xInterpPS.append(xInterpPS[-1] + tmp)
    tmp /= Alpha2PS
# print xInterpPS
# Finally, we interpolate the refined stretch stuff
c1PS = Curve(x=xPS, y=yPS, z=zPS, k=3)
XPS = c1PS(xInterpPS)
c2PS = Curve(X=XPS, k=3)
x1PS = c2PS.X[:, 0]
y1PS = c2PS.X[:, 1]


# ------------SS
# first compute how many stretching points do we need for both ends
tmp = dX1SS
for i in range(1000):
    if tmp > dXMaxSS:
        nStretch1SS = i
        break
    else:
        tmp = tmp * Alpha1SS
# print (nStretch1SS)
tmp = dX2SS
for i in range(1000):
    if tmp > dXMaxSS:
        nStretch2SS = i
        break
    else:
        tmp = tmp * Alpha2SS
# print (nStretch2SS)

# now compute how much length does these two stretching end and the constant portion have
xLSSConst = xSS[-1]
xLSS1 = 0
xLSS2 = 0
for i in range(nStretch1SS):
    xLSS1 += dX1SS * (Alpha1SS ** i)
    xLSSConst -= dX1SS * (Alpha1SS ** i)
for i in range(nStretch2SS):
    xLSS2 += dX2SS * (Alpha2SS ** i)
    xLSSConst -= dX2SS * (Alpha2SS ** i)
# print xLSS1,xLSS2,xLSSConst
# update dXMax, we just want to make sure these three portion add up
nXConstSS = int(xLSSConst / dXMaxSS)
dXMaxSS = xLSSConst / nXConstSS
# print(dXMaxSS)

# now we can add these three portions together
xInterpSS = [0]
tmp = dX1SS
for i in range(nStretch1SS):
    xInterpSS.append(xInterpSS[-1] + tmp)
    tmp = tmp * Alpha1SS
for i in range(nXConstSS):
    xInterpSS.append(xInterpSS[-1] + dXMaxSS)
tmp = dX2SS * (Alpha2SS ** (nStretch2SS - 1))
for i in range(nStretch2SS):
    xInterpSS.append(xInterpSS[-1] + tmp)
    tmp /= Alpha2SS
# print xInterpSS
# Finally, we interpolate the refined stretch stuff
c1SS = Curve(x=xSS, y=ySS, z=zSS, k=3)
XSS = c1SS(xInterpSS)
c2SS = Curve(X=XSS, k=3)
x1SS = c2SS.X[:, 0]
y1SS = c2SS.X[:, 1]

# Since the TE is open we need to close it. Close it multiple linear segments.
delta_y = numpy.linspace(y1PS[-1], y1SS[-1], NpTE, "d")
delta_x = numpy.linspace(x1PS[-1], x1SS[-1], NpTE, "d")
delta_y = delta_y[1:]
delta_x = delta_x[1:]

x1SS_Flip = x1SS[::-1]  # reverse the array #numpy.flip(x1SS,axis=0)
xAll = numpy.append(x1SS_Flip, x1PS[1:])
xAll = numpy.append(xAll, delta_x)

y1SS_Flip = y1SS[::-1]  # reverse the array # numpy.flip(y1SS,axis=0)
yAll = numpy.append(y1SS_Flip, y1PS[1:])
yAll = numpy.append(yAll, delta_y)


# print mesh statistics
print("nPoints for PS: ", nStretch1PS + nStretch2PS + nXConstPS)
print("nPoints for SS: ", nStretch1SS + nStretch2SS + nXConstSS)
print("nPoints for TE: ", NpTE)
print("nPoints Total: ", nStretch1PS + nStretch2PS + nXConstPS + nStretch1SS + nStretch2SS + nXConstSS + NpTE)
print(
    "Mesh cells: ",
    (nStretch1PS + nStretch2PS + nXConstPS + nStretch1SS + nStretch2SS + nXConstSS + NpTE - 1)
    * (NpExtrude - 1)
    * (nSpan - 1),
)

# plt.plot(xPS,yPS,'-k',linewidth=1)
# plt.plot(xAll,yAll,'ro',markersize=2)
# plt.plot(xSS,ySS,'-k',linewidth=1)
# plt.gca().set_aspect('equal', adjustable='box')
# plt.show()
# plt.savefig('figure.png',bbox_inches='tight')   # save the figure to file
# plt.close()    # close the figure


# Write the plot3d input file:
f = open("surfaceMesh.xyz", "w")
f.write("1\n")
f.write("%d %d %d\n" % (len(xAll), nSpan, 1))
for iDim in range(3):
    for z in numpy.linspace(0.0, ZSpan, nSpan):
        for i in range(len(xAll)):
            if iDim == 0:
                f.write("%20.16f\n" % xAll[i])
            elif iDim == 1:
                f.write("%20.16f\n" % yAll[i])
            else:
                f.write("%20.16f\n" % z)
f.close()

options = {
    # ---------------------------
    #        Input Parameters
    # ---------------------------
    "inputFile": "surfaceMesh.xyz",
    "unattachedEdgesAreSymmetry": False,
    "outerFaceBC": "farfield",
    "autoConnect": True,
    "BC": {1: {"jLow": "zSymm", "jHigh": "zSymm"}},
    "families": "wall",
    # ---------------------------
    #        Grid Parameters
    # ---------------------------
    "N": NpExtrude,
    "s0": yWall,
    "marchDist": marchDist,
    # ---------------------------
    #   Pseudo Grid Parameters
    # ---------------------------
    "ps0": -1.0,
    "pGridRatio": -1.0,
    "cMax": 1.0,
    # ---------------------------
    #   Smoothing parameters
    # ---------------------------
    "epsE": 2.0,
    "epsI": 4.0,
    "theta": 2.0,
    "volCoef": 0.20,
    "volBlend": 0.0005,
    "volSmoothIter": 20,
}


hyp = pyHyp(options=options)
hyp.run()
hyp.writePlot3D("volumeMesh.xyz")
