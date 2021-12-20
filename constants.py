POSITIONS_NAMES = ["Top", "Jungle", "Mid", "Bottom", "Support" ]
DATABASE_PRIO_NAMES = ["prioTop", "prioJungle", "prioMid", "prioBot", "prioSupport" ]
TYPE_JSON = 'application/json'

HTTP_OK = 200

def VALID_INDEX(index):
    return index == 0 or index == 1
