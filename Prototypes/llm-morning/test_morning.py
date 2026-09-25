"""Tests against the fake model and a stubbed API. No network, no quota.

    python -m unittest -v test_morning
"""
import contextlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest

import data
import metrics
import gemini
from gemini import Cache, FakeClient, GeminiClient, Oracle
from morning import run
from world import QUIET_TURNS, SYSTEM, Grudge, Morning, Track, estimate_tokens

# What the third version's prompts said about guilt, suspicion and grudges: verdicts, which
# the prompts must no longer contain.
OLD_VERDICTS = [
    "sits at the back of your mind", "weighs on you", "weighs on you heavily", "crushing",
    "You do not suspect anyone in particular", "You are not holding anything against anyone",
    "Your conscience:",
] + [v.format(x=x) for x in ("Daniel", "Elena", "Leo", "Mara") for v in (
    "You have a feeling {x} might have taken it", "You believe {x} took it", "You are sure {x} took it",
    "You are annoyed with {x}", "You are angry with {x}", "You are furious with {x}")]

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "..", "..", "Docs", "understanding", "target-morning.md")
MERGED = os.path.join(HERE, "..", "..", "Docs", "understanding", "understanding-all.md")


def target_text():
    """target-morning.md, or failing that its section of the merged understanding-all.md;
    None if neither is there."""
    if os.path.exists(TARGET):
        with open(TARGET, encoding="utf-8") as f:
            return f.read()
    if os.path.exists(MERGED):
        with open(MERGED, encoding="utf-8") as f:
            merged = f.read()
        start = merged.find("\n## target-morning.md\n")
        if start >= 0:
            end = merged.find("\n---\n", start + 1)
            return merged[start:end if end >= 0 else None]
    return None


CONFIG = os.path.join(HERE, "config.json")
SECRET = "SENTINEL-not-a-real-key-7731"


class Dirs:
    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="llm-morning-test-")
        self.runs = os.path.join(self.root, "runs")
        self.cache = os.path.join(self.root, "cache")

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


def quiet_run(*a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = run(*a, quiet=False, **k)
    return result, buf.getvalue()


def fake_morning(dirs, seed=7, **k):
    return quiet_run(seed, fake=True, config_path=CONFIG, runs_dir=dirs.runs, cache_dir=dirs.cache, **k)


def read(path, mode="r"):
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
        return f.read()


def cached_prompts(dirs):
    prompts = []
    for name in os.listdir(dirs.cache):
        prompts += [e["prompt"] for e in json.loads(read(os.path.join(dirs.cache, name))).values()]
    return prompts


class Exploding:
    requests = 0

    def generate(self, system, prompt):
        raise AssertionError("replay must not reach a client")


class FakeResponse:
    def __init__(self, text, tokens=321):
        self.text = text
        self.usage_metadata = type("U", (), {"prompt_token_count": tokens})()


class StubApi:
    """Stands in for genai.Client: .models.generate_content runs through a script."""

    def __init__(self, script):
        self.script = list(script)
        self.models = self
        self.calls = 0

    def generate_content(self, model, contents, config):
        self.calls += 1
        step = self.script.pop(0) if self.script else "ok"
        if isinstance(step, Exception):
            raise step
        return FakeResponse(FakeClient(invalid_every=0).generate("", contents))


def api_error(code, status, detail):
    from google.genai import errors
    return errors.ClientError(code, {"error": {"code": code, "status": status, "message": "quota",
                                               "details": detail}})


PER_MINUTE = [{"@type": "type.googleapis.com/google.rpc.QuotaFailure",
               "violations": [{"quotaId": "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"}]},
              {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "7s"}]
PER_DAY = [{"@type": "type.googleapis.com/google.rpc.QuotaFailure",
            "violations": [{"quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier"}]}]


class FakeMorningTest(unittest.TestCase):
    def setUp(self):
        self.dirs = Dirs()

    def tearDown(self):
        self.dirs.cleanup()

    def test_a_morning_completes_and_writes_a_story(self):
        (meta, code), out = fake_morning(self.dirs)
        self.assertEqual(code, 0, out)
        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed7.md"))
        self.assertIn("## The morning", story)
        self.assertIn("## What was said", story)
        self.assertLessEqual(meta["api_requests"], 150)
        self.assertGreater(meta["model_decisions"], 0)
        self.assertGreater(meta["routine_decisions"], 0)

    def test_every_kind_of_broken_answer_falls_back_to_the_rules(self):
        # Every answer broken: the four kinds land at minute 0, where everyone can speak.
        (meta, code), _ = fake_morning(self.dirs, client=FakeClient(invalid_every=1))
        self.assertEqual(code, 0)
        self.assertEqual(meta["model_decisions"], 0)
        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed7.md"))
        self.assertGreater(meta["fallbacks"], 0)
        for why in ("(not JSON)", "was not offered)", "(no `reason`)", "is speech but no words were given)"):
            self.assertIn(why, story)

    def test_replay_is_byte_for_byte_with_no_client_reached(self):
        (first, _), _ = fake_morning(self.dirs)
        (meta, code), out = fake_morning(self.dirs, replay=True, client=Exploding())
        self.assertEqual(code, 0, out)
        self.assertTrue(meta["identical_to_original"])
        self.assertEqual(meta["api_requests"], 0)
        self.assertEqual(meta["answers_live"], 0)
        self.assertEqual(meta["answers_from_cache"], first["answers_live"])
        a = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed7.md"), "rb")
        b = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed7.replay.md"), "rb")
        self.assertEqual(a, b)

    def test_replay_without_a_cache_stops_cleanly(self):
        (meta, code), out = fake_morning(self.dirs, replay=True)
        self.assertEqual(code, 3)
        self.assertIn("no cached answer", out)

    def test_seeds_do_not_share_answers(self):
        fake_morning(self.dirs, seed=1)
        (meta, _), _ = fake_morning(self.dirs, seed=2)
        self.assertEqual(meta["answers_from_cache"], 0)

    def test_at_most_one_call_per_person_per_turn(self):
        client = FakeClient()
        m = Morning(Oracle(Cache(os.path.join(self.dirs.root, "c.json")), "fake", 1, client=client), 1)
        for t in range(m.turns):
            before = client.requests
            m.turn(t)
            asked = [d["person"] for d in m.log[-1]["decisions"] if d["mode"] != "routine"]
            self.assertEqual(client.requests - before, len(asked))
            self.assertEqual(len(asked), len(set(asked)))

    def test_prompts_are_short(self):
        fake_morning(self.dirs)
        prompts = cached_prompts(self.dirs)
        self.assertTrue(prompts)
        for p in prompts:
            # The estimate tracked the API's own count closely in the first runs (1,250 against
            # 1,252); the real counts of the real runs are reported with them.
            self.assertLess(estimate_tokens(SYSTEM + p), 1450)

    def test_nothing_from_target_morning_reaches_a_prompt(self):
        fake_morning(self.dirs)
        prompts = [SYSTEM] + cached_prompts(self.dirs)
        target = target_text()
        if target is None:
            self.skipTest("neither target-morning.md nor its copy in understanding-all.md was found")
        pieces = []
        for line in target.splitlines():
            line = re.sub(r"^[#\-\d. ]+", "", line).strip()
            for piece in re.split(r"(?<=[.:;!?])\s+|\(|\)", line):
                piece = piece.strip(" .,:;\"'*")
                if len(piece.split()) >= 5:
                    pieces.append(piece)
        pieces += ["nobody eats alone", "don't look at me", "look innocent", "turning point",
                   "weighed down", "believable", "Possible", "Never"]
        # The four Never lines of the second step's brief (the merged copy predates them).
        pieces += ["Everyone speaks at once and nobody answers the line before theirs",
                   "A person repeats the same kind of line many turns in a row with no effect",
                   "Someone who was wronged forgives within minutes, with no lasting cost",
                   "A person mentions objects or places the house does not have"]
        self.assertGreater(len(pieces), 40)
        for p in prompts:
            for piece in pieces:
                self.assertNotIn(piece.lower(), p.lower(), f"target-morning text in a prompt: {piece!r}")

    def test_only_daniel_knows_and_only_daniel_may_confess(self):
        m = Morning(Oracle(Cache(os.path.join(self.dirs.root, "c.json")), "fake", 1, client=FakeClient()), 1)
        for pid, p in m.people.items():
            ate = [x for x in p.backstory if "eats a can" in x]
            ids = {o.id for o in m.options_for(p)}
            if pid == "daniel":
                self.assertEqual(ate, ["Day 3: In the night Daniel eats a can standing at the counter "
                                       "in the dark. Nobody sees. (you did it)"])
                self.assertIn("confess", ids)
                self.assertNotIn("ask_who", ids)
            else:
                self.assertEqual(ate, [])
                self.assertNotIn("confess", ids)
                self.assertIn("ask_who", ids)
            self.assertNotIn("deny", ids)       # nobody has asked yet
            self.assertTrue({"silent", "accuse_" + next(q for q in data.ORDER if q != pid)} <= ids)

    def test_an_admission_cannot_be_taken_back(self):
        m = Morning(Oracle(Cache(os.path.join(self.dirs.root, "c.json")), "fake", 1, client=FakeClient()), 1)
        daniel, leo = m.people["daniel"], m.people["leo"]
        for q in m.people.values():
            q.heard_question = True
        in_turn(m)
        m.apply(daniel, next(o for o in m.options_for(daniel) if o.id == "confess"),
                {"mode": "model", "say": "It was me.", "feeling": "ashamed"}, 1, [], new_record())
        out_of_turn(m)
        ids = {o.id for o in m.options_for(daniel)}
        self.assertFalse({"confess", "deny", "search", "keep_searching"} & ids)
        self.assertFalse([i for i in ids if i.startswith("accuse_")])
        ids = {o.id for o in m.options_for(leo)}
        self.assertEqual({i for i in ids if i.startswith("accuse_")}, {"accuse_daniel"})
        self.assertFalse({"ask_who", "search"} & ids)
        self.assertIn((3, 'Daniel admits taking it, to everyone: "It was me."'), leo.memory)
        self.assertIn('min 03: Daniel admitted taking the can: "It was me." (you heard it)', leo.sure)
        # However long the morning gets, both of them are still told.
        filler = [(60, f"filler line number {i} about nothing much at all") for i in range(200)]
        leo.memory += filler
        daniel.memory += filler
        for q in (daniel, leo):
            prompt = m.prompt_for(q, 20, m.options_for(q))
            self.assertIn("admitted", prompt)
            self.assertLess(estimate_tokens(SYSTEM + prompt), 1450)
        self.assertIn("you admitted aloud that you took the can",
                      m.prompt_for(daniel, 20, m.options_for(daniel)))

    def test_the_call_cap_counts_answers_from_an_earlier_run(self):
        cache = Cache(os.path.join(self.dirs.root, "cap.json"))
        cache.put(Cache.key("fake", 1, "s", "p1"), "p1", "earlier answer")
        oracle = Oracle(cache, "fake", 1, client=FakeClient(), max_calls=1)
        self.assertEqual(oracle.ask("s", "p1"), "earlier answer")
        with self.assertRaises(gemini.CallCapReached):
            oracle.ask("s", "p2")
        self.assertEqual(oracle.client.requests, 0)

    def test_the_call_cap_stops_the_morning_cleanly(self):
        (meta, code), out = fake_morning(self.dirs, client=FakeClient(max_calls=3))
        self.assertEqual(code, 3)
        self.assertIn("reached 3 API requests", out)
        self.assertIn("To resume", out)


class Scripted:
    """A model that answers by a policy: policy(who, minute, options, client) -> (option, say).
    Keeps every prompt, and who was asked at which minute."""

    def __init__(self, policy):
        self.policy = policy
        self.requests = 0
        self.prompts = []
        self.asked = []             # (minute, who)

    def generate(self, system, prompt):
        self.requests += 1
        who = re.match(r"You are (\w+),", prompt).group(1).lower()
        minute = int(re.search(r"^Now, minute (\d+)", prompt, flags=re.M).group(1))
        options = re.findall(r"^- (\w+):", prompt.split("Your options:")[-1], flags=re.M)
        self.prompts.append((minute, who, prompt))
        answer = self.policy(who, minute, options, self)
        option, say = answer[:2]
        suspects, angry_at = answer[2:] if len(answer) == 4 else ("nobody", "nobody")
        self.asked.append((minute, who))
        return json.dumps({"option": option, "say": say, "feeling": "tense", "reason": "Scripted.",
                           "suspects": suspects, "angry_at": angry_at})


def scripted(policy, dirs, seed=1, turns=None):
    client = Scripted(policy)
    m = Morning(Oracle(Cache(os.path.join(dirs.root, f"scripted-{seed}.json")), "fake", seed,
                       client=client), seed)
    for t in range(m.turns if turns is None else turns):
        m.turn(t)
    return m, client


def in_turn(m):
    """What a turn sets up, for calling apply() directly."""
    m.present = {r: [q for q in data.ORDER if m.people[q].room == r] for r in data.ROOMS}
    m.so_far = {r: [] for r in data.ROOMS}
    m.acted, m.moves = set(), []


def out_of_turn(m):
    m.present = m.so_far = m.acted = m.moves = None


def new_record():
    return {"events": [], "guilt": [], "grudges": []}


def reassure_or_silent(who, minute, options, client):
    return ("reassure_all", "It will be all right.") if "reassure_all" in options else ("silent", None)


class SequentialTalkTest(unittest.TestCase):
    def setUp(self):
        self.dirs = Dirs()

    def tearDown(self):
        self.dirs.cleanup()

    # ---- ordering ----
    def test_the_one_just_accused_acts_next(self):
        def policy(who, minute, options, client):
            if minute == 0 and client.requests == 1:
                done = {w for m, w in client.asked if m == 0} | {who}
                target = sorted(o[7:] for o in options if o.startswith("accuse_") and o[7:] not in done)[-1]
                client.target = target
                return f"accuse_{target}", "It was you."
            return "silent", None
        m, client = scripted(policy, self.dirs, turns=1)
        order = m.log[0]["decisions"]
        self.assertEqual(order[1]["person"], client.target)
        accuser = data.PEOPLE[order[0]["person"]]["name"]
        self.assertEqual(order[1]["order_reason"], f"just accused by {accuser}")

    def test_strongest_shown_feeling_goes_first_unless_someone_was_spoken_to(self):
        m = Morning(Oracle(Cache(os.path.join(self.dirs.root, "c.json")), "fake", 1, client=FakeClient()), 1)
        draw = {p: 0.5 for p in data.ORDER}
        m.people["mara"].feeling, m.people["mara"].feeling_until = "scared", 5
        m.people["leo"].feeling, m.people["leo"].feeling_until = "terrified", 5
        m.people["daniel"].feeling, m.people["daniel"].feeling_until = "guilty", 5   # does not show
        self.assertEqual(m.next_to_act(list(data.ORDER), 1, draw),
                         ("leo", "shows the strongest feeling here (terrified)"))
        m.people["daniel"].addressed = {"seq": 3, "who": "elena", "accused": False}
        self.assertEqual(m.next_to_act(list(data.ORDER), 1, draw), ("daniel", "just spoken to by Elena"))
        m.people["mara"].addressed = {"seq": 4, "who": "leo", "accused": True}     # more recent
        self.assertEqual(m.next_to_act(list(data.ORDER), 1, draw), ("mara", "just accused by Leo"))

    def test_ties_are_broken_by_the_seed(self):
        def silent(who, minute, options, client):
            return "silent", None
        orders = {}
        for seed in range(1, 7):
            m, _ = scripted(silent, self.dirs, seed=seed, turns=1)
            orders[seed] = [d["person"] for d in m.log[0]["decisions"]]
            self.assertTrue(all(d["order_reason"] in ("drawn by the seed among equals",
                                                      "the only one left to act here")
                                for d in m.log[0]["decisions"]))
        self.assertGreater(len({tuple(o) for o in orders.values()}), 1)
        again, _ = scripted(silent, self.dirs, seed=3, turns=1)
        self.assertEqual([d["person"] for d in again.log[0]["decisions"]], orders[3])

    # ---- the turn so far ----
    def test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn(self):
        def policy(who, minute, options, client):
            if minute == 0 and client.requests == 1:
                client.first = who
                return "accuse_" + next(o[7:] for o in options if o.startswith("accuse_")), "LINE-ONE"
            if minute == 0 and client.requests == 2:
                return "ask_who" if "ask_who" in options else "say_other", "LINE-TWO"
            return "silent", None
        m, client = scripted(policy, self.dirs, turns=1)
        first, second, third = [p for minute, who, p in client.prompts[:3]]
        self.assertIn("You are the first to act in the kitchen this turn.", first)
        accused = data.PEOPLE[m.log[0]["decisions"][0]["option"][7:]]["name"]
        line_one = f'accuses {accused} of taking it: "LINE-ONE"'
        self.assertIn("Said and done in the kitchen this turn, before you, in order:", second)
        self.assertIn(f"1. {data.PEOPLE[client.first]['name']} {line_one}", second)
        self.assertIn(line_one, third)
        self.assertIn('"LINE-TWO"', third)
        self.assertRegex(third, r"2\. \w+ (asks everyone who took the can|says to everyone): \"LINE-TWO\"")

    # ---- three in a row ----
    def test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again(self):
        def policy(who, minute, options, client):
            if who == "daniel":
                return reassure_or_silent(who, minute, options, client)
            # The others keep the talk going with accusations they have not made before.
            used = client.__dict__.setdefault("used", set())
            fresh = [o for o in options if o.startswith("accuse_") and (who, o) not in used]
            if fresh:
                used.add((who, fresh[0]))
                return fresh[0], "You did it."
            return "silent", None
        m, client = scripted(policy, self.dirs, turns=3)
        dan = m.people["daniel"]
        daniel = [next(d for d in rec["decisions"] if d["person"] == "daniel") for rec in m.log]
        self.assertEqual([d["option"] for d in daniel], ["reassure_all"] * 3)
        # What he would be told and offered at minute 9.
        opts = m.options_for(dan)
        self.assertFalse([o.id for o in opts if o.id.startswith("reassure")])
        prompt = m.prompt_for(dan, 3, opts)
        self.assertIn("you have reassured someone, 3 turns in a row", prompt)
        self.assertNotRegex(prompt, r"(?m)^- reassure_\w+:")
        self.assertIn("In that time:", prompt)
        self.assertRegex(prompt, r"(Nobody answered you differently|Answered you differently from one time)")
        m.turn(3)
        d = next(d for d in m.log[3]["decisions"] if d["person"] == "daniel")
        self.assertEqual(d["held_back"], "reassure")
        self.assertFalse(d["option"].startswith("reassure"))
        # After a turn of something else, it is offered again.
        self.assertIn("reassure_all", {o.id for o in m.options_for(dan)})

    def test_no_speech_act_runs_past_three_turns_in_any_fake_morning(self):
        for seed in range(1, 6):
            m = Morning(Oracle(Cache(os.path.join(self.dirs.root, f"f{seed}.json")), "fake", seed,
                               client=FakeClient(invalid_every=0)), seed).run()
            self.assertLessEqual(metrics.longest_run(m.transcript)[0], 3)

    # ---- talk running out ----
    def test_a_conversation_ends_after_two_full_turns_with_nothing_new(self):
        m, client = scripted(reassure_or_silent, self.dirs, turns=6)
        kitchen = [(minute, what, why) for minute, room, what, why in m.convos.log if room == "kitchen"]
        self.assertEqual(kitchen[:2], [(0, "started", "the count came up short"),
                                       (9, "ended", "2 full turns in a row with nothing new")])
        # After it ended, only inner moments reach the model (Daniel's guilt rose as he was reassured).
        for rec in m.log[3:]:
            for d in rec["decisions"]:
                if d["mode"] != "routine":
                    self.assertTrue(d.get("inner"), d)

    def test_an_inner_moment_can_start_the_talk_again(self):
        def policy(who, minute, options, client):
            if who == "mara" and minute >= 9 and "eat" in options:
                return "eat", None
            return reassure_or_silent(who, minute, options, client)
        m, client = scripted(policy, self.dirs, turns=3)
        self.assertIn((9, "kitchen", "ended", "2 full turns in a row with nothing new"), m.convos.log)
        m.people["mara"].hunger = 0.75                     # she has grown very hungry, alone with it
        m.turn(3)
        d = next(d for d in m.log[3]["decisions"] if d["person"] == "mara")
        self.assertEqual(d["inner"], ["hunger rose (now very hungry)"])
        self.assertEqual(d["option"], "eat")
        self.assertEqual(m.convos.log[-1], (9, "kitchen", "started", "Mara ate one of the portions"))
        self.assertTrue(m.start_by_inner[-1])

    def test_metrics_work_out_the_same_conversations_as_the_morning(self):
        for seed in range(1, 6):
            m = Morning(Oracle(Cache(os.path.join(self.dirs.root, f"g{seed}.json")), "fake", seed,
                               client=FakeClient()), seed).run()
            self.assertEqual([e[:3] for e in metrics.conversations(m.transcript, QUIET_TURNS)],
                             [e[:3] for e in m.convos.log])

    # ---- the prompt's world ----
    def test_the_prompt_gives_forms_of_address_and_the_only_things_in_the_house(self):
        m = Morning(Oracle(Cache(os.path.join(self.dirs.root, "c.json")), "fake", 1, client=FakeClient()), 1)
        for pid in data.ORDER:
            p = m.people[pid]
            prompt = m.prompt_for(p, 0, m.options_for(p))
            self.assertIn(data.HOUSE_THINGS, prompt)
            if pid == "elena":
                self.assertIn('Mara "Mara"', prompt)
            else:
                self.assertIn('Elena "Mom"', prompt)


class PressureTest(unittest.TestCase):
    def setUp(self):
        self.dirs = Dirs()

    def tearDown(self):
        self.dirs.cleanup()

    def morning(self, policy=None):
        client = Scripted(policy or (lambda who, minute, options, c: ("silent", None)))
        return Morning(Oracle(Cache(os.path.join(self.dirs.root, "p.json")), "fake", 1, client=client), 1), client

    # ---- suspicion and grudges ----
    def test_a_grudge_or_suspicion_rises_a_step_and_falls_at_most_a_step_per_15_minutes(self):
        t = Track()
        self.assertEqual([t.report("leo", m) for m in (0, 3, 6, 9)], ["rose", "rose", "rose", "same"])
        self.assertEqual(t.state(), ["leo", 3])
        self.assertEqual(t.report(None, 12), "fell")       # nobody: one step down
        self.assertEqual(t.report(None, 15), "held")       # but not again within 15 minutes
        self.assertEqual(t.report("mara", 24), "held")     # someone else counts as a step down too
        self.assertEqual(t.state(), ["leo", 2])
        self.assertEqual(t.report(None, 27), "fell")
        self.assertEqual(t.report("mara", 30), "held")
        self.assertEqual(t.report("mara", 42), "fell")     # down to 0, and the new name takes it
        self.assertEqual(t.state(), ["mara", 1])

    def test_a_grudge_falls_a_step_only_15_minutes_after_it_last_changed(self):
        g = Grudge()
        for minute in (0, 3, 6):
            g.rise(minute, "x")
        self.assertEqual(g.strength, 3)
        self.assertFalse(g.may_fall(9))        # 3 minutes after it last rose
        self.assertFalse(g.may_fall(18))
        self.assertTrue(g.may_fall(21))        # 15 minutes after
        self.assertFalse(g.may_fall(24))       # and not again for 15 more
        self.assertTrue(g.may_fall(36))
        self.assertEqual(g.strength, 1)

    def test_angry_at_raises_a_grudge_and_nobody_cannot_bring_it_down_faster(self):
        def policy(who, minute, options, client):
            return ("silent", None, "nobody", "Daniel" if minute < 9 else "nobody")
        m, client = self.morning(policy)
        leo = m.people["leo"]
        for t in range(12):                    # minutes 0 to 33
            m.ask_model(leo, t, m.options_for(leo), {})
        # Raised at 0, 3 and 6; "nobody" every 3 minutes after that lets it fall only at 21.
        self.assertEqual(leo.grudges["daniel"].strength, 2)
        prompt = m.prompt_for(leo, 12, m.options_for(leo))
        self.assertIn("Against Daniel (some): you were angry with Daniel at minutes 00, 03 and 06.", prompt)
        self.assertIn("About the can: you have not settled on who took it.", prompt)

    def test_naming_yourself_counts_as_nobody(self):
        m, _ = self.morning(lambda who, minute, options, c: ("silent", None, "Leo", "Leo"))
        leo = m.people["leo"]
        m.ask_model(leo, 0, m.options_for(leo), {})
        self.assertEqual((leo.suspicion.state(), leo.grudges), ([None, 0], {}))

    # ---- grudges from events ----
    def act(self, m, p, option, words="Words.", record=None):
        in_turn(m)
        opt = next(o for o in m.options_for(p) if o.id == option)
        m.apply(p, opt, {"mode": "model", "say": words, "feeling": "tense"}, 1, [], record or new_record())
        out_of_turn(m)

    def test_a_false_accusation_raises_a_grudge_toward_the_accuser(self):
        m, _ = self.morning()
        daniel, elena, leo, mara = (m.people[p] for p in data.ORDER)
        self.act(m, leo, "accuse_mara", "You took it.")
        self.assertEqual(mara.grudges["leo"].strength, 1)
        self.assertEqual(mara.grudges["leo"].events[0][1],
                         "Leo accused you of taking the can at minute 03, and you had not")
        self.act(m, leo, "accuse_daniel", "Or you.")          # true: no grudge
        self.assertNotIn("leo", daniel.grudges)
        prompt = m.prompt_for(mara, 2, m.options_for(mara))
        self.assertIn("Against Leo (a little): Leo accused you of taking the can at minute 03, "
                      "and you had not.", prompt)

    def test_confessing_after_denying_it_and_after_accusing(self):
        m, _ = self.morning()
        daniel, elena, leo, mara = (m.people[p] for p in data.ORDER)
        for q in m.people.values():
            q.heard_question = True
        self.act(m, daniel, "accuse_leo", "Leo did it.")       # Leo: +1, falsely accused
        self.act(m, daniel, "deny", "Not me.")                  # everyone hears him deny it
        self.act(m, daniel, "confess", "It was me.")
        self.assertEqual(leo.grudges["daniel"].strength, 3)     # +1 accused, +1 denied, +1 had accused
        self.assertEqual(elena.grudges["daniel"].strength, 1)   # +1 denied to her
        self.assertEqual(mara.grudges["daniel"].strength, 1)
        facts = [f for _, f, _ in leo.grudges["daniel"].events]
        self.assertEqual(facts, ["Daniel accused you of taking the can at minute 03, and you had not",
                                 "Daniel admitted taking it at minute 03, after denying it to you at minute 03",
                                 "Daniel had accused you of it at minute 03"])

    def test_eating_in_front_of_someone_hungry_raises_a_grudge_but_sharing_does_not(self):
        m, _ = self.morning()
        daniel, elena, leo, mara = (m.people[p] for p in data.ORDER)
        self.act(m, daniel, "eat", None)
        self.assertEqual(elena.grudges["daniel"].strength, 1)  # 0.60: hungry
        self.assertEqual(mara.grudges["daniel"].strength, 1)   # 0.50: hungry
        self.assertNotIn("daniel", leo.grudges)                # 0.45: a little hungry
        self.act(m, elena, "share", None)
        self.assertNotIn("elena", daniel.grudges)
        self.assertNotIn("elena", mara.grudges)

    def test_reassure_is_not_offered_toward_a_grudge_of_3(self):
        m, _ = self.morning()
        mara = m.people["mara"]
        for minute in (0, 3):
            mara.grudge("leo").rise(minute, "x")
        self.assertIn("reassure_leo", {o.id for o in m.options_for(mara)})
        mara.grudge("leo").rise(6, "x")
        ids = {o.id for o in m.options_for(mara)}
        self.assertNotIn("reassure_leo", ids)
        self.assertIn("reassure_daniel", ids)
        self.assertIn("reassure_all", ids)

    # ---- Daniel's guilt ----
    def test_daniels_guilt_rises_by_the_rules(self):
        m, _ = self.morning()
        daniel, elena, leo, mara = (m.people[p] for p in data.ORDER)
        for q in m.people.values():
            q.heard_question = True
        rec = new_record()

        def do(p, option, words):
            in_turn(m)
            opt = next(o for o in m.options_for(p) if o.id == option)
            m.apply(p, opt, {"mode": "model", "say": words, "feeling": "tense"}, 1, [], rec)
            out_of_turn(m)
            return daniel.guilt

        self.assertEqual(daniel.guilt, 1)                                      # he knows what he did
        self.assertEqual(do(daniel, "deny", "Not me."), 1)                    # his denial: nothing
        self.assertEqual(do(mara, "reassure_all", "We'll be fine."), 1)       # everyone: nothing
        self.assertEqual(do(leo, "accuse_daniel", "It was you."), 1)          # he is accused: nothing
        self.assertEqual(do(leo, "accuse_mara", "Or you."), 2)                # someone else, of what he did
        self.assertEqual(do(elena, "reassure_daniel", "It's all right."), 3)  # him personally
        self.assertEqual(do(mara, "reassure_daniel", "Really."), 3)           # never past 3
        self.assertEqual([(g, why) for _, g, why in rec["guilt"]],
                         [(2, "Leo accused Mara of what he did"), (3, "Elena reassured him"),
                          (3, "Mara reassured him")])
        prompt = m.prompt_for(daniel, 2, m.options_for(daniel))
        self.assertIn("On your conscience (a lot): you ate the can in the night, and nobody saw; "
                      "Leo accused Mara of what you did, at minute 03; Elena reassured you, at minute 03; "
                      "Mara reassured you, at minute 03.", prompt)

    def test_daniel_accusing_someone_counts_once(self):
        m, _ = self.morning()
        daniel = m.people["daniel"]
        in_turn(m)
        opt = next(o for o in m.options_for(daniel) if o.id == "accuse_leo")
        m.apply(daniel, opt, {"mode": "model", "say": "Leo did it.", "feeling": "tense"}, 1, [], new_record())
        self.assertEqual(daniel.guilt, 2)       # Leo accused of what he did, in his hearing: once
        self.assertEqual(daniel.guilt_events, [(3, "you accused Leo of what you did, at minute 03")])

    def test_no_prompt_holds_the_old_verdicts(self):
        prompts = []
        for seed in (1, 2, 3):
            client = FakeClient()
            m = Morning(Oracle(Cache(os.path.join(self.dirs.root, f"v{seed}.json")), "fake", seed,
                               client=client), seed).run()
            prompts += [e["prompt"] for e in m.oracle.cache.entries.values()]
        # And one with everything at its highest.
        m, _ = self.morning()
        daniel = m.people["daniel"]
        daniel.guilt = 3
        for t in ("leo", "mara"):
            for minute in (0, 3, 6):
                daniel.grudge(t).rise(minute, "x")
        for minute in (0, 3, 6):
            daniel.suspicion.report("leo", minute)
        daniel.suspected_at = [0, 3, 6]
        prompts.append(m.prompt_for(daniel, 3, m.options_for(daniel)))
        self.assertIn("(a lot)", prompts[-1])
        for p in prompts:
            for phrase in OLD_VERDICTS:
                self.assertNotIn(phrase.lower(), p.lower(), phrase)

    # ---- inner moments ----
    def test_inner_moments_come_at_most_once_every_9_minutes(self):
        def policy(who, minute, options, client):
            return ("silent", None, "nobody", "Leo" if who != "leo" else "Mara")
        m, client = scripted(policy, self.dirs, turns=12)
        inner = {}
        for rec in m.log:
            for d in rec["decisions"]:
                if d.get("inner"):
                    inner.setdefault(d["person"], []).append(rec["minute"])
                    self.assertTrue(all(" rose (now " in x for x in d["inner"]))
        self.assertTrue(any(len(v) >= 3 for v in inner.values()), inner)
        for who, minutes in inner.items():
            self.assertTrue(all(b - a >= 9 for a, b in zip(minutes, minutes[1:])), (who, minutes))
        # Daniel: the grudge he named at 0 rose, so an inner moment at 3, then 12, then 21.
        self.assertEqual(inner["daniel"][:3], [3, 12, 21])
        # Between them his grudge had risen again, but he was not asked.
        self.assertEqual(next(d for d in m.log[2]["decisions"] if d["person"] == "daniel")["mode"], "routine")

    # ---- taking someone aside ----
    def aside(self, answer):
        def policy(who, minute, options, client):
            if "accept_aside" in options:
                return answer, None
            if minute == 0 and client.requests == 1:
                client.taker = who
                client.taken = next(o for o in options if o.startswith("aside_"))[6:]
                return f"aside_{client.taken}", "Come with me a moment."
            return "silent", None
        m, client = scripted(policy, self.dirs, turns=2)
        return m, client, m.people[client.taker], m.people[client.taken]

    def test_take_aside_accepted(self):
        m, client, taker, taken = self.aside("accept_aside")
        own = next(r for r, owners in data.OWNERS.items() if taker.id in owners)
        self.assertEqual((taker.room, taken.room), (own, own))   # the taker's own room was empty
        first = m.log[0]["decisions"]
        self.assertEqual(first[1]["person"], taken.id)
        self.assertEqual(first[1]["order_reason"], f"asked aside by {taker.name}")
        self.assertEqual(first[1]["option"], "accept_aside")
        self.assertEqual(client.asked.count((0, taken.id)), 1)   # their answer is their one decision
        self.assertIn((3, own, "started", f"{taker.name} came in"), m.convos.log)
        there = [d for d in m.log[1]["decisions"] if d["room"] == own]
        self.assertEqual(there[0]["person"], taker.id)
        self.assertEqual(there[0]["order_reason"], f"took {taken.name} aside")
        self.assertTrue(all(d["mode"] == "model" for d in there))  # both are asked, alone together

    def test_take_aside_refused(self):
        m, client, taker, taken = self.aside("refuse_aside")
        self.assertEqual((taker.room, taken.room), ("kitchen", "kitchen"))
        self.assertEqual(m.log[0]["decisions"][1]["option"], "refuse_aside")
        self.assertEqual(client.asked.count((0, taken.id)), 1)
        first = m.log[1]["decisions"][0]
        self.assertEqual((first["person"], first["order_reason"]), (taker.id, f"just spoken to by {taken.name}"))

    def test_take_aside_needs_someone_yet_to_act_and_an_empty_room(self):
        m, _ = self.morning()
        daniel = m.people["daniel"]
        in_turn(m)
        m.acted = {"leo"}
        ids = {o.id for o in m.options_for(daniel)}
        self.assertIn("aside_elena", ids)
        self.assertNotIn("aside_leo", ids)
        for r in ("brothers_room", "back_room", "bathroom"):
            m.present[r] = ["x"]
        self.assertFalse([o for o in m.options_for(daniel) if o.id.startswith("aside_")])


class ScenarioTest(unittest.TestCase):
    def setUp(self):
        self.dirs = Dirs()

    def tearDown(self):
        self.dirs.cleanup()

    def morning(self, scenario, client=None):
        return Morning(Oracle(Cache(os.path.join(self.dirs.root, f"{scenario}.json")), "fake", 1,
                              client=client or FakeClient()), 1, scenario)

    def test_each_scenario_runs_with_the_fake_model(self):
        for scenario in data.SCENARIOS:
            (meta, code), out = fake_morning(self.dirs, seed=1, scenario=scenario)
            self.assertEqual(code, 0, out)
            story = read(os.path.join(self.dirs.runs, f"{scenario}-seed1.md"))
            self.assertIn(f"# The morning as a story: {scenario}, rules and a language model, seed 1", story)
            tr = json.loads(read(os.path.join(self.dirs.runs, f"{scenario}-seed1.transcript.json")))
            self.assertEqual((tr["scenario"], tr["culprit"]), (scenario, data.culprit(scenario)))
            if scenario != data.DEFAULT_SCENARIO:
                self.assertIn(f"`python morning.py --scenario {scenario} --seed 1 --fake`", story)

    def test_the_culprit_comes_from_the_scenario(self):
        for scenario, culprit in (("daniel_ate_it", "daniel"), ("mara_ate_it", "mara"), ("miscount", None)):
            m = self.morning(scenario)
            self.assertEqual(m.culprit, culprit)
            for pid, p in m.people.items():
                ids = {o.id for o in m.options_for(p)}
                night = [x for x in p.backstory if "In the night" in x and "eats a can" in x]
                if pid == culprit:
                    self.assertIn("confess", ids)
                    self.assertNotIn("ask_who", ids)
                    self.assertEqual((p.guilt, p.knows_culprit), (1, pid))
                    self.assertEqual(len(night), 1)
                    self.assertIn("On your conscience (a little)", m.prompt_for(p, 0, m.options_for(p)))
                else:
                    self.assertNotIn("confess", ids)
                    self.assertIn("ask_who", ids)
                    self.assertEqual((p.guilt, p.knows_culprit, night), (None, None, []))
                    self.assertNotIn("On your conscience", m.prompt_for(p, 0, m.options_for(p)))

    def test_in_miscount_every_accusation_is_false(self):
        m = self.morning("miscount")
        leo, daniel = m.people["leo"], m.people["daniel"]
        in_turn(m)
        opt = next(o for o in m.options_for(leo) if o.id == "accuse_daniel")
        m.apply(leo, opt, {"mode": "model", "say": "It was you.", "feeling": "tense"}, 1, [], new_record())
        out_of_turn(m)
        self.assertEqual(daniel.grudges["leo"].strength, 1)
        self.assertIsNone(daniel.guilt)

    def test_mara_as_the_culprit_carries_the_guilt(self):
        m = self.morning("mara_ate_it")
        leo, mara = m.people["leo"], m.people["mara"]
        rec = new_record()
        in_turn(m)
        opt = next(o for o in m.options_for(leo) if o.id == "accuse_daniel")
        m.apply(leo, opt, {"mode": "model", "say": "It was you.", "feeling": "tense"}, 1, [], rec)
        out_of_turn(m)
        self.assertEqual(mara.guilt, 2)
        self.assertEqual(rec["guilt"], [(3, 2, "Leo accused Daniel of what she did")])
        self.assertEqual(m.people["daniel"].grudges["leo"].strength, 1)   # false: Mara took it

    def test_the_story_speaks_of_the_culprit(self):
        (meta, code), _ = fake_morning(self.dirs, seed=1, scenario="mara_ate_it")
        story = read(os.path.join(self.dirs.runs, "mara_ate_it-seed1.md"))
        self.assertIn("- **Mara's guilt** starts at 1 and rises a step when someone else is accused of "
                      "what she did in her hearing (by anyone, herself included), or when someone "
                      "reassures her personally. Her denials", story)
        self.assertIn("| 3 | In the night Mara eats a can sitting on the kitchen floor. Nobody sees. | "
                      "not there | not there | not there | did it |", story)
        (meta, code), _ = fake_morning(self.dirs, seed=1, scenario="miscount")
        story = read(os.path.join(self.dirs.runs, "miscount-seed1.md"))
        self.assertIn("- Nobody took the can: the count was wrong from the start.", story)
        self.assertNotIn("In the night", story.split("## The morning")[0])

    def test_a_second_model_from_the_config(self):
        (meta, code), out = quiet_run(1, config_path=CONFIG, runs_dir=self.dirs.runs, cache_dir=self.dirs.cache,
                                      model_key="gemma", client=FakeClient())
        self.assertEqual(code, 0, out)
        self.assertEqual(meta["model"], "gemma-4-31b-it")
        self.assertTrue(os.path.exists(os.path.join(self.dirs.cache, "gemma-4-31b-it-daniel_ate_it-gemma-seed1.json")))
        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-gemma-seed1.md"))
        self.assertIn("`python morning.py --model gemma --seed 1`", story)
        self.assertIn("the model `gemma-4-31b-it` chooses", story)
        config = {**gemini.load_config(CONFIG), **gemini.load_config(CONFIG)["models"]["gemma"]}
        self.assertEqual((config["model"], config["min_seconds_between_calls"]), ("gemma-4-31b-it", 6.5))


class GeminiClientTest(unittest.TestCase):
    def setUp(self):
        self.old = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = SECRET
        self.dirs = Dirs()
        self.sleeps = []
        self.now = [0.0]

    def tearDown(self):
        if self.old is None:
            os.environ.pop("GEMINI_API_KEY", None)
        else:
            os.environ["GEMINI_API_KEY"] = self.old
        self.dirs.cleanup()

    def client(self, script, **over):
        config = {**gemini.load_config(CONFIG), **over}

        def sleep(s):
            self.sleeps.append(s)
            self.now[0] += s
        return GeminiClient(config, 1, api=StubApi(script), sleep=sleep, clock=lambda: self.now[0])

    def test_missing_key_stops_with_a_clear_message(self):
        os.environ.pop("GEMINI_API_KEY")
        with self.assertRaises(SystemExit) as e:
            gemini.require_api_key()
        self.assertIn("GEMINI_API_KEY is not set", str(e.exception))

    def test_calls_are_spaced(self):
        c = self.client([])
        c.generate(SYSTEM, "- silent: stay put")
        c.generate(SYSTEM, "- silent: stay put")
        self.assertEqual(self.sleeps, [4.5])
        self.assertEqual(c.last_prompt_tokens, 321)

    def test_per_minute_429_backs_off_and_retries(self):
        c = self.client([api_error(429, "RESOURCE_EXHAUSTED", PER_MINUTE),
                         api_error(429, "RESOURCE_EXHAUSTED", PER_MINUTE)])
        text = c.generate(SYSTEM, "- silent: stay put")
        self.assertEqual(json.loads(text)["option"], "silent")
        self.assertEqual(c.requests, 3)
        waits = [s for s in self.sleeps if s > 4.5]
        self.assertEqual(waits, [8.0, 10])     # max(5*2^0, retryDelay 7s + 1), then 5*2^1

    def test_repeated_429_gives_up_cleanly(self):
        c = self.client([api_error(429, "RESOURCE_EXHAUSTED", PER_MINUTE)] * 10, max_retries=2)
        with self.assertRaises(gemini.RateLimited):
            c.generate(SYSTEM, "- silent: stay put")
        self.assertEqual(c.requests, 3)

    def test_daily_quota_stops_keeps_the_cache_and_resumes(self):
        # 3 answers (minute 0 asks all four), then the day's quota is gone.
        script = ["ok"] * 3 + [api_error(429, "RESOURCE_EXHAUSTED", PER_DAY)]
        (meta, code), out = quiet_run(3, config_path=CONFIG, runs_dir=self.dirs.runs,
                                      cache_dir=self.dirs.cache, client=self.client(script))
        self.assertEqual(code, 3)
        self.assertIn("daily request quota", out)
        self.assertIn("To resume, run the same command again", out)
        cache_file = os.path.join(self.dirs.cache, "gemini-3.5-flash-lite-daniel_ate_it-seed3.json")  # noqa
        self.assertEqual(len(json.loads(read(cache_file))), 3)
        # The next day: the same command reuses all 3 and asks only for the rest.
        (meta, code), out = quiet_run(3, config_path=CONFIG, runs_dir=self.dirs.runs,
                                      cache_dir=self.dirs.cache, client=self.client([]))
        self.assertEqual(code, 0, out)
        self.assertEqual(meta["answers_from_cache"], 3)
        self.assertEqual(meta["max_prompt_tokens_counted_by_api"], 321)

    def test_the_key_is_never_printed_or_saved(self):
        (meta, code), out = quiet_run(4, config_path=CONFIG, runs_dir=self.dirs.runs,
                                      cache_dir=self.dirs.cache, client=self.client([]))
        self.assertEqual(code, 0)
        self.assertNotIn(SECRET, out)
        for folder, _, files in os.walk(self.dirs.root):
            for name in files:
                self.assertNotIn(SECRET, read(os.path.join(folder, name)))


if __name__ == "__main__":
    unittest.main()
