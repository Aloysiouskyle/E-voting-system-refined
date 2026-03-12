"""
=============================================================
  E-VOTING SYSTEM  ─  Security & Sessions Module
  Member 2: Security and Sessions
=============================================================
  Responsibilities:
    • Password hashing & masked input
    • Login / Logout (Admin & Voter)
    • Session state management
    • Voter self-registration (security layer)
    • Change password (voter)
    • Audit logging & audit log viewer
    • Vote-integrity hash generation  (used by cast_vote)
    • Account status enforcement (active / verified checks)
=============================================================
"""

import datetime
import hashlib
import random
import string
import sys
import os

# ── Re-use shared ANSI helpers from the main module ──────────────────────────
# When running standalone the constants below are defined here.
# When imported by the main module these will be overridden by the main
# module's own definitions (they are identical).

RESET          = "\033[0m"
BOLD           = "\033[1m"
DIM            = "\033[2m"
ITALIC         = "\033[3m"

RED            = "\033[31m"
GREEN          = "\033[32m"
YELLOW         = "\033[33m"
GRAY           = "\033[90m"
BRIGHT_YELLOW  = "\033[93m"
BRIGHT_CYAN    = "\033[96m"
BRIGHT_WHITE   = "\033[97m"
BG_GREEN       = "\033[42m"
BLACK          = "\033[30m"

THEME_LOGIN        = "\033[96m"   # BRIGHT_CYAN
THEME_VOTER        = "\033[94m"   # BRIGHT_BLUE
THEME_VOTER_ACCENT = "\033[35m"   # MAGENTA
THEME_ADMIN        = "\033[92m"   # BRIGHT_GREEN
THEME_ADMIN_ACCENT = "\033[33m"   # YELLOW


# ─────────────────────────────────────────────────────────────────────────────
#  UI helpers (duplicated here so the module is self-contained for testing)
# ─────────────────────────────────────────────────────────────────────────────

def _header(title, theme_color):
    width = 58
    # use simple '=' characters instead of box-drawing to avoid
    # UnicodeEncodeError on Windows terminals with cp1252 encoding
    line = '=' * width
    print(f"  {theme_color}{line}{RESET}")
    print(f"  {theme_color}{BOLD} {title.center(width - 2)} {RESET}{theme_color} {RESET}")
    print(f"  {theme_color}{line}{RESET}")

def _subheader(title, theme_color):
    print(f"\n  {theme_color}{BOLD}▸ {title}{RESET}")

def _table_header(fmt, theme_color):
    print(f"  {theme_color}{BOLD}{fmt}{RESET}")

def _table_divider(width, theme_color):
    print(f"  {theme_color}{'─' * width}{RESET}")

def _error(msg):   print(f"  {RED}{BOLD} {msg}{RESET}")
def _success(msg): print(f"  {GREEN}{BOLD} {msg}{RESET}")
def _warning(msg): print(f"  {YELLOW}{BOLD} {msg}{RESET}")
def _info(msg):    print(f"  {GRAY}{msg}{RESET}")

def _menu_item(number, text, color):
    print(f"  {color}{BOLD}{number:>3}.{RESET}  {text}")

def _prompt(text):
    return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()

def _status_badge(text, is_good):
    return f"{GREEN}{text}{RESET}" if is_good else f"{RED}{text}{RESET}"

def _pause():
    input(f"\n  {DIM}Press Enter to continue...{RESET}")

def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# ─────────────────────────────────────────────────────────────────────────────
#  1.  PASSWORD UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Return the SHA-256 hex digest of *password*."""
    return hashlib.sha256(password.encode()).hexdigest()


def masked_input(prompt_text: str = "Password: ") -> str:
    """
    Read a password from stdin, printing '*' for each character.
    Works on both Windows (msvcrt) and POSIX (termios/tty).
    """
    print(f"  {BRIGHT_WHITE}{prompt_text}{RESET}", end="", flush=True)
    password = ""

    if sys.platform == "win32":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                print(); break
            elif ch in ("\x08", "\b"):
                if password:
                    password = password[:-1]
                    sys.stdout.write("\b \b"); sys.stdout.flush()
            elif ch == "\x03":
                raise KeyboardInterrupt
            else:
                password += ch
                sys.stdout.write(f"{YELLOW}*{RESET}"); sys.stdout.flush()
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    print(); break
                elif ch in ("\x7f", "\x08"):
                    if password:
                        password = password[:-1]
                        sys.stdout.write("\b \b"); sys.stdout.flush()
                elif ch == "\x03":
                    raise KeyboardInterrupt
                else:
                    password += ch
                    sys.stdout.write(f"{YELLOW}*{RESET}"); sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    return password


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Enforce minimum password rules.
    Returns (is_valid: bool, reason: str).
    Currently requires length >= 6; extend rules here as needed.
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
#  2.  AUDIT LOGGING
# ─────────────────────────────────────────────────────────────────────────────

def log_action(audit_log: list, action: str, user: str, details: str) -> None:
    """
    Append a timestamped entry to *audit_log*.
    The list is managed by the main module (passed by reference).
    """
    audit_log.append({
        "timestamp": str(datetime.datetime.now()),
        "action":    action,
        "user":      user,
        "details":   details,
    })


# ─────────────────────────────────────────────────────────────────────────────
#  3.  VOTE INTEGRITY HASH
# ─────────────────────────────────────────────────────────────────────────────

def generate_vote_hash(voter_id: int, poll_id: int) -> str:
    """
    Create a short, unique reference token for a submitted ballot.
    Uses SHA-256 over voter_id + poll_id + current timestamp.
    The first 16 hex characters are returned (collision probability negligible).
    """
    timestamp = str(datetime.datetime.now())
    raw = f"{voter_id}{poll_id}{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ─────────────────────────────────────────────────────────────────────────────
#  4.  VOTER CARD NUMBER GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_voter_card_number() -> str:
    """Return a random 12-character alphanumeric voter card number."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


# ─────────────────────────────────────────────────────────────────────────────
#  5.  SESSION MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

class Session:
    """
    Lightweight session container.

    Attributes
    ----------
    user : dict | None
        The currently authenticated user record (from admins or voters dict).
    role : str | None
        Either 'admin' or 'voter'.
    """

    def __init__(self):
        self.user: dict | None = None
        self.role: str | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None

    def start(self, user: dict, role: str) -> None:
        self.user = user
        self.role = role

    def end(self) -> None:
        self.user = None
        self.role = None

    def require_role(self, *allowed_roles: str) -> bool:
        """Return True if the current session role is in *allowed_roles*."""
        return self.role in allowed_roles


# ─────────────────────────────────────────────────────────────────────────────
#  6.  LOGIN  (Admin & Voter)
# ─────────────────────────────────────────────────────────────────────────────

MIN_VOTER_AGE = 18   # duplicated here for standalone use

def login(session: Session, admins: dict, voters: dict,
          audit_log: list, save_fn, register_voter_fn) -> bool:
    """
    Show the login menu and authenticate the user.

    Parameters
    ----------
    session          : Session object to populate on success.
    admins           : dict of admin records.
    voters           : dict of voter records.
    audit_log        : shared audit list.
    save_fn          : callable – save_data() from main module.
    register_voter_fn: callable – register_voter() from main module.

    Returns True on successful login, False otherwise.
    """
    _clear()
    _header("E-VOTING SYSTEM", THEME_LOGIN)
    print()
    _menu_item(1, "Login as Admin",      THEME_LOGIN)
    _menu_item(2, "Login as Voter",      THEME_LOGIN)
    _menu_item(3, "Register as Voter",   THEME_LOGIN)
    _menu_item(4, "Exit",                THEME_LOGIN)
    print()
    choice = _prompt("Enter choice: ")

    # ── Admin login ───────────────────────────────────────────────────────────
    if choice == "1":
        _clear()
        _header("ADMIN LOGIN", THEME_ADMIN)
        print()
        username = _prompt("Username: ")
        password = masked_input("Password: ").strip()
        hashed   = hash_password(password)

        for admin in admins.values():
            if admin["username"] == username and admin["password"] == hashed:
                if not admin["is_active"]:
                    _error("This account has been deactivated.")
                    log_action(audit_log, "LOGIN_FAILED", username, "Account deactivated")
                    _pause(); return False
                session.start(admin, "admin")
                log_action(audit_log, "LOGIN", username, "Admin login successful")
                print(); _success(f"Welcome, {admin['full_name']}!")
                _pause(); return True

        _error("Invalid credentials.")
        log_action(audit_log, "LOGIN_FAILED", username, "Invalid admin credentials")
        _pause(); return False

    # ── Voter login ───────────────────────────────────────────────────────────
    elif choice == "2":
        _clear()
        _header("VOTER LOGIN", THEME_VOTER)
        print()
        voter_card = _prompt("Voter Card Number: ")
        password   = masked_input("Password: ").strip()
        hashed     = hash_password(password)

        for voter in voters.values():
            if voter["voter_card_number"] == voter_card and voter["password"] == hashed:
                if not voter["is_active"]:
                    _error("This voter account has been deactivated.")
                    log_action(audit_log, "LOGIN_FAILED", voter_card, "Voter account deactivated")
                    _pause(); return False
                if not voter["is_verified"]:
                    _warning("Your voter registration has not been verified yet.")
                    _info("Please contact an admin to verify your registration.")
                    log_action(audit_log, "LOGIN_FAILED", voter_card, "Voter not verified")
                    _pause(); return False
                session.start(voter, "voter")
                log_action(audit_log, "LOGIN", voter_card, "Voter login successful")
                print(); _success(f"Welcome, {voter['full_name']}!")
                _pause(); return True

        _error("Invalid voter card number or password.")
        log_action(audit_log, "LOGIN_FAILED", voter_card, "Invalid voter credentials")
        _pause(); return False

    # ── Voter self-registration ───────────────────────────────────────────────
    elif choice == "3":
        register_voter_fn()
        return False

    # ── Exit ──────────────────────────────────────────────────────────────────
    elif choice == "4":
        print(); _info("Goodbye!")
        save_fn(); exit()

    else:
        _error("Invalid choice.")
        _pause(); return False


def logout(session: Session, audit_log: list, save_fn) -> None:
    """
    Log the current user out, clear the session, and persist data.
    Call this from admin_dashboard / voter_dashboard before breaking the loop.
    """
    if session.user:
        identifier = (
            session.user.get("username") or
            session.user.get("voter_card_number", "unknown")
        )
        role_label = "Admin" if session.role == "admin" else "Voter"
        log_action(audit_log, "LOGOUT", identifier, f"{role_label} logged out")
    save_fn()
    session.end()


# ─────────────────────────────────────────────────────────────────────────────
#  7.  VOTER REGISTRATION  (security layer)
# ─────────────────────────────────────────────────────────────────────────────

def register_voter(voters: dict, voter_id_counter_ref: list,
                   voting_stations: dict, audit_log: list, save_fn) -> None:
    """
    Self-service voter registration with all security validations.

    *voter_id_counter_ref* is a one-element list so the integer counter can
    be mutated by reference: e.g. voter_id_counter_ref = [voter_id_counter]
    in the main module; after this call read voter_id_counter_ref[0].
    """
    _clear()
    _header("VOTER REGISTRATION", THEME_VOTER)
    print()

    # ── Personal details ──────────────────────────────────────────────────────
    full_name = _prompt("Full Name: ")
    if not full_name:
        _error("Name cannot be empty."); _pause(); return

    national_id = _prompt("National ID Number: ")
    if not national_id:
        _error("National ID cannot be empty."); _pause(); return

    if any(v["national_id"] == national_id for v in voters.values()):
        _error("A voter with this National ID already exists."); _pause(); return

    dob_str = _prompt("Date of Birth (YYYY-MM-DD): ")
    try:
        dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
        age = (datetime.datetime.now() - dob).days // 365
        if age < MIN_VOTER_AGE:
            _error(f"You must be at least {MIN_VOTER_AGE} years old to register.")
            _pause(); return
    except ValueError:
        _error("Invalid date format."); _pause(); return

    gender = _prompt("Gender (M/F/Other): ").upper()
    if gender not in ("M", "F", "OTHER"):
        _error("Invalid gender selection."); _pause(); return

    address = _prompt("Residential Address: ")
    phone   = _prompt("Phone Number: ")
    email   = _prompt("Email Address: ")

    # ── Password (security-owned) ─────────────────────────────────────────────
    password = masked_input("Create Password: ").strip()
    valid, reason = validate_password_strength(password)
    if not valid:
        _error(reason); _pause(); return

    confirm = masked_input("Confirm Password: ").strip()
    if password != confirm:
        _error("Passwords do not match."); _pause(); return

    # ── Station selection ─────────────────────────────────────────────────────
    active_stations = {sid: s for sid, s in voting_stations.items() if s["is_active"]}
    if not active_stations:
        _error("No voting stations available. Contact admin."); _pause(); return

    _subheader("Available Voting Stations", THEME_VOTER)
    for sid, s in active_stations.items():
        print(f"    {THEME_VOTER}{sid}.{RESET} {s['name']} {DIM}- {s['location']}{RESET}")

    try:
        station_choice = int(_prompt("\nSelect your voting station ID: "))
        if station_choice not in active_stations:
            _error("Invalid station selection."); _pause(); return
    except ValueError:
        _error("Invalid input."); _pause(); return

    # ── Create record ─────────────────────────────────────────────────────────
    voter_card = generate_voter_card_number()
    vid = voter_id_counter_ref[0]

    voters[vid] = {
        "id": vid, "full_name": full_name, "national_id": national_id,
        "date_of_birth": dob_str, "age": age, "gender": gender,
        "address": address, "phone": phone, "email": email,
        "password": hash_password(password),
        "voter_card_number": voter_card, "station_id": station_choice,
        "is_verified": False, "is_active": True, "has_voted_in": [],
        "registered_at": str(datetime.datetime.now()), "role": "voter",
    }

    log_action(audit_log, "REGISTER", full_name,
               f"New voter registered with card: {voter_card}")
    print()
    _success("Registration successful!")
    print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{voter_card}{RESET}")
    _warning("IMPORTANT: Save this number! You need it to login.")
    _info("Your registration is pending admin verification.")

    voter_id_counter_ref[0] += 1
    save_fn()
    _pause()


# ─────────────────────────────────────────────────────────────────────────────
#  8.  CHANGE VOTER PASSWORD
# ─────────────────────────────────────────────────────────────────────────────

def change_voter_password(session: Session, voters: dict,
                          audit_log: list, save_fn) -> None:
    """Allow an authenticated voter to change their own password."""
    _clear()
    _header("CHANGE PASSWORD", THEME_VOTER)
    print()

    old_pass = masked_input("Current Password: ").strip()
    if hash_password(old_pass) != session.user["password"]:
        _error("Incorrect current password."); _pause(); return

    new_pass = masked_input("New Password: ").strip()
    valid, reason = validate_password_strength(new_pass)
    if not valid:
        _error(reason); _pause(); return

    confirm = masked_input("Confirm New Password: ").strip()
    if new_pass != confirm:
        _error("Passwords do not match."); _pause(); return

    hashed = hash_password(new_pass)
    session.user["password"] = hashed
    for v in voters.values():
        if v["id"] == session.user["id"]:
            v["password"] = hashed
            break

    log_action(audit_log, "CHANGE_PASSWORD",
               session.user["voter_card_number"], "Password changed")
    print(); _success("Password changed successfully!")
    save_fn(); _pause()


# ─────────────────────────────────────────────────────────────────────────────
#  9.  AUDIT LOG VIEWER  (Admin feature)
# ─────────────────────────────────────────────────────────────────────────────

def view_audit_log(audit_log: list) -> None:
    """Interactive audit-log viewer for admin users."""
    _clear()
    _header("AUDIT LOG", THEME_ADMIN)

    if not audit_log:
        print(); _info("No audit records."); _pause(); return

    print(f"\n  {DIM}Total Records: {len(audit_log)}{RESET}")
    _subheader("Filter", THEME_ADMIN_ACCENT)
    _menu_item(1, "Last 20 entries",       THEME_ADMIN)
    _menu_item(2, "All entries",           THEME_ADMIN)
    _menu_item(3, "Filter by action type", THEME_ADMIN)
    _menu_item(4, "Filter by user",        THEME_ADMIN)
    choice = _prompt("\nChoice: ")

    entries = audit_log  # default: all

    if choice == "1":
        entries = audit_log[-20:]

    elif choice == "3":
        action_types = sorted(set(e["action"] for e in audit_log))
        for i, at in enumerate(action_types, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {at}")
        try:
            idx = int(_prompt("Select action type: ")) - 1
            entries = [e for e in audit_log if e["action"] == action_types[idx]]
        except (ValueError, IndexError):
            _error("Invalid choice."); _pause(); return

    elif choice == "4":
        uf = _prompt("Enter username / card number: ").lower()
        entries = [e for e in audit_log if uf in e["user"].lower()]

    print()
    _table_header(
        f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}",
        THEME_ADMIN
    )
    _table_divider(100, THEME_ADMIN)

    for entry in entries:
        action = entry["action"]
        if "CREATE" in action or action == "LOGIN":
            ac = GREEN
        elif "DELETE" in action or "DEACTIVATE" in action:
            ac = RED
        elif "UPDATE" in action:
            ac = YELLOW
        else:
            ac = RESET

        print(
            f"  {DIM}{entry['timestamp'][:19]}{RESET}  "
            f"{ac}{action:<25}{RESET} "
            f"{entry['user']:<20} "
            f"{DIM}{entry['details'][:50]}{RESET}"
        )

    _pause()


# ─────────────────────────────────────────────────────────────────────────────
#  INTEGRATION GUIDE  (for the main module)
# ─────────────────────────────────────────────────────────────────────────────
"""
HOW TO PLUG THIS MODULE INTO evoting_main.py
─────────────────────────────────────────────

1.  IMPORT at the top of the main file:

        from security_sessions import (
            Session,
            hash_password,
            masked_input,
            generate_voter_card_number,
            generate_vote_hash,
            log_action,
            login,
            logout,
            register_voter,
            change_voter_password,
            view_audit_log,
        )

2.  REPLACE global variables with a Session object:

        # Remove:  current_user = None; current_role = None
        # Add:
        session = Session()

3.  REPLACE the standalone log_action() calls:

        # Old:  log_action("LOGIN", username, "Admin login successful")
        # New:  log_action(audit_log, "LOGIN", username, "Admin login successful")

4.  REPLACE the login() call in main():

        logged_in = login(session, admins, voters, audit_log, save_data, register_voter)
        if logged_in:
            if session.role == "admin":  admin_dashboard()
            elif session.role == "voter": voter_dashboard()

5.  REPLACE logout lines in dashboards:

        # Old one-liners → use:
        logout(session, audit_log, save_data)
        break

6.  REPLACE generate_voter_card_number() calls → already imported above.

7.  IN cast_vote(), replace the manual hash line:

        # Old:
        vote_hash = hashlib.sha256(f"{current_user['id']}{pid}{...}".encode()).hexdigest()[:16]
        # New:
        vote_hash = generate_vote_hash(session.user['id'], pid)

8.  REPLACE register_voter() definition (remove from main file, use imported one):

        voter_id_counter_ref = [voter_id_counter]
        register_voter(voters, voter_id_counter_ref, voting_stations, audit_log, save_data)
        voter_id_counter = voter_id_counter_ref[0]

9.  REPLACE change_voter_password() call in voter_dashboard:

        change_voter_password(session, voters, audit_log, save_data)

10. REPLACE view_audit_log() call in admin_dashboard:

        view_audit_log(audit_log)
"""