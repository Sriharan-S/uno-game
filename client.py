# Save this as client.py
import socket
import threading
import time

# --- Global State ---
my_turn = False
waiting_for = None
current_top_card = "Waiting..."
my_hand_str = "Waiting for hand..."
my_valid_moves = []


def display_game_state():
    global current_top_card, my_hand_str, my_valid_moves, my_turn, waiting_for

    # 1. Print the Top Card Box
    print("\n" + "=" * 25)
    # .strip() to remove any extra newlines
    print(f"   TOP CARD: {current_top_card.strip()}")
    print("=" * 25 + "\n")

    # 2. Print the Hand, highlighting valid moves
    print("--- Your Hand ---")

    hand_lines = my_hand_str.strip().split('\n')

    # Iterate through the actual card lines
    # The hand string is now just "--- Your Hand ---\n...cards...\n-----------------"
    # So we skip the first line (header) and last line (footer)
    for line in hand_lines[1:-1]:
        if not line.strip():
            continue

        try:
            card_index = int(line.strip().split('.')[0])

            if card_index in my_valid_moves:
                print(f"{line}   <-- VALID")
            else:
                print(line)
        except:
            print(line)

    print("-----------------\n")

    # 3. Print the suggestion
    if not my_valid_moves:
        print(">>> You have no valid cards. You must type 'draw'.")
    else:
        print(">>> Type 'play N' (e.g., 'play 3') or 'draw'.")

    # 4. Set the turn flags
    my_turn = True
    waiting_for = None


# --- NEW: Message processing function ---
def process_message(message):
    global my_turn, waiting_for
    global current_top_card, my_hand_str, my_valid_moves

    # .strip() is crucial to remove the \n
    msg = message.strip()
    if not msg:
        return  # Ignore empty lines

    try:
        if msg.startswith("TOP_CARD:"):
            current_top_card = msg.split(':', 1)[1]

        elif msg.startswith("--- Your Hand ---"):
            # The hand message is multi-line, but send_hand() in server
            # sends it as one block with one \n at the end.
            my_hand_str = msg

        elif msg.startswith("VALID_MOVES:"):
            moves_str = msg.split(':', 1)[1]
            if moves_str:
                my_valid_moves = [int(x) for x in moves_str.split(',')]
            else:
                my_valid_moves = []

        elif msg == "NO_VALID_MOVES":
            my_valid_moves = []

        elif msg == "YOUR_TURN":
            display_game_state()

        elif msg == "CHOOSE_COLOR":
            my_turn = True
            waiting_for = "COLOR"
            print("\nWhat color? (RED, GREEN, BLUE, YELLOW)")

        elif msg == "DRAW_CHOICE":
            my_turn = True
            waiting_for = "DRAW"
            print("\nPlay the card you drew? (p)lay or (k)eep?")

        # --- Regular Broadcast Messages ---
        else:
            if "Top card is now:" in msg:
                pass  # We handle this with TOP_CARD:
            else:
                print(msg)  # Print all other messages

    except Exception as e:
        print(f"--- Error processing message: {msg} ---")
        print(f"--- {e} ---")


# --- UPDATED: Network Receiver ---
def receive_messages(client_socket):
    data_buffer = ""
    while True:
        try:
            # Receive data and add to buffer
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print("Disconnected from server.")
                break

            data_buffer += data

            # Process all complete messages (lines) in the buffer
            while '\n' in data_buffer:
                # Split off the first complete message
                message, data_buffer = data_buffer.split('\n', 1)
                process_message(message)

        except:
            print("An error occurred. Disconnecting.")
            client_socket.close()
            break


# --- Main Client Logic (UPDATED) ---
def main():
    global my_turn, waiting_for

    host_ip = input("Enter the Host's IP Address: ")
    PORT = 5555

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host_ip, PORT))
        print("Connected to server! Waiting for game to start...")
    except Exception as e:
        print(f"Failed to connect to {host_ip}:{PORT}. Error: {e}")
        return

    # Start the receiver thread
    receiver = threading.Thread(target=receive_messages, args=(client,), daemon=True)
    receiver.start()

    while True:
        try:
            if my_turn:
                command = input()
                if not command:
                    continue

                # We must add \n to our sends to match the server protocol
                command += '\n'

                if waiting_for == "COLOR":
                    client.send(command.encode('utf-8'))
                    my_turn = False

                elif waiting_for == "DRAW":
                    client.send(command.encode('utf-8'))
                    my_turn = False

                elif command.lower().startswith('play ') or command.lower() == 'draw\n':
                    client.send(command.encode('utf-8'))
                    my_turn = False

                else:
                    print("Invalid command. (e.g., 'play 3' or 'draw')")

            else:
                time.sleep(0.1)

        except (EOFError, KeyboardInterrupt):
            print("\nDisconnecting...")
            client.close()
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            client.close()
            break


if __name__ == "__main__":
    main()