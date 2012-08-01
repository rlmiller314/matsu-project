import jpype

classpath = "matsuAccumuloInterface.jar"
jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=%s" % classpath)
AccumuloInterface = jpype.JClass("org.occ.matsu.AccumuloInterface")

AccumuloInterface.connectForWriting("accumulo", "192.168.18.101:2181", "root", "password", "MatsuLevel2Tiles")

AccumuloInterface.write("T10-01561-01485-RGB", "{}", open("/tmp/map-reduce/T10-01561-01485.png").read())

AccumuloInterface.finishedWriting()

jpype.shutdownJVM()
