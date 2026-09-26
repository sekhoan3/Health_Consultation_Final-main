import sqlite3
import os

DB = os.path.join("backend", "health_platform.db")
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
GRAY   = "\033[90m"
WHITE  = "\033[97m"

def separator(char="=", width=80):
    print(GRAY + char * width + RESET)

def print_table(table_name):
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    if not rows:
        print(GRAY + "  (empty)" + RESET)
        return

    cols = [d[0] for d in cur.description]
    col_widths = [max(len(c), max((len(str(r[c])) for r in rows), default=0)) for c in cols]

    header = "  " + "  ".join(c.upper().ljust(col_widths[i]) for i, c in enumerate(cols))
    print(CYAN + header + RESET)
    print(GRAY + "  " + "  ".join("-" * w for w in col_widths) + RESET)

    for row in rows:
        line = "  " + "  ".join(str(row[c]).ljust(col_widths[i]) for i, c in enumerate(cols))
        print(WHITE + line + RESET)

    print(GREEN + f"\n  {len(rows)} row(s)" + RESET)

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [t[0] for t in cur.fetchall()]

separator()
print(BOLD + YELLOW + f"  DATABASE: {os.path.abspath(DB)}" + RESET)
print(YELLOW + f"  Tables: {', '.join(tables)}" + RESET)
separator()

for table in tables:
    print()
    separator("-", 80)
    print(BOLD + CYAN + f"  TABLE: {table.upper()}" + RESET)
    separator("-", 80)
    print_table(table)

separator()
conn.close()
