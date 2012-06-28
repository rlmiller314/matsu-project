from cassius import *

spectrum1 = []
spectrum2 = []
spectrum3 = []
spectrum4 = []
spectrum5 = []

getdata = False
for line in open("carbon_dioxide.jdx").xreadlines():
    if line.find("##XYDATA") != -1:
        getdata = True
    elif line.find("##END") != -1:
        getdata = False
    elif getdata:
        values = line.rstrip().split()
        x = 1e7/float(values[0])
        try:
            spectrum1.append((x, float(values[1])))
            spectrum2.append((x, float(values[2])))
            spectrum3.append((x, float(values[3])))
            spectrum4.append((x, float(values[4])))
            spectrum5.append((x, float(values[5])))
        except IndexError:
            pass

view(Scatter(spectrum1, sig=("x", "y"), marker=None, connector="unsorted", xmin=400, xmax=3400))


   
def wavelength(self, bandNumber):
    if bandNumber < 70.5:
        return (bandNumber - 10.) * 10.213 + 446.
    else:
        return (bandNumber - 79.) * 10.110 + 930.






    
