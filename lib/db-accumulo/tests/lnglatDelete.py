import jpype

classpath = "matsuAccumuloInterface.jar"
jpype.startJVM("/usr/lib/jvm/java-6-sun/jre/lib/amd64/server/libjvm.so", "-Djava.class.path=%s" % classpath)
AccumuloInterface = jpype.JClass("org.occ.matsu.AccumuloInterface")

AccumuloInterface.connectForReading("accumulo", "192.168.18.101:2181", "root", "password", "MatsuLevel2LngLat")
AccumuloInterface.connectForWriting("accumulo", "192.168.18.101:2181", "root", "password", "MatsuLevel2LngLat")

AccumuloInterface.delete("T10-01561-01481-0000000000", "T10-01561-01481-9999999999")

AccumuloInterface.finishedWriting()

jpype.shutdownJVM()
