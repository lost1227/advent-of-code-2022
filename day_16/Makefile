CXX = g++
CXXARGS = -Wall -Wextra -Werror --std=c++2a -march=native -pipe
#CXXARGS += -g -Og -g3 -fsanitize=address -fsanitize=undefined
CXXARGS += -O3

EXENAME = solution

all: $(EXENAME)

$(EXENAME): solution.cpp
	$(CXX) $(CXXARGS) -o $(EXENAME) solution.cpp

clean:
	rm $(EXENAME)
