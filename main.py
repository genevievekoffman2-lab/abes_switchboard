import sys
from db.connection import get_connection

from ui.dashboard import run_dashboard
def start_app():
    con = get_connection()
    print("connection successful")
    run_dashboard(con)

    try:
        con.close()
    except Exception:
        pass
    # con.close() # we have a close event in dashboard so not needed here

start_app()