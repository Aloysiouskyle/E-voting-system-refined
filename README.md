# E-voting-App

## About the Project

This is a little Python program we knocked together for a class assignment – a text‑based e‑voting system that runs in your terminal. Everyone on the team
picked a component and tried to keep it tidy so the whole thing didn't turn
into a big ball of spaghetti.

The original requirements called for things like admin and voter logins, a way
for candidates to be added and checked for eligibility, vote casting with
duplicate‑vote protection, and saving everything to disk. The app does all of
that and it's still easy to run or extend.


## Who Did What

* **Lomoro Paul** – built out the core election rules in
  `businesslogic.py` (the `ElectionEngine`).
* **Bukenya Jawadhu** – wrote the main application loop **Aijuka Jonah** wrote menus in `main.py`.
 **Kakaire Shawn ** – added the display helpers and small niceties in `utils.py`.
* **Kayongo Aloysious** – defined all the data models and the JSON persistence layer in
  `models.py`.
* **Mayinja Joel** – handled authentication, sessions, and the security helpers in
  `security_codeLines.py`.

If you run the program you'll notice the code is split accordingly; each of us
tried to stick to our own file except when we needed to call another module.

---

## Design in a Nutshell

### Modular structure

The project is deliberately small, but it's broken down in the way you'd hope
for a "real" application. There are five Python files, each with a specific job
(see the previous section). That made it easier to work in parallel and to
write tests for the logic without having to launch the whole UI.

### Object‑oriented bits

Most of the data is wrapped in classes – users, voters, candidates, polls, etc.
The `ElectionEngine` class is the brain of the system, and `DataManager`
hides the details of reading/writing `evoting_data.json`. Even the session is a
class object so the rest of the code can just ask it "who's logged in?".

### Keeping things separate

The UI lives in `main.py` (plus helpers), the rules live in
`businesslogic.py`, and persistence lives in `models.py`. That means I could
swap out the console menus for a web interface later and none of the
business logic would have to change. It also makes unit testing straightforward
– we can exercise the engine in isolation.

### Clean code

We tried to pick clear names (`cast_vote` instead of `doThing`), avoid
copy‑pasting the same code twice, and add comments where a reader might get
confused. One small bug we squashed was that the pretty box characters in the
headers caused a crash on Windows, so we replaced them with plain `=`s.

---

## Does it actually work?

Yep. Run it from any terminal, log in as the built‑in admin (`admin`/
`admin123`), add a candidate and a voter, log in as the voter and cast a vote.
The vote shows up when you view the results, and if you stop the program and
start it again the data is still there.

## Running the App

Open a command prompt or PowerShell, cd to the project folder and run:

```powershell
python main.py
```

Follow the on‑screen prompts. You can register voters yourself or let the
admin create them; you can register candidates; voters can only vote once per
poll; and everything is saved automatically.

---

## If You Keep Working on It

* Write more tests – especially around login/registration failure cases.
* Let the admin deactivate or verify users instead of editing the JSON by hand.


