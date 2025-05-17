CXX = g++
CXXFLAGS = -O3 -march=native -fPIC -fopenmp -mavx2 -mfma
LDFLAGS = -shared
AS = nasm
ASFLAGS = -f elf64

all: libfastops.so libquantum.so libparallel.so libnumerical.so libassembly.so

libfastops.so: fastops.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $<

libquantum.so: quantum_sim.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $<

libparallel.so: parallel_ops.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $<

libnumerical.so: numerical_ops.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $<

assembly_ops.o: assembly_ops.asm
	$(AS) $(ASFLAGS) -o $@ $<

libassembly.so: assembly_ops.o
	$(CXX) $(LDFLAGS) -o $@ $<

clean:
	rm -f *.so *.o 