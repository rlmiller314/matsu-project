import jpype
import struct

classpath = "matsuAccumuloInterface.jar"
jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=%s" % classpath)
AccumuloInterface = jpype.JClass("org.occ.matsu.accumulo.AccumuloInterface")

AccumuloInterface.connectForReading("accumulo", "192.168.18.101:2181", "root", "password", "MatsuLevel2Tiles")

picture = AccumuloInterface.readL2png("T10-01561-01485-RGB")

file = open("test.png", "wb")
for i in picture:
    file.write(struct.pack("b", i))

jpype.shutdownJVM()
