import json
import datetime
import os
from abc import ABC

# --- BASE ENTITY ---
class Entity(ABC):
    def __init__(self, entity_id):
        self.id = entity_id
        self.created_at = datetime.datetime.now()

# --- USER MODELS ---
class User(Entity):
    def __init__(self, user_id, full_name, role, email=None, is_active=True):
        super().__init__(user_id)
        self.full_name = full_name
        self.email = email
        self.role = role
        self.is_active = is_active

class Voter(User):
    def __init__(self, user_id, full_name, email, voter_card, station_id, dob_str, 
                 is_verified=False, has_voted_in=None, is_active=True):
        super().__init__(user_id, full_name, "voter", email, is_active)
        self.voter_card = voter_card
        self.station_id = station_id
        self.is_verified = is_verified
        self.has_voted_in = has_voted_in if has_voted_in else []
        self.dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d") if isinstance(dob_str, str) else dob_str

class Candidate(User):
    def __init__(self, user_id, full_name, party, education, manifesto, age, is_active=True):
        super().__init__(user_id, full_name, "candidate", None, is_active)
        self.party = party
        self.education = education
        self.manifesto = manifesto
        self.age = age
        self.votes = 0                     # track votes for business logic

# --- ELECTION MODELS ---
class Position:
    def __init__(self, pos_id, title, max_winners, min_age, level="National"):
        self.id = pos_id
        self.title = title
        self.max_winners = max_winners
        self.min_age = min_age
        self.level = level

class Poll(Entity):
    def __init__(self, poll_id, title, start_date, end_date, status="draft", positions=None):
        super().__init__(poll_id)
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.status = status # draft, open, closed
        # List of dicts: {"position_id": int, "candidate_ids": [int]}
        self.positions_config = positions if positions else []

class Vote:
    def __init__(self, vote_id, poll_id, position_id, voter_id, candidate_id=None, abstained=False):
        self.vote_id = vote_id
        self.poll_id = poll_id
        self.position_id = position_id
        self.voter_id = voter_id
        self.candidate_id = candidate_id
        self.abstained = abstained
        self.timestamp = datetime.datetime.now()

# --- CENTRAL DATA MANAGER ---
class DataManager:
    def __init__(self, file_path="evoting_data.json"):
        self.file_path = file_path
        self.voters = {}
        self.candidates = {}
        self.polls = {}
        self.positions = {}
        self.votes = []
        self.load_all()

    def load_all(self):
        if not os.path.exists(self.file_path): return
        with open(self.file_path, "r") as f:
            raw = json.load(f)

        # Migration Logic for all entities
        for vid, v in raw.get("voters", {}).items():
            self.voters[int(vid)] = Voter(int(vid), v['full_name'], v['email'], v['voter_card_number'], v['station_id'], v['date_of_birth'], v['is_verified'], v['has_voted_in'], v['is_active'])
        
        for cid, c in raw.get("candidates", {}).items():
            self.candidates[int(cid)] = Candidate(int(cid), c['full_name'], c['party'], c['education'], c['manifesto'], c['age'], c.get('is_active', True))
            
        for pid, p in raw.get("polls", {}).items():
            self.polls[int(pid)] = Poll(int(pid), p['title'], p['start_date'], p['end_date'], p['status'], p.get('positions', []))

        for pos_id, pos in raw.get("positions", {}).items():
            self.positions[int(pos_id)] = Position(int(pos_id), pos['title'], pos['max_winners'], pos['min_candidate_age'], pos['level'])

        self.votes = [Vote(**v) if isinstance(v, dict) else v for v in raw.get("votes", [])]

    def save_all(self):
        def custom_serializer(obj):
            if isinstance(obj, datetime.datetime): return obj.strftime("%Y-%m-%d %H:%M:%S")
            return obj.__dict__

        data = {
            "voters": {k: v.__dict__ for k, v in self.voters.items()},
            "candidates": {k: v.__dict__ for k, v in self.candidates.items()},
            "polls": {k: v.__dict__ for k, v in self.polls.items()},
            "positions": {k: v.__dict__ for k, v in self.positions.items()},
            "votes": [v.__dict__ for v in self.votes]
        }
        with open(self.file_path, "w") as f:
            json.dump(data, f, default=custom_serializer, indent=4)