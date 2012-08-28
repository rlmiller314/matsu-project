import jpype

classpath = "matsuAccumuloInterface.jar"
jpype.startJVM("/usr/lib/jvm/java-6-sun/jre/lib/amd64/server/libjvm.so", "-Djava.class.path=%s" % classpath)
AccumuloInterface = jpype.JClass("org.occ.matsu.AccumuloInterface")

AccumuloInterface.connectForReading("accumulo", "192.168.18.101:2181", "root", "password", "MatsuLevel2LngLat")

try:
    lnglats = AccumuloInterface.lnglat_read("T10-01560-01480")  # 4749578852
except jpype.JavaException, exception:
    raise RuntimeError(str(exception) + "\n" + exception.stacktrace())

for lnglat in lnglats:
    print lnglat.tileName, lnglat.timeStamp, lnglat.identifier, lnglat.longitude, lnglat.latitude, lnglat.metadata

jpype.shutdownJVM()
