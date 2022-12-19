#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <cassert>
#include <regex>
#include <fstream>
#include <memory>
#include <stdint.h>

using namespace std;


struct Valve {
    string label{};
    int flow_rate{};
    vector<string> tunnels{};
};

template<class T>
class SolutionBlock {
public:
    SolutionBlock(size_t num_valves, size_t num_possible_open_valves)
        : num_valves(num_valves)
        , num_possible_open_valves(num_possible_open_valves)
    {
        size_t blocksize = 26 * num_valves * num_valves * num_possible_open_valves;
        solutions = new T[blocksize];
        assert(solutions != nullptr);
        memset(solutions, 0xFF, blocksize * sizeof(T));
    }

    ~SolutionBlock() {
        delete[] solutions;
    }

    class SolutionPtr {
    public:
        SolutionPtr(T* solution)
            : solution(solution)
        {}

        T& operator*() {
            return *solution;
        }

        void maybe_update(T value) {
            assert(value != 0xffff);
            if(value > *solution) {
                *solution = value;
            }
        }
        T* solution{nullptr};
    };

    SolutionPtr index(size_t minute, size_t uvalve_idx, size_t evalve_idx, size_t open_valves_idx) {
        T* ptr = solutions + (minute * num_valves * num_valves * num_possible_open_valves)
        + (uvalve_idx * num_valves * num_possible_open_valves)
        + (evalve_idx * num_possible_open_valves)
        + open_valves_idx;
        return SolutionPtr(ptr);
    }

private:
    size_t num_valves{};
    size_t num_possible_open_valves{};
    T* solutions{nullptr};
};

typedef shared_ptr<Valve> vptr;

vector<string> split_tunnels(const string& tunnels) {
    vector<string> out;
    unsigned long start = 0;
    unsigned long end = 0;
    do {
        end = tunnels.find(", ", start);
        out.push_back(tunnels.substr(start, end - start));
        start = end + 2;
    } while(end != string::npos);
    return out;
}

vector<vptr> read_valves(const char* infile) {
    vector<vptr> valves;
    std::regex valve_regex(R"~~(Valve (\S+) has flow rate=(\d+); tunnels? leads? to valves? (.*))~~");
    ifstream inf;
    inf.open(infile);
    assert(inf.is_open());
    string line;

    smatch matches;
    while(getline(inf, line)) {
        if(!regex_match(line, matches, valve_regex)) {
            cout << "Bad valve: \"" << line << "\"" << endl;
            continue;
        }

        auto valve = make_shared<Valve>();
        valve->label = matches[1];
        valve->flow_rate = stoi(matches[2]);
        valve->tunnels = move(split_tunnels(matches[3]));

        valves.push_back(valve);
    }

    return valves;
}

void print_valves(const vector<vptr>& valves) {
    for(auto& valve : valves) {
        cout << "Valve " << valve->label << " has flow rate=" << valve->flow_rate << "; tunnels lead to valves ";
        for(unsigned long i = 0; i < valve->tunnels.size(); ++i) {
            cout << valve->tunnels[i];
            if(i < valve->tunnels.size()-1) {
                cout << ", ";
            }
        }
        cout << endl;
    }
}

vector<vector<vptr>> powerset(const vector<vptr>& valves) {
    vector<vector<vptr>> retval;
    if(valves.size() == 0) {
        retval.push_back(vector<vptr>());
        return retval;
    }

    vector<vptr> smaller_valves = vector<vptr>(valves.begin(), valves.end()-1);
    vector<vector<vptr>> smaller_powerset = powerset(smaller_valves);

    vptr last_item = valves.back();
    for(auto& set: smaller_powerset) {
        vector<vptr> setcpy = set;
        setcpy.push_back(last_item);
        retval.push_back(set);
        retval.push_back(setcpy);
    }

    return retval;
}

inline uint16_t valve_to_bit(map<string, size_t>& valve_map, const vptr& valve) {
    size_t pos = valve_map[valve->label];
    uint16_t out = 1 << pos;
    assert(out != 0);
    return out;
}

int main(int argc, char* argv[]) {
    assert(argc >= 2);
    cout << "Reading valves" << endl;
    auto valves = read_valves(argv[1]);
    map<string, size_t> valve_map;
    for(size_t i = 0; i < valves.size(); ++i) {
        valve_map.insert(pair<string,size_t>(valves[i]->label, i));
    }

    cout << "Identifying significant valves" << endl;
    vector<vptr> significant_valves;
    for(auto& valve : valves) {
        if(valve->flow_rate > 0) {
            significant_valves.push_back(valve);
        }
    }

    cout << "Collating significant valves" << endl;
    map<string, size_t> significant_valve_map;
    for(size_t i = 0; i < significant_valves.size(); ++i) {
        significant_valve_map.insert(pair<string, size_t>(significant_valves[i]->label, i));
    }

    cout << "Calculating possible open valve combinations" << endl;
    auto possible_open_valves = powerset(significant_valves);
    vector<uint16_t> possible_open_valves_ints;
    for(auto& valve_set : possible_open_valves) {
        uint16_t valve_set_int = 0;
        for(auto& valve : valve_set) {
            uint16_t valve_bit = valve_to_bit(significant_valve_map, valve);
            assert((valve_set_int & valve_bit) == 0);
            valve_set_int |= valve_bit;
        }
        possible_open_valves_ints.push_back(valve_set_int);
    }
    cout << "Collating possible open valve combinations" << endl;
    map<uint16_t, size_t> possible_open_valves_idx_map;
    for(size_t i = 0; i < possible_open_valves_ints.size(); ++i) {
        possible_open_valves_idx_map.insert(pair<uint16_t, size_t>(possible_open_valves_ints[i], i));
    }

#if 0
    cout << "All valves:" << endl;
    print_valves(valves);
    cout << endl;

    cout << "Significant valves:" << endl;
    print_valves(significant_valves);
    cout << endl;

    cout << "Possible open valve combos:" << endl;
    for(auto& valve_set : possible_open_valves) {
        cout << "[";
        for(unsigned long i = 0; i < valve_set.size(); ++i) {
            cout << valve_set[i]->label;
            if(i < valve_set.size() - 1) {
                cout << ",";
            }
        }
        cout << "]" << endl;
    }
#endif

    // solutions[sol_idx][uvalve][evalve][open_valves] -> score
    SolutionBlock<uint16_t> solutions(valves.size(), possible_open_valves.size());

    for(size_t minute = 0; minute < 26; ++minute) {
        for(size_t uvalve_idx = 0; uvalve_idx < valves.size(); ++uvalve_idx) {
            cout << "Progress: " << ((minute * valves.size()) + uvalve_idx) << "/" << (26 * valves.size()) << endl;
            auto& uvalve = valves[uvalve_idx];
            uint16_t uvalve_bit = (uvalve->flow_rate > 0) ? valve_to_bit(significant_valve_map, uvalve) : 0;
            for(size_t evalve_idx = 0; evalve_idx < valves.size(); ++evalve_idx) {
                auto& evalve = valves[evalve_idx];
                uint16_t evalve_bit = (evalve->flow_rate > 0) ? valve_to_bit(significant_valve_map, evalve) : 0;
                for(size_t open_valves_idx = 0; open_valves_idx < possible_open_valves_ints.size(); ++open_valves_idx) {
                    uint16_t open_valves = possible_open_valves_ints[open_valves_idx];
                    auto solution = solutions.index(minute, uvalve_idx, evalve_idx, open_valves_idx);
                    assert(*solution == 0xffff);
                    *solution = 0;
                    if(minute > 0) {
                        // 1. you move, elephant moves
                        for(auto& ut : uvalve->tunnels) {
                            for(auto& et : evalve->tunnels) {
                                solution.maybe_update(*solutions.index(minute-1, valve_map[ut], valve_map[et], open_valves_idx));
                            }
                        }

                        // 2. you move, elephant opens
                        if(evalve->flow_rate > 0 && (evalve_bit & open_valves) == 0) {
                            for(auto& ut : uvalve->tunnels) {
                                uint16_t new_open_valves = open_valves | evalve_bit;
                                size_t new_open_valves_idx = possible_open_valves_idx_map[new_open_valves];
                                solution.maybe_update(*solutions.index(minute-1, valve_map[ut], evalve_idx, new_open_valves_idx) + (evalve->flow_rate * minute));
                            }
                        }

                        // 3. you open, elephant moves
                        if(uvalve->flow_rate > 0 && (uvalve_bit & open_valves) == 0) {
                            for(auto& et : evalve->tunnels) {
                                uint16_t new_open_valves = open_valves | uvalve_bit;
                                size_t new_open_valves_idx = possible_open_valves_idx_map[new_open_valves];
                                solution.maybe_update(*solutions.index(minute-1, uvalve_idx, valve_map[et], new_open_valves_idx) + (uvalve->flow_rate * minute));
                            }
                        }

                        // 4. you open, elephant opens
                        if(uvalve_idx != evalve_idx && uvalve->flow_rate > 0 && evalve->flow_rate > 0 && ((uvalve_bit | evalve_bit) & open_valves) == 0) {
                            uint16_t new_open_valves = open_valves | uvalve_bit | evalve_bit;
                            size_t new_open_valves_idx = possible_open_valves_idx_map[new_open_valves];
                            solution.maybe_update(*solutions.index(minute-1, uvalve_idx, evalve_idx, new_open_valves_idx) + (uvalve->flow_rate * minute) + (evalve->flow_rate * minute));
                        }
                    }
                }
            }
        }
    }

    uint16_t solution = *solutions.index(25, valve_map["AA"], valve_map["AA"], 0);

    cout << "Part 2: " << solution << endl;

    return 0;
}
