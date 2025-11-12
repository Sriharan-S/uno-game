# UNO Game Project

## Overview
This project is a Python-based implementation of the popular card game UNO. It consists of a server-client architecture where players can connect to a server to play the game. The project is designed to simulate the gameplay of UNO, including card distribution, turn management, and game rules enforcement.

## Features
- Multiplayer support via server-client communication.
- Implementation of core UNO rules.
- Turn-based gameplay.
- Card drawing and playing mechanics.
- Simple and modular code structure.

## Project Structure
The project contains the following files:

- `server.py`: Handles the server-side logic, including managing player connections, broadcasting game state, and enforcing rules.
- `client.py`: Handles the client-side logic, including player interactions and communication with the server.
- `game.py`: Contains the core game logic, such as managing the deck, players, and game rules.
- `__pycache__/`: Contains compiled Python files for optimization (auto-generated).

## How to Run

### Prerequisites
- Python 3.11 or higher installed on your system.

### Steps
1. Clone the repository or download the project files.
2. Open a terminal and navigate to the project directory.
3. Start the server by running:
   ```cmd
   python server.py
   ```
4. Start one or more clients by running the following in separate terminals:
   ```cmd
   python client.py
   ```
5. Follow the on-screen instructions to play the game.

## How to Play
1. Connect to the server using the client.
2. Wait for all players to join.
3. Play your turn by selecting a card to play or drawing a card if no valid moves are available.
4. Follow the rules of UNO to win the game by being the first to play all your cards.

## Rules Implemented
- Players must match the color or number of the top card on the discard pile.
- Special cards (e.g., Skip, Reverse, Draw Two, Wild) are implemented.
- Players must say "UNO" when they have one card left.
- The first player to play all their cards wins.

## Future Improvements
- Add a graphical user interface (GUI) for better user experience.
- Implement advanced rules and variations of UNO.
- Add support for AI players.
- Improve error handling and robustness.

## Contributing
Contributions are welcome! Feel free to fork the repository and submit pull requests.

## License
This project is open-source and available under the MIT License.

## Acknowledgments
- Inspired by the classic UNO card game.
- Developed as a learning project for Python and networking concepts.
