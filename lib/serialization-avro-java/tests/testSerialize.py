import jpype
import struct

classpath = "/home/pivarski/matsu-project/Libraries/Serialization with Avro/geoPictureSerializer.jar"
jvmpath = jpype.getDefaultJVMPath()
# jvmpath = "/usr/lib/jvm/java-6-openjdk/jre/lib/amd64/server/libjvm.so"

jpype.startJVM(jvmpath, "-Djava.class.path=%s" % classpath)
GeoPictureSerializer = jpype.JClass("org.occ.matsu.GeoPictureSerializer")

geoPictureSerializer = GeoPictureSerializer()

geoPictureSerializer.loadSerialized(open("/home/pivarski/NOBACKUP/matsu_serialized/GobiDesert01.serialized").read())

print geoPictureSerializer.image("B016", "B023", "B029", 0., 0., True)

# picture = geoPictureSerializer.image(700, 0, 1000, 300, "B016", "(B023*B029)", "B029")

# print geoPictureSerializer.spectrum(700, 0, 1000, 300, False)

# print geoPictureSerializer.scatter(700, 0, 1000, 300, "2*B016", "B029")

# file = open("test.png", "wb")
# for i in picture:
#     file.write(struct.pack("b", i))

jpype.shutdownJVM()
