#include <iostream>
#include <stdint.h>
#include <vector>
#include <regex>
#include <fstream>
#include <cassert>
#include <string>
#include <map>
#include <algorithm>

#define USE_TRANSPOSITION_TABLES 0

using namespace std;

struct Resources {
    int ore{};
    int clay{};
    int obsidian{};
    int geodes{};

    Resources operator+(const Resources& other) const {
        return Resources {
            .ore = this->ore + other.ore,
            .clay = this->clay + other.clay,
            .obsidian = this->obsidian + other.obsidian,
            .geodes = this->geodes + other.geodes,
        };
    }

    Resources operator-(const Resources& other) const {
        return Resources {
            .ore = this->ore - other.ore,
            .clay = this->clay - other.clay,
            .obsidian = this->obsidian - other.obsidian,
            .geodes = this->geodes - other.geodes,
        };
    }

    void operator+=(const Resources& other) {
        ore += other.ore;
        clay += other.clay;
        obsidian += other.obsidian;
        geodes += other.geodes;
    }

    void operator-=(const Resources& other) {
        ore -= other.ore;
        clay -= other.clay;
        obsidian -= other.obsidian;
        geodes -= other.geodes;
    }

    bool can_afford(const Resources& other) const {
        return ore >= other.ore
            && clay >= other.clay
            && obsidian >= other.obsidian
            && geodes >= other.geodes;
    }
};

struct Blueprint {
    int id {};
    Resources ore_robot_cost;
    Resources clay_robot_cost;
    Resources obsidian_robot_cost;
    Resources geode_robot_cost;

    Blueprint(int id, Resources ore_robot_cost, Resources clay_robot_cost, Resources obsidian_robot_cost, Resources geode_robot_cost)
        : id(id)
        , ore_robot_cost(ore_robot_cost)
        , clay_robot_cost(clay_robot_cost)
        , obsidian_robot_cost(obsidian_robot_cost)
        , geode_robot_cost(geode_robot_cost)
    {
        max_costs = Resources {
            .ore = max({ore_robot_cost.ore, clay_robot_cost.ore, obsidian_robot_cost.ore, geode_robot_cost.ore}),
            .clay = max({ore_robot_cost.clay, clay_robot_cost.clay, obsidian_robot_cost.clay, geode_robot_cost.clay}),
            .obsidian = max({ore_robot_cost.obsidian, clay_robot_cost.obsidian, obsidian_robot_cost.obsidian, geode_robot_cost.obsidian}),
            .geodes = max({ore_robot_cost.geodes, clay_robot_cost.geodes, obsidian_robot_cost.geodes, geode_robot_cost.geodes}),
        };
    }

    const Resources& get_max_costs() const {
        return max_costs;
    }

private:
    Resources max_costs;
};

struct GameState {
    int minutes_left {};
    Resources resources;
    Resources robots;

    bool operator<(const GameState& other) const {
        if(minutes_left != other.minutes_left) {
            return minutes_left < other.minutes_left;
        }
        if(resources.geodes != other.resources.geodes) {
            return resources.geodes < other.resources.geodes;
        }
        if(resources.obsidian != other.resources.obsidian) {
            return resources.obsidian < other.resources.obsidian;
        }
        if(resources.clay != other.resources.clay) {
            return resources.clay < other.resources.clay;
        }
        if(resources.ore != other.resources.ore) {
            return resources.ore < other.resources.ore;
        }
        if(robots.geodes != other.robots.geodes) {
            return robots.geodes < other.robots.geodes;
        }
        if(robots.obsidian != other.robots.obsidian) {
            return robots.obsidian < other.robots.obsidian;
        }
        if(robots.clay != other.robots.clay) {
            return robots.clay < other.robots.clay;
        }
        if(robots.ore != other.robots.ore) {
            return robots.ore < other.robots.ore;
        }
        return false;
    }

    void tick() {
        assert(minutes_left > 0);
        resources += robots;
        minutes_left -= 1;
    }
};

struct SearchState {
    int max_so_far{};
#if USE_TRANSPOSITION_TABLES
    map<GameState, int> transposition_table;
#endif
};

int max_geodes(const Blueprint& bp, const GameState& gameState, SearchState& searchState) {
    if(gameState.minutes_left == 0) {
        return gameState.resources.geodes;
    }

#if USE_TRANSPOSITION_TABLES
    auto transpositionEntry = searchState.transposition_table.find(gameState);
    if(transpositionEntry != searchState.transposition_table.end()) {
        return transpositionEntry->second;
    }
#endif

    GameState next_state;

    int max_so_far = 0;

    if(gameState.robots.ore < bp.get_max_costs().ore && gameState.robots.ore > 0) {
        next_state = gameState;
        while(!next_state.resources.can_afford(bp.ore_robot_cost) && next_state.minutes_left > 0) {
            next_state.tick();
        }
        if(next_state.minutes_left > 0) {
            next_state.tick();
            next_state.resources -= bp.ore_robot_cost;
            next_state.robots.ore += 1;
        }
        max_so_far = max(max_so_far, max_geodes(bp, next_state, searchState));
    }

    if(gameState.robots.clay < bp.get_max_costs().clay && gameState.robots.ore > 0) {
        next_state = gameState;
        while(!next_state.resources.can_afford(bp.clay_robot_cost) && next_state.minutes_left > 0) {
            next_state.tick();
        }
        if(next_state.minutes_left > 0) {
            next_state.tick();
            next_state.resources -= bp.clay_robot_cost;
            next_state.robots.clay += 1;
        }
        max_so_far = max(max_so_far, max_geodes(bp, next_state, searchState));
    }

    if(gameState.robots.obsidian < bp.get_max_costs().obsidian && gameState.robots.ore > 0 && gameState.robots.clay > 0) {
        next_state = gameState;
        while(!next_state.resources.can_afford(bp.obsidian_robot_cost) && next_state.minutes_left > 0) {
            next_state.tick();
        }
        if(next_state.minutes_left > 0) {
            next_state.tick();
            next_state.resources -= bp.obsidian_robot_cost;
            next_state.robots.obsidian += 1;
        }
        max_so_far = max(max_so_far, max_geodes(bp, next_state, searchState));
    }

    if(gameState.robots.ore > 0 && gameState.robots.obsidian > 0) {
        next_state = gameState;
        while(!next_state.resources.can_afford(bp.geode_robot_cost) && next_state.minutes_left > 0) {
            next_state.tick();
        }
        if(next_state.minutes_left > 0) {
            next_state.tick();
            next_state.resources -= bp.geode_robot_cost;
            next_state.robots.geodes += 1;
        }
        max_so_far = max(max_so_far, max_geodes(bp, next_state, searchState));
    }

#if USE_TRANSPOSITION_TABLES
    searchState.transposition_table[gameState] = max_so_far;
#endif
    searchState.max_so_far = max(searchState.max_so_far, max_so_far);

    return max_so_far;
}

vector<Blueprint> read_file(const char* filename) {
    vector<Blueprint> blueprints;
    regex valve_regex(R"~~(Blueprint (\d+): Each ore robot costs (\d+) ore. Each clay robot costs (\d+) ore. Each obsidian robot costs (\d+) ore and (\d+) clay. Each geode robot costs (\d+) ore and (\d+) obsidian.)~~");
    ifstream inf;
    inf.open(filename);
    assert(inf.is_open());
    string line;

    smatch matches;
    while(getline(inf, line)) {
        if(!regex_match(line, matches, valve_regex)) {
            cout << "Bad blueprint: \"" << line << "\"" << endl;
            continue;
        }

        Blueprint blueprint(
            stoi(matches[1]),
            Resources{
                .ore = stoi(matches[2])
            },
            Resources{
                .ore = stoi(matches[3])
            },
            Resources{
                .ore = stoi(matches[4]),
                .clay = stoi(matches[5])
            },
            Resources {
                .ore = stoi(matches[6]),
                .obsidian = stoi(matches[7])
            }
        );

        blueprints.push_back(blueprint);
    }

    return blueprints;
}

int main(int argc, char* argv[]) {
    assert(argc >= 2);
    auto blueprints = read_file(argv[1]);

    GameState start_state {
        .minutes_left = 24,
        .resources = Resources{},
        .robots = Resources {
            .ore = 1
        }
    };

    int quality_level_sum = 0;

    for(auto& bp : blueprints) {
        SearchState search_state{};
        int max_geodes_for_bp = max_geodes(bp, start_state, search_state);
        cout << "Blueprint " << bp.id <<": " << max_geodes_for_bp << " geodes" << endl;

        int quality_level = bp.id * max_geodes_for_bp;
        quality_level_sum += quality_level;
    }

    cout << endl;
    cout << "Part 1: " << quality_level_sum << endl;

    // PART 2
    cout << endl << endl;
    start_state.minutes_left = 32;
    int blueprint_count = min(static_cast<size_t>(3), blueprints.size());
    int geode_product = 1;
    for(int i = 0; i < blueprint_count; ++i) {
        const Blueprint& bp = blueprints[i];
        SearchState search_state{};
        int max_geodes_for_bp = max_geodes(bp, start_state, search_state);
        cout << "Blueprint " << bp.id <<": " << max_geodes_for_bp << " geodes" << endl;

        geode_product *= max_geodes_for_bp;
    }

    cout << "Part 2: " << geode_product << endl;

    return 0;
}
