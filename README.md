# D-MRTAI: Dynamic Multi-Robot Task Assignment with Implements

A sophisticated optimization system for dynamic multi-robot task allocation considering tool compatibility, battery constraints, and real-time events.

## Overview

**D-MRTAI** (Dynamic Multi-Robot Task Assignment with Implements) is an advanced optimization framework that solves the problem of assigning tasks to robot-implement pairs in dynamic environments. The system uses Mixed Integer Programming (MIP) to find optimal assignments while considering:

- **Multi-period planning horizons** with battery management
- **Dynamic events** (task/vehicle/implement appearance/disappearance)
- **Compatibility constraints** between robots, implements, and tasks
- **Energy consumption** and battery recharging strategies
- **Cost minimization** balancing distance and task penalties

## Key Features

### Core Capabilities
- **Static & Time-Extended Models**: Single-period or multi-period optimization
- **Dynamic Event Handling**: Real-time adaptation to environment changes
- **Battery Management**: Automatic recharging and energy tracking
- **Real-time Visualization**: Animated simulation of vehicle movements
- **Batch Experiments**: Support for JSON-based experiment configurations
- **ROS Integration**: Optional integration with Robot Operating System

### Optimization Models
- **Static Model**: Single-period task assignment (StaticModelSMC.py)
- **Time-Extended Model**: Multi-period planning with battery dynamics (TimeExtendModelSMC.py)
- **Event-Driven Re-optimization**: Automatic replanning when events occur

## Architecture

```
D-MRTAI/
├── Main.py                    # GUI entry point and experiment manager
├── Algorithm/
│   └── DoMRTAI.py            # Core optimization algorithm
├── Models/
│   ├── StaticModelSMC.py     # Single-period MIP model
│   └── TimeExtendModelSMC.py # Multi-period MIP model
├── Data/
│   ├── Data.py               # Position and compatibility data management
│   └── Cost.py               # Cost calculation functions
├── Events/
│   ├── Events.py             # Dynamic event definitions
│   └── EventLogger.py        # Event tracking system
├── Processing/
│   └── PostProcessing.py     # State updates and metrics calculation
├── View/
│   ├── Movement.py           # Animated visualization
│   └── Result.py             # Real-time results display
├── Tools/
│   └── Defactorise.py        # Solution variable extraction utilities
└── ROS/
    └── RealCost.py           # ROS navigation integration
```

## Quick Start

### Prerequisites

- Python 3.8+
- Gurobi Optimizer (with valid license)
- Linux/Unix environment (for GTK3Agg backend)

## Configuration Parameters

### Problem Instance Parameters
- `num_implements`: Number of available implements
- `num_tasks`: Number of tasks to complete
- `num_vehicles`: Number of available vehicles/robots
- `seed`: Random seed for reproducible data generation
- `full`: Boolean for full compatibility (true) or partial (false)

### Temporal Parameters
- `time_horizon`: Maximum simulation time
- `num_periods`: Number of planning periods (1 for static, >1 for time-extended)

### Dynamic Event Probabilities
- `probabilityTA`: Task appearance probability
- `probabilityTD`: Task disappearance probability
- `probabilityVA`: Vehicle appearance probability
- `probabilityVD`: Vehicle disappearance probability
- `probabilityIA`: Implement appearance probability
- `probabilityID`: Implement disappearance probability

## Example Configuration

```json
{
  "num_implements": 5,
  "num_tasks": 10,
  "num_vehicles": 3,
  "seed": 42,
  "full": true,
  "time_horizon": 1000,
  "num_periods": 2,
  "probabilityTA": 0.1,
  "probabilityTD": 0.05,
  "probabilityVA": 0.1,
  "probabilityVD": 0.05,
  "probabilityIA": 0.1,
  "probabilityID": 0.05
}
```

## Optimization Models

### Static Model (Single Period)

**Decision Variables:**
- `x[i,k,v]`: Binary, 1 if implement i with vehicle v performs task k
- `y[k]`: Binary, 1 if task k is assigned
- `z[v]`: Binary, 1 if vehicle v returns to depot

**Objective Function:**
```
Minimize: α × (normalized_costs) + β × (penalties_for_unassigned_tasks)
```

**Key Constraints:**
- Each implement assigned to at most one task
- Each task assigned to exactly one implement-vehicle pair
- Each vehicle either assigned or returns to depot
- Battery capacity constraints

### Time-Extended Model (Multi-Period)

**Additional Decision Variables:**
- `x[i,k,v,t]`: Task assignment in period t
- `T[v,t]`: Continuous battery level of vehicle v at period t
- `o[k,t]`: Binary, 1 if task k is still outstanding in period t

**Additional Features:**
- Battery dynamics across periods
- Automatic recharging at depot
- Task availability propagation
- Multi-period cost accumulation

## Output and Results

### CSV Results (Results/Results.csv)
Contains comprehensive metrics for each experiment:
- Execution times (total and optimization)
- Objective function values
- Costs breakdown (distance, penalty, static)
- Task completion statistics
- Distance traveled per vehicle
- Performance metrics

### Real-time Visualization
- **Movement Animation**: Shows vehicles executing assignments
  - Orange arrows: Vehicle → Implement
  - Green arrows: Vehicle+Implement → Task
  - Red arrows: Vehicle → Depot
- **Results Window**: Live metrics display updated every 500ms

## Visualization Features

### Movement Animation
- Real-time vehicle trajectory simulation
- Three-phase movement visualization
- Pause/resume functionality
- Dynamic event triggering during execution

### Entity Representation
- **Implements**: Black triangles (▲)
- **Tasks**: Blue squares (available) / Red squares (completed)
  - Size proportional to task area
- **Vehicles**: Red hexagons with labels
- **Depot**: Green square at origin (0,0)

## Advanced Features

### ROS Integration
Connect to real robots for path validation:
```python
from ROS import RealCost as rc
Error, UpdatedCost = rc.RealCost(Assignments, Implements, Tasks, Vehicles, CostMatrix, client)
```

### Custom Compatibility Matrices
Define specific implement-task and implement-vehicle compatibilities:
- Place CSV files in `Data/Compatibility/Compatibility-(I,K,V)/`
- Files: `IK.csv`, `IV.csv`, `VK.csv`

### Position Data Management
- Automatic generation with random seeds
- Cached in `Data/Positions/Positions-(I,K,V)-seed/`
- Contains: `Implements.csv`, `Tasks.csv`, `Vehicles.csv`

## Experiment Generation

Use the experiment generator to create batch configurations:

```python
from Experiments import Experiments_Generator
# Generate systematic experiments with parameter sweeps
```

## Troubleshooting

### Common Issues

**Gurobi License Error**
```
Error: No Gurobi license found
Solution: Install license with `grbgetkey YOUR-KEY`
```

**GTK Backend Error**
```
Error: Cannot initialize GTK3Agg
Solution: Install GTK3: sudo apt-get install python3-gi-cairo
```

**Infeasible Model**
```
The model is infeasible. Stopping optimization.
Solution: Check compatibility matrices and battery capacities
```

## Publications

If you use this software in your research, please cite:

```bibtex
@article{d-mrtai-2024,
  title={D-MRTAI: Dynamic Multi-Robot Task Assignment with Implements},
  author={Jorge},
  year={2024}
}
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is licensed under the terms specified in the LICENSE file.

## Author

**Jorge**

## Acknowledgments

- Universidad Rey Juan Carlos (URJC)
- Università degli Studi di Roma "Tor Vergata"

---

## Quick Reference

### Key Files
- `Main.py`: Start here
- `Algorithm/DoMRTAI.py`: Main algorithm
- `Models/StaticModelSMC.py`: Single-period model
- `Models/TimeExtendModelSMC.py`: Multi-period model

### Key Functions
- `DoMRTAI.init()`: Run optimization algorithm
- `Data.PositionData()`: Load/generate entity positions
- `Cost.DynamicCalculation()`: Calculate distance-based costs
- `PostProcessing.TrueObj()`: Calculate actual objective value

### Data Structures
- **Implements**: `[x, y, efficiency, state]`
- **Tasks**: `[x, y, area, penalty, state]`
- **Vehicles**: `[x, y, efficiency, T_max, T_current, state]`

---

**Last Updated**: 2024
**Version**: 1.0
