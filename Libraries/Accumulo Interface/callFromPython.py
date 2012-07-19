import jpype

classpath = "matsuAccumuloInterface.jar"

jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=%s" % classpath)

WriteToAccumulo = jpype.JClass("org.occ.matsu.accumulo.WriteToAccumulo")

WriteToAccumulo.write()
WriteToAccumulo.read()

t = WriteToAccumulo()
t.sayhello()

jpype.shutdownJVM()
