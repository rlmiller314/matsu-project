import jpype
import struct

classpath = "/home/pivarski/matsu-project/Libraries/Serialization with Avro/geoPictureSerializer.jar"
jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=%s" % classpath)
GeoPictureSerializer = jpype.JClass("org.occ.matsu.GeoPictureSerializer")

geoPictureSerializer = GeoPictureSerializer()

geoPictureSerializer.loadSerialized(open("/home/pivarski/NOBACKUP/matsu_serialized/GobiDesert01.serialized").read())

print geoPictureSerializer.bandNames()

picture = geoPictureSerializer.image("B016", "B023", "B029")

# file = open("test.png", "wb")
# for i in picture:
#     file.write(struct.pack("b", i))

jpype.shutdownJVM()
