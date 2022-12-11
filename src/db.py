import psycopg2
from config.database_config import config

class db:
    def __init__(self):
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        self.conn = psycopg2.connect(**params)

    def update(self, cmd):
        cur = self.conn.cursor()
        cur.execute(cmd)
        self.conn.commit()
        cur.close()

    def read(self, cmd):
        cur = self.conn.cursor()
        cur.execute(cmd)
        print("Row cout: ", cur.rowcount)
        row = cur.fetchone()
        res = []
        if (row is not None):res.append(row)
        while row is not None:
            # print(row)
            row = cur.fetchone()
            res.append(row)
        return  res
