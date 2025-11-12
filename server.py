# Save this as server.py
import socket
import threading
import time
from game import Deck, Hand, Card, single_card_check

# --- Server Configuration ---
HOST = '0.0.0.0'
PORT = 5555
MIN_PLAYERS = 2
MAX_PLAYERS = 10

# --- Global Game State ---
clients = []
player_hands = []
deck = Deck()
top_card = None
turn = 0
game_running = False
reverse_direction = False
game_start_lock = threading.Lock()
game_has_started = False


"""
Broadcasts a message to all connected clients.

Args:
    message (str): The message to broadcast.
"""
# --- Broadcasting Functions (UPDATED) ---
def broadcast(message):
    message += '\n'  # Add newline
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            clients.remove(client)


"""
Sends a message to a specific client.

Args:
    client (socket): The client socket to send the message to.
    message (str): The message to send.
"""
def send_to_client(client, message):
    message += '\n'  # Add newline
    try:
        client.send(message.encode('utf-8'))
    except:
        clients.remove(client)


"""
Sends the current hand of a player to their client.

Args:
    player_index (int): The index of the player whose hand is to be sent.
"""
def send_hand(player_index):
    hand = player_hands[player_index]
    hand_str = "\n--- Your Hand ---\n" + hand.get_hand_str() + "-----------------\n"
    send_to_client(clients[player_index], hand_str.strip())


"""
Notifies a player that it is their turn and provides valid moves.

Args:
    player_index (int): The index of the player to notify.
"""
# --- NEW: Helper function to start a player's turn (UPDATED) ---
def notify_player_of_turn(player_index):
    global top_card

    active_client = clients[player_index]
    active_hand = player_hands[player_index]

    broadcast(f"Top card is now: {top_card}")
    broadcast(f"It is Player {player_index + 1}'s turn.")

    send_to_client(active_client, f"TOP_CARD:{top_card}")
    send_hand(player_index)

    valid_indices = []
    for i, card in enumerate(active_hand.cards):
        if single_card_check(top_card, card):
            valid_indices.append(i + 1)

    if valid_indices:
        send_to_client(active_client, f"VALID_MOVES:{','.join(map(str, valid_indices))}")
    else:
        send_to_client(active_client, "NO_VALID_MOVES")

    send_to_client(active_client, "YOUR_TURN")


"""
Starts the game by shuffling the deck, dealing cards, and setting the top card.
"""
# --- Game Logic Functions ---
def start_game():
    global game_running, deck, top_card, turn, player_hands
    deck.shuffle()
    player_hands = []

    for i in range(len(clients)):
        hand = Hand()
        for _ in range(7):
            hand.add_card(deck.deal())
        player_hands.append(hand)

    top_card = deck.deal()
    while top_card.cardtype != 'number':
        deck.deck.append(top_card)
        deck.shuffle()
        top_card = deck.deal()

    game_running = True
    turn = 0
    broadcast(f"--- GAME STARTING! ---")
    broadcast(f"All {len(clients)} players have joined.")
    time.sleep(1)

    notify_player_of_turn(turn)


"""
Determines the next player's turn based on the current game state.
"""
def get_next_turn():
    global turn, reverse_direction
    if reverse_direction:
        turn = (turn - 1) % len(clients)
    else:
        turn = (turn + 1) % len(clients)


"""
Handles a player playing a card, including game logic for special cards.

Args:
    player_index (int): The index of the player playing the card.
    card_index (int): The index of the card being played in the player's hand.
"""
def play_card(player_index, card_index):
    global top_card, turn, reverse_direction, game_running

    hand = player_hands[player_index]

    if card_index < 1 or card_index > hand.no_of_cards():
        send_to_client(clients[player_index], "Invalid index. Try again.")
        send_to_client(clients[player_index], "YOUR_TURN")
        return

    played_card = hand.get_card(card_index)

    if not single_card_check(top_card, played_card):
        send_to_client(clients[player_index], f"Cannot play {played_card}. It doesn't match {top_card}.")
        send_to_client(clients[player_index], "YOUR_TURN")
        return

    top_card = hand.remove_card(card_index)
    broadcast(f"Player {player_index + 1} played: {top_card}")

    if hand.no_of_cards() == 0:
        broadcast(f"--- GAME OVER ---")
        broadcast(f"PLAYER {player_index + 1} WINS!")
        game_running = False
        return

    if hand.no_of_cards() == 1:
        broadcast(f"Player {player_index + 1} yells UNO!")

    if played_card.cardtype == 'number':
        get_next_turn()

    elif played_card.rank == 'Skip':
        skip_target_index = (turn + 1) % len(clients)
        if reverse_direction:
            skip_target_index = (turn - 1) % len(clients)
        broadcast(f"Player {skip_target_index + 1} is skipped!")
        get_next_turn()
        get_next_turn()

    elif played_card.rank == 'Reverse':
        reverse_direction = not reverse_direction
        broadcast("Direction REVERSED!")
        get_next_turn()

    elif played_card.rank == 'Draw2':
        draw_target_index = (turn + 1) % len(clients)
        if reverse_direction:
            draw_target_index = (turn - 1) % len(clients)

        broadcast(f"Player {draw_target_index + 1} draws 2 cards!")
        player_hands[draw_target_index].add_card(deck.deal())
        player_hands[draw_target_index].add_card(deck.deal())
        send_hand(draw_target_index)

        get_next_turn()
        get_next_turn()

    elif played_card.cardtype == 'action_nocolor':
        send_to_client(clients[player_index], "CHOOSE_COLOR")
        return

    if game_running:
        notify_player_of_turn(turn)


"""
Handles a player's choice of color after playing a Wild or Draw4 card.

Args:
    player_index (int): The index of the player choosing the color.
    color_choice (str): The chosen color.
"""
def handle_color_choice(player_index, color_choice):
    global top_card, turn, game_running

    if color_choice not in ('RED', 'GREEN', 'BLUE', 'YELLOW'):
        send_to_client(clients[player_index], "Invalid color. (RED, GREEN, BLUE, YELLOW)")
        send_to_client(clients[player_index], "CHOOSE_COLOR")
        return

    top_card.color = color_choice
    broadcast(f"Player {player_index + 1} chose {color_choice}.")

    if top_card.rank == 'Draw4':
        draw_target_index = (turn + 1) % len(clients)
        if reverse_direction:
            draw_target_index = (turn - 1) % len(clients)

        broadcast(f"Player {draw_target_index + 1} draws 4 cards!")
        for _ in range(4):
            player_hands[draw_target_index].add_card(deck.deal())
        send_hand(draw_target_index)

        get_next_turn()
        get_next_turn()
    else:
        get_next_turn()

    if game_running:
        notify_player_of_turn(turn)


"""
Handles a player drawing a card from the deck.

Args:
    player_index (int): The index of the player drawing the card.
"""
def player_draws(player_index):
    global turn, game_running
    card = deck.deal()
    player_hands[player_index].add_card(card)
    broadcast(f"Player {player_index + 1} draws a card.")

    send_to_client(clients[player_index], f"You drew: {card}")

    if single_card_check(top_card, card):
        send_to_client(clients[player_index], "You can play this card! (p)lay or (k)eep?")
        send_hand(player_index)
        send_to_client(clients[player_index], f"VALID_MOVES:{player_hands[player_index].no_of_cards()}")
        send_to_client(clients[player_index], "DRAW_CHOICE")
    else:
        send_to_client(clients[player_index], "You cannot play this card.")
        get_next_turn()

        if game_running:
            notify_player_of_turn(turn)


"""
Handles a player's decision after drawing a card (play or keep).

Args:
    player_index (int): The index of the player making the decision.
    choice (str): The player's choice ('p' to play, 'k' to keep).
"""
def handle_draw_choice(player_index, choice):
    global top_card, turn, reverse_direction, game_running
    hand = player_hands[player_index]
    drawn_card = hand.get_card(hand.no_of_cards())

    if choice == 'p':
        top_card = hand.remove_card(hand.no_of_cards())
        broadcast(f"Player {player_index + 1} played the drawn card: {top_card}")

        if hand.no_of_cards() == 0:
            broadcast(f"--- GAME OVER ---")
            broadcast(f"PLAYER {player_index + 1} WINS!")
            game_running = False
            return
        if hand.no_of_cards() == 1:
            broadcast(f"Player {player_index + 1} yells UNO!")

        if drawn_card.rank == 'Skip':
            skip_target_index = (turn + 1) % len(clients)
            if reverse_direction:
                skip_target_index = (turn - 1) % len(clients)
            broadcast(f"Player {skip_target_index + 1} is skipped!")
            get_next_turn()
            get_next_turn()
        elif drawn_card.rank == 'Reverse':
            reverse_direction = not reverse_direction
            broadcast("Direction REVERSED!")
            get_next_turn()
        elif drawn_card.rank == 'Draw2':
            draw_target_index = (turn + 1) % len(clients)
            if reverse_direction:
                draw_target_index = (turn - 1) % len(clients)
            broadcast(f"Player {draw_target_index + 1} draws 2 cards!")
            player_hands[draw_target_index].add_card(deck.deal())
            player_hands[draw_target_index].add_card(deck.deal())
            send_hand(draw_target_index)
            get_next_turn()
            get_next_turn()
        else:  # Number card
            get_next_turn()

    elif choice == 'k':
        broadcast(f"Player {player_index + 1} keeps the card.")
        get_next_turn()

    else:
        send_to_client(clients[player_index], "Invalid choice. (p)lay or (k)eep?")
        send_to_client(clients[player_index], "DRAW_CHOICE")
        return

    if game_running:
        notify_player_of_turn(turn)


"""
Handles communication with a single client, processing their actions.

Args:
    client (socket): The client socket to handle.
"""
# --- Main Client Handler (UPDATED) ---
def handle_client(client):
    player_index = clients.index(client)
    player_state = "PLAYING"

    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message or not game_running:
                break

            # --- UPDATED: Process all clumped messages ---
            for msg_line in message.strip().split('\n'):
                if not msg_line:
                    continue

                if player_state == "CHOOSING_COLOR":
                    handle_color_choice(player_index, msg_line.upper())
                    player_state = "PLAYING"
                    continue

                if player_state == "DRAW_CHOICE":
                    handle_draw_choice(player_index, msg_line.lower())
                    player_state = "PLAYING"
                    continue

                if clients.index(client) == turn and player_state == "PLAYING":

                    if msg_line == "CHOOSE_COLOR":
                        player_state = "CHOOSING_COLOR"
                        continue
                    if msg_line == "DRAW_CHOICE":
                        player_state = "DRAW_CHOICE"
                        continue

                    if msg_line.startswith('play '):
                        try:
                            card_index = int(msg_line.split(' ')[1])
                            play_card(player_index, card_index)
                        except:
                            send_to_client(client, "Invalid command. Use 'play N' where N is card number.")

                    elif msg_line == 'draw':
                        player_draws(player_index)

                    else:
                        send_to_client(client, "Invalid command. (e.g., 'play 3' or 'draw')")
                        send_to_client(client, "YOUR_TURN")

                elif msg_line:
                    send_to_client(client, "It's not your turn.")

        except Exception as e:
            print(f"Error with Player {player_index + 1}: {e}")
            break

    print(f"Player {player_index + 1} disconnected.")
    clients.remove(client)
    if game_running:
        broadcast(f"Player {player_index + 1} has left. The game cannot continue.")


"""
Waits for the host to start the game or for enough players to join.

Args:
    server_socket (socket): The server socket to monitor.
"""
# --- Host Start & Main Loop (UPDATED) ---
def wait_for_host_start(server_socket):
    global game_has_started

    while not game_has_started:
        if len(clients) >= MIN_PLAYERS:
            break
        time.sleep(0.5)

    if game_has_started:
        return

    try:
        input(f"\n{len(clients)} players are in. Press Enter to start the game...\n")
    except EOFError:
        print("Server shutting down.")
        return

    with game_start_lock:
        if game_has_started:
            return

        print("Host pressed Enter. Starting game...")
        game_has_started = True
        broadcast(f"The host has started the game with {len(clients)} players!")

    try:
        server_socket.close()
    except Exception as e:
        print(f"Error closing server socket: {e}")


"""
Main function to start the server and manage the game lifecycle.
"""
def main():
    global game_has_started, game_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
    except Exception as e:
        print(f"Failed to bind to port {PORT}. Is another server running? Error: {e}")
        return

    server.listen()
    print(f"--- UNO Server Started ---")
    print(f"Lobby is open on {HOST}:{PORT}")
    print(f"Waiting for at least {MIN_PLAYERS} players (max {MAX_PLAYERS})...")

    host_thread = threading.Thread(target=wait_for_host_start, args=(server,), daemon=True)
    host_thread.start()

    while not game_has_started:
        try:
            conn, addr = server.accept()

            with game_start_lock:
                if game_has_started:
                    send_to_client(conn, "Sorry, the game has already started.")
                    conn.close()
                    continue

                if len(clients) >= MAX_PLAYERS:
                    send_to_client(conn, "Sorry, the lobby is full.")
                    conn.close()
                    continue

                clients.append(conn)
                player_num = len(clients)

                print(f"Player {player_num} connected from {addr}")
                send_to_client(conn, f"Welcome, Player {player_num}!")
                broadcast(f"Player {player_num} has joined the lobby. ({len(clients)}/{MAX_PLAYERS})")

                if len(clients) == MAX_PLAYERS:
                    print("Max players reached. Starting game automatically...")
                    game_has_started = True
                    broadcast("Max players reached! Starting game automatically...")
                    server.close()

        except Exception as e:
            if game_has_started:
                print("Lobby closed. Proceeding to start game.")
            else:
                print(f"Server error: {e}")
            break

    if len(clients) < MIN_PLAYERS:
        print(f"Not enough players to start. ({len(clients)}/{MIN_PLAYERS})")
        return

    print(f"\nStarting game with {len(clients)} players.")

    for client in clients:
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

    start_game()

    try:
        while game_running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServer shutting down (Ctrl+C)...")
        broadcast("Server is shutting down.")
        game_running = False

    print("Game over. Server process finished.")


if __name__ == "__main__":
    main()