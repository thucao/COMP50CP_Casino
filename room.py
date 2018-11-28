import threading

class Room:
    def __init__(self, game_fun):
        self.roomBusy = False
        
        self.roomLock = threading.Lock()
        self.roomAvailable = threading.Condition(self.roomLock)

        self.roomReadyLock = threading.Lock()
        self.roomReady = threading.Condition(self.roomReadyLock)

        self.room = []
        self.max = 5

        self.game_fun = game_fun

    def addToRoom(self, user):
        with self.roomLock:
            while self.roomBusy:
                self.roomAvailable.wait()
            self.room.append(user)
            with self.roomReadyLock:
                if len(self.room) >= 2:
                    self.roomReady.notify()

    def waitForMinPlayers(self):
        with self.roomLock and self.roomReadyLock:
            while len(self.room) < 2:
                self.roomReady.wait()
            self.roomBusy = True
            return self.game_fun(self.room)

    def doneWithRoom(self):
        with self.roomLock:
            self.roomBusy = False
            self.roomAvailable.notify()

    def roomBusy(self):
        return self.roomBusy

    def contains(self, user):
        with self.roomLock:
            if user in self.room:
                return True
            else:
                return False
    def size(self):
        with self.roomLock:
            return len(self.room)