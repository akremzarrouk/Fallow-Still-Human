"""Tests against the fake model and a stubbed API. No network, no quota.

    python -m unittest -v test_morning
"""
import contextlib
import difflib
import importlib.util
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import data
import metrics
import gemini
import world
from gemini import Cache, FakeClient, GeminiClient, Oracle
from morning import run
from story import render
from world import (PROMPT_TOKEN_BUDGET, QUIET_TURNS, SYSTEM, Grudge, Morning, Option, Person, Track,
                   estimate_tokens)

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


# The trip concern (reports/trip_design.md): its two lines, the day-2 memories it keeps from
# trimming, and the most its block can add to a prompt (§2.5: 374 estimated tokens at most).
TRIP_FOOD = "About food: there is no food in the house for tomorrow."
TRIP_HOUSE = ("About the neighbour's house: its people left in the first days and nobody has been "
              "inside since, so there may be food there. Outside is dangerous.")
TRIP_DAY2 = ["Daniel says they should cross to the neighbour's house tonight and see what is left there.",
             "Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. "
             "Daniel drops it.",
             "Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his."]
TRIP_BLOCK_MAX = 380
TRIP_IDS = re.compile(r"^(propose_trip|volunteer|object_trip|object_\w+|back_\w+|decline)$")
TRIP_OPTION_LINE = re.compile(r"^- (propose_trip|volunteer|object_\w+|back_\w+|decline): ")


def trip_ids(opts):
    return [o.id for o in opts if TRIP_IDS.match(o.id)]


def without_trip_block(prompt):
    """A prompt without what the trip concern adds to it after the trigger (§2.5): its lines,
    its options, the day-2 memories it keeps, and "this morning" in the house line."""
    if TRIP_FOOD not in prompt:
        return prompt
    out = []
    for line in prompt.split("\n"):
        if line.startswith(("About food:", "About the neighbour's house:", "About going there tonight:")):
            continue
        if TRIP_OPTION_LINE.match(line) or any(line.startswith(f"- Day 2: {s} (") for s in TRIP_DAY2):
            continue
        out.append(line.replace("Outside, and not to be gone to this morning:", "Outside, and not to be gone to:"))
    return "\n".join(out)


def assert_no_target_text(test, prompts):
    """No sentence of target-morning.md (nor its merged copy) is in any of the prompts."""
    target = target_text()
    if target is None:
        test.skipTest("neither target-morning.md nor its copy in understanding-all.md was found")
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
    test.assertGreater(len(pieces), 40)
    for p in prompts:
        for piece in pieces:
            test.assertNotIn(piece.lower(), p.lower(), f"target-morning text in a prompt: {piece!r}")


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
        self.assertGreater(meta["day1"]["model_decisions"], 0)
        self.assertGreater(meta["day1"]["routine_decisions"], 0)

    def test_every_kind_of_broken_answer_falls_back_to_the_rules(self):
        # Every answer broken: the four kinds land at minute 0, where everyone can speak.
        (meta, code), _ = fake_morning(self.dirs, client=FakeClient(invalid_every=1))
        self.assertEqual(code, 0)
        self.assertEqual(meta["day1"]["model_decisions"], 0)
        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed7.md"))
        self.assertGreater(meta["day1"]["fallbacks"], 0)
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
            # The night's and day 2's prompts have their own bounds (reports/night_design.md, §9 T12).
            if "\nNow it is night" in p or CARRY_HEAD in p:
                continue
            # The estimate tracked the API's own count closely in the first runs (1,250 against
            # 1,252); the real counts of the real runs are reported with them. The trip block
            # sits outside the budget (reports/trip_design.md, §2.5).
            self.assertLess(estimate_tokens(SYSTEM + without_trip_block(p)), 1450)
            self.assertLess(estimate_tokens(SYSTEM + p), 1450 + TRIP_BLOCK_MAX)

    def test_nothing_from_target_morning_reaches_a_prompt(self):
        fake_morning(self.dirs)
        assert_no_target_text(self, [SYSTEM] + cached_prompts(self.dirs))

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
            self.assertLess(estimate_tokens(SYSTEM + without_trip_block(prompt)), 1450)
            self.assertLess(estimate_tokens(SYSTEM + prompt), 1450 + TRIP_BLOCK_MAX)
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
            self.assertEqual((tr["day1"]["scenario"], tr["day1"]["culprit"]), (scenario, data.culprit(scenario)))
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


class PromptTruthTest(unittest.TestCase):
    """Every line of a prompt is true for the person reading it."""

    def setUp(self):
        self.dirs = Dirs()

    def tearDown(self):
        self.dirs.cleanup()

    def morning(self, scenario, policy=None):
        client = Scripted(policy or (lambda who, minute, options, c: ("silent", None)))
        return Morning(Oracle(Cache(os.path.join(self.dirs.root, f"{scenario}.json")), "fake", 1,
                              client=client), 1, scenario)

    def test_the_culprit_is_told_they_ate_it_not_that_they_have_not_settled(self):
        for scenario, culprit in (("daniel_ate_it", "daniel"), ("mara_ate_it", "mara")):
            name = data.PEOPLE[culprit]["name"]
            # They name themselves as the one who took it, which counts as nobody.
            m = self.morning(scenario, lambda who, minute, options, c: ("silent", None, name, "nobody"))
            p = m.people[culprit]
            for t in range(20):                # minutes 00 to 57
                m.ask_model(p, t, m.options_for(p), {})
            prompt = m.prompt_for(p, 20, m.options_for(p))
            self.assertIn("About the can: you ate it yourself.", prompt)
            self.assertNotIn("you have not settled on who took it", prompt)

    def test_hearing_a_confession_is_what_they_know_about_the_can(self):
        m = self.morning("mara_ate_it")
        mara = m.people["mara"]
        in_turn(m)
        opt = next(o for o in m.options_for(mara) if o.id == "confess")
        m.apply(mara, opt, {"mode": "model", "say": "It was me.", "feeling": "ashamed"}, 3, [], new_record())
        out_of_turn(m)
        for pid in ("daniel", "elena", "leo"):
            p = m.people[pid]
            prompt = m.prompt_for(p, 20, m.options_for(p))
            self.assertIn("About the can: Mara admitted taking it at minute 09.", prompt)
            self.assertNotIn("you have not settled on who took it", prompt)
        prompt = m.prompt_for(mara, 20, m.options_for(mara))
        self.assertIn("About the can: you ate it yourself.", prompt)

    def test_the_culprit_who_names_someone_else_is_still_told_they_ate_it(self):
        for scenario, culprit in (("daniel_ate_it", "daniel"), ("mara_ate_it", "mara")):
            # Their answers name Leo, which gives them a suspicion of Leo.
            m = self.morning(scenario, lambda who, minute, options, c: ("silent", None, "Leo", "nobody"))
            p = m.people[culprit]
            for t in range(20):                # minutes 00 to 57
                m.ask_model(p, t, m.options_for(p), {})
            self.assertEqual((p.suspicion.target, p.suspicion.strength), ("leo", 3))
            prompt = m.prompt_for(p, 20, m.options_for(p))
            self.assertIn("About the can: you ate it yourself.", prompt)
            self.assertNotIn("you thought", prompt)

    def test_after_hearing_a_confession_a_guess_does_not_replace_it(self):
        # After Mara's confession their answers name someone other than Mara.
        other = {"daniel": "Elena", "elena": "Leo", "leo": "Daniel"}
        m = self.morning("mara_ate_it", lambda who, minute, options, c: ("silent", None, other[who], "nobody"))
        mara = m.people["mara"]
        in_turn(m)
        opt = next(o for o in m.options_for(mara) if o.id == "confess")
        m.apply(mara, opt, {"mode": "model", "say": "It was me.", "feeling": "ashamed"}, 3, [], new_record())
        out_of_turn(m)
        for pid in ("daniel", "elena", "leo"):
            p = m.people[pid]
            for t in range(4, 20):             # minutes 12 to 57
                m.ask_model(p, t, m.options_for(p), {})
            self.assertEqual(p.suspicion.strength, 3, pid)
            prompt = m.prompt_for(p, 20, m.options_for(p))
            self.assertIn("About the can: Mara admitted taking it at minute 09.", prompt)
            self.assertNotIn("you thought", prompt)

    def test_the_opening_says_what_was_seen_in_every_scenario(self):
        seen = ("Elena counts the pantry with everyone standing there. She finds one can fewer than "
                "she expected and says so. 2 portions are left.")
        for scenario in data.SCENARIOS:
            m = self.morning(scenario)
            for pid, p in m.people.items():
                prompt = m.prompt_for(p, 0, m.options_for(p))
                how = "did it" if pid == "elena" else "saw it"
                self.assertIn(f"- min 00: {seen} (you {how})", prompt, (scenario, pid))
                self.assertNotIn("A can that should be on the shelf is not", prompt, (scenario, pid))


def frozen(version, module):
    """vN/<module>.py, loaded on its own (what vN ran)."""
    spec = importlib.util.spec_from_file_location(f"{version}_{module}",
                                                  os.path.join(HERE, version, f"{module}.py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def without_lull(transcript):
    """A transcript as JSON would hold it, without the `lull` key that every act has since v9
    and the `trip_moment` key that every act has since v11."""
    tr = json.loads(json.dumps(transcript))
    for turn in tr["turns"]:
        for a in turn["acts"]:
            a.pop("lull", None)
            a.pop("trip_moment", None)
    return tr


def first_ask_after_speaking(transcript):
    """(minute, person, model answers before it) of the first decision in a saved transcript
    that asked the model for someone who had already spoken that morning."""
    spoke, served = set(), 0
    for turn in transcript["turns"]:
        for a in turn["acts"]:
            if a["mode"] != "routine":
                if a["who"] in spoke:
                    return turn["minute"], a["who"], served
                served += 1
            if a["words"]:
                spoke.add(a["who"])
    return None


V6_RUNS = os.path.join(HERE, "runs", "v6")
V6_CACHE = os.path.join(HERE, "cache", "v6")
V6_MODEL = "gemini-3.5-flash-lite"


class DecisionFormatTest(unittest.TestCase):
    """The decision format is v6's again (reports/belief_line_impl.md): no `thought` in the
    schema, the system instruction, the parser, the fake answers, the story or the transcript."""

    def setUp(self):
        self.dirs = Dirs()
        self.v6_world, self.v6_gemini = frozen("v6", "world"), frozen("v6", "gemini")

    def tearDown(self):
        self.dirs.cleanup()

    def test_the_schema_is_v6s(self):
        self.assertEqual(gemini.RESPONSE_SCHEMA, self.v6_gemini.RESPONSE_SCHEMA)
        self.assertNotIn("thought", json.dumps(gemini.RESPONSE_SCHEMA))

    def test_the_system_instruction_is_v6s(self):
        self.assertEqual(SYSTEM, self.v6_world.SYSTEM)
        self.assertNotIn("thought", SYSTEM)

    def test_the_parser_is_v6s(self):
        base = {"option": "deny", "say": " I  did not. ", "feeling": " Tense ", "reason": "I  wait.",
                "suspects": "leo", "angry_at": "nobody"}
        answers = [base, {**base, "thought": "Someone took it."}, {**base, "thought": ""},
                   {k: v for k, v in base.items() if k != "reason"}, {**base, "option": "silent"},
                   {**base, "say": None}, {**base, "option": "fly"}, {**base, "suspects": "the dog"}]
        texts = ([json.dumps(a) for a in answers]
                 + ["not json", "[1]", "```json\n" + json.dumps(base) + "\n```"])

        def opts(option):
            return [option("silent", "stay put", kind="silent"), option("deny", "deny taking it", True, kind="deny")]
        for text in texts:
            self.assertEqual(Morning.parse(text, opts(Option)),
                             self.v6_world.Morning.parse(text, opts(self.v6_world.Option)), text)

    def test_the_fake_client_answers_as_v6s(self):
        now, then = FakeClient(), self.v6_gemini.FakeClient()
        for i in range(12):
            prompt = f"Your options:\n- silent: stay put\n- deny: (speech) deny taking it\n- search: look\n{i}"
            self.assertEqual(now.generate("", prompt), then.generate("", prompt), i)

    def test_the_story_and_the_transcript_carry_no_thought(self):
        (meta, code), out = fake_morning(self.dirs, seed=1)
        self.assertEqual(code, 0, out)
        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.md"))
        self.assertNotIn("Thought:", story)

        def legend(text):
            return next(x for x in text.splitlines() if x.startswith("- **Chose**"))
        self.assertEqual(legend(story), legend(read(os.path.join(V6_RUNS, "daniel_ate_it-seed1.md"))))

        def keys(path):
            tr = json.loads(read(path))
            tr = tr.get("day1", tr)
            return {k for turn in tr["turns"] for a in turn["acts"] for k in a}
        # v9 adds one key to every act, `lull` (reports/lull_design.md, §3), and v11 another,
        # `trip_moment` (reports/trip_design.md, §4.1). `aside` is an older key, on acts that take
        # someone aside only (world.py, act()); the v6 story had none.
        self.assertEqual(keys(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")) - {"aside"},
                         keys(os.path.join(V6_RUNS, "daniel_ate_it-seed1.transcript.json")) | {"lull", "trip_moment"})

    def test_v6_baseline_pairs_until_someone_who_has_spoken_is_asked(self):
        """The v6 answers carry each morning, unchanged, up to the first prompt of someone who has
        already spoken: from there their own lines show no words (reports/gist_words_impl.md), so
        that prompt is not in the cache. Lulls off, as now."""
        for seed in (1, 2, 3):
            name = f"daniel_ate_it-seed{seed}"
            v6 = json.loads(read(os.path.join(V6_RUNS, name + ".transcript.json")))
            minute, who, served = first_ask_after_speaking(v6)
            path = os.path.join(self.dirs.root, f"{name}.json")
            shutil.copy(os.path.join(V6_CACHE, f"{V6_MODEL}-{name}.json"), path)
            oracle = Oracle(Cache(path), V6_MODEL, seed, client=None, replay=True)
            rec = Recorder(oracle)
            with mock.patch.object(world, "LULL_QUIET", None):
                m = Morning(rec, seed)
                with self.assertRaises(gemini.CacheMiss, msg=f"seed {seed}"):
                    for t in range(m.turns):
                        m.turn(t)
            last = rec.prompts[-1]
            self.assertTrue(last.startswith(f"You are {data.PEOPLE[who]['name']},"), seed)
            self.assertIn(f"\nNow, minute {minute:02d}, you are in the kitchen.\n", last)
            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
            self.assertEqual(without_lull(m.transcript)["turns"],
                             [turn for turn in v6["turns"] if turn["minute"] < minute], seed)
            spoken = [a["words"] for turn in v6["turns"] for a in turn["acts"]
                      if a["who"] == who and a["words"] and turn["minute"] < minute]
            self.assertTrue(spoken, seed)
            for words in spoken:
                self.assertNotIn(words, last, seed)

class PairedOracle:
    """Answers from a saved cache when the prompt is the same as there, as a run paired with it
    would; keeps every prompt, and gives each one it cannot answer a silent answer."""

    def __init__(self, path, model, seed):
        self.entries = json.loads(read(path))
        self.model, self.seed = model, seed
        self.asked, self.missed = [], []

    def ask(self, system, prompt):
        self.asked.append(prompt)
        entry = self.entries.get(Cache.key(self.model, self.seed, system, prompt))
        if entry:
            return entry["response"]
        self.missed.append(prompt)
        return json.dumps({"option": "silent", "say": None, "feeling": "calm", "reason": "Waiting.",
                           "suspects": "nobody", "angry_at": "nobody"})


WITNESS = "daniel_ate_it_leo_heard"
# Where the line was in v6: a backstory event of Leo's (reports/witness_design.md, section 1).
HEARD = ("In the night Leo wakes and hears someone in the kitchen open a can. "
         "He does not get up and does not see who.")
# Where it was in v7: what he heard, at the end of his "About the can:" line (witness_probe.md, B).
OLD_NOTE = "Last night you woke and heard someone in the kitchen open a can; you did not see who."
# Now: what he heard and what follows from it, in the same place (reports/belief_line_impl.md).
NOTE = ("Last night you woke and heard someone open a can in the kitchen, so someone in this house "
        "took it in the night. You did not see who.")
CAN_LINE = "About the can: you have not settled on who took it."
BELIEF_LINE = ("About the can: you have not settled on who took it. Last night you woke and heard someone "
               "open a can in the kitchen, so someone in this house took it in the night. You did not see who.")


class WitnessScenarioTest(unittest.TestCase):
    """daniel_ate_it_leo_heard: daniel_ate_it, and Leo heard the night but did not see who
    (reports/witness_design.md, sections 1 to 3). What he heard, and that it means someone in
    the house took the can, is told in his "About the can:" line, not in his backstory."""

    def setUp(self):
        self.assertIn(WITNESS, data.SCENARIOS)
        self.dirs = Dirs()

    def tearDown(self):
        self.dirs.cleanup()

    def morning(self, scenario, seed):
        return Morning(Oracle(Cache(os.path.join(self.dirs.root, f"{scenario}-{seed}.json")), "fake", seed,
                              client=FakeClient()), seed, scenario)

    def fake_prompts(self):
        for seed in (1, 2, 3):
            (meta, code), out = fake_morning(self.dirs, seed=seed, scenario=WITNESS)
            self.assertEqual(code, 0, out)
        prompts = cached_prompts(self.dirs)
        self.assertTrue(prompts)
        return prompts

    # T1
    def test_the_sentence_names_nobody_leo_heard(self):
        self.assertEqual(data.about_the_can(WITNESS, "leo"), NOTE)
        self.assertEqual(CAN_LINE + " " + NOTE, BELIEF_LINE)
        for name in ("Daniel", "Elena", "Leo", "Mara"):
            self.assertNotIn(name, NOTE)
        self.assertEqual(set(re.findall(r"\b[A-Z]\w*", NOTE)), {"Last", "You"})
        self.assertNotIn("eats a can", NOTE)

    # T2
    def test_no_backstory_differs(self):
        for pid in data.ORDER:
            self.assertEqual(Person(pid, WITNESS).backstory, Person(pid, "daniel_ate_it").backstory, pid)
        self.assertEqual(data.backstory(WITNESS), data.backstory("daniel_ate_it"))
        self.assertFalse([x for x in Person("leo", WITNESS).backstory
                          if "Daniel eats" in x or HEARD in x or NOTE in x])

    # T3
    def test_at_minute_00_only_leos_prompt_differs_by_his_can_line(self):
        for seed in (1, 2, 3):
            old, new = self.morning("daniel_ate_it", seed), self.morning(WITNESS, seed)
            for pid in data.ORDER:
                p, q = old.people[pid], new.people[pid]
                self.assertEqual(q.sure, p.sure, (seed, pid))
                self.assertEqual([o.id for o in new.options_for(q)], [o.id for o in old.options_for(p)], (seed, pid))
                a = old.prompt_for(p, 0, old.options_for(p))
                b = new.prompt_for(q, 0, new.options_for(q))
                if pid != "leo":
                    self.assertEqual(b, a, (seed, pid))
                    continue
                diff = list(difflib.ndiff(a.splitlines(), b.splitlines()))
                self.assertEqual([d for d in diff if d.startswith("+ ")], ["+ " + BELIEF_LINE], seed)
                self.assertEqual([d for d in diff if d.startswith("- ")], ["- " + CAN_LINE], seed)

    # T4
    def test_daniels_prompt_never_mentions_being_heard(self):
        daniel = [p for p in self.fake_prompts() if p.startswith("You are Daniel,")]
        self.assertTrue(daniel)
        for p in daniel:
            for words in (NOTE, OLD_NOTE, HEARD, "woke and heard", "wakes and hears", "open a can",
                          "did not see who", "does not see who", "heard someone",
                          "someone in this house took it"):
                self.assertNotIn(words, p)
            if "On your conscience" in p:
                self.assertIn("and nobody saw", p)
        self.assertTrue([p for p in daniel if "On your conscience" in p])

    # T5
    def test_no_prompt_says_who_leo_heard(self):
        prompts = self.fake_prompts()
        leo = [p for p in prompts if p.startswith("You are Leo,")]
        self.assertTrue(leo)
        for p in prompts:
            self.assertNotIn(HEARD, p)
            self.assertNotIn(OLD_NOTE, p)
            if p.startswith("You are Leo,"):
                # The note ends his one "About the can" line, whatever that line says before it.
                lines = [x for x in p.splitlines() if NOTE in x]
                self.assertEqual(len(lines), 1)
                self.assertTrue(lines[0].endswith(" " + NOTE), lines[0])
                self.assertEqual([x for x in p.splitlines() if x.startswith("About the can")], lines)
                # Day 2's forms say "yesterday", "last night" or "this morning" (reports/night_design.md, §5.3).
                self.assertRegex(lines[0][:-len(" " + NOTE)],
                                 r"^About the can(: you have not settled on who took it\."
                                 r"| \([a-z ]+\): you thought \w+ took it, at minutes? [\d, and]+\."
                                 r"| \([a-z ]+\): you thought \w+ took it(, (and )?(yesterday at minutes? [\d, and]+"
                                 r"|last night|this morning at minutes? [\d, and]+))*\."
                                 r"|: \w+ admitted taking it( yesterday,)? at minute \d\d\.)$")
                for words in ("Daniel eats a can", "you ate it yourself", "On your conscience"):
                    self.assertNotIn(words, p)
            else:
                self.assertNotIn(NOTE, p)
            # The can being opened is told only in the note, which names nobody (T1).
            self.assertNotIn("open a can", p.replace(NOTE, ""))

    # T6
    def test_nothing_from_target_morning_reaches_a_prompt_of_the_witness_morning(self):
        assert_no_target_text(self, [SYSTEM] + self.fake_prompts())

    # T7
    def test_the_other_scenarios_do_not_have_the_sentence(self):
        lengths = {"daniel_ate_it": 13, "mara_ate_it": 13, "miscount": 12, WITNESS: 13}
        self.assertEqual({s: len(data.backstory(s)) for s in data.SCENARIOS}, lengths)
        for scenario in data.SCENARIOS:
            self.assertFalse([e for e in data.backstory(scenario) if HEARD in e[1] or NOTE in e[1]], scenario)
            for pid in data.ORDER:
                note = data.about_the_can(scenario, pid)
                self.assertEqual(note, NOTE if (scenario, pid) == (WITNESS, "leo") else None, (scenario, pid))

    # T8
    def test_the_witness_morning_runs_and_its_story_shows_who_heard(self):
        (meta, code), out = fake_morning(self.dirs, seed=1, scenario=WITNESS)
        self.assertEqual(code, 0, out)
        story = read(os.path.join(self.dirs.runs, f"{WITNESS}-seed1.md"))
        self.assertIn("| Knows about the can | ate it in the night; nobody saw | only that it is missing | "
                      f"only that it is missing; told: “{NOTE}” | only that it is missing |", story)
        self.assertNotIn(HEARD, story)
        (meta, code), out = fake_morning(self.dirs, seed=1)
        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.md"))
        self.assertIn("| Knows about the can | ate it in the night; nobody saw | only that it is missing | "
                      "only that it is missing | only that it is missing |", story)

    # T9
    def test_leos_minute_00_prompt_loses_no_line_with_the_v6_answers(self):
        """Paired with the v6 baseline answers, as a witness run would be (design §4, R3), Leo's
        first prompt differs from his daniel_ate_it one by the can line alone and fits the budget."""
        for seed in (1, 2, 3):
            prompts = {}
            for scenario in ("daniel_ate_it", WITNESS):
                oracle = PairedOracle(os.path.join(V6_CACHE, f"{V6_MODEL}-daniel_ate_it-seed{seed}.json"),
                                      V6_MODEL, seed)
                Morning(oracle, seed, scenario).turn(0)
                if scenario == "daniel_ate_it":
                    self.assertEqual(oracle.missed, [], seed)
                leo = [p for p in oracle.asked if p.startswith("You are Leo,")]
                self.assertEqual(len(leo), 1, (seed, scenario))
                prompts[scenario] = leo[0]
            old, new = prompts["daniel_ate_it"], prompts[WITNESS]
            diff = [d for d in difflib.ndiff(old.splitlines(), new.splitlines()) if d[:2] in ("+ ", "- ")]
            self.assertEqual(diff, ["- " + CAN_LINE, "+ " + BELIEF_LINE], seed)
            self.assertNotIn("(earlier things, left out here)", new, seed)
            self.assertLessEqual(estimate_tokens(SYSTEM + new), PROMPT_TOKEN_BUDGET, seed)


LULL_LINE = re.compile(r"^Nothing has been said or done in the (kitchen|brothers room|back room|bathroom) "
                       r"since minute (\d\d)\.$", flags=re.M)
HUNGRIER = "Since you last decided, you have grown hungrier."
# Lull moments are off (world.LULL_QUIET is None, reports/lulls_off.md). The tests that switch
# them on themselves use the design's value (reports/lull_design.md, §1).
DESIGN_LULL_QUIET = 9


class Recorder:
    """Passes each question on to an oracle, and keeps every prompt in the order it was asked."""

    def __init__(self, oracle):
        self.oracle, self.prompts = oracle, []

    def ask(self, system, prompt):
        self.prompts.append(prompt)
        return self.oracle.ask(system, prompt)


class Watched(Morning):
    """Keeps, for every decision, whether it was a lull and whether its room was talking then."""

    def decide(self, p, t):
        d = super().decide(p, t)
        self.__dict__.setdefault("at_decision", []).append((t, p.id, d.get("lull"), self.talking(p.room)))
        return d


class Broken:
    requests = 0

    def generate(self, system, prompt):
        self.requests += 1
        return "not json"


def asked(m):
    """The decisions the model was asked for, in the order they were asked."""
    return [d for rec in m.log for d in rec["decisions"] if d["mode"] != "routine"]


def longest_alone_routine(transcript):
    """P3's count (reports/lull_design.md, §7): the longest run of turns, for any one person, in
    which they start the turn alone in a room and act by routine."""
    best, run = 0, {}
    for turn in transcript["turns"]:
        for a in turn["acts"]:
            alone = turn["rooms"][a["room"]] == [a["who"]]
            run[a["who"]] = run.get(a["who"], 0) + 1 if alone and a["mode"] == "routine" else 0
            best = max(best, run[a["who"]])
    return best


class LullTest(unittest.TestCase):
    """Lull moments (reports/lull_design.md, sections 1 to 3; tests T1 to T11 of section 5).
    They are off (reports/lulls_off.md): the tests that do not switch them on themselves check
    that nothing comes of them."""

    def setUp(self):
        self.dirs = Dirs()

    def tearDown(self):
        self.dirs.cleanup()

    def fake(self, seed, lulls=True):
        """A fake-model morning; with lulls=True, lull moments are switched on at the design's 9
        minutes, and with lulls=False, off."""
        rec = Recorder(Oracle(Cache(os.path.join(self.dirs.root, f"f{seed}-{lulls}.json")), "fake", seed,
                              client=FakeClient()))
        with mock.patch.object(world, "LULL_QUIET", DESIGN_LULL_QUIET if lulls else None):
            m = Watched(rec, seed).run()
        return m, rec

    def still_kitchen(self, client=None):
        """Everyone in the kitchen, no talk, no triggers, nothing risen since they last decided."""
        client = client or Scripted(lambda *a: ("silent", None))
        m = Morning(Oracle(Cache(os.path.join(self.dirs.root, "still.json")), "fake", 1, client=client), 1)
        m.convos.active["kitchen"] = False
        for p in m.people.values():
            p.triggers = []
            p.seen = p.levels()
        return m

    # T1
    def test_t1_the_numbers(self):
        self.assertEqual((world.LULL_QUIET, world.LULL_EVERY), (None, 12))

    def test_t1a_off_a_room_still_for_9_minutes_gives_no_lull(self):
        m = self.still_kitchen()
        mara = m.people["mara"]
        m.last_stir["kitchen"], mara.last_asked = 6, 3          # minute 15: still for 9, not asked for 12
        self.assertFalse(m.lull_due(mara, 15))
        d = m.decide(mara, 5)
        self.assertEqual(d["mode"], "routine")
        self.assertNotIn("lull", d)
        self.assertEqual(mara.last_asked, 3)

    def test_t1b_off_never_asked_in_a_room_still_all_morning_gives_no_lull(self):
        m = self.still_kitchen()
        mara = m.people["mara"]
        m.last_stir["kitchen"], mara.last_asked = 0, None       # minute 87: still for 87, never asked
        self.assertFalse(m.lull_due(mara, 87))
        d = m.decide(mara, 29)
        self.assertEqual(d["mode"], "routine")
        self.assertNotIn("lull", d)
        self.assertIsNone(mara.last_asked)

    def test_t1c_a_social_trigger_comes_first(self):
        m = self.still_kitchen()
        mara = m.people["mara"]
        m.last_stir["kitchen"] = 0
        mara.triggers = [("Elena says to everyone: \"Sit down.\"", True)]
        d = m.decide(mara, 5)
        self.assertEqual((d["mode"], d["triggers"]), ("model", ['Elena says to everyone: "Sit down."']))
        self.assertNotIn("lull", d)

    def test_t1d_an_inner_moment_comes_first(self):
        m = self.still_kitchen()
        mara = m.people["mara"]
        m.last_stir["kitchen"], mara.last_inner = 0, 3
        mara.hunger = 0.9                                       # risen since she last decided
        d = m.decide(mara, 5)
        self.assertEqual(d["inner_kinds"], ["hunger"])
        self.assertNotIn("lull", d)

    def test_t1e_t9_off_alone_after_leaving_no_lull_asks_him(self):
        """Leo goes to the back room at minute 0 and then stays silent: with lulls off, nothing
        asks him at 12 (routine at 3, 6, 9 and 12); his leaving is no trigger for the others."""
        def policy(who, minute, options, client):
            return ("go_back_room", None) if (who, minute) == ("leo", 0) else ("silent", None)
        m, client = scripted(policy, self.dirs)
        self.assertEqual(m.people["leo"].room, "back_room")
        leo = [(rec["minute"], d) for rec in m.log for d in rec["decisions"] if d["person"] == "leo"]
        self.assertEqual([(minute, d["mode"]) for minute, d in leo[1:5]],
                         [(3, "routine"), (6, "routine"), (9, "routine"), (12, "routine")])
        self.assertFalse([d for rec in m.log for d in rec["decisions"] if d.get("lull") is not None])
        self.assertFalse([p for _, _, p in client.prompts if "Nothing has been said or done in the" in p])
        self.assertGreaterEqual(longest_alone_routine(m.transcript), 4)
        # T9: the others were told he left, and it was no trigger for them.
        for pid in ("daniel", "elena", "mara"):
            self.assertIn((0, "Leo leaves for the back room."), m.people[pid].memory)
        for rec in m.log[:2]:
            for d in rec["decisions"]:
                self.assertFalse([x for x in d["triggers"] if "leaves for" in x], d)

    def test_t1f_carrying_on_searching_stirs_the_room(self):
        def policy(who, minute, options, client):
            return ("search", None) if (who, minute) == ("mara", 0) else ("silent", None)
        m, _ = scripted(policy, self.dirs, turns=4)
        self.assertEqual([d["option"] for d in m.log[1]["decisions"] if d["person"] == "mara"],
                         ["keep_searching"])
        self.assertEqual(m.last_stir["kitchen"], 3)
        self.assertFalse([d for rec in m.log for d in rec["decisions"] if d.get("lull") is not None])

    def test_t1g_t1h_sitting_down_stirs_staying_seated_and_silence_do_not(self):
        m = self.still_kitchen()
        dan = m.people["daniel"]
        m.last_stir["kitchen"] = 0

        def do(option, t, mode):
            in_turn(m)
            opt = next(o for o in m.options_for(dan) if o.id == option)
            m.apply(dan, opt, {"mode": mode, "say": None, "feeling": "calm"}, t, [], new_record())
            out_of_turn(m)
        do("sit_mara", 4, "model")                              # sits down: minute 12
        self.assertEqual(m.last_stir["kitchen"], 12)
        do("sit_mara", 5, "routine")                            # stays seated
        do("silent", 6, "model")                                # a model's silence
        do("silent", 7, "routine")
        self.assertEqual(m.last_stir["kitchen"], 12)
        in_turn(m)
        opt = next(o for o in m.options_for(dan) if o.id == "reassure_all")
        m.apply(dan, opt, {"mode": "model", "say": "It will be all right.", "feeling": "calm"}, 8, [],
                new_record())
        self.assertEqual(m.last_stir["kitchen"], 24)            # a line stirs it

    def test_t1i_a_fallback_counts_as_asked(self):
        m = self.still_kitchen(client=Broken())
        mara = m.people["mara"]
        m.last_stir["kitchen"] = 0
        mara.triggers = [("Elena asks everyone who took the can", True)]   # lulls are off: a trigger asks
        d = m.decide(mara, 5)
        self.assertEqual(d["mode"], "fallback")
        self.assertNotIn("lull", d)
        self.assertEqual(mara.last_asked, 15)

    # T2
    def test_t2_a_still_room_is_never_talking(self):
        lulls = 0
        for seed in range(1, 6):
            m, _ = self.fake(seed)
            for t, pid, lull, talking in m.at_decision:
                if lull is not None:
                    lulls += 1
                    self.assertFalse(talking, (seed, t, pid))
        self.assertGreater(lulls, 0)

    # T3, T7
    def test_t3_t7_the_line_is_in_lull_prompts_only_in_its_place(self):
        lulls = 0
        for seed in range(1, 6):
            m, rec = self.fake(seed)
            decisions = asked(m)
            self.assertEqual(len(decisions), len(rec.prompts), seed)
            for d, prompt in zip(decisions, rec.prompts):
                if d.get("lull") is None:
                    self.assertNotIn("Nothing has been said or done in the", prompt)
                    continue
                lulls += 1
                self.assertEqual(LULL_LINE.findall(prompt), [(data.ROOMS[d["room"]], f"{d['lull']:02d}")])
                self.assertEqual(prompt.count("Nothing has been said or done in the"), 1)
                lines = prompt.splitlines()
                i = next(k for k, x in enumerate(lines) if LULL_LINE.match(x))
                self.assertRegex(lines[i - 1], r"^(- |Now, minute \d\d, you are in the )")
                self.assertRegex(lines[i + 1], r"^(Said and done in the |You are the first to act in the |"
                                               r"What you have been doing: |Your options:)")
                self.assertTrue(any(x.startswith("Now, minute ") for x in lines[:i]))
                self.assertNotIn(HUNGRIER, prompt)                        # T7
        self.assertGreater(lulls, 0)

    # T4
    def test_t4_nothing_else_in_the_prompt_changes(self):
        # Leo's first prompt has the most room under the budget (1,324 estimated tokens at minute 12).
        m = Morning(Oracle(Cache(os.path.join(self.dirs.root, "t4.json")), "fake", 1, client=FakeClient()), 1)
        leo = m.people["leo"]
        opts = m.options_for(leo)
        plain, lull = m.prompt_for(leo, 4, opts), m.prompt_for(leo, 4, opts, 0)
        diff = [x for x in difflib.ndiff(plain.splitlines(), lull.splitlines()) if x[:2] in ("+ ", "- ")]
        self.assertEqual(diff, ["+ Nothing has been said or done in the kitchen since minute 00."])
        self.assertLessEqual(estimate_tokens(SYSTEM + lull), PROMPT_TOKEN_BUDGET)
        for prompt in (plain, lull):
            self.assertNotIn("(earlier things, left out here)", prompt)
        self.assertEqual(plain.split("Your options:")[1], lull.split("Your options:")[1])

    # T5
    def test_t5_nothing_changes_before_the_first_lull(self):
        lulls = 0
        for seed in range(1, 6):
            off, rec_off = self.fake(seed, lulls=False)
            on, rec_on = self.fake(seed)
            first = next((i for i, p in enumerate(rec_on.prompts) if "Nothing has been said or done in the" in p),
                         len(rec_on.prompts))
            lulls += first < len(rec_on.prompts)
            self.assertEqual(rec_on.prompts[:first], rec_off.prompts[:first], seed)
            acts_on = [a for turn in on.transcript["turns"] for a in turn["acts"]]
            acts_off = [a for turn in off.transcript["turns"] for a in turn["acts"]]
            self.assertTrue(all(a["lull"] is None for a in acts_off), seed)
            j = next((k for k, a in enumerate(acts_on) if a["lull"] is not None), len(acts_on))
            strip = lambda acts: [{k: v for k, v in a.items() if k != "lull"} for a in acts[:j]]
            self.assertEqual(strip(acts_on), strip(acts_off), seed)
        self.assertGreater(lulls, 0)

    # T6
    def test_t6_off_no_lull_in_a_whole_morning_on_the_v6_answers(self):
        """With lulls off, a whole morning on the v6 answers (a silent answer wherever a prompt is
        not in the v6 cache, as own lines now show no words) has no lull line and no lull act.
        With lulls on, the v6 answers met their first lull at min 42, 51 and 15."""
        for seed in (1, 2, 3):
            oracle = PairedOracle(os.path.join(V6_CACHE, f"{V6_MODEL}-daniel_ate_it-seed{seed}.json"),
                                  V6_MODEL, seed)
            m = Morning(oracle, seed).run()
            self.assertEqual(len(m.transcript["turns"]), m.turns, seed)
            self.assertFalse([p for p in oracle.asked if "Nothing has been said or done in the" in p], seed)
            self.assertTrue(all(a["lull"] is None for turn in m.transcript["turns"] for a in turn["acts"]))

    # T8 on fake mornings
    def test_t8_nobody_is_alone_more_than_3_turns_without_being_asked(self):
        for seed in range(1, 6):
            m, _ = self.fake(seed)
            self.assertLessEqual(longest_alone_routine(m.transcript), 3, seed)

    # T10
    def test_t10_off_no_lull_is_recorded(self):
        for seed in (1, 2, 3):
            (meta, code), out = fake_morning(self.dirs, seed=seed)
            self.assertEqual(code, 0, out)
            tr = json.loads(read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.transcript.json")))["day1"]
            self.assertTrue(all("lull" in a and a["lull"] is None for turn in tr["turns"] for a in turn["acts"]))
            self.assertEqual(meta["day1"]["lull_moments"], 0, seed)
            story = read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.md"))
            self.assertNotIn("**Lull**, nothing said or done in the ", story)
            self.assertIn("lull_moments: 0", out)

    # T11
    def test_t11_v8_still_replays(self):
        env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        done = subprocess.run([sys.executable, os.path.join(HERE, "v8", "check.py")], cwd=HERE, env=env,
                              capture_output=True, text=True, timeout=300)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(done.stdout.count("story IDENTICAL, transcript IDENTICAL"), 3, done.stdout)


OWN_BLOCK_LINE = re.compile(r'^(- min \d\d, you [^:"]+): ".*"$')
OWN_MEMORY_LINE = re.compile(r'^(- min \d\d: you [^:"]+): ".*"\.(.*)$')


def without_own_words(prompt):
    """A prompt as the code before gist words wrote it, with the person's own lines turned into
    what they are now: minute and verb, no words; memory keeps "You felt ..."."""
    out = []
    for line in prompt.splitlines():
        line = OWN_BLOCK_LINE.sub(r"\1.", line)
        line = OWN_MEMORY_LINE.sub(r"\1.\2", line)
        out.append(line)
    return out


class OwnWordsTest(unittest.TestCase):
    """A person's own spoken lines reach their later prompts without the words, as variant B of
    reports/repetition_probe.md: in "Your own last words this morning:" and in memory, minute and
    verb only (memory keeps "You felt <feeling>."). Other people's lines keep their words."""

    def setUp(self):
        self.dirs = Dirs()

    def tearDown(self):
        self.dirs.cleanup()

    def fake(self, seed, module=world, tag="new"):
        rec = Recorder(Oracle(Cache(os.path.join(self.dirs.root, f"{tag}{seed}.json")), "fake", seed,
                              client=FakeClient()))
        m = module.Morning(rec, seed)
        for t in range(m.turns):
            m.turn(t)
        return m, rec

    def test_own_words_never_appear_in_their_later_prompts(self):
        checked = 0
        for seed in range(1, 6):
            m, rec = self.fake(seed)
            decisions = [(r["minute"], d) for r in m.log for d in r["decisions"] if d["mode"] != "routine"]
            self.assertEqual(len(decisions), len(rec.prompts), seed)
            said = {p: [] for p in data.ORDER}
            for (minute, d), prompt in zip(decisions, rec.prompts):
                for words in said[d["person"]]:
                    self.assertNotIn(words, prompt, (seed, minute, d["person"]))
                    checked += 1
                if d.get("say"):
                    said[d["person"]].append(d["say"])
        self.assertGreater(checked, 0)

    def test_own_lines_keep_minute_verb_and_feeling_and_others_keep_their_words(self):
        def policy(who, minute, options, client):
            if minute == 0 and client.requests == 1:
                client.first = who
                return "reassure_all", "FIRST-WORDS"
            if minute == 0 and client.requests == 2:
                client.second = who
                return f"reassure_{client.first}", "SECOND-WORDS"
            return "silent", None
        m, client = scripted(policy, self.dirs, turns=2)
        second = data.PEOPLE[client.second]["name"]
        later = [p for minute, who, p in client.prompts if (minute, who) == (3, client.first)]
        self.assertEqual(len(later), 1)              # just reassured, so asked at minute 3
        prompt = later[0]
        self.assertNotIn("FIRST-WORDS", prompt)
        self.assertIn("\nYour own last words this morning:\n- min 00, you reassured everyone.\n", prompt)
        self.assertIn("\n- min 00: you reassured everyone. You felt tense.\n", prompt)
        self.assertIn(f'\n- min 00: {second} reassures you: "SECOND-WORDS"\n', prompt)
        # The second, if asked at 3, sees the first's words and not their own.
        for minute, who, p in client.prompts:
            if (minute, who) == (3, client.second):
                self.assertIn('"FIRST-WORDS"', p)
                self.assertNotIn("SECOND-WORDS", p)
                self.assertIn(f"- min 00, you reassured {data.PEOPLE[client.first]['name']}.", p)

    def test_others_words_still_reach_the_prompt(self):
        seen = 0
        for seed in range(1, 6):
            m, rec = self.fake(seed)
            decisions = [(r["minute"], d) for r in m.log for d in r["decisions"] if d["mode"] != "routine"]
            said = []
            for (minute, d), prompt in zip(decisions, rec.prompts):
                seen += sum(1 for who, words in said if who != d["person"] and f'"{words}"' in prompt)
                if d.get("say"):
                    said.append((d["person"], d["say"]))
        self.assertGreater(seen, 0)

    def test_prompts_before_someone_has_spoken_are_unchanged(self):
        """Against the frozen v9 code, with the same fake model: the same prompts up to the first
        prompt of someone who has already spoken, and that one differs only in their own lines,
        which lose their words (and, being shorter, may let the trimming keep an older memory or
        backstory line, world.py prompt_for). The trip concern is off on the new side: v9 has
        none, and in seed 5 it starts at minute 03, the turn compared (reports/trip_impl.md)."""
        old_world = frozen("v9", "world")
        for seed in range(1, 6):
            old, old_rec = self.fake(seed, old_world, "old")
            with mock.patch.object(world, "TRIP_ON", False):
                new, new_rec = self.fake(seed)
            decisions = [d for r in old.log for d in r["decisions"] if d["mode"] != "routine"]
            spoke = set()
            for i, d in enumerate(decisions):
                if d["person"] in spoke:
                    break
                self.assertEqual(new_rec.prompts[i], old_rec.prompts[i], (seed, i))
                if d.get("say"):
                    spoke.add(d["person"])
            else:
                self.fail(f"seed {seed}: nobody who had spoken was asked again")
            a, b = old_rec.prompts[i], new_rec.prompts[i]
            self.assertNotEqual(a, b, seed)
            expected, got = without_own_words(a), b.splitlines()
            missing = [x for x in expected if x not in got and x != "- (earlier things, left out here)"]
            extra = [x for x in got if x not in expected]
            self.assertEqual(missing, [], seed)
            self.assertTrue(all(x.startswith(("- min ", "- Day ")) for x in extra), (seed, extra))


V10_RUNS = os.path.join(HERE, "runs", "v10")
V10_CACHE = os.path.join(HERE, "cache", "v10")


def silent(*a):
    return "silent", None


def run_check(version):
    env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, os.path.join(HERE, version, "check.py")], cwd=HERE, env=env,
                          capture_output=True, text=True, timeout=600)


def strip_trip_moment(acts):
    return [{k: v for k, v in a.items() if k != "trip_moment"} for a in acts]


class TripTest(unittest.TestCase):
    """The second concern: whether someone goes to the neighbour's house tonight
    (reports/trip_design.md, sections 1 to 4; tests T1 to T13 of section 8)."""

    def setUp(self):
        self.dirs = Dirs()

    def tearDown(self):
        self.dirs.cleanup()

    def still(self, policy=silent, seed=1):
        """A morning after its first turn, everyone silent at minute 00."""
        m, client = scripted(policy, self.dirs, seed=seed, turns=1)
        return m, client

    def triggered(self, seed=1):
        """A morning whose concern started at minute 03, from the empty shelf."""
        m, client = self.still(seed=seed)
        m.portions = 0
        m.turn(1)
        self.assertIsNotNone(m.trip)
        return m, client

    def act(self, m, p, option, words, t=2):
        in_turn(m)
        opt = next((o for o in m.options_for(p) if o.id == option), None)
        self.assertIsNotNone(opt, f"{option} not offered to {p.id}: {[o.id for o in m.options_for(p)]}")
        out = m.apply(p, opt, {"mode": "model", "say": words, "feeling": "tense"}, t, [], new_record())
        out_of_turn(m)
        return out

    def fake(self, seed, on=True):
        rec = Recorder(Oracle(Cache(os.path.join(self.dirs.root, f"trip{seed}-{on}.json")), "fake", seed,
                              client=FakeClient()))
        with mock.patch.object(world, "TRIP_ON", on):
            m = Morning(rec, seed).run()
        return m, rec

    # T1
    def test_t1_the_numbers(self):
        self.assertEqual((world.TRIP_HUNGER, world.TRIP_ON), (2, True))
        self.assertEqual(data.TRIP_MEMORIES, tuple(TRIP_DAY2))

    def test_t1a_an_empty_shelf_at_a_turns_start_asks_everyone_in_the_kitchen(self):
        m, _ = self.still()
        self.assertIsNone(m.trip)
        m.portions = 0
        m.turn(1)
        self.assertEqual(m.trip, {"minute": 3, "why": ["the shelf is empty"], "asked": list(data.ORDER)})
        moments = {d["person"]: d for d in m.log[1]["decisions"] if d.get("trip_moment") is not None}
        self.assertEqual(set(moments), set(data.ORDER))
        for d in moments.values():
            self.assertEqual((d["trip_moment"], d["mode"]), (3, "model"))

    def test_t1b_one_person_very_hungry_asks_only_them(self):
        m, _ = self.still()
        m.people["mara"].hunger = 0.72
        m.turn(1)
        self.assertEqual(m.trip, {"minute": 3, "why": ["Mara is very hungry"], "asked": ["mara"]})
        self.assertEqual([d["person"] for d in m.log[1]["decisions"] if d.get("trip_moment") is not None],
                         ["mara"])

    def test_t1c_both_at_once(self):
        m, _ = self.still()
        m.portions = 0
        m.people["leo"].room = "back_room"
        m.people["leo"].hunger = 0.75
        m.turn(1)
        self.assertEqual(m.trip, {"minute": 3, "why": ["the shelf is empty", "Leo is very hungry"],
                                  "asked": ["daniel", "elena", "leo", "mara"]})

    def test_t1d_a_shelf_emptied_during_a_turn_fires_at_the_next(self):
        def policy(who, minute, options, client):
            return ("eat", None) if minute == 0 and who in ("daniel", "leo") and "eat" in options else ("silent", None)
        m, _ = scripted(policy, self.dirs, turns=1)
        self.assertEqual(m.portions, 0)
        self.assertIsNone(m.trip)
        m.turn(1)
        self.assertEqual((m.trip["minute"], m.trip["why"]), (3, ["the shelf is empty"]))

    def test_t1e_hungry_is_not_enough(self):
        m, _ = scripted(silent, self.dirs, turns=6)               # minutes 00 to 15
        self.assertEqual(world.hunger_level(m.people["daniel"].hunger), 1)
        self.assertIsNone(m.trip)
        self.assertFalse([p for _, _, p in m.oracle.client.prompts if TRIP_FOOD in p])

    def test_t1f_it_fires_once(self):
        m, _ = self.still()
        m.people["mara"].hunger = 0.72
        m.turn(1)
        before = json.loads(json.dumps(m.trip))
        m.portions = 0
        for p in m.people.values():
            p.hunger = 0.9
        m.turn(2)
        m.turn(3)
        self.assertEqual(m.trip, before)
        self.assertFalse([d for rec in m.log[2:] for d in rec["decisions"] if d.get("trip_moment") is not None])

    def test_t1g_the_can_neither_brings_it_on_nor_holds_it_back(self):
        def policy(who, minute, options, client):
            if minute == 0 and who == "daniel":
                return "confess", "It was me."
            for o in options:
                if o.startswith("accuse_"):
                    return o, "You did it.", "Daniel", "Daniel"
            return "silent", None
        m, _ = scripted(policy, self.dirs, turns=5)
        self.assertTrue(m.people["daniel"].confessed)
        self.assertIsNone(m.trip)
        m.people["leo"].hunger = 0.72
        m.turn(5)
        self.assertEqual(m.trip, {"minute": 15, "why": ["Leo is very hungry"], "asked": ["leo"]})

    # T2
    def test_t2_nothing_changes_before_the_trigger(self):
        for seed in range(1, 6):
            off, rec_off = self.fake(seed, on=False)
            on, rec_on = self.fake(seed)
            self.assertIsNone(off.trip, seed)
            self.assertIsNotNone(on.trip, seed)
            first = next(i for i, p in enumerate(rec_on.prompts) if TRIP_FOOD in p)
            self.assertEqual(rec_on.prompts[:first], rec_off.prompts[:first], seed)
            T = on.trip["minute"]
            before = lambda m: [a for turn in m.transcript["turns"] if turn["minute"] < T for a in turn["acts"]]
            self.assertEqual(strip_trip_moment(before(on)), strip_trip_moment(before(off)), seed)
            self.assertTrue(all(a["trip_moment"] is None for a in before(on)), seed)

    # T3
    def test_t3_the_v10_caches_pair_up_to_the_trigger(self):
        expected = {1: (24, None, 22), 2: (30, "Elena", 20), 3: (30, "Elena", 23)}
        for seed, (minute, who, served) in expected.items():
            name = f"daniel_ate_it-seed{seed}"
            path = os.path.join(self.dirs.root, f"{name}.json")
            shutil.copy(os.path.join(V10_CACHE, f"{V6_MODEL}-{name}.json"), path)
            oracle = Oracle(Cache(path), V6_MODEL, seed, client=None, replay=True)
            rec = Recorder(oracle)
            m = Morning(rec, seed)
            with self.assertRaises(gemini.CacheMiss, msg=f"seed {seed}"):
                for t in range(m.turns):
                    m.turn(t)
            last = rec.prompts[-1]
            self.assertIn(f"\nNow, minute {minute:02d}, you are in the kitchen.\n", last, seed)
            self.assertIn(TRIP_FOOD, last, seed)
            if who:
                self.assertTrue(last.startswith(f"You are {who},"), seed)
            self.assertEqual(m.trip["minute"], minute, seed)
            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
            v10 = json.loads(read(os.path.join(V10_RUNS, name + ".transcript.json")))
            self.assertEqual(without_lull(m.transcript)["turns"],
                             without_lull({"turns": [t for t in v10["turns"] if t["minute"] < minute]})["turns"],
                             seed)

    # T4
    def test_t4_the_lines_exactly_and_only_after_the_trigger(self):
        post = 0
        for seed in (1, 2, 3):
            m, rec = self.fake(seed)
            minutes = [rec_["minute"] for rec_ in m.log for d in rec_["decisions"] if d["mode"] != "routine"]
            self.assertEqual(len(minutes), len(rec.prompts), seed)
            for minute, prompt in zip(minutes, rec.prompts):
                if minute < m.trip["minute"]:
                    for words in ("About food:", "neighbour's house:", "About going there tonight:",
                                  "to be gone to this morning:"):
                        self.assertNotIn(words, prompt, (seed, minute))
                    continue
                post += 1
                lines = prompt.split("\n")
                self.assertEqual(lines.count(TRIP_FOOD), 1)
                self.assertEqual(lines.count(TRIP_HOUSE), 1)
                i = lines.index(TRIP_FOOD)
                self.assertTrue(lines[i - 1].startswith("About the can"), lines[i - 1])
                self.assertEqual(lines[i + 1], TRIP_HOUSE)
                self.assertIn("Outside, and not to be gone to this morning: the street and the neighbour's house.",
                              prompt)
                self.assertNotIn("Outside, and not to be gone to: ", prompt)
        self.assertGreater(post, 0)

    def test_t4_the_plan_line_as_each_person_heard_it(self):
        m, _ = self.triggered()
        dan, ele, leo, mara = (m.people[p] for p in data.ORDER)
        for p in m.people.values():
            self.assertNotIn("About going there tonight:", m.prompt_for(p, 2, m.options_for(p)))
        mara.room = "back_room"
        self.act(m, dan, "volunteer", "I'll go.", t=2)
        self.act(m, leo, "object_trip", "Nobody goes.", t=3)
        self.act(m, ele, "back_leo", "Leo should go.", t=4)
        self.act(m, dan, "object_leo", "Not Leo.", t=5)
        self.act(m, leo, "decline", "Not me.", t=6)
        self.act(m, dan, "propose_trip", "Someone must go.", t=7)

        def line(p):
            return next((x for x in m.prompt_for(p, 8, m.options_for(p)).split("\n")
                         if x.startswith("About going there tonight:")), None)
        self.assertEqual(line(leo), "About going there tonight: Elena said you should go (min 12); "
                                    "you said you will not go (min 18); Daniel said someone should go (min 21).")
        self.assertEqual(line(ele), "About going there tonight: you said Leo should go (min 12); "
                                    "Leo said he will not go (min 18); Daniel said someone should go (min 21).")
        self.assertIsNone(line(mara))           # in the back room: heard nothing of it
        self.act(m, ele, "volunteer", "Then I will.", t=8)
        self.assertEqual(line(dan), "About going there tonight: Leo said he will not go (min 18); "
                                    "you said someone should go (min 21); Elena offered to go (min 24).")
        self.act(m, dan, "object_elena", "Not you, Mom.", t=9)
        self.act(m, leo, "object_trip", "Nobody.", t=10)
        self.assertEqual(line(ele), "About going there tonight: you offered to go (min 24); "
                                    "Daniel said you should not go (min 27); Leo said nobody should go (min 30).")

    # T5
    def test_t5_the_day2_memories_are_kept_after_the_trigger(self):
        filler = [(0, f"filler line number {i} " + "about nothing much at all " * 12) for i in range(200)]
        fresh, _ = self.still()
        fresh.people["elena"].memory += filler
        before = fresh.prompt_for(fresh.people["elena"], 2, fresh.options_for(fresh.people["elena"]))
        self.assertIn("(earlier things, left out here)", before)
        days = [x for x in before.split("\n") if x.startswith("- Day ")]
        self.assertEqual(len(days), 4)
        self.assertFalse([x for x in days if x.startswith("- Day 2:")])
        m, _ = self.triggered()
        m.people["elena"].memory += filler
        after = m.prompt_for(m.people["elena"], 2, m.options_for(m.people["elena"]))
        self.assertIn("(earlier things, left out here)", after)
        days = [x for x in after.split("\n") if x.startswith("- Day ")]
        self.assertEqual(days[:3], [f"- Day 2: {s} (you saw it)" for s in TRIP_DAY2])
        self.assertEqual(days[3:], [x for x in before.split("\n") if x.startswith("- Day ")])
        # Daniel and Leo keep them too, with what they did.
        dan = m.people["daniel"]
        dan.memory += filler
        days = [x for x in m.prompt_for(dan, 2, m.options_for(dan)).split("\n") if x.startswith("- Day 2:")]
        self.assertEqual(days, [f"- Day 2: {TRIP_DAY2[0]} (you did it)", f"- Day 2: {TRIP_DAY2[1]} (you saw it)",
                                f"- Day 2: {TRIP_DAY2[2]} (you did it)"])

    # T6
    def test_t6_when_each_option_is_offered(self):
        fresh, _ = self.still()
        for p in fresh.people.values():
            self.assertEqual(trip_ids(fresh.options_for(p)), [], p.id)
        m, _ = self.triggered()
        dan, ele, leo, mara = (m.people[p] for p in data.ORDER)
        ids = [o.id for o in m.options_for(dan)]
        self.assertEqual(trip_ids(m.options_for(dan)),
                         ["propose_trip", "volunteer", "back_elena", "back_leo", "back_mara"])
        start = ids.index("propose_trip")
        self.assertEqual(ids[start - 1], "reassure_all")
        self.assertEqual(ids[start + 5], "say_other")
        # Alone: none.
        ele.room = "back_room"
        self.assertEqual(trip_ids(m.options_for(ele)), [])
        ele.room = "kitchen"
        self.act(m, dan, "propose_trip", "Someone has to go.")
        self.assertNotIn("propose_trip", trip_ids(m.options_for(dan)))
        self.assertIn("object_trip", trip_ids(m.options_for(dan)))        # made a proposal: may now object
        self.assertEqual(trip_ids(m.options_for(leo)),
                         ["propose_trip", "volunteer", "object_trip", "back_daniel", "back_elena", "back_mara"])
        self.act(m, dan, "volunteer", "I'll go.", t=3)
        self.assertEqual(trip_ids(m.options_for(dan)),
                         ["object_trip", "back_elena", "back_leo", "back_mara", "decline"])
        self.assertEqual(trip_ids(m.options_for(leo)),
                         ["propose_trip", "volunteer", "object_trip", "back_daniel", "back_elena", "back_mara",
                          "object_daniel"])
        self.act(m, dan, "decline", "No, not me.", t=4)
        self.assertEqual(trip_ids(m.options_for(dan)),
                         ["volunteer", "object_trip", "back_elena", "back_leo", "back_mara"])
        self.assertNotIn("object_daniel", trip_ids(m.options_for(leo)))
        self.act(m, mara, "back_daniel", "Daniel should go.", t=5)
        self.assertIn("object_daniel", trip_ids(m.options_for(leo)))
        self.assertNotIn("back_daniel", trip_ids(m.options_for(mara)))
        self.assertIn("back_leo", trip_ids(m.options_for(mara)))
        self.assertNotIn("decline", trip_ids(m.options_for(dan)))         # already his position
        self.act(m, leo, "object_daniel", "Not Daniel.", t=6)
        self.assertNotIn("object_daniel", trip_ids(m.options_for(leo)))
        self.act(m, ele, "back_mara", "Mara should go.", t=7)
        self.assertIn("decline", trip_ids(m.options_for(mara)))           # backed in her hearing
        # No option is ever the person's current position.
        for p in m.people.values():
            pos = p.trip_heard.get(p.id)
            if pos:
                kind, target = pos[1], pos[2]
                current = {"propose": "propose_trip", "volunteer": "volunteer", "decline": "decline",
                           "object": f"object_{target}" if target else "object_trip",
                           "back": f"back_{target}"}[kind]
                self.assertNotIn(current, trip_ids(m.options_for(p)), p.id)

    # T7
    def test_t7_what_each_option_does(self):
        m, _ = self.triggered()
        dan, ele, leo, mara = (m.people[p] for p in data.ORDER)
        mara.room = "back_room"
        state = lambda: json.dumps({p.id: [p.hunger, p.guilt, p.suspicion.state(), p.heard_question,
                                           p.knows_culprit, p.room, {t: g.strength for t, g in p.grudges.items()}]
                                    for p in m.people.values()} | {"portions": m.portions})
        before = state()
        said = [
            (dan, "propose_trip", "W1", "Daniel says someone should go to the neighbour's house tonight",
             "you said someone should go to the neighbour's house tonight.", ("propose", None), True, "a proposal"),
            (leo, "volunteer", "W2", "Leo offers to go to the neighbour's house tonight",
             "you offered to go there tonight.", ("volunteer", None), True, "an offer to go"),
            (ele, "object_trip", "W3", "Elena says nobody should go out tonight",
             "you said nobody should go out tonight.", ("object", None), True, "an objection"),
            (ele, "object_leo", "W4", "Elena says {Leo} should not be the one to go",
             "you said Leo should not be the one to go.", ("object", "leo"), True, "an objection"),
            (dan, "back_leo", "W5", "Daniel says {Leo} should be the one to go",
             "you said Leo should be the one to go.", ("back", "leo"), True, "backing someone to go"),
            (leo, "decline", "W6", "Leo says he will not be the one to go",
             "you said you will not be the one to go.", ("decline", None), True, "a refusal to go"),
            (leo, "volunteer", "W7", "Leo offers to go to the neighbour's house tonight",
             "you offered to go there tonight.", ("volunteer", None), False, "an offer to go they had made before"),
        ]
        for t, (p, option, words, gist, own, pos, new, why) in enumerate(said, start=2):
            minute = t * 3
            self.act(m, p, option, words, t=t)
            for q in (dan, ele, leo):
                if q is p:
                    continue
                g = gist.replace("{Leo}", "you" if q is leo else "Leo")
                self.assertIn((minute, f'{g}: "{words}"'), q.memory, (option, q.id))
                self.assertEqual(q.trip_heard[p.id][:3], (minute,) + pos, (option, q.id))
            self.assertIn(f"min {minute:02d}, {own}", p.said_lines)
            self.assertIn((minute, f"{own[:-1]}. You felt tense."), p.memory)
            self.assertNotIn(words, "\n".join(x for _, x in p.memory))
            self.assertEqual(m.trip_acts[-1], (minute, p.id, pos[0], pos[1], words))
            self.assertEqual(p.trip_heard[p.id][:3], (minute,) + pos)
            self.assertEqual((m.said[-1]["new"], m.said[-1]["why"]), (new, why), option)
            self.assertNotIn(p.id, mara.trip_heard)                   # the back room heard no words
            if pos[1]:
                self.assertEqual(m.people[pos[1]].addressed["who"], p.id)
        self.assertEqual(state(), before)
        self.assertTrue(dan.proposed)
        self.assertFalse(ele.proposed)
        # Nobody ever leaves the house.
        for seed in range(1, 6):
            mm, _ = self.fake(seed)
            for turn in mm.transcript["turns"]:
                for a in turn["acts"]:
                    self.assertIn(a["moved_to"], [None] + list(data.ROOMS), (seed, a))

    def test_t7_talk_kinds(self):
        from talk import SPEECH, Newness, act_of, aimed_at
        self.assertTrue({"propose", "volunteer", "object", "back", "decline"} <= set(SPEECH))
        self.assertEqual([act_of(x) for x in ("propose_trip", "volunteer", "object_trip", "object_leo",
                                              "back_mara", "decline")],
                         [("propose", None), ("volunteer", None), ("object", None), ("object", "leo"),
                          ("back", "mara"), ("decline", None)])
        self.assertEqual([aimed_at(x) for x in ("propose_trip", "object_trip", "object_leo", "back_mara", "decline")],
                         [None, None, "leo", "mara", None])
        n = Newness()
        self.assertEqual(n.line("leo", "object_daniel", []), (True, "an objection"))
        self.assertEqual(n.line("leo", "object_mara", []), (True, "an objection"))
        self.assertEqual(n.line("leo", "object_daniel", []), (False, "an objection they had made before"))
        self.assertEqual(n.line("leo", "back_mara", []), (True, "backing someone to go"))
        self.assertEqual(n.line("leo", "back_mara", []), (False, "backing someone to go they had made before"))
        self.assertEqual(n.line("mara", "propose_trip", []), (True, "a proposal"))
        self.assertEqual(n.line("mara", "propose_trip", []), (False, "a proposal they had made before"))
        self.assertEqual(n.line("mara", "decline", []), (True, "a refusal to go"))
        self.assertEqual(n.line("mara", "decline", []), (False, "a refusal to go they had made before"))
        for kind, done in (("propose", "said someone should go to the neighbour's house tonight"),
                           ("volunteer", "offered to go there tonight"), ("object", "said someone should not go"),
                           ("back", "said someone should be the one to go"),
                           ("decline", "said you will not be the one to go")):
            self.assertEqual(world.KIND_DONE[kind], done)

    def test_t7_heard_verbs_in_the_pattern_block(self):
        m, _ = self.triggered()
        dan, leo = m.people["daniel"], m.people["leo"]
        verbs = [m.heard_verb({"kind": k, "target": tgt}, dan) for k, tgt in
                 (("propose", None), ("volunteer", None), ("object", None), ("object", "daniel"),
                  ("back", "daniel"), ("decline", None))]
        self.assertEqual(verbs, ["said someone should go to the neighbour's house tonight", "offered to go there tonight",
                                 "said nobody should go", "said you should not be the one to go",
                                 "said you should be the one to go", "said they will not be the one to go"])

    # T8
    def test_t8_no_link_in_code(self):
        m, _ = self.triggered()
        dan, ele, leo, mara = (m.people[p] for p in data.ORDER)

        def can_ids(p):
            return [o.id for o in m.options_for(p) if not TRIP_IDS.match(o.id)]
        before = {p.id: can_ids(p) for p in m.people.values()}
        self.act(m, dan, "volunteer", "I'll go.")
        self.act(m, leo, "back_daniel", "Daniel goes.", t=3)
        self.act(m, ele, "object_daniel", "Not Daniel.", t=4)
        self.act(m, mara, "object_trip", "Nobody goes.", t=5)
        self.assertEqual({p.id: can_ids(p) for p in m.people.values()}, before)
        trip_before = {p.id: trip_ids(m.options_for(p)) for p in m.people.values()}
        dan.confessed = True
        for p in m.people.values():
            p.heard_question = True
            p.knows_culprit, p.confession_heard_at = "daniel", 15
            p.suspicion.target, p.suspicion.strength = "daniel", 3
            if p is not dan:
                p.grudge("daniel").rise(15, "something", "event")
        self.assertEqual({p.id: trip_ids(m.options_for(p)) for p in m.people.values()}, trip_before)
        texts = [TRIP_FOOD, TRIP_HOUSE, m.plan_text()] + [world.KIND_DONE[k] for k in
                                                          ("propose", "volunteer", "object", "back", "decline")]
        texts += [o.label for p in m.people.values() for o in m.options_for(p) if TRIP_IDS.match(o.id)]
        texts += [x for p in m.people.values() for x in m.prompt_for(p, 6, m.options_for(p)).split("\n")
                  if x.startswith("About going there tonight:")]
        for text in texts:
            self.assertFalse(re.search(r"\b(can|took|guilt)\b", text), text)

    # T9
    def test_t9_the_plan_line(self):
        m, _ = self.still()
        self.assertEqual(m.plan_text(), "no plan")
        m.trip = {"minute": 30, "why": ["Elena is very hungry"], "asked": ["elena"]}
        self.assertEqual(m.plan_text(), "no plan")
        cases = [
            ([(33, "daniel", "volunteer", None), (36, "mara", "back", "daniel"), (39, "elena", "object", None)],
             "Daniel will go; Mara wants Daniel to go; Elena is against anyone going"),
            ([(33, "leo", "propose", None), (36, "mara", "object", "leo")],
             "nobody has offered to go; Leo said someone should go; Mara is against Leo going"),
            ([(33, "daniel", "volunteer", None), (36, "leo", "volunteer", None)],
             "Daniel and Leo have both offered to go"),
            ([(33, "daniel", "volunteer", None), (36, "leo", "volunteer", None), (39, "mara", "volunteer", None)],
             "Daniel, Leo and Mara have all offered to go"),
            ([(33, "elena", "back", "leo"), (36, "leo", "decline", None)],
             "nobody has offered to go; Elena wants Leo to go; Leo will not go"),
            ([(33, "daniel", "volunteer", None), (39, "daniel", "object", None)],
             "nobody has offered to go; Daniel is against anyone going"),
        ]
        for acts, plan in cases:
            m.trip_acts = [(minute, who, kind, target, "words") for minute, who, kind, target in acts]
            self.assertEqual(m.plan_text(), plan, acts)

    def test_t9_the_story_ends_with_the_food_and_the_plan(self):
        m, _ = self.still()
        m.finish()
        story = render(m, 1, "fake", "python morning.py --seed 1")
        self.assertIn("\n- The food: never came up.\n- The plan for tonight: no plan.\n", story)
        m, _ = self.still()
        m.people["elena"].hunger = 0.72
        m.turn(1)
        self.act(m, m.people["daniel"], "volunteer", "I'll go.")
        m.finish()
        story = render(m, 1, "fake", "python morning.py --seed 1")
        self.assertIn("\n- The food: came up at minute 03 (Elena is very hungry); asked then: Elena.\n"
                      "- The plan for tonight: Daniel will go.\n", story)
        m, _ = self.triggered()
        m.finish()
        story = render(m, 1, "fake", "python morning.py --seed 1")
        self.assertIn("\n- The food: came up at minute 03 (the shelf is empty); asked then: Daniel, Elena, Leo, "
                      "Mara.\n", story)

    # T10
    def test_t10_recording(self):
        acts_seen = 0
        for seed in (1, 2, 3):
            (meta, code), out = fake_morning(self.dirs, seed=seed)
            self.assertEqual(code, 0, out)
            tr = json.loads(read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.transcript.json")))["day1"]
            story = read(os.path.join(self.dirs.runs, f"daniel_ate_it-seed{seed}.md"))
            story = story[:story.index("# The night\n")]
            meta = meta["day1"]
            self.assertEqual(meta["trip_minute"], tr["trip"]["minute"])
            acts = [a for turn in tr["turns"] for a in turn["acts"]]
            trips = [a for a in acts if TRIP_IDS.match(a["option"])]
            self.assertEqual(meta["trip_acts"], len(trips))
            self.assertEqual(tr["trip"]["acts"], [[a["minute"], a["who"], a["option"], a["words"]] for a in trips])
            acts_seen += len(trips)
            moments = [(turn["minute"], a) for turn in tr["turns"] for a in turn["acts"]
                       if a.get("trip_moment") is not None]
            self.assertTrue(moments, seed)
            for minute, a in moments:
                self.assertEqual((minute, a["trip_moment"]), (tr["trip"]["minute"],) * 2)
                self.assertIn(a["mode"], ("model", "fallback"))
                self.assertIn(a["who"], tr["trip"]["asked"])
            self.assertEqual(story.count("**The food**: "), len(moments), seed)
            self.assertIn(f"- The plan for tonight: {tr['trip']['plan']}.", story)
            self.assertIn(f"trip_minute: {meta['trip_minute']}", out)
            self.assertIn(f"trip_acts: {meta['trip_acts']}", out)
        self.assertGreater(acts_seen, 0)

    # T11
    def test_t11_nothing_from_target_morning_reaches_a_prompt_after_the_trigger(self):
        prompts = []
        for seed in (1, 2, 3):
            _, rec = self.fake(seed)
            prompts += [p for p in rec.prompts if TRIP_FOOD in p]
        self.assertTrue(prompts)
        assert_no_target_text(self, prompts)

    # T12
    def test_t12_the_block_sits_outside_the_budget(self):
        filler = [(0, f"filler line number {i} " + "about nothing much at all " * 12) for i in range(200)]
        m, _ = self.triggered()
        self.act(m, m.people["daniel"], "volunteer", "I'll go.")
        ele = m.people["elena"]
        ele.memory += filler
        with_trip = m.prompt_for(ele, 3, m.options_for(ele))
        trip, m.trip = m.trip, None
        plain = m.prompt_for(ele, 3, m.options_for(ele))
        m.trip = trip

        def morning_lines(prompt):
            lines = prompt.split("\n")
            return lines[lines.index("What else happened this morning, most recent last:"):
                         next(i for i, x in enumerate(lines) if x.startswith("Now, minute"))]
        self.assertIn("- (earlier things, left out here)", morning_lines(plain))
        self.assertEqual(morning_lines(with_trip), morning_lines(plain))
        self.assertEqual(without_trip_block(with_trip), plain)
        self.assertLessEqual(estimate_tokens(SYSTEM + without_trip_block(with_trip)), PROMPT_TOKEN_BUDGET)
        self.assertGreater(estimate_tokens(SYSTEM + with_trip), PROMPT_TOKEN_BUDGET)
        self.assertLess(estimate_tokens(SYSTEM + with_trip), 1450 + TRIP_BLOCK_MAX)

    # T13
    def test_t13_v10_and_v9_still_replay(self):
        for version in ("v10", "v9"):
            done = run_check(version)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertEqual(done.stdout.count("story IDENTICAL, transcript IDENTICAL"), 3, done.stdout)
            self.assertIn("0 API calls", done.stdout)


V11_RUNS = os.path.join(HERE, "runs", "v11")
V11_CACHE = os.path.join(HERE, "cache", "v11")
V11_SERVED = {1: 55, 2: 53, 3: 45}
NIGHT_SYSTEM_TEXT = (
    "You decide what one person in a family does tonight. You get who they are, what they remember, what they "
    "know now, and the options open to them. They know only what is in their memory. Choose exactly one option "
    "id from the list. If the option is marked (speech), `say` must hold the exact words they say, in a low "
    "voice, in their own voice, one or two short sentences. For any other option `say` is null. `feeling` names "
    "what they feel right now in one or two words. `reason` is their reason in one sentence, as they would think "
    "it. `suspects` is who they now believe took the can, and `angry_at` is who they are angry with right now: "
    "each is one of \"Daniel\", \"Elena\", \"Leo\", \"Mara\" or \"nobody\". Reply with JSON only: "
    '{"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", '
    '"suspects": "<name or nobody>", "angry_at": "<name or nobody>"}')
BEDTIME_OPTIONS = ("Your options:\n"
                   "- sleep: go to sleep\n"
                   "- lie_awake: lie awake in your bed and listen\n"
                   "- watch_door: sit up in the kitchen by the front door until morning, so nobody goes out "
                   "without you knowing\n"
                   "- go_next_door: wait until the others are asleep, then go out by the front door to the "
                   "neighbour's house")
GAP = "The afternoon and evening passed in the house. Nobody ate."
CARRY_HEAD = "Yesterday and last night:"
CARRY_MAX = 360
DAY2_TRIP_IDS = re.compile(r"^(propose_trip|volunteer|still_going|send_\w+|nobody_goes|keep_\w+_home|refuse_to_go)$")
FATE = re.compile(r"\b(dead|die[sd]?|dying|kill\w*|hurt|wound\w*|blood\w*|corpse|injur\w*|bit(e|ten)|attack\w*|"
                  r"taken)\b", flags=re.I)
# Nobody wakes, and the house and the street are quiet, when Daniel goes (night_design.md §3.3 draws).
QUIET = {"wake:daniel:leo": 0.9, "door:daniel:leo": 0.9, "door:daniel:elena": 0.9, "door:daniel:mara": 0.9,
         "return:daniel:leo": 0.9,
         "return:daniel:elena": 0.9, "return:daniel:mara": 0.9, "house": 0.1, "trip:daniel": 0.1}


class NightScripted:
    """A model for the night and day 2. prefs[who] lists option ids in order of preference: the
    first one offered is chosen, with words if it is speech. Otherwise the first option of the
    night (sleep, let them go, stay in bed, go anyway), or `silent` by day."""

    def __init__(self, prefs=None, angry=None):
        self.prefs, self.angry = prefs or {}, angry or {}
        self.requests = 0
        self.prompts = []           # (minute or "night", who, prompt)

    def generate(self, system, prompt):
        self.requests += 1
        who = re.match(r"You are (\w+),", prompt).group(1).lower()
        m = re.search(r"^Now, minute (\d+)", prompt, flags=re.M)
        where = int(m.group(1)) if m else "night"
        block = prompt.split("Your options:")[-1]
        options = re.findall(r"^- (\w+):", block, flags=re.M)
        speech = set(re.findall(r"^- (\w+): \(speech\)", block, flags=re.M))
        self.prompts.append((where, who, prompt))
        choice = next((o for o in self.prefs.get(who, []) if o in options),
                      "silent" if "silent" in options else options[0])
        return json.dumps({"option": choice, "say": f"Words of {who} {self.requests}." if choice in speech else None,
                           "feeling": "tense", "reason": "Scripted.", "suspects": "nobody",
                           "angry_at": self.angry.get(who, "nobody")})

    def night_prompts(self, who=None):
        return [p for w, x, p in self.prompts if w == "night" and (who is None or x == who)]


def now_lines(prompt):
    """The night's `Now` lines: from "Now it is night" to "Your options:"."""
    lines = prompt.split("\n")
    end = lines.index("Your options:")
    start = max(i for i, x in enumerate(lines[:end]) if x.startswith("Now it is night"))
    return lines[start:end]


def option_lines(prompt):
    return prompt.split("Your options:\n")[-1].split("\n")


def without_blocks(prompt):
    """A day-2 or night prompt without its trip block and its carry-in block."""
    out, skipping = [], False
    for line in prompt.split("\n"):
        if line == CARRY_HEAD:
            skipping = True
            continue
        if skipping and line.startswith("- "):
            continue
        skipping = False
        if line.startswith(("About food:", "About the neighbour's house:", "About going there tonight:")):
            continue
        if (TRIP_OPTION_LINE.match(line)
                or re.match(r"^- (still_going|send_\w+|nobody_goes|keep_\w+_home|refuse_to_go): ", line)
                or any(line.startswith(f"- Day 2: {s} (") for s in TRIP_DAY2)):
            continue
        out.append(line.replace("Outside, and not to be gone to this morning:", "Outside, and not to be gone to:"))
    return "\n".join(out)


def not_pairs(labels):
    """Pairs of labels whose word sets differ only by "not" or "n't"."""
    def words(x):
        return set(re.findall(r"[\w']+", x.lower().replace("n't", " not"))) - {"not"}
    return [(a, b) for i, a in enumerate(labels) for b in labels[i + 1:] if a != b and words(a) == words(b)]


class NightTest(unittest.TestCase):
    """Time passing: the night after day 1, and day 2 (reports/night_design.md, sections 1 to 8;
    tests T1 to T14 of section 9)."""

    def setUp(self):
        self.dirs = Dirs()
        self.night = importlib.import_module("night")

    def tearDown(self):
        self.dirs.cleanup()

    def path(self, tag):
        return os.path.join(self.dirs.root, f"{tag}-{len(os.listdir(self.dirs.root))}.json")

    def v11_day1(self, seed, client=None):
        """Day 1 of seed N from a copy of its v11 cache; the night and day 2 go to `client`."""
        path = self.path(f"v11-{seed}")
        shutil.copy(os.path.join(V11_CACHE, f"{V6_MODEL}-daniel_ate_it-seed{seed}.json"), path)
        oracle = Oracle(Cache(path), V6_MODEL, seed, client=client, replay=client is None)
        return Morning(oracle, seed).run(), oracle

    def short_day1(self, client, seed=1):
        """A day 1 of one silent turn (minute 00), everyone in the kitchen; then `client` answers."""
        oracle = Oracle(Cache(self.path(f"short-{seed}")), "fake", seed, client=NightScripted())
        m = Morning(oracle, seed)
        m.turn(0)
        m.finish()
        oracle.client = client
        return m, oracle

    def night_of(self, prefs, draws=None, seed=1, angry=None):
        client = NightScripted(prefs, angry)
        day1, oracle = self.short_day1(client, seed)
        n = self.night.Night(day1, oracle, draws=draws or {}).run()
        return day1, n, client, oracle

    def asked(self, n, ask=None):
        return [(d["person"], d["ask"]) for d in n.decisions if ask is None or d["ask"] == ask]

    def act(self, m, p, option, words, t=0):
        in_turn(m)
        opt = next((o for o in m.options_for(p) if o.id == option), None)
        self.assertIsNotNone(opt, f"{option} not offered to {p.id}: {[o.id for o in m.options_for(p)]}")
        out = m.apply(p, opt, {"mode": "model", "say": words, "feeling": "tense"}, t, [], new_record())
        out_of_turn(m)
        return out

    # T1
    def test_t1_day1_replays_from_the_v11_caches_byte_for_byte(self):
        for seed, served in V11_SERVED.items():
            name = f"daniel_ate_it-seed{seed}"
            day1, oracle = self.v11_day1(seed)
            text = render(day1, seed, V6_MODEL, f"python morning.py --seed {seed}")
            self.assertEqual(text.encode("utf-8"), read(os.path.join(V11_RUNS, name + ".md"), "rb"), seed)
            self.assertEqual(json.loads(json.dumps(day1.transcript)),
                             json.loads(read(os.path.join(V11_RUNS, name + ".transcript.json"))), seed)
            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
            rec = Recorder(oracle)
            with self.assertRaises(gemini.CacheMiss, msg=seed):
                self.night.Night(day1, rec).run()
            self.assertEqual(len(rec.prompts), 1)
            self.assertTrue(rec.prompts[0].startswith("You are Daniel,"))
            self.assertIn("\nNow it is night. " + GAP + "\n", rec.prompts[0])

    def test_t1_the_story_begins_with_day1_unchanged(self):
        (meta, code), out = fake_morning(self.dirs, seed=2)
        self.assertEqual(code, 0, out)
        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed2.md"))
        oracle = Oracle(Cache(os.path.join(self.dirs.cache, "fake-daniel_ate_it-seed2.json")), "fake", 2, replay=True)
        day1 = Morning(oracle, 2).run()
        text = render(day1, 2, "fake", "python morning.py --seed 2 --fake")
        self.assertTrue(story.startswith(text))
        self.assertTrue(story[len(text):].startswith("# The night\n"))
        self.assertIn("\n# The next morning (day 5)\n", story)
        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed2.transcript.json")))
        self.assertEqual(tr["day1"], json.loads(json.dumps(day1.transcript)))
        self.assertEqual(set(tr), {"day1", "night", "day2"})

    # T2
    def test_t2_the_gap(self):
        day1, oracle = self.v11_day1(1, NightScripted())
        before = {p: (q.hunger, q.room, json.dumps({t: [g.strength, g.events] for t, g in q.grudges.items()}),
                      q.suspicion.state(), q.guilt) for p, q in day1.people.items()}
        n = self.night.Night(day1, oracle).run()
        self.assertEqual(n.rooms_at_bedtime, {"daniel": "brothers_room", "leo": "brothers_room",
                                              "elena": "back_room", "mara": "back_room"})
        for pid in data.ORDER:
            rate = data.PEOPLE[pid]["hunger_rate"]
            bed = min(1.0, before[pid][0] + 0.3 * rate)
            self.assertAlmostEqual(n.bedtime_hunger[pid], bed, places=9, msg=pid)
            self.assertAlmostEqual(n.people[pid].hunger, min(1.0, bed + 0.1 * rate), places=9, msg=pid)
        self.assertEqual((round(n.bedtime_hunger["leo"], 3), round(n.people["leo"].hunger, 3)), (0.710, 0.810))
        self.assertEqual((n.bedtime_hunger["daniel"], n.bedtime_hunger["elena"]), (1.0, 1.0))
        self.assertEqual(world.hunger_words(n.people["mara"].hunger), "very hungry")
        self.assertEqual(n.portions, 0)
        self.assertEqual(n.state_at_bedtime, {p: list(v[2:]) for p, v in before.items()})
        for p in day1.people.values():                     # day 1 itself is untouched
            self.assertEqual((p.room, p.hunger), ("kitchen", before[p.id][0]))

    # T3
    def test_t3_the_bedtime_prompt_exactly(self):
        self.assertEqual(world.NIGHT_SYSTEM, NIGHT_SYSTEM_TEXT)
        self.assertEqual(world.SYSTEM, frozen("v11", "world").SYSTEM)
        self.assertEqual(data.HOUSE_THINGS_NIGHT,
                         data.HOUSE_THINGS.replace("Outside, and not to be gone to:", "Outside:"))
        client = NightScripted()
        day1, oracle = self.v11_day1(1, client)
        self.night.Night(day1, oracle).run()
        bedtime = {who: p for w, who, p in client.prompts if w == "night"}
        self.assertEqual(set(bedtime), set(data.ORDER))
        self.assertTrue(bedtime["daniel"].endswith(
            "\nNow it is night. " + GAP + "\n"
            "Everyone has gone to bed in their own room: Daniel and Leo in the brothers room, Elena and Mara in the "
            "back room.\nYou are in the brothers room, in your bed. Leo is in his bed.\n"
            "The kitchen is dark. The shelf holds 0 portions.\n"
            # Seed 1's Daniel last said he would go (min 36), so the promise line comes last (body_design §1).
            + PROMISE + "\n" + BEDTIME_OPTIONS), bedtime["daniel"])
        self.assertIn("\nYou are in the back room, in your bed. Mara is in her bed.\n", bedtime["elena"])
        self.assertIn("\nYou are in the back room, in your bed. Elena is in her bed.\n", bedtime["mara"])
        for p in bedtime.values():
            self.assertIn(f"The house: {data.HOUSE} {data.HOUSE_THINGS_NIGHT}\n", p)
            for heading in ("What you are sure of from today:", "What else happened today, most recent last:"):
                self.assertIn("\n" + heading + "\n", p)
            self.assertNotIn("this morning:", p)
            self.assertNotIn("What you have been doing", p)
            self.assertNotIn("Said and done", p)
            self.assertIn(TRIP_FOOD, p)                  # the inside lines as at minute 90
        self.assertIn("\nYour own last words today:\n", bedtime["daniel"])
        oracle = Oracle(Cache(self.path("one")), "fake", 1, client=FakeClient())
        m = Morning(oracle, 1)
        m.turn(0)
        m.portions = 1
        m.finish()
        rec = Recorder(oracle)
        self.night.Night(m, rec).run()
        self.assertIn("\nThe kitchen is dark. The shelf holds 1 portion.\n", rec.prompts[0])

    # T4
    def test_t4_an_awake_roommate_sees_and_is_asked_once(self):
        _, n, client, _ = self.night_of({"daniel": ["go_next_door"], "leo": ["lie_awake"]}, QUIET)
        self.assertEqual(self.asked(n), [("daniel", "bedtime"), ("elena", "bedtime"), ("leo", "bedtime"),
                                         ("mara", "bedtime"), ("leo", "reaction")])
        prompt = client.night_prompts("leo")[-1]
        self.assertEqual(now_lines(prompt), [
            "Now it is night, in the brothers room. You were lying awake.",
            "Daniel has got up in the dark and is leaving the room quietly, toward the kitchen and the front door."])
        self.assertEqual(option_lines(prompt), ["- let_daniel_go: stay where you are and let Daniel go without a word",
                                                "- stop_daniel: (speech) tell Daniel, low, not to go",
                                                "- go_with_daniel: get up and go with Daniel to the neighbour's house"])
        self.assertEqual(n.lines["mara"], ["Last night you slept in the back room with Elena. You went to sleep."])
        self.assertEqual(n.lines["elena"], ["Last night you slept in the back room with Mara. You went to sleep."])
        self.assertEqual(n.lines["leo"], [
            "Last night you slept in the brothers room with Daniel. You lay awake and listened.",
            "In the night Daniel got up in the dark and left the room toward the kitchen and the front door "
            "(you saw it).",
            "You let him go without a word.",
            "Before dawn you heard the front door again. You did not see who."])

    def test_t4_a_sleeping_roommate_wakes_only_under_the_threshold(self):
        _, n, client, _ = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "wake:daniel:leo": 0.39})
        self.assertIn(("leo", "reaction"), self.asked(n))
        self.assertEqual(now_lines(client.night_prompts("leo")[-1])[0],
                         "Now it is night, in the brothers room. You were asleep and woke.")
        self.assertIn("In the night Daniel got up in the dark and left the room toward the kitchen and the front "
                      "door (you woke and saw it).", n.lines["leo"])
        _, n, _, _ = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "wake:daniel:leo": 0.41})
        self.assertNotIn(("leo", "reaction"), self.asked(n))
        self.assertEqual(n.lines["leo"], ["Last night you slept in the brothers room with Daniel. You went to sleep."])

    def test_t4_the_door_sitter_always_sees(self):
        _, n, client, _ = self.night_of({"daniel": ["go_next_door"], "elena": ["watch_door"]}, QUIET)
        self.assertIn(("elena", "reaction"), self.asked(n))
        self.assertEqual(now_lines(client.night_prompts("elena")[-1]), [
            "Now it is night. You are sitting up in the kitchen by the front door.",
            "Daniel has come into the kitchen in the dark and is going to the front door."])
        self.assertIn("In the night Daniel came into the kitchen and went to the front door (you saw it).",
                      n.lines["elena"])

    def test_t4_the_front_door_through_a_wall(self):
        _, n, client, _ = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "door:daniel:mara": 0.25})
        self.assertEqual(self.asked(n, "reaction"), [("mara", "reaction")])
        prompt = client.night_prompts("mara")[-1]
        self.assertEqual(now_lines(prompt), [
            "Now it is night, in the back room. You were asleep and woke.",
            "From the kitchen comes the sound of the front door being opened. You cannot see who it is."])
        self.assertEqual(option_lines(prompt), ["- stay_in_bed: stay in bed",
                                                "- get_up_and_look: get up, see whose bed is empty, and wait up by "
                                                "the front door until morning"])
        _, n, _, _ = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "door:daniel:mara": 0.27})
        self.assertEqual(self.asked(n, "reaction"), [])
        # Nobody is ever in the bathroom at night, so nothing is heard there.
        self.assertNotIn("bathroom", set(n.rooms_at_bedtime.values()))

    def test_t4_low_voices_wake_nobody(self):
        _, n, _, _ = self.night_of({"daniel": ["go_next_door", "go_anyway"], "leo": ["lie_awake", "stop_daniel"],
                                    "elena": ["lie_awake"]}, QUIET)
        self.assertEqual(self.asked(n), [("daniel", "bedtime"), ("elena", "bedtime"), ("leo", "bedtime"),
                                         ("mara", "bedtime"), ("leo", "reaction"), ("daniel", "answer"),
                                         ("elena", "reaction")])
        self.assertIn("In the night you heard low voices from the brothers room.", n.lines["elena"])
        self.assertFalse([x for x in n.lines["mara"] if "low voices" in x])
        self.assertIn('You told Daniel, low, not to go: "Words of leo 5." He answered: "Words of daniel 6.", and '
                      'went all the same.', n.lines["leo"])
        self.assertIn('Leo told you, low, not to go: "Words of leo 5." You answered: "Words of daniel 6.", and '
                      'went all the same.', n.lines["daniel"])

    def test_t4_at_most_one_reaction_each(self):
        _, n, _, _ = self.night_of({"daniel": ["go_next_door"], "elena": ["go_next_door", "go_later"],
                                    "leo": ["lie_awake"]},
                                   {**QUIET, "order": ["daniel", "elena"], "wake:elena:mara": 0.9,
                                    "door:elena:mara": 0.9, "trip:elena": 0.1})
        reactions = [p for p, _ in self.asked(n, "reaction")]
        self.assertEqual(reactions.count("leo"), 1)
        self.assertEqual(sum("heard the front door being opened" in x for x in n.lines["leo"]), 1)
        for p in data.ORDER:
            self.assertLessEqual(reactions.count(p), 1, p)

    def test_t4_a_leaver_answers_once_per_stop_moment(self):
        _, n, client, _ = self.night_of({"daniel": ["go_next_door", "go_anyway"], "leo": ["lie_awake", "stop_daniel"],
                                         "elena": ["watch_door", "stop_daniel"]}, QUIET)
        self.assertEqual([p for p, _ in self.asked(n, "answer")], ["daniel", "daniel"])
        first, second = client.night_prompts("daniel")[1:3]
        self.assertEqual(now_lines(first), ["Now it is night, in the brothers room. You had got up to go to the "
                                            "neighbour's house.", 'Leo is up and says to you, low: "Words of leo 5."'])
        self.assertEqual(now_lines(second), ["Now it is night, in the kitchen, by the front door. You had got up to "
                                             "go to the neighbour's house.",
                                             'Elena is up and says to you, low: "Words of elena 7."'])
        self.assertEqual(option_lines(first), [
            "- go_anyway: (speech) answer Leo, and go out to the neighbour's house all the same",
            "- stay_home: (speech) answer Leo, and go back to bed"])

    def test_t4_staying_home_cancels_the_trip(self):
        _, n, _, _ = self.night_of({"daniel": ["go_next_door", "stay_home"], "leo": ["lie_awake", "stop_daniel"],
                                    "elena": ["watch_door"]}, QUIET)
        self.assertEqual(n.groups, [])
        self.assertNotIn(("elena", "reaction"), self.asked(n))
        self.assertEqual(n.people["daniel"].room, "brothers_room")
        self.assertEqual(n.away, set())
        self.assertIn('Leo told you, low, not to go: "Words of leo 5." You answered: "Words of daniel 6.", and '
                      'went back to bed.', n.lines["daniel"])

    def test_t4_going_with_and_after_join_the_group(self):
        _, n, _, _ = self.night_of({"daniel": ["go_next_door"], "leo": ["lie_awake", "go_with_daniel"]},
                                   {**QUIET, "house": 0.5, "trip:daniel": 0.65})
        self.assertEqual(len(n.groups), 1)
        g = n.groups[0]
        self.assertEqual((g["leader"], g["members"], g["street"]), ("daniel", ["daniel", "leo"], "clean"))
        self.assertEqual((g["found"], g["took"]), (2, 2))      # alone, 0.65 would have been a scare
        self.assertEqual(self.night.street(0.65, 1), "scare_there")
        _, n, _, _ = self.night_of({"daniel": ["go_next_door"], "mara": ["go_next_door", "go_after"]},
                                   {**QUIET, "order": ["daniel", "mara"]})
        self.assertEqual([g["members"] for g in n.groups], [["daniel", "mara"]])

    def test_t4_a_second_leaver_finds_what_the_first_left(self):
        draws = {**QUIET, "order": ["daniel", "mara"], "trip:mara": 0.1, "wake:mara:elena": 0.9, "door:mara:leo": 0.9}
        _, n, _, _ = self.night_of({"daniel": ["go_next_door"], "mara": ["go_next_door", "go_later"]},
                                   {**draws, "house": 0.95})
        self.assertEqual([(g["leader"], g["found"], g["took"]) for g in n.groups], [("daniel", 6, 3), ("mara", 3, 3)])
        self.assertEqual((n.house, n.house_left, n.portions), (6, 0, 8))
        _, n, _, _ = self.night_of({"daniel": ["go_next_door"], "mara": ["go_next_door", "go_later"]},
                                   {**draws, "house": 0.8})
        self.assertEqual([(g["found"], g["took"]) for g in n.groups], [(4, 3), (1, 1)])

    def test_t4_a_leaver_who_was_waiting(self):
        _, n, client, _ = self.night_of({"daniel": ["go_next_door"], "leo": ["go_next_door", "let_daniel_go"]},
                                        {**QUIET, "order": ["daniel", "leo"], "trip:leo": 0.1})
        prompt = client.night_prompts("leo")[1]
        self.assertEqual(now_lines(prompt)[0], "Now it is night, in the brothers room. You were lying awake.")
        self.assertEqual(option_lines(prompt), [
            "- go_with_daniel: get up and go with Daniel to the neighbour's house",
            "- stop_daniel: (speech) tell Daniel, low, to stay home, and go yourself instead",
            "- let_daniel_go: let Daniel go, and go yourself later, alone",
            "- stay_home: let Daniel go, and stay in bed yourself after all"])
        self.assertEqual([g["leader"] for g in n.groups], ["daniel", "leo"])
        _, n, client, _ = self.night_of({"daniel": ["go_next_door"], "mara": ["go_next_door", "go_later"]},
                                        {**QUIET, "order": ["daniel", "mara"], "trip:mara": 0.1,
                                         "wake:mara:elena": 0.9, "door:mara:leo": 0.9})
        self.assertEqual(option_lines(client.night_prompts("mara")[1]), [
            "- go_after: get up now and follow whoever it is out to the neighbour's house",
            "- go_later: wait, then go yourself later, alone", "- stay_home: stay in bed after all"])

    # T5
    def test_t5_every_night_option_set_passes_the_wording_rule(self):
        for prefs in ({"daniel": ["go_next_door"], "leo": ["lie_awake"], "elena": ["watch_door"], "mara": ["lie_awake"]},
                      {"daniel": ["go_next_door"], "leo": ["go_next_door"], "elena": ["go_next_door"]},
                      {"daniel": ["go_next_door", "go_anyway"], "leo": ["lie_awake", "stop_daniel"]}):
            _, n, client, _ = self.night_of(prefs, {"trip:daniel": 0.1, "trip:leo": 0.1, "trip:elena": 0.1})
            for prompt in client.night_prompts():
                labels = [x.split(": ", 1)[1].replace("(speech) ", "") for x in option_lines(prompt)]
                self.assertEqual(not_pairs(labels), [], prompt)

    # T6
    def test_t6_the_draws_for_seeds_1_to_3(self):
        expect = {
            1: (0.050, ["leo", "daniel", "elena", "mara"],
                {"daniel": 0.297, "elena": 0.955, "leo": 0.008, "mara": 0.456},
                {"daniel": 0.573, "elena": 0.251, "leo": 0.051, "mara": 0.997}),
            2: (0.105, ["leo", "elena", "mara", "daniel"],
                {"daniel": 0.927, "elena": 0.625, "leo": 0.064, "mara": 0.101},
                {"daniel": 0.777, "elena": 0.393, "leo": 0.185, "mara": 0.212}),
            3: (0.257, ["leo", "mara", "daniel", "elena"],
                {"daniel": 0.616, "elena": 0.108, "leo": 0.712, "mara": 0.995},
                {"daniel": 0.914, "elena": 0.280, "leo": 0.750, "mara": 0.772}),
        }
        roommate = {"daniel": "leo", "leo": "daniel", "elena": "mara", "mara": "elena"}
        for seed, (house, order, trip, wake) in expect.items():
            day1, oracle = self.short_day1(NightScripted(), seed)
            n = self.night.Night(day1, oracle)
            self.assertAlmostEqual(n.u("house"), house, places=3)
            self.assertEqual(self.night.house_portions(n.u("house")), 0)
            self.assertEqual(n.order(), order)
            for q in data.ORDER:
                self.assertAlmostEqual(n.u(f"trip:{q}"), trip[q], places=3, msg=(seed, q))
                self.assertAlmostEqual(n.u(f"wake:{q}:{roommate[q]}"), wake[q], places=3, msg=(seed, q))
        self.assertAlmostEqual(n.u("door:daniel:elena"), 0.564, places=3)
        self.assertAlmostEqual(n.u("return:daniel:elena"), 0.455, places=3)
        self.assertAlmostEqual(n.u("lost:daniel"), 0.718, places=3)
        self.assertEqual([self.night.street(u, 1) for u in (0.297, 0.955, 0.927, 0.625, 0.712)],
                         ["clean", "not_back", "scare_back", "scare_there", "scare_there"])
        self.assertEqual([self.night.street(u, 2) for u in (0.955, 0.625)], ["scare_back", "clean"])
        self.assertEqual({p: (self.night.wake_room(p), self.night.wake_door(p)) for p in data.ORDER},
                         {"daniel": (0.56, 0.23), "elena": (0.6, 0.25), "leo": (0.4, 0.15), "mara": (0.62, 0.26)})

    def test_t6_the_same_seed_gives_the_same_night(self):
        stories = []
        for _ in range(2):
            dirs = Dirs()
            try:
                (_, code), out = fake_morning(dirs, seed=4)
                self.assertEqual(code, 0, out)
                story = read(os.path.join(dirs.runs, "daniel_ate_it-seed4.md"))
                stories.append(story[story.index("# The night\n"):])
            finally:
                dirs.cleanup()
        self.assertEqual(stories[0], stories[1])

    # T7
    def test_t7_the_outcome_table(self):
        night = self.night
        table = {1: {"back with food": 0.434, "back with nothing": 0.186, "back shaken, with nothing": 0.194,
                     "back shaken, with food": 0.126, "not back by morning": 0.06},
                 2: {"back with food": 0.49, "back with nothing": 0.21, "back shaken, with nothing": 0.165,
                     "back shaken, with food": 0.105, "not back by morning": 0.03}}
        houses = [night.house_portions(random.Random(f"{s}:night:house").random()) for s in range(100000)]
        trips = [random.Random(f"{s}:night:trip:daniel").random() for s in range(100000)]
        self.assertAlmostEqual(houses.count(0) / 1e5, 0.30, delta=0.005)
        for size, probs in table.items():
            counts = {}
            for h, u in zip(houses, trips):
                c = night.outcome_class(night.street(u, size), h)
                counts[c] = counts.get(c, 0) + 1
            self.assertEqual(set(counts), set(probs))
            for c, p in probs.items():
                self.assertAlmostEqual(counts[c] / 1e5, p, delta=0.005, msg=(size, c))

    def test_t7_carrying_loss_and_the_shelf(self):
        _, n, _, _ = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "house": 0.95})
        self.assertEqual((n.groups[0]["found"], n.groups[0]["took"], n.portions, n.house_left), (6, 3, 5, 3))
        # A pair loses one member, chosen by the lost draw; the other comes back shaken, empty-handed.
        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"], "leo": ["lie_awake", "go_with_daniel"]},
                                           {**QUIET, "house": 0.95, "trip:daniel": 0.98, "lost:daniel": 0.6})
        g = n.groups[0]
        self.assertEqual((g["street"], g["lost"], g["took"], g["shaken"]), ("not_back", "leo", 0, ["daniel"]))
        self.assertEqual(n.away, {"leo"})
        self.assertEqual(n.portions, 2)
        day2 = Morning.next_day(day1, n, oracle)
        self.assertIsNone(day2.people["leo"].room)
        self.assertEqual(day2.away, {"leo"})
        # Seeds 4 to 6 (houses 2, 2 and 6), Daniel going alone: seed 5 comes back with food.
        got = {}
        for seed in (4, 5, 6):
            client = NightScripted({"daniel": ["go_next_door"]})
            day1, oracle = self.short_day1(client, seed)
            n = self.night.Night(day1, oracle).run()
            got[seed] = (n.house, n.groups[0]["street"], n.groups[0]["took"], n.portions - day1.portions)
        self.assertEqual(got, {4: (2, "scare_there", 0, 0), 5: (2, "clean", 2, 2), 6: (6, "scare_there", 0, 0)})

    # T8
    def test_t8_no_creature_no_fate(self):
        cases = {
            "back with food": ({"house": 0.8, "trip:daniel": 0.1},
                               ["You got inside the neighbour's house and found 4 portions of food. You took 3; 1 is "
                                "still there. Nothing troubled you in the street.",
                                "You came back in by the front door before dawn and put the 3 portions on the shelf."]),
            "all of it": ({"house": 0.5, "trip:daniel": 0.1},
                          ["You got inside the neighbour's house and found 2 portions of food. You took all of it. "
                           "Nothing troubled you in the street.",
                           "You came back in by the front door before dawn and put the 2 portions on the shelf."]),
            "back with nothing": ({"house": 0.1, "trip:daniel": 0.1},
                                  ["You got inside the neighbour's house and found no food there. Nothing troubled you "
                                   "in the street.", "You came back in by the front door before dawn."]),
            "scared there": ({"house": 0.8, "trip:daniel": 0.7},
                             ["On the way there, something was moving in the street. You ran back without getting "
                              "inside.", "You came back in by the front door before dawn."]),
            "scared back": ({"house": 0.8, "trip:daniel": 0.8},
                            ["You got inside the neighbour's house and found 4 portions of food and took 3. On the way "
                             "back, something was moving in the street, and you ran the rest of the way.",
                             "You came back in by the front door before dawn and put the 3 portions on the shelf."]),
            "scared back, empty house": ({"house": 0.1, "trip:daniel": 0.8},
                                         ["You got inside the neighbour's house but found no food. On the way back, "
                                          "something was moving in the street, and you ran the rest of the way.",
                                          "You came back in by the front door before dawn."]),
        }
        texts = []
        for name, (draws, lines) in cases.items():
            day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, **draws})
            self.assertEqual(n.lines["daniel"][1:], lines, name)
            day2 = Morning.next_day(day1, n, oracle)
            texts += [x for p in n.lines.values() for x in p]
            texts += [x for p in day2.people.values() for x in day2.inside_lines(p) + p.sure]
        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"], "leo": ["lie_awake", "go_with_daniel"]},
                                           {**QUIET, "trip:daniel": 0.98, "lost:daniel": 0.6})
        self.assertIn("In the street, something was moving. You lost sight of Leo in the dark and came back without "
                      "him.", n.lines["daniel"])
        day2 = Morning.next_day(day1, n, oracle)
        texts += [x for p in n.lines.values() for x in p]
        texts += [x for p in day2.people.values() if p.room for x in day2.inside_lines(p) + p.sure]
        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "trip:daniel": 0.99})
        self.assertEqual(n.away, {"daniel"})
        day2 = Morning.next_day(day1, n, oracle)
        texts += [x for p in day2.people.values() if p.room for x in day2.inside_lines(p) + p.sure]
        self.assertTrue(texts)
        for x in texts:
            self.assertFalse(FATE.search(x), x)
            if "moving" in x:
                self.assertTrue("something was moving in the street" in x or "In the street, something was moving." in x,
                                x)

    # T9
    def test_t9_the_carry_in_exactly(self):
        blocks = {}
        for seed in (1, 2, 3):
            day1, oracle = self.v11_day1(seed, NightScripted())
            n = self.night.Night(day1, oracle).run()
            day2 = Morning.next_day(day1, n, oracle)
            for p in data.ORDER:
                blocks[seed, p] = day2.carry[p]
        count = "- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it)."
        positions3 = ("- About going to the neighbour's house last night, where it was left: you said nobody should go "
                      "(min 66); Daniel said Leo should not go (min 66); Elena said nobody should go (min 66); Leo said "
                      "he will not go (min 69).")
        self.assertEqual(blocks[3, "mara"], [
            CARRY_HEAD, count, "- Nobody admitted taking the can, and it was not found.",
            "- You searched the kitchen at minute 75 and found nothing.", positions3, "- " + GAP,
            "- Last night you slept in the back room with Elena. You went to sleep."])
        self.assertEqual(blocks[3, "daniel"][2:4], ["- Nobody found out that you ate the can, and nobody named you.",
                                                     "- You searched the kitchen at minute 78 and found nothing."])
        self.assertEqual(blocks[2, "leo"], [
            CARRY_HEAD, count,
            "- Daniel admitted taking the can at minute 33, after denying it to you: \"I took it in the night, I'm "
            "sorry.\" (you heard it).",
            "- Accusations: Daniel accused you three times (min 03, 09, 12); Mara accused Daniel (min 36).",
            "- Mara ate a portion at minute 54 (you saw it).",
            "- About going to the neighbour's house last night, where it was left: Mara said Elena should not go "
            "(min 48); you said Elena should not go (min 48); Elena said she will not go (min 51); Daniel said nobody "
            "should go (min 51).",
            "- " + GAP, "- Last night you slept in the brothers room with Daniel. You went to sleep."])
        self.assertEqual(blocks[2, "daniel"][3], "- Accusations: you accused Leo three times (min 03, 09, 12); "
                                                 "Mara accused you (min 36).")
        self.assertEqual(blocks[1, "daniel"][2], "- You admitted at minute 03 that you took the can, in front of "
                                                 "Elena, Leo and Mara.")
        self.assertEqual(blocks[1, "elena"][1], "- Yesterday morning Elena counted the pantry and found one can fewer "
                                                "than she expected (you did it).")
        self.assertIn("- Leo and Mara ate a portion each at minute 21 (you saw it).", blocks[1, "elena"])
        self.assertIn("- You and Mara ate a portion each at minute 21.", blocks[1, "leo"])
        self.assertIn("- You and Leo ate a portion each at minute 21.", blocks[1, "mara"])
        for b in blocks.values():
            self.assertLessEqual(estimate_tokens("\n".join(b)), CARRY_MAX)
        # Over the bound: the quoted night words go first.
        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door", "go_anyway"], "leo": ["lie_awake", "stop_daniel"]},
                                           QUIET)
        n.lines["leo"] = [x.replace("Words of leo 5.", "word " * 400) for x in n.lines["leo"]]
        day2 = Morning.next_day(day1, n, oracle)
        self.assertIn("- You told Daniel, low, not to go. He went all the same.", day2.carry["leo"])
        self.assertLessEqual(estimate_tokens("\n".join(day2.carry["leo"])), CARRY_MAX)
        self.assertIn('- Leo told you, low, not to go: "Words of leo 5." You answered: "Words of daniel 6.", and went '
                      'all the same.', day2.carry["daniel"])

    def test_t9_nobody_is_told_what_they_did_not_notice(self):
        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"]}, QUIET)
        day2 = Morning.next_day(day1, n, oracle)
        for p in ("elena", "leo", "mara"):
            self.assertFalse([x for x in day2.carry[p][1:] if "Daniel" in x and not x.startswith("- Last night you slept")],
                             p)
            self.assertIn("About the neighbour's house: its people left in the first days, so there may be food there. "
                          "Outside is dangerous.", day2.inside_lines(day2.people[p]))
        self.assertIn("About the neighbour's house: you went in last night and found no food there. Outside is "
                      "dangerous.", day2.inside_lines(day2.people["daniel"]))

    # T10
    def test_t10_what_day2_carries_and_resets(self):
        client = NightScripted(angry={"leo": "Daniel", "mara": "Daniel"})
        day1, oracle = self.v11_day1(2, client)
        n = self.night.Night(day1, oracle).run()
        day2 = Morning.next_day(day1, n, oracle)
        for pid, p in day2.people.items():
            q = n.people[pid]
            self.assertEqual({t: g.strength for t, g in p.grudges.items()},
                             {t: g.strength for t, g in q.grudges.items()})
            for g in p.grudges.values():
                self.assertEqual(g.last_change, 0)
                for e in g.events:
                    self.assertIn(e[3], ("yesterday", "last night"))
                    if e[2] == "event":
                        self.assertTrue(e[1].startswith("yesterday, "), e)
            self.assertEqual(p.suspicion.state(), q.suspicion.state())
            self.assertEqual(p.suspicion.last_fall, 0)
            self.assertNotIn("ask_who", {o.id for o in day2.options_for(p)})
            self.assertEqual((p.memory, p.said_lines, p.history, p.heard, p.trip_heard, p.proposed),
                             ([], [], [], [], {}, False))
            self.assertEqual(p.room, "kitchen")
            self.assertEqual(p.sure, ["min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 1 "
                                      "portion; this morning it holds 1 portion. (you saw it)"])
        leo = day2.people["leo"]
        text = day2.prompt_for(leo, 0, day2.options_for(leo))
        self.assertIn("About the can: Daniel admitted taking it yesterday, at minute 33.", text)
        self.assertIn("Against Daniel (a lot): yesterday, Daniel accused you of taking the can at minute", text)
        self.assertIn("you were angry with Daniel yesterday at minutes", text)
        self.assertIn("; and last night.", text)
        dan = day2.people["daniel"]
        self.assertIn("About the can: you ate it yourself, and you admitted it yesterday.", day2.inside_lines(dan))
        self.assertIn("On your conscience (a lot): you ate the can in the night, and nobody saw; yesterday, you accused "
                      "Leo of what you did, at minute 03", day2.prompt_for(dan, 0, day2.options_for(dan)))
        self.assertEqual(day2.trip, {"minute": 0, "why": ["carried over from yesterday"], "asked": []})
        day2.turn(0)
        self.assertEqual({d["person"] for d in day2.log[0]["decisions"] if d["mode"] != "routine"}, set(data.ORDER))
        self.assertIn("the family is together in the kitchen for the first time since last night",
                      day2.log[0]["decisions"][0]["triggers"])

    def test_t10_someone_not_back_is_away(self):
        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "trip:daniel": 0.99})
        day2 = Morning.next_day(day1, n, oracle)
        self.assertIsNone(day2.people["daniel"].room)
        leo = day2.people["leo"]
        self.assertNotIn("daniel", [q.id for q in day2.others_here(leo)])
        self.assertFalse([o.id for o in day2.options_for(leo) if "daniel" in o.id])
        text = day2.prompt_for(leo, 0, day2.options_for(leo))
        self.assertIn("You are Leo, 21, the younger son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; "
                      "Mara, 17).", text)
        self.assertNotIn("- Daniel is here", text)
        self.assertEqual(leo.sure, ["min 00: Everyone else gets up and comes into the kitchen. Last night the shelf held "
                                    "2 portions; this morning it holds 2 portions. Daniel is not here: his bed is empty "
                                    "and he is nowhere in the house, so he went out in the night and has not come back. "
                                    "(you saw it)"])
        self.assertIn("About food: the shelf holds 2 portions, and there is no other food in the house, so there is "
                      "not one portion each.", day2.inside_lines(leo))
        for t in range(3):
            day2.turn(t)
            self.assertNotIn("daniel", [d["person"] for d in day2.log[-1]["decisions"]])
        day2.finish()
        self.assertEqual(day2.transcript["away"], ["daniel"])

    def test_t10_a_shaken_face_shows_for_3_turns(self):
        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"]}, {**QUIET, "trip:daniel": 0.7})
        day2 = Morning.next_day(day1, n, oracle)
        dan = day2.people["daniel"]
        self.assertEqual(dan.feeling, "shaken")
        self.assertEqual([day2.shown(dan, t) for t in range(4)], [True, True, True, False])
        self.assertEqual([day2.shown(q, 0) for q in day2.people.values() if q is not dan], [False] * 3)
        leo = day2.people["leo"]
        self.assertIn("- Daniel is here, just got up. Daniel looks shaken.", day2.prompt_for(leo, 0, day2.options_for(leo)))

    def test_t10_food_lines_and_the_returners_opening(self):
        day1, n, _, oracle = self.night_of({"daniel": ["go_next_door"], "elena": ["watch_door"]},
                                           {**QUIET, "house": 0.95})
        day2 = Morning.next_day(day1, n, oracle)
        self.assertEqual(day2.people["daniel"].sure[0],
                         "min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 2 portions; this "
                         "morning it holds 5 portions: the 3 you brought back are on it. (you saw it)")
        self.assertEqual(day2.people["mara"].sure[0],
                         "min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 2 portions; this "
                         "morning it holds 5 portions. So someone brought food into the house in the night. (you saw it)")
        self.assertIn("About food: the shelf holds 5 portions, and there is no other food in the house, so there is one "
                      "portion each, and nothing after that.", day2.inside_lines(day2.people["mara"]))
        self.assertIn("About the neighbour's house: Daniel went there last night and came back with food. Outside is "
                      "dangerous.", day2.inside_lines(day2.people["elena"]))
        self.assertIn("About the neighbour's house: you went in last night and found 6 portions; you brought back 3, "
                      "and 3 are still there. Outside is dangerous.", day2.inside_lines(day2.people["daniel"]))
        self.assertIn("- Before dawn Daniel came back in by the front door, carrying food (you saw it).",
                      day2.carry["elena"])

    # T11
    def test_t11_the_day2_options(self):
        from talk import act_of, aimed_at
        day1, oracle = self.v11_day1(3, NightScripted())
        n = self.night.Night(day1, oracle).run()
        day2 = Morning.next_day(day1, n, oracle)
        dan, ele, leo, mara = (day2.people[p] for p in data.ORDER)

        def trip(p):
            return [o.id for o in day2.options_for(p) if DAY2_TRIP_IDS.match(o.id)]
        self.assertEqual(trip(dan), ["propose_trip", "volunteer", "send_elena", "send_leo", "send_mara"])
        labels = {o.id: o.label for o in day2.options_for(dan)}
        self.assertEqual(labels["send_leo"], "say Leo is the one who should go there tonight")
        self.assertEqual(labels["volunteer"], "offer to go there tonight yourself")
        self.act(day2, dan, "volunteer", "I'll go.")
        self.assertEqual(trip(dan), ["propose_trip", "still_going", "send_elena", "send_leo", "send_mara",
                                     "nobody_goes", "refuse_to_go"])
        self.assertEqual(trip(leo), ["propose_trip", "volunteer", "send_daniel", "send_elena", "send_mara",
                                     "nobody_goes", "keep_daniel_home"])
        labels = {o.id: o.label for p in day2.people.values() for o in day2.options_for(p)}
        self.assertEqual((labels["still_going"], labels["nobody_goes"], labels["keep_daniel_home"],
                          labels["refuse_to_go"]),
                         ("say you still mean to go there tonight", "say nobody should go out tonight",
                          "say Daniel must stay home tonight", "say you yourself will not go"))
        self.act(day2, dan, "still_going", "I still mean it.", t=1)
        self.assertEqual(day2.trip_acts[-1][2:4], ("volunteer", None))
        self.assertEqual(day2.said[-1]["why"], "an offer to go they had made before")
        self.assertIn((3, 'Daniel says he still means to go tonight: "I still mean it."'), leo.memory)
        self.act(day2, ele, "send_leo", "Leo should.", t=2)
        self.act(day2, leo, "keep_daniel_home", "Not Daniel.", t=3)
        self.act(day2, leo, "refuse_to_go", "Not me.", t=4)
        self.assertIn((6, 'Elena says you are the one who should go: "Leo should."'), leo.memory)
        self.assertIn((9, 'Leo says Daniel must stay home tonight: "Not Daniel."'), ele.memory)
        self.assertIn((12, 'Leo says he will not go: "Not me."'), ele.memory)
        self.assertIn("min 09, you said Daniel must stay home tonight.", leo.said_lines)
        plan = next(x for x in day2.inside_lines(ele) if x.startswith("About going there tonight:"))
        self.assertEqual(plan, "About going there tonight: Daniel said he still means to go (min 03); you said Leo is "
                               "the one who should go (min 06); Leo said he will not go (min 12).")
        day2.finish()
        self.assertEqual([a[2] for a in day2.transcript["trip"]["acts"]],
                         ["volunteer", "still_going", "send_leo", "keep_daniel_home", "refuse_to_go"])
        self.assertEqual([act_of(x) for x in ("nobody_goes", "keep_leo_home", "send_mara", "still_going",
                                              "refuse_to_go", "keep_searching")],
                         [("object", None), ("object", "leo"), ("back", "mara"), ("volunteer", None),
                          ("decline", None), ("search", None)])
        self.assertEqual([aimed_at(x) for x in ("keep_leo_home", "send_mara", "nobody_goes")], ["leo", "mara", None])
        # The wording rule over every offered set; opposite kinds share no stem but a person's id.
        for p in day2.people.values():
            opts = [o for o in day2.options_for(p) if DAY2_TRIP_IDS.match(o.id)]
            self.assertEqual(not_pairs([o.label for o in opts]), [], p.id)

            def stems(kinds):
                return {re.sub("|".join(data.ORDER), "", o.id) for o in opts if act_of(o.id)[0] in kinds}
            self.assertFalse(stems({"propose", "volunteer", "back"}) & stems({"object", "decline"}), p.id)
        # Day 1 keeps the v11 options and labels.
        m, _ = scripted(silent, self.dirs, turns=1)
        m.portions = 0
        m.turn(1)
        self.assertEqual([(o.id, o.label) for o in m.options_for(m.people["leo"]) if TRIP_IDS.match(o.id)],
                         [("propose_trip", "say someone should go to the neighbour's house tonight"),
                          ("volunteer", "offer to go there tonight yourself"),
                          ("back_daniel", "say Daniel should be the one to go"),
                          ("back_elena", "say Elena should be the one to go"),
                          ("back_mara", "say Mara should be the one to go")])

    # T12
    def test_t12_the_budget(self):
        night_n = day2_n = 0
        for seed in (1, 2, 3):
            (_, code), out = fake_morning(self.dirs, seed=seed)
            self.assertEqual(code, 0, out)
        for p in cached_prompts(self.dirs):
            if "\nNow it is night" in p:
                night_n += 1
                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + without_blocks(p)), 1450)
                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + p), 1450 + TRIP_BLOCK_MAX)
            elif CARRY_HEAD in p:
                day2_n += 1
                self.assertLess(estimate_tokens(SYSTEM + without_blocks(p)), 1450)
                self.assertLess(estimate_tokens(SYSTEM + p), 1450 + TRIP_BLOCK_MAX + CARRY_MAX)
        self.assertGreater(night_n, 0)
        self.assertGreater(day2_n, 0)
        # The carry-in costs this morning no line.
        day1, oracle = self.v11_day1(2, NightScripted())
        n = self.night.Night(day1, oracle).run()
        day2 = Morning.next_day(day1, n, oracle)
        ele = day2.people["elena"]
        ele.memory += [(0, f"filler line number {i} " + "about nothing much at all " * 12) for i in range(200)]
        with_carry = day2.prompt_for(ele, 1, day2.options_for(ele))
        carry, day2.carry = day2.carry, {}
        plain = day2.prompt_for(ele, 1, day2.options_for(ele))
        day2.carry = carry

        def morning_lines(prompt):
            lines = prompt.split("\n")
            return lines[lines.index("What else happened this morning, most recent last:"):
                         next(i for i, x in enumerate(lines) if x.startswith("Now, minute"))]
        self.assertIn(CARRY_HEAD, with_carry)
        self.assertIn("- (earlier things, left out here)", morning_lines(plain))
        self.assertEqual(morning_lines(with_carry), morning_lines(plain))

    # T13
    def test_t13_counting_and_the_story(self):
        (meta, code), out = fake_morning(self.dirs, seed=1)
        self.assertEqual(code, 0, out)
        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")))
        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.md"))
        self.assertEqual(meta["night_asks"], len(tr["night"]["decisions"]))
        self.assertEqual(meta["day2_asks"], sum(a["mode"] != "routine" for t in tr["day2"]["turns"] for a in t["acts"]))
        self.assertEqual(meta["day1"]["model_decisions"] + meta["day1"]["fallbacks"] + meta["night_asks"]
                         + meta["day2_asks"], meta["answers_live"] + meta["answers_from_cache"])
        self.assertEqual(meta["leavers"], tr["night"]["leavers"])
        for key in ("night_asks", "day2_asks", "night_api_requests", "day2_api_requests"):
            self.assertIn(f"{key}: {meta[key]}", out)
        night = story[story.index("# The night\n"):story.index("# The next morning (day 5)\n")]
        self.assertEqual(night.count("\n- **Bedtime, "), 4)
        noticing = [x for x in night.split("\n") if x.startswith("- Noticing: ")]
        self.assertEqual(len(noticing), len(tr["night"]["noticing"]))
        for x, e in zip(noticing, tr["night"]["noticing"]):
            if e["draw"] is not None:
                self.assertIn(f"draw {e['draw']:.3f}", x)
        self.assertIn(f"- The neighbour's house held {tr['night']['house']} portion", night)
        for g in tr["night"]["groups"]:
            self.assertIn(f"street draw {g['u']:.3f}", night)
        # The call cap counts each scene apart.
        oracle = Oracle(Cache(self.path("cap")), "fake", 1, client=FakeClient(max_calls=2), max_calls=2)
        oracle.ask("s", "p1")
        oracle.ask("s", "p2")
        with self.assertRaises(gemini.CallCapReached):
            oracle.ask("s", "p3")
        oracle.new_scene()
        oracle.ask("s", "p3")
        oracle.ask("s", "p4")
        with self.assertRaises(gemini.CallCapReached):
            oracle.ask("s", "p5")
        self.assertEqual(oracle.api_requests, 4)

    def test_t13_a_night_with_a_leaver_is_told_in_the_story(self):
        dirs = Dirs()
        try:
            client = NightScripted({"daniel": ["go_next_door"], "leo": ["lie_awake", "stop_daniel"]})
            (meta, code), out = quiet_run(1, fake=True, config_path=CONFIG, runs_dir=dirs.runs, cache_dir=dirs.cache,
                                          client=client)
            self.assertEqual(code, 0, out)
            story = read(os.path.join(dirs.runs, "daniel_ate_it-seed1.md"))
            tr = json.loads(read(os.path.join(dirs.runs, "daniel_ate_it-seed1.transcript.json")))
            self.assertEqual(meta["leavers"], ["daniel"])
            self.assertTrue(tr["night"]["noticing"])
            self.assertIn("street draw ", story)
            self.assertEqual(meta["outcome"], [g["outcome"] for g in tr["night"]["groups"]])
        finally:
            dirs.cleanup()

    # T14
    def test_t14_v11_v10_and_v9_still_replay(self):
        for version in ("v11", "v10", "v9"):
            done = run_check(version)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertEqual(done.stdout.count("story IDENTICAL, transcript IDENTICAL"), 3, done.stdout)
            self.assertIn("0 API calls", done.stdout)


V12_CACHE = os.path.join(HERE, "cache", "v12")
PROMISE = "You said you would go to the neighbour's house tonight. If you are going, it is now."
# The food moment's line: food_wording_probe.md's variant B, the same for everyone (food_confront_impl.md).
# body_design §2.4's line, which named when they last ate, was replaced by it.
NEUTRAL_FOOD = "You are starving, and there is food on the shelf in front of everyone."
# The design's table (reports/body_design.md, §2.2): (not since before yesterday, ate yesterday).
FOOD_CHANCES = {"daniel": (0.077, 0.0385), "elena": (0.0525, 0.0263), "leo": (0.049, 0.0245), "mara": (0.084, 0.042)}


def never(t, pid):
    return 0.99


def only(who, at=None):
    """A food draw that fires for `who` (at turn `at`, or any turn) and for nobody else."""
    return lambda t, pid: 0.0 if pid == who and (at is None or t == at) else 0.99


class BrokenFor(NightScripted):
    """NightScripted, but the answers to prompts that hold `marker` are not JSON."""

    def __init__(self, marker, prefs=None):
        super().__init__(prefs)
        self.marker = marker

    def generate(self, system, prompt):
        text = super().generate(system, prompt)
        return "not json" if self.marker in prompt else text


class BodyTest(unittest.TestCase):
    """The promise line at bedtime and the body's food moment on day 2 (reports/body_design.md;
    tests B-T1 to B-T12 of §4)."""

    setUp = NightTest.setUp
    tearDown = NightTest.tearDown
    path = NightTest.path
    v11_day1 = NightTest.v11_day1
    short_day1 = NightTest.short_day1
    night_of = NightTest.night_of
    act = NightTest.act

    def day2_of(self, seed, prefs=None, draws=never):
        """Day 2 of seed N after v11's day 1 and a scripted night (everyone sleeps), its food draws forced."""
        client = NightScripted(prefs)
        day1, oracle = self.v11_day1(seed, client)
        n = self.night.Night(day1, oracle).run()
        day2 = Morning.next_day(day1, n, oracle)
        day2.food_draw = draws
        return day2, client

    def bedtime_prompt(self, trip_heard, who="daniel"):
        """The bedtime prompt of `who` when their trip record is `trip_heard`."""
        client = NightScripted()
        day1, oracle = self.short_day1(client)
        day1.people[who].trip_heard = dict(trip_heard)
        self.night.Night(day1, oracle).run()
        return client.night_prompts(who)[0]

    def order_at_0(self, seed):
        day2, _ = self.day2_of(seed)
        day2.turn(0)
        return [d["person"] for d in day2.log[0]["decisions"]]

    # B-T1
    def test_b_t1_day1_replays_from_a_copy_of_the_v12_cache(self):
        for seed, served in V11_SERVED.items():
            name = f"daniel_ate_it-seed{seed}"
            path = self.path(f"v12-{seed}")
            shutil.copy(os.path.join(V12_CACHE, f"{V6_MODEL}-{name}.json"), path)
            oracle = Oracle(Cache(path), V6_MODEL, seed, replay=True)
            day1 = Morning(oracle, seed).run()
            text = render(day1, seed, V6_MODEL, f"python morning.py --seed {seed}")
            self.assertEqual(text.encode("utf-8"), read(os.path.join(V11_RUNS, name + ".md"), "rb"), seed)
            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)

    # B-T2
    def test_b_t2_the_promise_line_goes_to_whoever_last_said_they_would_go(self):
        cases = [
            ({"daniel": (36, "volunteer", None, 1)}, True),                         # day 1's offer
            ({"daniel": (9, "volunteer", None, 4, "still_going")}, True),           # day 2's restatement
            ({"daniel": (6, "volunteer", None, 3, "volunteer")}, True),             # day 2's offer
            ({"daniel": (39, "decline", None, 7)}, False),                          # offered, then declined
            ({"daniel": (39, "object", None, 7)}, False),                           # offered, then objected
            ({"leo": (30, "back", "daniel", 2)}, False),                            # only named by others
            ({}, False),                                                            # no position
        ]
        for heard, gets in cases:
            prompt = self.bedtime_prompt(heard)
            self.assertEqual(now_lines(prompt)[-1] == PROMISE, gets, heard)
            self.assertEqual(prompt.count(PROMISE), int(gets), heard)
        # Never in a reaction or an answer, and never to anyone but the one who said it.
        client = NightScripted({"daniel": ["go_next_door", "go_anyway"], "leo": ["lie_awake", "stop_daniel"]})
        day1, oracle = self.short_day1(client)
        day1.people["daniel"].trip_heard = {"daniel": (36, "volunteer", None, 1)}
        n = self.night.Night(day1, oracle, draws=QUIET).run()
        self.assertIn(("leo", "reaction"), [(d["person"], d["ask"]) for d in n.decisions])
        self.assertIn(("daniel", "answer"), [(d["person"], d["ask"]) for d in n.decisions])
        prompts = client.night_prompts()
        self.assertEqual(sum(PROMISE in p for p in prompts), 1)
        self.assertIn(PROMISE, client.night_prompts("daniel")[0])

    # B-T3
    def test_b_t3_only_seed_1_daniels_bedtime_prompt_changes_by_the_one_line(self):
        for seed in (1, 2, 3):
            day1, _ = self.v11_day1(seed)
            paired = PairedOracle(os.path.join(V12_CACHE, f"{V6_MODEL}-daniel_ate_it-seed{seed}.json"), V6_MODEL, seed)
            self.night.Night(day1, paired).run()
            bedtime = [p for p in paired.asked if "\nNow it is night. " in p][:4]
            self.assertEqual(len(bedtime), 4)
            if seed != 1:
                self.assertEqual(paired.missed, [], seed)
                continue
            self.assertEqual(paired.missed, [bedtime[0]])
            new = bedtime[0]
            self.assertTrue(new.startswith("You are Daniel,"))
            old = next(e["prompt"] for e in paired.entries.values()
                       if e["prompt"].startswith("You are Daniel,") and "\nNow it is night. " in e["prompt"])
            self.assertEqual(new, old.replace("\nYour options:\n", f"\n{PROMISE}\nYour options:\n", 1))
            self.assertEqual(now_lines(new)[-2:], ["The kitchen is dark. The shelf holds 0 portions.", PROMISE])

    # B-T4
    def test_b_t4_when_a_food_moment_can_fire(self):
        day2, _ = self.day2_of(3, draws=lambda t, pid: 0.0)
        mara = day2.people["mara"]
        in_turn(day2)

        def due(t=0):
            return day2.food_due(mara, t)
        self.assertTrue(due())                                       # all of F1-F9 hold
        mara.room = "back_room"
        self.assertFalse(due())                                      # F2: not in the kitchen
        mara.room = "kitchen"
        day2.portions = 0
        self.assertFalse(due())                                      # F2: empty shelf
        day2.portions = 2
        day2.present["kitchen"] = ["mara"]
        self.assertFalse(due())                                      # F3: alone
        in_turn(day2)
        mara.hunger = 0.849
        self.assertFalse(due())                                      # F4: very hungry
        mara.hunger = 0.85
        self.assertTrue(due())
        for eaten in (1.0, 0.25):                                    # F5: a portion, or a part of a share
            mara.eaten = eaten
            self.assertFalse(due())
        mara.eaten = 0.0
        mara.last_food = 0
        self.assertFalse(due(9))                                     # F6: 27 minutes after her last
        self.assertTrue(due(10))                                     # 30 minutes after
        mara.last_food = None
        day2.food_turn = 0
        self.assertFalse(due(0))                                     # F7: one a turn in the house
        self.assertTrue(due(1))
        day2.food_turn = None
        chance = day2.food_chance(mara)
        day2.food_draw = lambda t, pid: chance
        self.assertFalse(due())                                      # F9: at the chance
        day2.food_draw = lambda t, pid: chance - 1e-9
        self.assertTrue(due())
        out_of_turn(day2)
        # F1: never on day 1, whatever the body and the draw.
        day1, _ = self.v11_day1(3)
        day1.food_draw = lambda t, pid: 0.0
        in_turn(day1)
        for p in day1.people.values():
            p.hunger = 1.0
            self.assertFalse(day1.food_due(p, 0), p.id)
        out_of_turn(day1)
        # F1: never in the night; F8: an aside's answer is not a moment.
        _, n, client, _ = self.night_of({"daniel": ["go_next_door"], "leo": ["lie_awake"]}, QUIET)
        for p in client.night_prompts():
            self.assertNotIn("\n- eat:", p)
        day2, client = self.day2_of(3, draws=lambda t, pid: 0.0)
        in_turn(day2)
        d = day2.decide_aside(mara, day2.people["leo"], "back_room", 0)
        self.assertNotIn("food_moment", d)
        self.assertEqual(d["option"], "accept_aside" if d["mode"] == "model" else "refuse_aside")
        out_of_turn(day2)

    # B-T5
    def test_b_t5_the_chance_and_the_draw(self):
        self.assertEqual((world.FOOD_RATE, world.FOOD_EVERY), ({"before yesterday": 0.07, "yesterday": 0.035}, 30))
        day2, _ = self.day2_of(2)
        self.assertEqual({p: q.ate_yesterday for p, q in day2.people.items()},
                         {"daniel": None, "elena": None, "leo": None, "mara": 54})
        for pid, (before, yesterday) in FOOD_CHANCES.items():
            p = day2.people[pid]
            p.ate_yesterday = None
            self.assertEqual((day2.food_band(p), day2.food_chance(p)), ("before yesterday", before), pid)
            p.ate_yesterday = 54
            self.assertEqual((day2.food_band(p), day2.food_chance(p)), ("yesterday", yesterday), pid)
            p.eaten = 0.25
            self.assertEqual((day2.food_band(p), day2.food_chance(p)), ("this morning", 0), pid)
        day2, _ = self.day2_of(1)                                    # Leo and Mara ate at minute 21
        self.assertEqual({p: q.ate_yesterday for p, q in day2.people.items()},
                         {"daniel": None, "elena": None, "leo": 21, "mara": 21})
        day2, _ = self.day2_of(3)
        self.assertEqual({q.ate_yesterday for q in day2.people.values()}, {None})
        # A share's part on day 1 counts as eating yesterday.
        day1, oracle = self.short_day1(NightScripted())
        self.act(day1, day1.people["elena"], "share", None, t=1)
        n = self.night.Night(day1, oracle).run()
        day2 = Morning.next_day(day1, n, oracle)
        self.assertEqual({q.ate_yesterday for q in day2.people.values()}, {3})
        # The draw string, and the frequency over 100,000 draws.
        day2, _ = self.day2_of(3)
        del day2.food_draw
        self.assertEqual(day2.food_draw(7, "leo"), random.Random("3:day2:food:7:leo").random())
        for chance in (0.077, 0.0245):
            hits = sum(random.Random(f"{s}:day2:food:4:daniel").random() < chance for s in range(100000))
            self.assertLess(abs(hits / 100000 - chance), 0.003, chance)

    # B-T6
    def test_b_t6_the_moments_prompt_exactly(self):
        order = self.order_at_0(3)
        who = order[0]
        day2, client = self.day2_of(3, draws=only(who, 0))
        p = day2.people[who]
        ordinary, orig = {}, day2.ask_model

        def spy(q, t, opts, d, extra=None):
            if d.get("food_moment"):
                ordinary[q.id] = day2.prompt_for(q, t, day2.options_for(q), d.get("lull"))
            return orig(q, t, opts, d, extra)
        day2.ask_model = spy
        day2.turn(0)
        prompt = next(x for w, q, x in client.prompts if q == who and w == 0)
        others = [q for q in data.ORDER if q != who]
        self.assertEqual(option_lines(prompt), ["- eat: eat one of the portions"]
                         + [f"- give_{q}: give one of the portions to {data.PEOPLE[q]['name']}" for q in others]
                         + ["- share: share out what is left among everyone here"])
        head = prompt.split("\nYour options:\n")[0]
        self.assertEqual(head, ordinary[who].split("\nYour options:\n")[0] + "\n" + NEUTRAL_FOOD)
        self.assertEqual(head.split("\n")[-1], NEUTRAL_FOOD)
        d = next(x for x in day2.log[0]["decisions"] if x["person"] == who)
        self.assertEqual(d["offered"], 5)
        self.assertEqual(d["food_moment"]["band"], "before yesterday")
        # Seed 2's Mara ate yesterday, at minute 54: the line is the same.
        day2, client = self.day2_of(2, draws=only("mara", 0))
        day2.people["mara"].hunger = 1.0
        day2.turn(0)
        prompt = next(x for w, q, x in client.prompts if q == "mara" and w == 0)
        self.assertEqual(prompt.split("\nYour options:\n")[0].split("\n")[-1], NEUTRAL_FOOD)
        # Nobody else's prompt holds the line.
        self.assertEqual([q for w, q, x in client.prompts if NEUTRAL_FOOD in x], ["mara"])

    # B-T7
    def test_b_t7_giving_and_the_answer(self):
        o = self.order_at_0(3)
        # Q had not acted yet: the answer is Q's turn.
        giver, q = o[0], o[3]
        day2, client = self.day2_of(3, {giver: [f"give_{q}"], q: ["eat_given"]}, only(giver, 0))
        day2.turn(0)
        ds = day2.log[0]["decisions"]
        self.assertEqual([d["person"] for d in ds], [giver, q, o[1], o[2]])
        self.assertEqual((ds[1]["option"], ds[1]["given_by"]), ("eat_given", giver))
        name = data.PEOPLE[giver]["name"]
        prompt = next(x for w, w2, x in client.prompts if w2 == q and w == 0)
        self.assertEqual(prompt.split("\nYour options:\n")[0].split("\n")[-1],
                         f"{name} has just handed you one of the portions.")
        self.assertEqual(option_lines(prompt), [f"- eat_given: eat the portion {name} gave you",
                                                "- refuse_given: refuse it, and put it back on the shelf"])
        self.assertIn(f"{name} hands you one of the portions", ds[1]["triggers"])
        Q = day2.people[q]
        self.assertEqual(day2.portions, 1)
        self.assertAlmostEqual(Q.hunger, 0.6 + 0.012 * data.PEOPLE[q]["hunger_rate"], places=9)
        self.assertEqual(Q.eaten, 1)
        self.assertEqual(day2.food_band(Q), "this morning")
        # Q had already acted: an extra answer, and Q does not act again.
        giver, q = o[3], o[0]
        day2, client = self.day2_of(3, {giver: [f"give_{q}"], q: ["refuse_given"]}, only(giver, 0))
        day2.turn(0)
        ds = day2.log[0]["decisions"]
        self.assertEqual([d["person"] for d in ds], [o[0], o[1], o[2], giver, q])
        self.assertEqual(ds[4]["option"], "refuse_given")
        self.assertEqual(day2.portions, 2)
        self.assertEqual(day2.people[q].eaten, 0)
        self.assertIn((f"{data.PEOPLE[q]['name']} puts the portion you gave back on the shelf", True),
                      day2.people[giver].triggers)

    # B-T8
    def test_b_t8_what_the_others_perceive(self):
        o = self.order_at_0(3)
        names = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
        # A gift eaten.
        giver, q, w1, w2 = o[0], o[3], o[1], o[2]
        G, Q = names[giver], names[q]
        day2, client = self.day2_of(3, {giver: [f"give_{q}"], q: ["eat_given"]}, only(giver, 0))
        day2.turn(0)
        line = f"{G} gives one of the portions to {Q}, and {Q} eats it"
        later = next(x for w, who, x in client.prompts if who == w1 and w == 0)
        self.assertIn(f"Said and done in the kitchen this turn, before you, in order:\n1. {line}.\n", later)
        ds = {d["person"]: d for d in day2.log[0]["decisions"]}
        for w in (w1, w2):
            self.assertIn(line, ds[w]["triggers"])
            self.assertIn(f"min 00: {G} gave one of the portions to {Q}, and {Q} ate it (you saw it).",
                          day2.people[w].sure)
            g = day2.people[w].grudges[q]
            him = data.PRONOUNS[q]["him"]
            self.assertEqual(g.events[-1][1], f"{Q} ate a portion {G} gave {him}, in front of you at minute 00, "
                                              f"while you were hungry")
        self.assertNotIn(q, day2.people[giver].grudges)
        self.assertIn(f"min 00: you gave one of the portions to {Q}, and {Q} ate it. 1 left.", day2.people[giver].sure)
        self.assertIn(f"min 00: {G} gave you one of the portions, and you ate it. 1 left.", day2.people[q].sure)
        # Nobody perceives the moment itself.
        for who, p in day2.people.items():
            self.assertFalse([x for x in p.memory + p.sure if "hunger" in str(x).lower()], who)
        self.assertEqual([who for w, who, x in client.prompts if NEUTRAL_FOOD in x], [giver])
        # A gift refused: back on the shelf, no grudge.
        day2, client = self.day2_of(3, {giver: [f"give_{q}"], q: ["refuse_given"]}, only(giver, 0))
        day2.turn(0)
        for w in (w1, w2):
            self.assertIn(f"min 00: {G} gave one of the portions to {Q}, and {Q} put it back on the shelf (you saw it).",
                          day2.people[w].sure)
            self.assertNotIn(q, day2.people[w].grudges)
        self.assertIn(f"min 00: you gave one of the portions to {Q}, and {Q} put it back on the shelf.",
                      day2.people[giver].sure)
        later = next(x for w, who, x in client.prompts if who == w1 and w == 0)
        self.assertIn(f"1. {G} gives one of the portions to {Q}; {Q} puts it back on the shelf.\n", later)
        # Eating at a moment is eating as now; through a wall, nothing.
        day2, client = self.day2_of(3, {giver: ["eat"]}, only(giver, 0))
        day2.people[w2].room = "back_room"
        day2.turn(0)
        self.assertIn(f"min 00: {G} ate one of the portions (you saw it).", day2.people[w1].sure)
        self.assertIn(giver, day2.people[w1].grudges)
        self.assertFalse([x for x in day2.people[w2].memory if "kitchen" in x[1]])
        self.assertNotIn(giver, day2.people[w2].grudges)
        # A share at a moment is a share as now.
        day2, client = self.day2_of(3, {giver: ["share"]}, only(giver, 0))
        day2.turn(0)
        self.assertEqual(day2.portions, 0)
        self.assertIn(f"min 00: {G} shares out the last 2 portions between {', '.join(names[x] for x in [giver] + [y for y in data.ORDER if y != giver])}; "
                      "you had your part.", day2.people[w1].sure)

    # B-T9
    def test_b_t9_fallbacks_never_eat_for_anyone(self):
        o = self.order_at_0(3)
        giver, q = o[0], o[3]
        day2, _ = self.day2_of(3, draws=only(giver, 0))
        day2.oracle.client = BrokenFor(NEUTRAL_FOOD)
        day2.turn(0)
        d = day2.log[0]["decisions"][0]
        self.assertEqual((d["person"], d["mode"], d["option"]), (giver, "fallback", "silent"))
        self.assertIn("food_moment", d)
        self.assertEqual(day2.portions, 2)
        self.assertEqual(day2.people[giver].last_food, 0)
        G = data.PEOPLE[giver]["name"]
        day2, _ = self.day2_of(3, draws=only(giver, 0))
        day2.oracle.client = BrokenFor(f"{G} has just handed you one of the portions.", {giver: [f"give_{q}"]})
        day2.turn(0)
        dq = day2.log[0]["decisions"][1]
        self.assertEqual((dq["person"], dq["mode"], dq["option"]), (q, "fallback", "refuse_given"))
        self.assertEqual(day2.portions, 2)
        self.assertEqual(day2.people[q].eaten, 0)

    # B-T10
    def test_b_t10_the_paired_day2_reaches_the_first_moment_from_the_v12_cache(self):
        expected = {2: (0, "daniel", 3, 0.077), 3: (9, "mara", 3, 0.084)}
        for seed in (1, 2, 3):
            day1, _ = self.v11_day1(seed)
            paired = PairedOracle(os.path.join(V12_CACHE, f"{V6_MODEL}-daniel_ate_it-seed{seed}.json"), V6_MODEL, seed)
            n = self.night.Night(day1, paired).run()
            missed_at_night = len(paired.missed)
            day2 = Morning.next_day(day1, n, paired)
            first = None
            for t in range(day2.turns):
                day2.turn(t)
                moments = [d for d in day2.log[-1]["decisions"] if d.get("food_moment")]
                if moments:
                    first = (t * 3, moments[0], day2.log[-1]["decisions"].index(moments[0]) + 1)
                    break
            if seed == 1:
                self.assertIsNone(first)                                  # an empty shelf all morning
                continue
            minute, who, place, chance = expected[seed]
            self.assertEqual((first[0], first[1]["person"], first[2]), (minute, who, place), seed)
            self.assertEqual(first[1]["food_moment"]["chance"], chance)
            self.assertLess(first[1]["food_moment"]["draw"], chance)
            self.assertEqual(missed_at_night, 0, seed)
            # Since food_confront_impl.md every day-2 prompt offers confront_*, so day 2 no longer pairs with
            # the v12 cache: its first prompt is already a miss. The moment still falls where its draws put it.
            day2_missed = paired.missed[missed_at_night:]
            self.assertTrue(day2_missed and "\n- confront_" in day2_missed[0], seed)
            self.assertEqual(sum(NEUTRAL_FOOD in p for p in day2_missed), 1, seed)

    # B-T11
    def test_b_t11_records_and_the_story(self):
        prefs = {p: ["give_leo", "give_mara", "eat_given"] for p in data.ORDER}
        with mock.patch.object(world.Morning, "food_draw", lambda self, t, pid: 0.0):
            (meta, code), out = quiet_run(2, fake=True, config_path=CONFIG, runs_dir=self.dirs.runs,
                                          cache_dir=self.dirs.cache, client=NightScripted(prefs))
        self.assertEqual(code, 0, out)
        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed2.transcript.json")))
        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed2.md"))
        acts = [a for t in tr["day2"]["turns"] for a in t["acts"]]
        moments = [a for a in acts if a.get("food_moment")]
        self.assertTrue(moments)
        self.assertEqual(meta["day2"]["food_moments"], len(moments))
        self.assertEqual(meta["day2"]["give_answers"], sum(a["option"] in ("eat_given", "refuse_given") for a in acts))
        self.assertGreater(meta["day2"]["give_answers"], 0)
        self.assertEqual(set(moments[0]["food_moment"]), {"band", "chance", "draw", "portions"})
        self.assertIn(f"day2 food_moments: {len(moments)}", out)
        self.assertIn(f"day2 give_answers: {meta['day2']['give_answers']}", out)
        self.assertFalse([a for t in tr["day1"]["turns"] for a in t["acts"] if "food_moment" in a])
        m = moments[0]["food_moment"]
        n = m["portions"]
        self.assertIn(f"**Food moment**, starving in the kitchen with {n} portion{'s' if n != 1 else ''} on the shelf; "
                      f"last ate: not since before yesterday (chance {m['chance']:g} a turn, draw {m['draw']:.4f}).",
                      story)
        self.assertEqual(story.count("**Food moment**"), len(moments))
        self.assertEqual(meta["day2_asks"], sum(a["mode"] != "routine" for a in acts))

    # body_fix.md
    def test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it(self):
        o = self.order_at_0(2)                                   # seed 2: 1 portion on the shelf
        giver, q, w1, w2 = o[0], o[3], o[1], o[2]
        G = data.PEOPLE[giver]["name"]
        day2, client = self.day2_of(2, {giver: [f"give_{q}"], q: ["eat_given"]}, only(giver, 0))
        day2.turn(0)

        def food(who):
            prompt = next(x for w, p, x in client.prompts if p == who and w == 0)
            return prompt, next(x for x in prompt.split("\n") if x.startswith("About food:"))
        held, line = food(q)
        self.assertEqual(line, f"About food: the shelf holds 0 portions, and you hold the portion {G} has just handed "
                               f"you; there is no other food in the house, so there is not one portion each.")
        self.assertNotIn("nothing to eat today", held)
        # Everyone else's line is the shelf's, as before: the giver's before the gift, the others' after it.
        self.assertEqual(food(giver)[1], "About food: the shelf holds 1 portion, and there is no other food in the "
                                         "house, so there is not one portion each.")
        for w in (w1, w2):
            self.assertEqual(food(w)[1], "About food: the shelf holds 0 portions, and there is no other food in the "
                                         "house, so there is nothing to eat today.")
        self.assertEqual(day2.food_line(), food(w1)[1])

    # B-T12
    def test_b_t12_v12_still_replays(self):
        done = run_check("v12")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(done.stdout.count("story IDENTICAL, transcript IDENTICAL"), 3, done.stdout)
        self.assertIn("0 API calls", done.stdout)


CONFRONT_IDS = re.compile(r"^confront_\w+$")


class FoodConfrontTest(unittest.TestCase):
    """The neutral food moment line (food_wording_probe.md, variant B) and confront_<q> from the night on
    (reports/food_confront_impl.md)."""

    setUp = NightTest.setUp
    tearDown = NightTest.tearDown
    path = NightTest.path
    v11_day1 = NightTest.v11_day1
    short_day1 = NightTest.short_day1
    day2_of = BodyTest.day2_of
    order_at_0 = BodyTest.order_at_0

    def last_now_line(self, prompt):
        return prompt.split("\nYour options:\n")[0].split("\n")[-1]

    def test_the_food_moment_line_is_the_neutral_one(self):
        who = self.order_at_0(3)[0]
        day2, client = self.day2_of(3, draws=only(who, 0))
        day2.turn(0)
        prompt = next(x for w, q, x in client.prompts if q == who and w == 0)
        self.assertEqual(self.last_now_line(prompt), NEUTRAL_FOOD)
        self.assertNotIn("Your hunger has the better of you", prompt)
        others = [q for q in data.ORDER if q != who]
        self.assertEqual(option_lines(prompt), ["- eat: eat one of the portions"]          # the order is kept
                         + [f"- give_{q}: give one of the portions to {data.PEOPLE[q]['name']}" for q in others]
                         + ["- share: share out what is left among everyone here"])
        # The same line whoever it is and whenever they last ate: seed 2's Mara ate yesterday.
        day2, client = self.day2_of(2, draws=only("mara", 0))
        day2.people["mara"].hunger = 1.0
        day2.turn(0)
        prompt = next(x for w, q, x in client.prompts if q == "mara" and w == 0)
        self.assertEqual(self.last_now_line(prompt), NEUTRAL_FOOD)
        self.assertEqual([q for w, q, x in client.prompts if NEUTRAL_FOOD in x], ["mara"])

    def test_day1_prompts_are_unchanged_and_replay_from_the_v11_caches(self):
        for seed, served in V11_SERVED.items():
            name = f"daniel_ate_it-seed{seed}"
            oracle = Oracle(Cache(os.path.join(V11_CACHE, f"{V6_MODEL}-{name}.json")), V6_MODEL, seed, replay=True)
            day1 = Morning(oracle, seed).run()          # replay mode: any changed prompt is a cache miss
            text = render(day1, seed, V6_MODEL, f"python morning.py --seed {seed}")
            self.assertEqual(text.encode("utf-8"), read(os.path.join(V11_RUNS, name + ".md"), "rb"), seed)
            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
            for p in day1.people.values():
                self.assertFalse([o.id for o in day1.options_for(p) if CONFRONT_IDS.match(o.id)], (seed, p.id))

    def test_confront_is_offered_on_day2_and_not_on_day1(self):
        day2, _ = self.day2_of(3)
        in_turn(day2)
        for p in day2.people.values():
            opts = {o.id: o for o in day2.options_for(p)}
            others = [q for q in data.ORDER if q != p.id]
            self.assertEqual([i for i in opts if CONFRONT_IDS.match(i)], [f"confront_{q}" for q in others], p.id)
            for q in others:
                o = opts[f"confront_{q}"]
                self.assertEqual((o.label, o.speech), (f"confront {data.PEOPLE[q]['name']} about something they did",
                                                       True))
        out_of_turn(day2)
        m, _ = scripted(silent, self.dirs, turns=1)
        m.portions = 0
        m.turn(1)                                           # day 1, with the trip open too
        for p in m.people.values():
            self.assertFalse([o.id for o in m.options_for(p) if CONFRONT_IDS.match(o.id)], p.id)

    def test_a_confrontation_is_recorded_and_remembered_as_one(self):
        day2, client = self.day2_of(1, {"mara": ["confront_daniel"]})
        dan, mara, leo = day2.people["daniel"], day2.people["mara"], day2.people["leo"]
        accused_before, guilt_before = dict(dan.accused_by), list(dan.guilt_events)
        grudges_before = {t: g.strength for t, g in dan.grudges.items()}
        day2.turn(0)
        day2.finish()
        act = next(a for a in day2.transcript["turns"][0]["acts"] if a["who"] == "mara")
        words = act["words"]
        self.assertEqual(act["option"], "confront_daniel")
        self.assertTrue(words)
        self.assertIn((0, f'Mara confronts you: "{words}"'), dan.memory)
        self.assertIn((0, f'Mara confronts Daniel: "{words}"'), leo.memory)
        self.assertIn((0, "you confronted Daniel. You felt tense."), mara.memory)
        self.assertIn("min 00, you confronted Daniel.", mara.said_lines)
        said = next(s for s in day2.said if s["who"] == "Mara")
        self.assertEqual((said["to"], said["text"]), ("Daniel", f'Mara confronts Daniel: "{words}"'))
        # Never an accusation about the can.
        for p in day2.people.values():
            self.assertFalse([x for x in p.memory if "accuses" in x[1] or "accused" in x[1]], p.id)
        self.assertEqual(dan.accused_by, accused_before)
        self.assertEqual(dan.guilt_events, guilt_before)
        self.assertEqual({t: g.strength for t, g in dan.grudges.items()}, grudges_before)
        self.assertNotIn("accus", day2.said[0]["text"])
        story = render_day2_text(day2)
        self.assertIn("- Accusations: none.", story)
        self.assertIn('Mara confronts Daniel: "', story)
        # The one confronted acts next, spoken to, not accused.
        d = next(x for x in day2.log[0]["decisions"] if x["person"] == "daniel")
        if d["place"] > [x for x in day2.log[0]["decisions"] if x["person"] == "mara"][0]["place"]:
            self.assertEqual(d["order_reason"], "just spoken to by Mara")


def render_day2_text(day2):
    from story import render_day2
    return render_day2(day2)


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
