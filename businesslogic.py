"""
Business Logic Layer for the National E-Voting System.

Responsibilities:
- Candidate eligibility validation
- Vote verification (prevent duplicate voting)
- Vote casting
- Result tallying
- Voter turnout statistics
- Poll lifecycle management

NOTE:
This file contains NO UI code.
It does not use print() or input().
It only processes data and returns results.
"""

import hashlib
from collections import defaultdict


class ElectionEngine:
    """
    Core business logic of the voting system.

    Follows SOLID principles:
    - Single Responsibility: Handles election rules only
    - Independent from UI layer
    """

    def __init__(self):
        # Stores polls and their details
        self.polls = {}

        # Stores computed results
        self.results = defaultdict(dict)

    # =====================================================
    # SECURITY FUNCTIONS
    # =====================================================

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256.
        Used for secure password storage.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    # =====================================================
    # CANDIDATE VALIDATION
    # =====================================================

    @staticmethod
    def check_candidate_eligibility(age, education, has_criminal_record):
        """
        Check if a candidate satisfies election requirements.
        """

        required_education = [
            "Bachelor's Degree",
            "Master's Degree",
            "PhD"
        ]

        if not (25 <= age <= 75):
            return False, "Age must be between 25 and 75."

        if education not in required_education:
            return False, "Candidate must have at least a Bachelor's Degree."

        if has_criminal_record:
            return False, "Candidate with criminal record is disqualified."

        return True, "Candidate eligible."

    # =====================================================
    # VOTING LOGIC
    # =====================================================

    @staticmethod
    def verify_vote(voter, poll_id):
        """
        Prevent duplicate voting.
        Returns True if voter has not voted in the poll.
        """

        if poll_id in voter.voted_polls:
            return False

        return True

    def cast_vote(self, voter, candidate, poll_id):
        """
        Record a vote for a candidate.
        """

        if not self.verify_vote(voter, poll_id):
            return False, "Voter has already voted in this poll."

        candidate.votes += 1
        voter.voted_polls.append(poll_id)

        return True, "Vote recorded successfully."

    # =====================================================
    # RESULT CALCULATIONS
    # =====================================================

    def tally_results(self, candidates):
        """
        Calculate vote totals for candidates.
        """

        results = {}

        for candidate in candidates:
            results[candidate.full_name] = candidate.votes

        return results

    def calculate_turnout(self, voters):
        """
        Calculate voter turnout percentage.
        """

        total_voters = len(voters)

        if total_voters == 0:
            return 0

        voted_count = sum(1 for voter in voters if voter.voted_polls)

        turnout = (voted_count / total_voters) * 100

        return round(turnout, 2)

    # =====================================================
    # POLL MANAGEMENT
    # =====================================================

    def create_poll(self, poll_id, title, candidates):
        """
        Create a new election poll.
        """

        self.polls[poll_id] = {
            "title": title,
            "candidates": candidates,
            "is_active": True
        }

    def close_poll(self, poll_id):
        """
        Close an active poll.
        """

        if poll_id in self.polls:
            self.polls[poll_id]["is_active"] = False
            return True

        return False

    def get_poll(self, poll_id):
        """
        Retrieve poll information.
        """

        return self.polls.get(poll_id, None)