import jpype

classpath = "matsuAccumuloInterface.jar"

jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=%s" % classpath)

WriteToAccumulo = jpype.JClass("org.occ.matsu.accumulo.WriteToAccumulo")

WriteToAccumulo.write()
WriteToAccumulo.read()

t = WriteToAccumulo()
t.sayhello()

WriteToAccumulo.testInput(jpype.JArray(jpype.JByte, 1)("".join(chr(i) for i in xrange(256))))
print ">" + str([i for i in WriteToAccumulo.testOutput()]) + "<"

jpype.shutdownJVM()
