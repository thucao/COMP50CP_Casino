import socket
import sys
import threading
import json
from Queue import *
import blackjack_server

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
INIT_MONEY = 1000

def init_game_connection(ip_addr, port, game_fun):
    game = threading.Thread(target=game_fun, args=(ip_addr, port))
    game.start()
    conn, addr = SERVER.accept()
    print("connected to game server")
    return [game, conn, addr]

def init_game_servers(games, ip_addr, port, game_queue):
    game_list = {
        'blackjack' : blackjack_server.connect_to_casino
        # roulette server
        # baccarat server
    }

    for game, fun in game_list.iteritems():
        games[game] = init_game_connection(ip_addr, port, fun)
        game_listen = threading.Thread(target=listen_for_game,
                      args=(games, game, games[game][1], game_queue))
        game_listen.start()
        print(game)

def init_user_loop(games, users, usr_queue):
    # adds user -> address to users dict
    while True:
        name = ''
        game = ''
        conn, addr = SERVER.accept()

        print("got user")
        conn.send("What is your name?")
        while True:
            try:
                name = conn.recv(2048)[0:-1]
                if name not in users:
                    users[name] = [conn, INIT_MONEY]
                    print(name + " connected")
                    break
                else:
                    conn.send("Sorry, name is taken, try again.")
            except:
                continue

        # add game to dict
        conn.send("Which game do you want to join? Baccarat, Blackjack, " \
                  + "or Roulette?")
        while True:
            try:
                game = conn.recv(2048).lower()[0:-1]
                if game == 'baccarat':
                    conn.send("Joined Baccarat!")
                    break
                elif game == 'blackjack':
                    conn.send("Joined Blackjack!")
                    break
                elif game == 'roulette':
                    conn.send("Joined Roulette!")
                    break
                else:
                    conn.send("Invalid option. Please choose between " \
                              + "Baccarat, Blackjack, or Roulette.")
            except:
                continue

        msg_from_user_to_game(games, game, name, users[name][1], 0, 'join')
        users[name].append(game)
        user_listen = threading.Thread(target=listen_for_user, 
                                       args=(users, name, conn, usr_queue))
        user_listen.start()

def msg_from_user_to_game(games, game, user, money, betsize, msg):
    proper_msg = set(['join', 'quit']) # add more msg later
    if msg not in proper_msg:
        return False

    game_conn = games[game][1]
    game_conn.send(json.dumps([msg, user, money, betsize]))
    return True

def listen_for_game(games, name, conn, game_queue):
    actions = {
        'users' : print_users
        # add more actions later
    }
    while True:
        try:
            message = json.loads(conn.recv(2048))
            if message:
                action = message[0]
                actions[action](message[1:])
        except:
            continue

def listen_for_user(users, name, conn, usr_queue):
    while True:
        try:
            message = conn.recv(2048)
            if message:
                usr_queue.put((name, message))
            else:
                users.pop(name)
        except:
            continue

def print_users(users):
    print(users)

def broadcast(message, users, sender):
    for user, data in users.iteritems():
        if user != sender:
            try:
                data[0].send(sender + ": " + message)
            except:
                data[0].close()
                users.pop(user)

def server_loop(ip_addr, port):
    games = {}
    users = {}
    game_queue = Queue()
    usr_queue = Queue()

    game_loop = threading.Thread(target=init_game_servers,
                                 args=(games, ip_addr, port, game_queue))
    game_loop.start()
    user_loop = threading.Thread(target=init_user_loop, 
                                 args=(games, users, usr_queue))
    user_loop.start()
    while True:
        if usr_queue.empty():
            continue
        else:
            sender, msg = usr_queue.get()
            broadcast(msg, users, sender)

def main(args):
    if len(args) != 3:
        sys.exit("Usage: script, IP address, port number")

    ip_addr = str(args[1])
    port    = int(args[2])

    SERVER.bind((ip_addr, port))
    SERVER.listen(100)

    server_loop(ip_addr, port)

if __name__ == '__main__':
    main(sys.argv)