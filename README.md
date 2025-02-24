# Tetris AI

This project implements a Tetris AI using a generic model for selection in genetic algorithms. The AI plays Tetris by evaluating board states and selecting the best possible moves based on various metrics such as height, gaps, and bumpiness.

## Features
- Simulated Tetris environment (`TetrisEnv`) with AI-controlled gameplay.
- Uses a heuristic function and a generic model for selection in genetic algorithms to optimize performance.
- Visual representation using `Visor.py` (Tkinter-based UI for board visualization).
- Configurable parameters for AI evolution and gameplay tuning.

## Installation
### Requirements
Ensure you have Python installed along with the following dependencies:

```sh
pip install numpy pygame
```

## Usage
1. Run the AI Tetris script:
   ```sh
   python TetrisSIE.py
   ```
2. Modify AI parameters in `TetrisSIE.py` to adjust scoring and evolution behavior.
3. View the board visualization (if enabled) to monitor AI performance.

## Generic Model for Selection
The AI utilizes a genetic algorithm with a generic model for selection, which ensures the best candidates are chosen based on fitness scores. The process includes:
- **Fitness Evaluation:** Each AI candidate is scored based on board heuristics.
- **Selection Mechanism:** Candidates are selected using probabilistic methods, favoring higher-scoring individuals while maintaining diversity.
- **Crossover & Mutation:** Selected individuals undergo crossover and mutation to create the next generation.

This approach allows the AI to evolve and improve its gameplay over multiple generations, refining its decision-making process dynamically.

## Configuration
- Genetic Algorithm Parameters:
  - `POPULATION_SIZE`: Number of AI candidates per generation.
  - `MUTATION_RATE`: Probability of mutations in AI evolution.
  - `CROSSOVER_RATE`: Rate of crossover between selected parents.
- Scoring Heuristics:
  - Max height, bumpiness, well depths, and gaps are considered.

## Files Overview
- `TetrisSIE.py`: Main AI and game logic.
- `Visor.py`: Visualization module using Tkinter.

## Future Improvements
- Improve scoring functions with deep reinforcement learning.
- Optimize genetic algorithm parameters dynamically.
- Add more visualization features.

## Credits
Developed by [Your Name]. Contributions and feedback are welcome!

## License
MIT License.

