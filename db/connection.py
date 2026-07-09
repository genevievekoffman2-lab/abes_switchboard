import firebird.driver as fdb
from firebird.driver import tpb, Isolation, TraAccessMode
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    con = fdb.connect(
        database=f"{os.getenv('DB_HOST')}:{os.getenv('DB_PATH')}",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    # set default txn to read only (any attempt in code to write to DB will throw error)
    read_only_tpb = tpb(Isolation.SNAPSHOT, access_mode=TraAccessMode.READ)
    con.begin(tpb=read_only_tpb)
    return con