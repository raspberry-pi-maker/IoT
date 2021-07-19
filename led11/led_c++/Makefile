CC=g++

RGB_LIB_DISTRIBUTION=/usr/local/src/rpi-rgb-led-matrix
RGB_INCDIR=$(RGB_LIB_DISTRIBUTION)/include
RGB_LIBDIR=$(RGB_LIB_DISTRIBUTION)/lib
RGB_LIBRARY_NAME=rgbmatrix
RGB_LIBRARY=$(RGB_LIBDIR)/lib$(RGB_LIBRARY_NAME).a
LDFLAGS+=-L$(RGB_LIBDIR) -l$(RGB_LIBRARY_NAME) -lrt -lm -lpthread


CFLAGS=-c -Wall  -std=c++11  -O3 -g -Wextra -Wno-unused-parameter

#SOURCES=main.cpp log.cpp ini.cpp 
SOURCES=main.cpp log.cpp util.cpp
OBJECTS=$(SOURCES:.cpp=.o)
BACKUP=$(SOURCES:.cpp=.cpp-)
EXECUTABLE=net_player

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	$(CC) $(OBJECTS)  $(LDFLAGS) -o $@


%.o : %.cpp
	$(CC) -I$(RGB_INCDIR) $(CXXFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJECTS) $(OUT)  $(BACKUP)
