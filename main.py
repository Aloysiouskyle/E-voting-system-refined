# main.py
# Entry point of the E-Voting System

from models import Candidate, Voter, DataManager
from businesslogic import ElectionEngine

# security module handles authentication, sessions, and related utilities
# file was renamed to security_codeLines.py
from security_codeLines import (
    Session,
    login,
    logout,
    register_voter,
    hash_password,
    log_action,
)

from utils import View, Theme


class VotingApp:

    def __init__(self):
        # business logic engine instance (correct class name)
        self.engine = ElectionEngine()
        self.ui = View()

        # session object replaces prior Auth instance
        self.session = Session()

        # application state (persisted through DataManager)
        self.data = DataManager()
        self.voters = self.data.voters          # dict[int, Voter]
        self.candidates = self.data.candidates  # dict[int, Candidate]
        self.audits = []          # audit log list

        # counters for generating unique IDs (derived from existing keys)
        self.next_voter_id = max(self.voters.keys(), default=0) + 1
        self.next_candidate_id = max(self.candidates.keys(), default=0) + 1

    def save_data(self):
        """Persist all runtime data via the DataManager."""
        self.data.save_all()

    def run(self):
        # ensure admins exist for demonstration
        self.admins = {1: {"username": "admin", "password": hash_password("admin123"), "full_name": "Administrator", "is_active": True}}

        while True:
            self.ui.draw_header("NATIONAL E-VOTING SYSTEM")

            # delegate authentication to security module
            logged = login(
                self.session,
                self.admins,
                self.voters,
                self.audits,
                self.save_data,
                lambda: register_voter(
                    self.voters,
                    [self.next_voter_id],
                    {},
                    self.audits,
                    self.save_data
                )
            )

            if not logged:
                # exit or try again
                continue

            # route to appropriate dashboard
            if self.session.role == "admin":
                self.admin_menu()
            else:
                self.voter_menu()

            # after dashboard return, log out user automatically
            logout(self.session, self.audits, self.save_data)

            # on exit from dashboard, ask whether to quit
            if not self.session.is_authenticated:
                break

    def admin_menu(self):
        self.ui.draw_header("ADMIN PANEL", Theme.GREEN)

        choice = self.ui.show_menu([
            "Register Candidate",
            "Register Voter (security)",
            "View Results",
            "Back"
        ])

        if choice == "1":
            name = input("Candidate Name: ")
            party = input("Party: ")
            age = int(input("Age: "))
            edu = input("Education: ")
            manifesto = input("Manifesto: ")
            has_criminal = input("Criminal record? (y/n): ").strip().lower() == "y"

            # ensure eligibility via business logic
            eligible, reason = self.engine.check_candidate_eligibility(age, edu, has_criminal)
            if not eligible:
                print(f"Cannot register candidate: {reason}")
                return

            cid = self.next_candidate_id
            c = Candidate(cid, name, party, edu, manifesto, age)
            self.candidates[cid] = c
            self.next_candidate_id += 1
            self.save_data()
            print("Candidate Registered Successfully")

        elif choice == "2":
            # security module handles voter registration
            register_voter(
                self.voters,
                [self.next_voter_id],
                {},
                self.audits,
                self.save_data
            )
            self.next_voter_id += 1

        elif choice == "3":
            # use business logic to tally
            results = self.engine.tally_results(self.candidates.values())
            print("Election Results:")
            for name, votes in results.items():
                print(f"  {name}: {votes}")

        # 'Back' will return to run() loop

    def voter_menu(self):
        self.ui.draw_header("VOTER PORTAL")

        # lookup the authenticated voter
        voter = self.session.user
        if not voter or voter["role"] != "voter":
            print("Access denied")
            return

        print("\nCandidates:")
        for cid, candidate in self.candidates.items():
            print(cid, "-", candidate.full_name)

        choice = int(input("Enter Candidate ID: "))
        if choice in self.candidates:
            ok, msg = self.engine.cast_vote(voter, self.candidates[choice], poll_id=1)
            print(msg)
            if ok:
                self.save_data()
        else:
            print("Invalid Candidate")


# Program start
if __name__ == "__main__":
    app = VotingApp()
    app.run()