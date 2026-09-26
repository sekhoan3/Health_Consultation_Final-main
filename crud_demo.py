import sqlite3

conn = sqlite3.connect("backend/health_platform.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=" * 55)
print("  CRUD DEMO on health_platform.db")
print("=" * 55)

# ── CREATE ────────────────────────────────────────────────
print("\n[CREATE] Inserting a new test user...")
cur.execute(
    "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, ?)",
    ("Test User", "test@demo.com", "testhash123", "patient"),
)
new_id = cur.lastrowid
conn.commit()
print(f"  Inserted -> id={new_id}, name='Test User', role='patient'")

# ── READ ──────────────────────────────────────────────────
print("\n[READ] All users in database:")
cur.execute("SELECT id, full_name, email, role FROM users ORDER BY id")
for row in cur.fetchall():
    r = dict(row)
    print(f"  id={r['id']}  {r['full_name']:<22} {r['email']:<28} role={r['role']}")

# ── UPDATE ────────────────────────────────────────────────
print(f"\n[UPDATE] Changing id={new_id} role from 'patient' to 'doctor'...")
cur.execute("UPDATE users SET role = ? WHERE id = ?", ("doctor", new_id))
conn.commit()
cur.execute("SELECT id, full_name, role FROM users WHERE id = ?", (new_id,))
updated = dict(cur.fetchone())
print(f"  Updated -> id={updated['id']}, name='{updated['full_name']}', role='{updated['role']}'")

# ── DELETE ────────────────────────────────────────────────
print(f"\n[DELETE] Removing test user id={new_id}...")
cur.execute("DELETE FROM users WHERE id = ?", (new_id,))
conn.commit()
cur.execute("SELECT COUNT(*) FROM users WHERE id = ?", (new_id,))
remaining = cur.fetchone()[0]
print(f"  Deleted. Rows remaining with id={new_id}: {remaining}")

# ── Final state ───────────────────────────────────────────
print("\n[READ] Final users table:")
cur.execute("SELECT id, full_name, role FROM users ORDER BY id")
for row in cur.fetchall():
    r = dict(row)
    print(f"  id={r['id']}  {r['full_name']:<22} role={r['role']}")

print("\n" + "=" * 55)
conn.close()
