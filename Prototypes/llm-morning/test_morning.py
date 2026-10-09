"""Tests against the fake model and a stubbed API. No network, no quota.

    python -m unittest -v test_morning
"""
import contextlib
import difflib
import hashlib
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
        # The call cap counts each scene apart (reports/night_design.md, §8; days_design.md, §2.1).
        for scene in ("day1", "night", "mind1", "day2", "night2", "mind2", "day3"):
            self.assertLessEqual(meta[scene]["api_requests"], 150, scene)
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
            # From the second night on, Daniel can himself wake at the front door (reports/days_design.md): those
            # lines are the night's, not Leo's can.
            p = "\n".join(x for x in p.split("\n") if "the front door" not in x)
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
                # Day 2's forms say "yesterday", "last night" or "this morning" (reports/night_design.md, §5.3); day 3's
                # also "two days ago" and "the night before last" (reports/days_design.md, §3.5).
                day = r"(yesterday|two days ago|\w+ days ago)"
                night = r"(last night|the night before last|\w+ nights ago)"
                # Day 3 runs to 21:00: its minutes from 90 on are the clock (reports/quiet_day_fixes.md, fix 3).
                at = r"(at minutes? [\d, and]+(, and at [\d:, and]+)?|at \d\d:\d\d[\d:, and]*)"
                self.assertRegex(lines[0][:-len(" " + NOTE)],
                                 r"^About the can(: you have not settled on who took it\."
                                 rf"| \([a-z ]+\): you thought \w+ took it, {at}\."
                                 rf"| \([a-z ]+\): you thought \w+ took it(, (and )?({day} {at}"
                                 rf"|{night}|(this morning|today) {at}))*\."
                                 rf"|: \w+ admitted taking it( {day},)? at (minute \d\d|\d\d:\d\d)\.)$")
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
MEMORY_HARD = 610           # blocks A, B and C at most, once trimmed (reports/days_design.md, §3.4)
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

    def __init__(self, prefs=None, angry=None, minds=None):
        self.prefs, self.angry = prefs or {}, angry or {}
        self.minds = minds or {}    # who -> answers to their night-mind prompts, in turn (reports/days_design.md, §2)
        self.requests = 0
        self.prompts = []           # (minute or "night", who, prompt)
        self.mind_prompts = []      # (who, system, prompt, schema)

    def generate(self, system, prompt, schema=None):
        self.requests += 1
        who = re.match(r"You are (\w+),", prompt).group(1).lower()
        if schema is not None:      # a night mind: the queued answer, or one memory citing the first record
            self.mind_prompts.append((who, system, prompt, schema))
            queue = self.minds.get(who)
            if queue:
                answer = queue.pop(0)
                return answer if isinstance(answer, str) else json.dumps(answer)
            ids = re.findall(r"^\[([DN]\d+-\d+)\] ", prompt, flags=re.M)
            return json.dumps({"memories": [{"ids": ids[:1], "meaning": f"A thought of {who}, {self.requests}."}],
                               "feeling": "tired", "intent": f"Get through it, {who}."})
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
    """A day-2 or night prompt without its trip block and its carry-in block (from day 3 on, the memory blocks A, B
    and C: reports/days_design.md, §3)."""
    out, skipping = [], False
    for line in prompt.split("\n"):
        if line in (CARRY_HEAD, B_HEAD, EARLIER):
            skipping = True
            continue
        if skipping and line.startswith("- "):
            continue
        skipping = False
        if line.startswith("About water:") or line in world.W1_NOW or re.match(
                r"^- (save_water|ration_water|collect_rain|rain_out): ", line):      # W1's lines (world_design §6)
            continue
        if line.startswith(("About food:", "About the neighbour's house:", "About going there tonight:",
                            "About the street:",            # stage B's W5 line is in the trip block too
                            "About going out at night:")):  # and so is the outings line (facts_and_evening, fix 3)
            continue
        if (TRIP_OPTION_LINE.match(line)
                or re.match(r"^- (still_going|send_\w+|nobody_goes|keep_\w+_home|refuse_to_go|propose_far|"
                            r"volunteer_far): ", line)
                or any(line.startswith(f"- Day 2: {s} (") for s in TRIP_DAY2)):
            continue
        out.append(line.replace("Outside, and not to be gone to this morning:", "Outside, and not to be gone to:")
                   .replace("the street, the neighbour's house and the houses further along the street",
                            "the street and the neighbour's house")
                   .replace(data.YARD[1], data.YARD[0]))                   # W1's yard, from day 3
    return "\n".join(out)


def trimmed_to_the_end(prompt):
    """Nothing left to trim: every line of the day was cut, and no more than four lines of the days before are left
    (world.Morning.prompt_parts keeps the trip's own; reports/trip_design.md, §2.3)."""
    lines = prompt.split("\n")
    if "- (earlier things, left out here)" not in lines:
        return False
    i = lines.index("What you remember from the days before:")
    back = [x for x in lines[i + 1:] if x.startswith("- Day ")]
    return len(back) <= len(TRIP_DAY2) + 4


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
        self.assertEqual(set(tr), {"day1", "night", "mind1", "day2", "night2", "mind2", "day3", "chronicle"})

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
            # Who went, and what came home, is the house's by morning (reports/household_knowledge.md); what they
            # noticed in the night (block A, above) is still only their own.
            self.assertIn("About the neighbour's house: Daniel went there last night and came back with nothing. "
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
                                    "and he is nowhere in the house. "
                                    "(you saw it)"])        # Leo slept through it (stage B, amendment 4; where he
        # went is the house's by morning: reports/household_knowledge.md)
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
            # A second night's prompts carry day 2's blocks; every morning's blocks are bounded together at most at
            # MEMORY_HARD (reports/days_design.md, §3.4).
            if "\nNow it is night" in p:
                night_n += 1
                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + without_blocks(p)), 1450)
                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + p),
                                1450 + TRIP_BLOCK_MAX + (MEMORY_HARD if CARRY_HEAD in p else 0))
            elif CARRY_HEAD in p:
                day2_n += 1
                bare = estimate_tokens(SYSTEM + without_blocks(p))
                if bare >= 1450:
                    # A quiet day's prompt can hold more than the budget that trimming cannot touch: meeting lines,
                    # the turn's lines, grudges (reports/w1_impl.md). It must then have been trimmed to the end, and
                    # stay under the run's bound (reports/days_v21.md, T2: 2600).
                    self.assertTrue(trimmed_to_the_end(p), bare)
                    self.assertLess(estimate_tokens(SYSTEM + p), 2600)
                    continue
                self.assertLess(estimate_tokens(SYSTEM + p), 1450 + TRIP_BLOCK_MAX + MEMORY_HARD)
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
                         + meta["day2_asks"] + meta["mind1_asks"] + meta["night2_asks"] + meta["mind2_asks"]
                         + meta["day3_asks"], meta["answers_live"] + meta["answers_from_cache"])
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


NIGHT_MIND_TEXT = (
    "You write the private thoughts of one person in a family at the end of a day, once the night is over. You get who "
    "they are, what they hold against the others, what stayed with them from earlier days, and every thing they did, "
    "saw or heard today and tonight, each with an id. Nothing else happened. `memories` holds one to three things from "
    "these that they will carry: for each, `ids` lists the one to three ids it is about, and `meaning` is one sentence "
    "of their own thought about it, as they see it, in their own voice. A meaning may judge, excuse, blame, forgive or "
    "doubt, as this person would, but it must not add anything that happened beyond the records: no other event, no "
    "number, no quotation that is not in the records, and no word for when (today, tonight, yesterday, tomorrow). "
    "`feeling` names how the day leaves them, in one to three words. `intent` is what they mean to do tomorrow, in one "
    "sentence, as they would think it. Reply with JSON only: {\"memories\": [{\"ids\": [\"<id>\"], \"meaning\": "
    "\"<sentence>\"}], \"feeling\": \"<words>\", \"intent\": \"<sentence>\"}")
MIND_END = "The night is over. What does today leave in you?"
MIND_RECORDS = "What you did, saw and heard today and tonight, in order (each with its id):"
EARLIER = "What stays with you from earlier days:"
B_HEAD = "What yesterday left in you (your own thoughts, last night):"
RECORD_LINE = re.compile(r"^\[([DN]\d+-\d+)\] (min \d\d|tonight): ")
WITNESS_MODES = {"did", "saw", "heard", "voices", "knew"}
EVENT_KEYS = {"id", "scene", "minute", "kind", "option", "actor", "target", "members", "words", "room", "witnesses",
              "text", "gist", "group", "effects", "views", "outcome"}


def mind_answer(ids, meaning, feeling="tired", intent="Keep watch over them."):
    return json.dumps({"memories": [{"ids": ids, "meaning": meaning}], "feeling": feeling, "intent": intent})


class DaysTest(unittest.TestCase):
    """Days that follow one another: the night mind, the chronicle, the memory blocks and the second night and third
    morning (reports/days_design.md, tests N-T1 to N-T14 of §7.1, and the amendment to §3.3's table)."""

    setUp_ = NightTest.setUp
    tearDown = NightTest.tearDown
    path = NightTest.path
    v11_day1 = NightTest.v11_day1
    short_day1 = NightTest.short_day1
    night_of = NightTest.night_of
    act = NightTest.act

    def setUp(self):
        self.setUp_()
        self.chron = importlib.import_module("chronicle")
        self.mind = importlib.import_module("mind")
        self.memory = importlib.import_module("memory")

    def three_days(self, seed=2, client=None, draws1=None, draws2=None, day2_turns=1, day2_food=never, prefs2=None):
        """Day 1 of seed N from v11's answers, then night 1, mind 1, a short day 2, night 2, mind 2 and day 3 (not
        played), all answered by `client`. prefs2 replaces the client's preferences before night 2."""
        client = client or NightScripted()
        day1, oracle = self.v11_day1(seed, client)
        chron = self.chron.Chronicle(seed, day1.culprit)
        chron.add_day(day1)
        n1 = self.night.Night(day1, oracle, draws=draws1 or {}).run()
        chron.add_night(n1)
        self.mind.NightMind(n1, chron, oracle).run()
        day2 = Morning.next_day(day1, n1, oracle, chronicle=chron)
        day2.food_draw = day2_food
        for t in range(day2_turns):
            day2.turn(t)
        day2.finish()
        chron.add_day(day2)
        if prefs2 is not None:
            client.prefs = prefs2
        n2 = self.night.Night(day2, oracle, draws=draws2 or {}, number=2, house=chron.house_state()).run()
        chron.add_night(n2)
        self.mind.NightMind(n2, chron, oracle).run()
        day3 = Morning.next_day(day2, n2, oracle, chronicle=chron)
        return type("Days", (), dict(day1=day1, n1=n1, day2=day2, n2=n2, day3=day3, chron=chron, client=client,
                                     oracle=oracle))

    def handmade(self, events, culprit="daniel"):
        """A chronicle written by hand: each event a dict, with defaults filled by Chronicle.add."""
        c = self.chron.Chronicle(1, culprit)
        for e in events:
            c.add(e)
        return c

    # N-T1
    def test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone(self):
        for seed, served in V11_SERVED.items():
            name = f"daniel_ate_it-seed{seed}"
            day1, oracle = self.v11_day1(seed)
            chron = self.chron.Chronicle(seed, day1.culprit)
            chron.add_day(day1)
            text = render(day1, seed, V6_MODEL, f"python morning.py --seed {seed}")
            self.assertEqual(text.encode("utf-8"), read(os.path.join(V11_RUNS, name + ".md"), "rb"), seed)
            self.assertEqual(json.loads(json.dumps(day1.transcript)),
                             json.loads(read(os.path.join(V11_RUNS, name + ".transcript.json"))), seed)
            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
            self.assertTrue(chron.events and all(e["scene"] == "D1" for e in chron.events), seed)

    # N-T2
    def test_n_t2_the_cycle(self):
        (meta, code), out = fake_morning(self.dirs, seed=1)
        self.assertEqual(code, 0, out)
        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")))
        self.assertEqual(set(tr), {"day1", "night", "mind1", "day2", "night2", "mind2", "day3", "chronicle"})
        self.assertEqual([s["id"] for s in tr["chronicle"]["scenes"]], ["D1", "G1", "N1", "D2", "G2", "N2", "D3"])
        # Day 3 is no longer 30 turns: it is a quiet day, played to bedtime (reports/quiet_day_design.md, §3).
        self.assertEqual(max(s["end"] for s in tr["day3"]["quiet"]["spans"]), 840)
        # The day's 40, and Q5's own 8 on top (reports/facts_and_evening.md, fix 5).
        evening = sum(s["asks"] for s in tr["day3"]["quiet"]["stretches"] if s["trigger"] == "Q5")
        rain = sum(s["asks"] for s in tr["day3"]["quiet"]["stretches"] if s["trigger"] == "Q6")     # W1
        self.assertLessEqual(evening, 8)
        self.assertLessEqual(rain, 8)
        self.assertLessEqual(meta["day3_quiet"]["day_asks"] - evening - rain, 40)
        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.md"))
        heads = ["# The night\n", "## What the night left in them\n", "# The next morning (day 5)\n",
                 "# The second night\n", "## What the night left in them\n", "# The third morning (day 6)\n"]
        at = 0
        for h in heads:
            at = story.index(h, at) + 1
        self.assertNotIn("# The third night", story)
        for key in ("night1_asks", "mind1_asks", "day2_asks", "night2_asks", "mind2_asks", "day3_asks"):
            self.assertIn(key, meta)
        # Hunger over gap 2 and night 2; day 3 is a Morning of day 6 with the trip open from minute 00.
        d = self.three_days(seed=2)
        for pid in data.ORDER:
            rate = data.PEOPLE[pid]["hunger_rate"]
            bed = min(1.0, d.day2.people[pid].hunger + 0.3 * rate)
            self.assertAlmostEqual(d.n2.bedtime_hunger[pid], bed, places=9, msg=pid)
            self.assertAlmostEqual(d.day3.people[pid].hunger, min(1.0, bed + 0.1 * rate), places=9, msg=pid)
        self.assertEqual(d.day3.day, 6)
        self.assertEqual(d.day3.trip, {"minute": 0, "why": ["carried over from yesterday"], "asked": []})
        self.assertEqual(d.n2.number, 2)

    # N-T3
    def test_n_t3_the_night_minds_prompt_exactly(self):
        self.assertEqual(self.mind.NIGHT_MIND_SYSTEM, NIGHT_MIND_TEXT)
        d = self.three_days(seed=2)
        night1 = [x for x in d.client.mind_prompts if "[N1-" in x[2] and "[N2-" not in x[2]]
        self.assertEqual([w for w, *_ in night1], data.ORDER)
        who, system, prompt, schema = next(x for x in night1 if x[0] == "leo")
        self.assertEqual(system, NIGHT_MIND_TEXT)
        lines = prompt.split("\n")
        self.assertEqual(lines[0], "You are Leo, 21, the younger son of the family (Elena, 42, the mother; Daniel, 25; "
                                   "Leo, 21; Mara, 17).")
        for i, start in enumerate(("How you address them: ", "Who you are: ", "Temperament: ", "What matters to you: ",
                                   "Your body: ", "About the can: Daniel admitted taking it at minute 33.")):
            self.assertTrue(lines[1 + i].startswith(start), lines[1 + i])
        for gone in ("About food:", "About the neighbour's house:", "About going there tonight:"):
            self.assertFalse([x for x in lines if x.startswith(gone)], gone)
        at = lines.index(EARLIER + " nothing yet.")
        self.assertEqual(lines[at + 1], MIND_RECORDS)
        self.assertEqual(lines[-1], MIND_END)
        records = lines[at + 2:-1]
        self.assertTrue(records and all(RECORD_LINE.match(x) for x in records), records)
        ids = [RECORD_LINE.match(x).group(1) for x in records]
        self.assertEqual(ids, sorted(ids, key=lambda i: (i[0] == "N", int(i[1:].split("-")[0]), int(i.split("-")[1]))))
        self.assertEqual(records[0], "[D1-001] min 00: Elena counts the pantry with everyone standing there. She finds one "
                                     "can fewer than she expected and says so. 2 portions are left. (you saw it)")
        # R1 and R7: Daniel's three accusations of Leo, folded into the first.
        self.assertTrue([x for x in records if re.match(r'^\[D1-\d{3}\] min 03: Daniel accuses you of taking it: ".+" '
                                                        r'Then 2 more times, to min 12; last: ".+"$', x)], records)
        # R2: Leo's own words, with the feeling he gave.
        self.assertTrue([x for x in records if re.match(r'^\[D1-\d{3}\] min \d\d: you [^"]+, saying: ".+"', x)], records)
        # R3: an act seen, one record, from the pinned line; a confession heard, with its words.
        self.assertTrue([x for x in records if "min 54: Mara ate one of the portions (you saw it)" in x])
        self.assertEqual(sum("Mara ate one of the portions" in x or "Mara says to everyone, while eating" in x
                             for x in records), 1)
        self.assertIn("min 33: Daniel admitted taking the can: \"I took it in the night, I'm sorry.\" (you heard it)",
                      "\n".join(records))
        # R5: the night, in the night's own words.
        self.assertRegex(records[-1], r"^\[N1-\d\d\] tonight: You went to bed in the brothers room with Daniel\. "
                                      r"You went to sleep\.$")
        enum = schema["properties"]["memories"]["items"]["properties"]["ids"]["items"]["enum"]
        self.assertEqual(enum, ids)
        # Night 2: the earlier days are B of day 2, each line with its ids.
        who, _, prompt2, schema2 = next(x for x in d.client.mind_prompts if x[0] == "leo" and "[N2-" in x[2])
        lines2 = prompt2.split("\n")
        at = lines2.index(EARLIER)
        self.assertTrue(lines2[at + 1].startswith("- [D1-"), lines2[at + 1])
        self.assertIn('A thought of leo', lines2[at + 1])
        shown = re.findall(r"\[([DN]\d+-\d+)", "\n".join(lines2[at:]))
        self.assertEqual(schema2["properties"]["memories"]["items"]["properties"]["ids"]["items"]["enum"],
                         list(dict.fromkeys(shown)))
        # R8: at most 1,600 tokens of records; reassurances lose their words first, never the night's or a confession.
        many = [(f"D1-{i:03d}", f'min 03: Elena reassures you: "{"so very long words " * 12}"') for i in range(1, 60)]
        many += [("D1-060", 'min 33: Daniel admitted taking the can: "I took it in the night." (you heard it)'),
                 ("N1-01", 'tonight: Leo told you, low, not to go: "Do not go." You answered: "I must.", and went all '
                           'the same.')]
        bounded = self.mind.bound_records(many)
        self.assertLessEqual(estimate_tokens("\n".join(f"[{i}] {x}" for i, x in bounded)), self.mind.RECORDS_MAX)
        self.assertEqual(bounded[-2:], many[-2:])
        self.assertEqual(bounded[0][1], "min 03: Elena reassures you.")

    # N-T4
    def test_n_t4_records_hold_only_what_was_perceived(self):
        (meta, code), out = fake_morning(self.dirs, seed=3)
        self.assertEqual(code, 0, out)
        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed3.transcript.json")))
        events = {e["id"]: e for e in tr["chronicle"]["events"]}
        minds = [p for p in cached_prompts(self.dirs) if p.endswith(MIND_END)]
        self.assertTrue(minds)
        for prompt in minds:
            who = re.match(r"You are (\w+),", prompt).group(1).lower()
            for line in prompt.split("\n"):
                m = re.match(r"^\[([DN]\d+-\d+)\] ", line)
                if m:
                    self.assertIn(who, events[m.group(1)]["witnesses"], line)
                if "Voices from the" in line:
                    self.assertNotIn('"', line)
        # By day: whoever saw an act was in its room when the turn began; nobody hears into or out of the bathroom.
        for scene in ("day1", "day2", "day3"):
            k = scene[-1]
            for turn in tr[scene]["turns"]:
                for a in turn["acts"]:
                    e = next((e for e in events.values() if e["scene"] == f"D{k}" and e["minute"] == turn["minute"]
                              and e["actor"] == a["who"] and e["option"] == a["option"]), None)
                    if e is None:
                        continue
                    for w, how in e["witnesses"].items():
                        self.assertIn(how, WITNESS_MODES)
                        if how == "saw" and e["kind"] not in ("go", "aside", "accept_aside"):   # arrivals are seen
                            self.assertIn(w, turn["rooms"][a["room"]] + [a["who"]], (scene, e["id"]))
                        if how == "voices":
                            self.assertNotEqual(a["room"], "bathroom", e["id"])

    # N-T5
    def test_n_t5_the_checks(self):
        c = self.handmade([
            {"id": "D1-001", "scene": "D1", "minute": 3, "kind": "accuse", "option": "accuse_leo", "actor": "daniel",
             "target": "leo", "words": "You took it, Leo.", "witnesses": {p: "saw" for p in data.ORDER} | {"daniel": "did"}},
            {"id": "D1-002", "scene": "D1", "minute": 9, "kind": "accuse", "option": "accuse_leo", "actor": "daniel",
             "target": "leo", "words": "It was you.", "witnesses": {p: "saw" for p in data.ORDER} | {"daniel": "did"}},
            {"id": "D1-003", "scene": "D1", "minute": 21, "kind": "eat", "option": "eat", "actor": "mara",
             "witnesses": {p: "saw" for p in data.ORDER} | {"mara": "did"}},
            {"id": "D1-004", "scene": "D1", "minute": 30, "kind": "eat", "option": "eat", "actor": "leo",
             "witnesses": {p: "saw" for p in data.ORDER} | {"leo": "did"}},
            {"id": "D1-005", "scene": "D1", "minute": 30, "kind": "deny", "option": "deny", "actor": "leo",
             "words": "I did not.", "witnesses": {p: "saw" for p in data.ORDER} | {"leo": "did"}},
            {"id": "D1-006", "scene": "D1", "minute": 33, "kind": "confess", "option": "confess", "actor": "daniel",
             "words": "I took it in the night, I'm sorry.", "witnesses": {p: "saw" for p in data.ORDER} | {"daniel": "did"}},
            {"id": "N1-01", "scene": "N1", "minute": 90, "kind": "bedtime", "option": "go_next_door", "actor": "daniel",
             "witnesses": {"daniel": "did"}},
            {"id": "N1-02", "scene": "N1", "minute": 90, "kind": "stop", "option": "stop_daniel", "actor": "leo",
             "target": "daniel", "words": "Daniel, stop, you are not going out there tonight.",
             "witnesses": {"leo": "did", "daniel": "heard"}},
            {"id": "N1-03", "scene": "N1", "minute": 90, "kind": "went_out", "actor": "daniel", "members": ["daniel"],
             "witnesses": {"daniel": "did", "leo": "knew"}},
        ])
        shown = {i: f"text of {i}" for i in ("D1-001", "D1-002", "D1-003", "D1-004", "D1-005", "D1-006", "N1-02", "N1-03")}
        shown["D1-006"] = "min 33: Daniel admitted taking the can: \"I took it in the night, I'm sorry.\" (you heard it)"

        def verdict(pid, ids, meaning, carried=(), shown_ids=shown):
            r = self.mind.check_answer(mind_answer(ids, meaning), pid, shown_ids, c, carried)
            return r["memories"][0]["verdict"]

        def warned(pid, ids, meaning, shown_ids=shown):
            """S4 and S8 keep the memory and warn (reports/checks_to_warnings.md): the reasons of its warnings."""
            r = self.mind.check_answer(mind_answer(ids, meaning), pid, shown_ids, c, ())
            self.assertEqual(r["memories"][0]["verdict"], "kept", meaning)
            return [w["reason"] for w in r["warnings"] if w["of"] == "memory"]
        # §2.7's five examples.
        self.assertEqual(verdict("daniel", ["N1-02"], "Leo had no right to stop me when I was the only one willing to "
                                                     "act."), "kept")
        self.assertTrue(warned("mara", ["D1-004", "D1-005"], "Leo ate mine too and lied to my face about it.")[0]
                        .startswith("S8"))
        self.assertTrue(warned("leo", ["D1-006"], "Daniel never admitted anything until he was cornered.")[0]
                        .startswith("S8"))
        self.assertEqual(verdict("mara", ["D1-006"], "If Daniel had gone out instead of eating, we might have food."),
                         "kept")
        self.assertEqual(verdict("mara", ["D1-003"], "He hid food in his bag."), "kept")
        # One failing case for each check.
        cases = [
            ([], "He blamed me.", "S1"),
            (["D1-001", "D1-002", "D1-003", "D1-004"], "He blamed me.", "S1"),
            (["D1-001"], " ".join(["word"] * 31) + ".", "S1"),
            (["D1-001"], "He lied. He knew.", "S1"),
            (["D1-999"], "He blamed me.", "S2"),
            (["N1-01"], "He went to bed.", "S2"),
            (["D1-003"], "Mara ate two portions.", "S3"),
            (["D1-001"], "Tonight I saw who he really is.", "S5"),
            (["D1-006"], 'Daniel said "I will fix everything" and smiled.', "S6"),
            (["D1-006"], "Daniel probably hid bread somewhere.", "S7"),
        ]
        for ids, meaning, check in cases:
            got = verdict("leo", ids, meaning, shown_ids={**shown, "N1-01": "x"} if "N1-01" in ids else shown)
            self.assertTrue(got.startswith(f"rejected: {check}"), (meaning, got))
        # One warning case for each of S4 and S8: kept, with the check's reason.
        for ids, meaning, check in [(["D1-001"], "Mom never trusted me.", "S4"),
                                    (["D1-003"], "Mara stole the can.", "S8"),
                                    (["D1-003"], "Mara ate again.", "S8")]:
            got = warned("leo", ids, meaning)
            self.assertEqual(len(got), 1, (meaning, got))
            self.assertTrue(got[0].startswith(check), (meaning, got))
        self.assertEqual(verdict("leo", ["D1-001", "D1-002"], "Daniel accused me again."), "kept")
        self.assertEqual(verdict("leo", ["D1-001"], "Daniel would have let me take the blame."), "kept")
        self.assertEqual(verdict("leo", ["D1-006"], 'Daniel said "I took it in the night" at last.'), "kept")
        self.assertTrue(verdict("leo", ["D1-001"], "Daniel let me take the blame.",
                                carried=["Daniel let me take the blame."]).startswith("rejected: S9"))
        # Feeling and intent; a fourth memory is dropped unread; an answer that is not usable carries nothing.
        r = self.mind.check_answer(json.dumps({"memories": [{"ids": ["D1-001"], "meaning": "He blamed me."}] * 4,
                                               "feeling": "very very tired and sad", "intent": "Find bread for Mara."}),
                                   "leo", shown, c, ())
        self.assertEqual(len(r["memories"]), 3)
        self.assertEqual(r["memories"][0]["verdict"], "kept")
        self.assertTrue(r["memories"][1]["verdict"].startswith("rejected: S9"))
        self.assertTrue(r["feeling_verdict"].startswith("rejected"))
        self.assertTrue(r["intent_verdict"].startswith("rejected: S7"))
        self.assertEqual([m["meaning"] for m in r["kept"]], ["He blamed me."])
        r = self.mind.check_answer("not json", "leo", shown, c, ())
        self.assertEqual((r["mode"], r["kept"], r["feeling"], r["intent"]), ("fallback", [], None, None))

    # reports/v22_fixes.md, rule 1
    def test_s6_a_sentence_the_person_spoke_is_a_quotation_not_in_the_records(self):
        mine = "Risking your life doesn't give you the right to put everyone else in danger by sneaking out without a word, Daniel."
        c = self.handmade([
            {"id": "D1-006", "scene": "D1", "minute": 33, "kind": "confess", "option": "confess", "actor": "daniel",
             "words": "I took it in the night, I'm sorry.", "witnesses": {p: "saw" for p in data.ORDER} | {"daniel": "did"}},
            {"id": "D1-007", "scene": "D1", "minute": 40, "kind": "confront", "option": "confront_daniel", "actor": "leo",
             "target": "daniel", "words": mine, "witnesses": {p: "saw" for p in data.ORDER} | {"leo": "did"}},
        ])
        shown = {"D1-006": "min 33: Daniel admitted taking the can: \"I took it in the night, I'm sorry.\" (you heard it)",
                 "D1-007": f"min 40: you confronted Daniel, saying: \"{mine}\" You felt resentful."}

        def verdict(pid, meaning):
            return self.mind.check_answer(mind_answer(["D1-006" if pid != "leo" else "D1-007"], meaning), pid, shown, c, ()
                                          )["memories"][0]["verdict"]
        S6 = "rejected: S6 a quotation not in the records"
        # The person's own sentence, unquoted, quoted, or part of it quoted: the same verdict as a quotation that is
        # not in the records.
        self.assertEqual(verdict("leo", mine), S6)
        self.assertEqual(verdict("leo", f'I told Daniel "{mine}"'), S6)
        self.assertEqual(verdict("leo", 'I told Daniel "put everyone else in danger" and he did not listen.'), S6)
        self.assertEqual(verdict("daniel", "I said \"I took it in the night, I'm sorry\" and nobody answered."), S6)
        # Other people's words are as before, quoted or not, and so is the person's own gist.
        self.assertEqual(verdict("leo", 'Daniel said "I took it in the night" at last.'), "kept")
        self.assertEqual(verdict("leo", "I took it in the night, I'm sorry."), "kept")
        self.assertEqual(verdict("leo", "I told Daniel that risking his life put the rest of us in danger."), "kept")
        # The intent is held to the same rule.
        def intent(pid, text):
            return self.mind.check_answer(mind_answer(["D1-006"], "He blamed me.", intent=text), pid, shown, c, ()
                                          )["intent_verdict"]
        self.assertEqual(intent("leo", mine), S6)
        self.assertEqual(intent("leo", f'Say it again: "{mine}"'), S6)
        self.assertEqual(intent("leo", 'Ask Daniel why he said "I took it in the night".'), "kept")

    # N-T6
    def test_n_t6_the_blocks_exactly(self):
        # A on day 2 is v13's carry-in, byte for byte; B follows it.
        client = NightScripted()
        day1, oracle = self.v11_day1(3, client)
        n = self.night.Night(day1, oracle).run()
        plain = Morning.next_day(day1, n, oracle)
        d = self.three_days(seed=3)
        for p in data.ORDER:
            self.assertEqual(d.day2.carry[p][:len(plain.carry[p])], plain.carry[p], p)
            self.assertEqual(d.day2.carry[p][len(plain.carry[p])], B_HEAD, p)
        # A on day 3: yesterday's facts by the Y lines, then the night.
        d = self.three_days(seed=2, client=NightScripted({"mara": ["confront_daniel"], "leo": ["eat"]}))
        a = d.day3.blocks["mara"]["A"]
        self.assertEqual(a, [CARRY_HEAD,
                             "- Yesterday morning the shelf held 1 portion.",
                             "- Confrontations: you confronted Daniel (min 00).",
                             "- Leo ate a portion at minute 00 (you saw it).",
                             "- " + GAP,
                             "- Last night you slept in the back room with Elena. You went to sleep."])
        # B, written around the night mind's words.
        c = self.handmade([{"id": "D1-001", "scene": "D1", "minute": 33, "kind": "confess", "option": "confess",
                            "actor": "daniel", "witnesses": {"daniel": "did", "leo": "saw"}}])
        b = self.memory.block_b({"kept": [{"ids": ["D1-001"], "meaning": "He let me take the blame."}],
                                 "feeling": "bitter", "intent": "Make him answer for it."}, c, "leo")
        self.assertEqual(b, [B_HEAD, '- About Daniel admitting taking the can: "He let me take the blame."',
                             '- You meant to: "Make him answer for it."', "- How it left you: bitter."])
        # C: one line per person by weight, older on a tie, the night's words, one older thought per line.
        everyone = {p: "saw" for p in data.ORDER}
        events = [
            {"id": "D1-001", "scene": "D1", "minute": 3, "kind": "accuse", "option": "accuse_leo", "actor": "daniel",
             "target": "leo", "witnesses": everyone | {"daniel": "did"}},
            {"id": "D1-002", "scene": "D1", "minute": 3, "kind": "reassure", "option": "reassure_leo", "actor": "elena",
             "target": "leo", "witnesses": everyone | {"elena": "did"}},
            {"id": "D1-003", "scene": "D1", "minute": 9, "kind": "accuse", "option": "accuse_leo", "actor": "daniel",
             "target": "leo", "witnesses": everyone | {"daniel": "did"}},
            {"id": "D1-004", "scene": "D1", "minute": 21, "kind": "eat", "option": "eat", "actor": "mara",
             "witnesses": everyone | {"mara": "did"}},
            {"id": "D1-005", "scene": "D1", "minute": 30, "kind": "give", "option": "give_leo", "actor": "elena",
             "target": "leo", "witnesses": everyone | {"elena": "did"}},
            {"id": "D1-006", "scene": "D1", "minute": 33, "kind": "confess", "option": "confess", "actor": "daniel",
             "witnesses": everyone | {"daniel": "did"}},
            {"id": "D1-007", "scene": "D1", "minute": 36, "kind": "accuse", "option": "accuse_mara", "actor": "elena",
             "target": "mara", "witnesses": everyone | {"elena": "did"}},
            {"id": "N1-01", "scene": "N1", "minute": 90, "kind": "stop", "option": "stop_daniel", "actor": "leo",
             "target": "daniel", "witnesses": {"leo": "did", "daniel": "heard"}},
            {"id": "D2-001", "scene": "D2", "minute": 0, "kind": "eat", "option": "eat", "actor": "daniel",
             "witnesses": everyone | {"daniel": "did"}},
        ]
        c = self.handmade(events)
        c.minds[1] = {"leo": {"kept": [{"ids": ["D1-006"], "meaning": "He let me take the blame."},
                                        {"ids": ["D1-006"], "meaning": "He only spoke when cornered."}]}}
        lines = [x[2:] for x in self.memory.render_c(self.memory.block_c(c, "leo", 6))[1:]]
        self.assertEqual(lines, ['Two days ago, Daniel admitted taking the can, after accusing you of it. You thought '
                                 'then: "He only spoke when cornered."',
                                 "Two days ago, Elena reassured you.",
                                 "The night before last, you told Daniel, low, not to go.",
                                 "Two days ago, Mara ate a portion in front of you."])
        # Without the confession: the can is a standing line, and the accusations are counted.
        c = self.handmade([e for e in events if e["id"] != "D1-006"])
        lines = [x["line"] for x in self.memory.block_c(c, "leo", 6)]
        self.assertEqual(lines[:2], ["Two days ago Elena counted the pantry and found one can fewer than she expected. "
                                     "Nobody has admitted taking it.",
                                     "Two days ago, Daniel accused you of taking the can twice, and you had not."])
        # Someone not back is a standing line.
        c = self.handmade(events + [{"id": "N1-02", "scene": "N1", "minute": 90, "kind": "went_out", "actor": "mara",
                                     "members": ["mara"], "witnesses": {"mara": "did", "leo": "knew"}}])
        lines = [x["line"] for x in self.memory.block_c(c, "leo", 6, away={"mara"})]
        self.assertEqual(lines[0], "Mara went out the night before last and has not come back.")
        self.assertFalse([x for x in lines[1:] if x.startswith("Two days ago, Mara")])

    # N-T7
    def test_n_t7_the_bound(self):
        M = self.memory
        self.assertEqual(M.MEMORY_MAX, 560)
        a = [[CARRY_HEAD] + [f'- line {i}: "{"quoted words " * 6}" (min 01, 02, 03)' for i in range(9)],
             [CARRY_HEAD] + [f"- line {i}. (min 01, 02, 03)" for i in range(9)],
             [CARRY_HEAD] + [f"- line {i}." for i in range(9)]]
        b = [B_HEAD, '- About Daniel eating a portion: "' + "word " * 25 + '"', '- You meant to: "' + "word " * 25 + '"',
             "- How it left you: bitter."]
        c = [{"line": "Two days ago Elena counted the pantry. Nobody has admitted taking it.", "weight": 9,
              "standing": True, "thought": None, "self": False, "order": 0},
             {"line": "Two days ago, Daniel admitted taking the can.", "weight": 5, "standing": False,
              "thought": "He only spoke when cornered and never once said sorry to any of us at all.",
              "self": False, "order": 1},
             {"line": "Two days ago, Elena reassured you.", "weight": 3, "standing": False, "thought": None,
              "self": False, "order": 2},
             {"line": "Two days ago, you ate a portion in front of the others.", "weight": 4, "standing": False,
              "thought": None, "self": True, "order": 3}]
        full = M.bounded(a, b, c, 10 ** 6)
        size = lambda r: estimate_tokens("\n".join(r["C"] + r["A"] + r["B"]))
        steps = []
        cap = size(full)
        while True:
            r = M.bounded(a, b, c, cap - 1)
            if size(r) >= cap:
                break
            steps.append(r)
            cap = size(r)
        trail = [(r["A"] == a[0], r["A"] == a[1], r["A"] == a[2], any("You thought then" in x for x in r["C"]),
                  len(r["C"]), "- How it left you: bitter." in r["B"], any("You meant to" in x for x in r["B"]))
                 for r in steps]
        self.assertEqual(trail, [(False, True, False, True, 5, True, True),        # 1. A's quoted words
                                 (False, False, True, True, 5, True, True),        # 2. A's minutes
                                 (False, False, True, False, 5, True, True),       # 3. the older thought
                                 (False, False, True, False, 4, True, True),       # 4. lowest weight: Elena's line
                                 (False, False, True, False, 3, True, True),       # 5. then the self line (weight 4)
                                 (False, False, True, False, 2, True, True),       # 6. then Daniel's (weight 5)
                                 (False, False, True, False, 2, False, True),      # 7. B's feeling
                                 (False, False, True, False, 2, False, False)])    # 8. B's intent
        last = M.bounded(a, b, c, 0)
        self.assertIn("- Two days ago Elena counted the pantry. Nobody has admitted taking it.", last["C"])
        self.assertIn(b[1], last["B"])
        # Thirty days of everything: C keeps at most 6 lines, the blocks at most 610, the prompt at most 2,420.
        events, kinds = [], [("accuse", "accuse_leo", "leo"), ("eat", "eat", None), ("reassure", "reassure_leo", "leo"),
                             ("sit", "sit_leo", "leo"), ("confront", "confront_leo", "leo"), ("give", "give_leo", "leo")]
        for day in range(1, 31):
            for i, (kind, option, target) in enumerate(kinds):
                for actor in ("daniel", "elena", "mara", "leo"):
                    if actor == target:
                        continue
                    events.append({"id": f"D{day}-{len(events) + 1:03d}", "scene": f"D{day}", "minute": 3 * i,
                                   "kind": kind, "option": option, "actor": actor, "target": target,
                                   "witnesses": {p: "saw" for p in data.ORDER} | {actor: "did"}})
            events.append({"id": f"N{day}-01", "scene": f"N{day}", "minute": 90, "kind": "went_out", "actor": "daniel",
                           "members": ["daniel"], "witnesses": {"daniel": "did", "leo": "knew"}})
        c = self.handmade(events)
        items = M.block_c(c, "leo", 3 + 33)
        self.assertLessEqual(len(items), 6)
        big_a = [CARRY_HEAD] + [f"- {'fact ' * 20}{i}." for i in range(12)]
        big_a = [big_a[:1 + 11]] * 3
        self.assertGreater(estimate_tokens("\n".join(big_a[0])), 300)
        big_b = [B_HEAD] + [f'- About Daniel eating a portion: "{"word " * 29}end."'] * 3 + \
                [f'- You meant to: "{"word " * 29}end."', "- How it left you: very tired."]
        r = M.bounded(big_a, big_b, items, M.MEMORY_MAX)
        self.assertLessEqual(estimate_tokens("\n".join(r["C"] + r["A"] + r["B"])), 610)
        d = self.three_days(seed=2)
        leo = d.day3.people["leo"]
        d.day3.carry["leo"] = r["C"] + r["A"] + r["B"]
        leo.memory += [(0, f"filler line number {i} " + "about nothing much at all " * 12) for i in range(200)]
        self.assertLessEqual(estimate_tokens(SYSTEM + d.day3.prompt_for(leo, 0, d.day3.options_for(leo))), 2420)

    # N-T8
    def test_n_t8_day_words(self):
        w = world.when_words
        self.assertEqual([w(s, 6) for s in (("D", 2), ("N", 2), ("D", 1), ("N", 1))],
                         ["yesterday", "last night", "two days ago", "the night before last"])
        self.assertEqual([w(s, 7) for s in (("D", 1), ("N", 1), ("D", 2), ("N", 2))],
                         ["three days ago", "three nights ago", "two days ago", "the night before last"])
        d = self.three_days(seed=2, client=NightScripted({"daniel": ["go_next_door"]}, angry={"leo": "Daniel"}),
                            draws1={**QUIET, "house": 0.1}, prefs2={})
        leo, dan = d.day3.people["leo"], d.day3.people["daniel"]
        text = d.day3.prompt_for(leo, 0, d.day3.options_for(leo))
        self.assertIn("About the can: Daniel admitted taking it two days ago, at minute 33.", text)
        self.assertIn("Against Daniel (a lot): two days ago, Daniel accused you of taking the can at minute", text)
        self.assertRegex(text, r"you were angry with Daniel two days ago at minutes? ")
        self.assertNotIn("yesterday, yesterday", text)
        for p in d.day3.people.values():
            for g in p.grudges.values():
                for e in g.events:
                    self.assertFalse(e[1].startswith(("yesterday, yesterday", "two days ago, yesterday")), e)
        lines = d.day3.inside_lines(dan)
        self.assertIn("About the can: you ate it yourself, and you admitted it two days ago.", lines)
        self.assertIn("About the neighbour's house: you went in the night before last and found no food there. Outside is "
                      "dangerous.", lines)
        conscience = next(x for x in lines if x.startswith("On your conscience"))
        self.assertIn("two days ago, you accused Leo of what you did, at minute 03", conscience)
        # Suspicion minutes keep the day they were named on.
        mara = d.day3.people["mara"]
        mara.knows_culprit, mara.confessed = None, False
        mara.suspicion.target, mara.suspicion.strength = "leo", 1
        mara.suspected_past = [(("D", 1), [3]), (("N", 2), True)]
        mara.suspected_at = [3]
        about = next(x for x in d.day3.inside_lines(mara) if x.startswith("About the can"))
        self.assertEqual(about, "About the can (a little): you thought Leo took it, two days ago at minute 03, and last "
                                "night, and this morning at minute 03.")

    # N-T9
    def test_n_t9_the_chronicle(self):
        (meta, code), out = fake_morning(self.dirs, seed=1)
        self.assertEqual(code, 0, out)
        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")))
        ch = tr["chronicle"]
        for e in ch["events"]:
            # A routine span and a need crossing carry their own fields too (reports/quiet_day_design.md, §3).
            quiet_keys = set(self.chron.QUIET_KEYS) if e["kind"] in ("routine", "need") else set()
            self.assertLessEqual(set(e), EVENT_KEYS | quiet_keys, e)
            self.assertTrue(set(e["witnesses"].values()) <= WITNESS_MODES, e)
        ids = [e["id"] for e in ch["events"]]
        self.assertEqual(len(ids), len(set(ids)))
        # Every model act that is not silence is an event of its day, with its actor as `did`.
        for k, scene in ((1, "day1"), (2, "day2"), (3, "day3")):
            for turn in tr[scene]["turns"]:
                for a in turn["acts"]:
                    if a["mode"] != "model" or a["option"] == "silent":
                        continue
                    e = [e for e in ch["events"] if e["scene"] == f"D{k}" and e["minute"] == turn["minute"]
                         and e["actor"] == a["who"] and e["option"] == a["option"]]
                    self.assertEqual(len(e), 1, (scene, turn["minute"], a["who"], a["option"]))
                    self.assertEqual(e[0]["witnesses"][a["who"]], "did")
        # Run again: the same chronicle, byte for byte.
        dirs = Dirs()
        try:
            (meta2, code2), out2 = fake_morning(dirs, seed=1)
            self.assertEqual(code2, 0, out2)
            tr2 = json.loads(read(os.path.join(dirs.runs, "daniel_ate_it-seed1.transcript.json")))
            self.assertEqual(json.dumps(tr2["chronicle"]), json.dumps(ch))
        finally:
            dirs.cleanup()
        # The neighbour's house is fixed once, at the first entry, and night 2 finds what night 1 left.
        draws = {**QUIET, "house": 0.95, "trip:daniel": 0.1}
        d = self.three_days(seed=2, client=NightScripted({"daniel": ["go_next_door"]}), draws1=draws, draws2=draws)
        self.assertEqual((d.n1.house, d.n1.house_left), (6, 3))
        self.assertEqual(d.chron.fixed["neighbour_house"]["scene"], "N1")
        self.assertEqual(d.chron.fixed["neighbour_house"]["value"], 6)
        self.assertEqual(d.chron.fixed["neighbour_house"]["string"], "2:night:house")
        self.assertEqual((d.n2.groups[0]["found"], d.n2.groups[0]["took"], d.n2.house_left), (3, 3, 0))
        # The draw strings (§4.4).
        self.assertEqual((d.n1.draw_string("trip:daniel"), d.n2.draw_string("trip:daniel"), d.n2.draw_string("house")),
                         ("2:night:trip:daniel", "2:night2:trip:daniel", "2:night:house"))
        self.assertEqual((d.day1.order_string(4, "kitchen"), d.day2.order_string(4, "kitchen"),
                          d.day3.order_string(4, "kitchen")), ("2:4:kitchen", "2:4:kitchen", "2:day3:4:kitchen"))
        self.assertEqual((d.day2.food_string(4, "leo"), d.day3.food_string(4, "leo")),
                         ("2:day2:food:4:leo", "2:day3:food:4:leo"))
        self.assertIn("culprit", d.chron.fixed)

    # N-T10
    def test_n_t10_thoughts_stay_private(self):
        (meta, code), out = fake_morning(self.dirs, seed=2)
        self.assertEqual(code, 0, out)
        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed2.transcript.json")))
        prompts = cached_prompts(self.dirs)
        kept = [(pid, m["meaning"]) for night in ("mind1", "mind2") for pid, r in tr[night].items()
                for m in r["memories"] if m["verdict"] == "kept"]
        self.assertTrue(kept)
        for pid, meaning in kept:
            holders = {re.match(r"You are (\w+),", p).group(1).lower() for p in prompts if f'"{meaning}"' in p}
            self.assertLessEqual(holders, {pid}, meaning)

    # N-T11
    def test_n_t11_the_plan_line_says_you_are(self):
        client = NightScripted()
        day1, oracle = self.v11_day1(3, client)
        n = self.night.Night(day1, oracle).run()
        day2 = Morning.next_day(day1, n, oracle)
        ele, leo = day2.people["elena"], day2.people["leo"]
        self.act(day2, ele, "send_leo", "Leo should.")
        plan = next(x for x in day2.inside_lines(leo) if x.startswith("About going there tonight:"))
        self.assertEqual(plan, "About going there tonight: Elena said you are the one who should go (min 00).")
        plan = next(x for x in day2.inside_lines(day2.people["mara"]) if x.startswith("About going there tonight:"))
        self.assertEqual(plan, "About going there tonight: Elena said Leo is the one who should go (min 00).")

    # N-T12
    def test_n_t12_schema_plumbing(self):
        class Spy:
            requests = 0

            def __init__(self):
                self.calls = []

            def generate(self, system, prompt, schema=None):
                self.calls.append(schema)
                self.requests += 1
                return "{}"
        spy = Spy()
        oracle = Oracle(Cache(self.path("spy")), "fake", 1, client=spy)
        oracle.ask("s", "p1")
        oracle.ask("s", "p2", schema={"type": "object"})
        self.assertEqual(spy.calls, [None, {"type": "object"}])
        self.assertEqual(Cache.key("m", 1, "s", "p"), frozen("v13", "gemini").Cache.key("m", 1, "s", "p"))
        # The API gets RESPONSE_SCHEMA for decisions and the night mind's own for a night mind.
        seen = []

        class Api(StubApi):
            def generate_content(self, model, contents, config):
                seen.append(config.response_schema)
                return super().generate_content(model, contents, config)
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": SECRET}):
            client = GeminiClient({**json.loads(read(CONFIG)), "min_seconds_between_calls": 0}, 1, api=Api([]),
                                  sleep=lambda s: None)
            client.generate("s", "You are Leo, 21\nYour options:\n- silent: stay put")
            schema = self.mind.schema(["D1-001", "N1-01"])
            client.generate("s", "You are Leo, 21\n[D1-001] min 00: x\n" + MIND_END, schema=schema)
        self.assertEqual(seen, [gemini.RESPONSE_SCHEMA, schema])
        self.assertEqual(schema["properties"]["memories"]["items"]["properties"]["ids"]["items"]["enum"],
                         ["D1-001", "N1-01"])
        self.assertEqual(set(schema["required"]), {"memories", "feeling", "intent"})
        # The fake answers a night mind in shape, citing ids of the prompt, and breaks every n-th answer.
        fake = FakeClient(invalid_every=2)
        prompt = "You are Leo, 21\n[D1-001] min 00: x\n[N1-01] tonight: y\n" + MIND_END
        good = json.loads(fake.generate("s", prompt, schema=schema))
        self.assertTrue(good["memories"] and set(good["memories"][0]["ids"]) <= {"D1-001", "N1-01"})
        self.assertTrue(good["feeling"] and good["intent"])
        bad = fake.generate("s", prompt, schema=schema)
        c = self.handmade([{"id": "D1-001", "scene": "D1", "minute": 0, "kind": "opening", "actor": "elena",
                            "witnesses": {"leo": "saw", "elena": "did"}},
                           {"id": "N1-01", "scene": "N1", "minute": 90, "kind": "bedtime", "actor": "leo",
                            "witnesses": {"leo": "did"}}])
        r = self.mind.check_answer(bad, "leo", {"D1-001": "x", "N1-01": "y"}, c, ())
        self.assertTrue(r["mode"] == "fallback" or not r["kept"], r)

    # N-T13
    def test_n_t13_counting(self):
        (meta, code), out = fake_morning(self.dirs, seed=1)
        self.assertEqual(code, 0, out)
        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")))
        self.assertEqual(meta["night1_asks"], len(tr["night"]["decisions"]))
        self.assertEqual(meta["night2_asks"], len(tr["night2"]["decisions"]))
        self.assertEqual(meta["mind1_asks"], len(tr["mind1"]))
        self.assertEqual(meta["mind2_asks"], len(tr["mind2"]))
        self.assertEqual(meta["day2_asks"], sum(a["mode"] != "routine" for t in tr["day2"]["turns"] for a in t["acts"]))
        # Day 3 has a budget (quiet.py, §4): a decision made after it is spent, an aside's answer in the same turn,
        # is a fallback that asked nobody. Q5's stretch has its own (reports/facts_and_evening.md, fix 5).
        unasked = len(re.findall(r"could not be used \((this stretch's \d+|the day's \d+|the evening's \d+) asks are "
                                 r"spent\)",
                                 read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.md"))))
        self.assertEqual(meta["day3_asks"],
                         sum(a["mode"] != "routine" for t in tr["day3"]["turns"] for a in t["acts"]) - unasked)
        total = (meta["day1"]["model_decisions"] + meta["day1"]["fallbacks"] + meta["night1_asks"] + meta["mind1_asks"]
                 + meta["day2_asks"] + meta["night2_asks"] + meta["mind2_asks"] + meta["day3_asks"])
        self.assertEqual(total, meta["answers_live"] + meta["answers_from_cache"])
        for k in ("mind1", "mind2"):
            m = meta[k]
            self.assertEqual(m["memories_proposed"], m["memories_kept"] + m["memories_rejected"])
            self.assertEqual(m["memories_proposed"], sum(len(r["memories"]) for r in tr[k].values()))
        for key in ("night2_asks", "mind1_asks", "mind2_asks", "day3_asks"):
            self.assertIn(f"{key}: {meta[key]}", out)

    # N-T14
    def test_n_t14_frozen_versions_still_replay(self):
        for version in ("v14", "v13", "v12", "v11", "v10", "v9"):
            done = run_check(version)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertEqual(done.stdout.count("story IDENTICAL, transcript IDENTICAL"), 3, done.stdout)
            self.assertIn("0 API calls", done.stdout)

    # The amendment to §3.3's table C2: the kind acts between two people, at weight 3.
    def test_amendment_kind_acts_between_two_people(self):
        M = self.memory
        self.assertEqual(M.KIND_ACTS, ("reassure", "sit"))
        self.assertEqual({k: M.WEIGHT[k] for k in M.KIND_ACTS}, {"reassure": 3, "sit": 3})
        everyone = {p: "saw" for p in data.ORDER}
        c = self.handmade([
            {"id": "D1-001", "scene": "D1", "minute": 3, "kind": "reassure", "option": "reassure_all", "actor": "daniel",
             "witnesses": everyone | {"daniel": "did"}},
            {"id": "D1-002", "scene": "D1", "minute": 6, "kind": "sit", "option": "sit_leo", "actor": "elena",
             "target": "leo", "witnesses": everyone | {"elena": "did"}},
            {"id": "D1-003", "scene": "D1", "minute": 9, "kind": "reassure", "option": "reassure_leo", "actor": "elena",
             "target": "leo", "witnesses": everyone | {"elena": "did"}},
            {"id": "D1-004", "scene": "D1", "minute": 12, "kind": "reassure", "option": "reassure_mara", "actor": "leo",
             "target": "mara", "witnesses": everyone | {"leo": "did"}},
            {"id": "D1-005", "scene": "D1", "minute": 15, "kind": "reassure", "option": "reassure_mara", "actor": "leo",
             "target": "mara", "witnesses": everyone | {"leo": "did"}},
            {"id": "D1-006", "scene": "D1", "minute": 18, "kind": "confess", "option": "confess", "actor": "daniel",
             "witnesses": everyone | {"daniel": "did"}},
        ])
        lines = [x["line"] for x in M.block_c(c, "leo", 6)]
        self.assertEqual(lines, ["Two days ago, Daniel admitted taking the can.",
                                 "Two days ago, Elena sat with you.",              # a tie at 3 keeps the older
                                 "Two days ago, you reassured Mara twice."])
        lines = [x["line"] for x in M.block_c(c, "mara", 6)]
        self.assertIn("Two days ago, Leo reassured you twice.", lines)
        # Reassuring everyone is not an act between two people: Daniel's line is his confession, and nobody's
        # line comes from reassure_all.
        self.assertFalse([x for p in data.ORDER for x in M.block_c(c, p, 6) if "D1-001" in x["ids"]])

    # The pattern rule (reports/c_patterns.md): the same act, 3 or more times in one day, is a C line.
    def test_c_pattern_seed3_day1_denials_and_questions(self):
        """v15 seed 3's day 1 was Daniel's denials and Mara's "who took it?", none in the table: on day 3 every C
        keeps both, with the counts of the chronicle."""
        M = self.memory
        tr = json.loads(read(os.path.join(HERE, "runs", "v15", "daniel_ate_it-seed3.transcript.json")))
        c = self.chron.Chronicle(3, tr["chronicle"]["fixed"]["culprit"]["value"])
        for e in tr["chronicle"]["events"]:
            c.add(e)
        count = lambda who, option: sum(e["scene"] == "D1" and e["actor"] == who and e["option"] == option
                                        for e in c.events)
        denied, asked, elena_asked = count("daniel", "deny"), count("mara", "ask_who"), count("elena", "ask_who")
        self.assertEqual((denied, asked, elena_asked), (6, 6, 3))
        n = lambda k: M.times(k).strip()
        for pid in data.ORDER:
            lines = [x[2:] for x in M.render_c(M.block_c(c, pid, 6))[1:]]
            d = "you denied" if pid == "daniel" else "Daniel denied"
            a = "you asked" if pid == "mara" else "Mara asked"
            e = "you asked" if pid == "elena" else "Elena asked"
            self.assertIn(f"Two days ago, {d} taking the can {n(denied)}.", lines, pid)
            self.assertIn(f"Two days ago, {a} who took the can {n(asked)}.", lines, pid)
            self.assertIn(f"Two days ago, {e} who took the can {n(elena_asked)}.", lines, pid)
        self.assertEqual({M.WEIGHT[k] for k in M.PATTERNS}, {M.WEIGHT["accuse"]})

    def test_c_pattern_not_at_two_repeats(self):
        from talk import act_of
        M = self.memory
        everyone = {p: "saw" for p in data.ORDER}
        acts = [("D1", "daniel", "deny"), ("D1", "mara", "ask_who"), ("D1", "mara", "search"),
                ("D1", "daniel", "deny"), ("D1", "mara", "ask_who"), ("D1", "mara", "search"),
                ("D1", "leo", "search"), ("D1", "leo", "keep_searching"), ("D1", "leo", "keep_searching"),
                ("D2", "daniel", "deny"), ("D2", "mara", "ask_who"), ("D2", "mara", "search")]
        c = self.handmade([{"id": f"{scene}-{i:03d}", "scene": scene, "minute": 3 * i, "kind": act_of(option)[0],
                            "option": option, "actor": who, "witnesses": everyone | {who: "did"}}
                           for i, (scene, who, option) in enumerate(acts, 1)])
        # Day 1: Daniel denied twice, Mara asked twice and started two searches, Leo started one search and carried
        # it on twice. Day 2: one more of each, so three in all over two days, never three in one day.
        people = lambda day: [x["line"] for p in data.ORDER for x in M.block_c(c, p, day) if not x["standing"]]
        self.assertEqual(people(6), [])
        self.assertEqual(people(7), [])


class CheckErrorsTest(unittest.TestCase):
    """The night-mind checks on v15's own answers (reports/check_errors.md): each answer is checked again on the input
    it had, i.e. the records its prompt showed (from cache/v15, read only), the chronicle up to that night and the
    meanings it already carried. The four check errors of reports/days_v15.md §4 now keep a true thought, and the two own
    sentences of Mara's now fail S6; every other verdict stays as v15 gave it."""
    # Plus, from reports/v22_fixes.md (rule 1): two memories of Mara's (seed 1, night 2) that were her own spoken
    # sentences, kept in v15 and now rejected by S6.
    FIXED = {(1, 1, "elena", 1), (3, 2, "elena", 1), (1, 2, "daniel", 2), (1, 1, "mara", "intent"),
             (1, 2, "mara", 1), (1, 2, "mara", 2)}
    @classmethod
    def setUpClass(cls):
        cls.mind = importlib.import_module("mind")
        cls.chron = importlib.import_module("chronicle")
        cls.runs = cls.load("v15")

    @staticmethod
    def load(version):
        """seed -> (transcript, cache) of a live run, read only."""
        runs = {}
        for seed in (1, 2, 3):
            tr = json.loads(read(os.path.join(HERE, "runs", version, f"daniel_ate_it-seed{seed}.transcript.json")))
            cache = json.loads(read(os.path.join(HERE, "cache", version,
                                                 f"gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json")))
            runs[seed] = (tr, cache)
        return runs

    def inputs(self, seed, k, pid):
        """(the run's record of this night mind, the records its prompt showed, the chronicle up to that night, the
        meanings it already carried)."""
        tr, cache = self.runs[seed]
        rec = tr[f"mind{k}"][pid]
        prompts = [e["prompt"] for e in cache.values()
                   if e["response"] == rec["answer"] and e["prompt"].startswith(f"You are {world.NAMES[pid]},")]
        self.assertEqual(len(prompts), 1, (seed, k, pid))
        shown = {}
        for line in prompts[0].split("\n"):
            m = re.match(r"^(?:- )?\[([A-Z0-9, -]+)\] (.*)$", line)
            if m:
                for i in m.group(1).split(", "):
                    shown.setdefault(i, m.group(2))
        c = self.chron.Chronicle(seed, tr["chronicle"]["fixed"]["culprit"]["value"])
        for e in tr["chronicle"]["events"]:
            if int(e["scene"][1:]) <= k:
                c.add(e)
        carried = [m["meaning"] for j in range(1, k) for m in tr[f"mind{j}"][pid]["memories"] if m["verdict"] == "kept"]
        return rec, shown, c, carried

    def checked(self, seed, k, pid):
        """(the run's record of this night mind, its answer checked again now)."""
        rec, shown, c, carried = self.inputs(seed, k, pid)
        return rec, self.mind.check_answer(rec["answer"], pid, shown, c, carried)

    def memory(self, seed, k, pid, i, meaning, v15_verdict):
        rec, r = self.checked(seed, k, pid)
        self.assertEqual((rec["memories"][i]["meaning"], rec["memories"][i]["verdict"]), (meaning, v15_verdict))
        return r["memories"][i]["verdict"]

    # 1. Seed 1, mind 1, Elena: "found Daniel's bed empty" (N1-08) is not finding food.
    def test_found_is_not_finding_food(self):
        self.assertEqual(self.memory(1, 1, "elena", 1, "I heard the front door open in the night and found Daniel's "
                                     "bed empty before he returned with nothing in his hands.",
                                     "rejected: S8 elena find: no such event"), "kept")

    # 2. Seed 3, mind 2, Elena: "my children took risks" is not taking food.
    def test_took_risks_is_not_taking_food(self):
        self.assertEqual(self.memory(3, 2, "elena", 1, "Someone went out into the dark and came back before dawn and "
                                     "I stayed in bed while my children took risks.",
                                     "rejected: S8 elena take: no such event"), "kept")

    # 3. Seed 1, mind 2, Daniel: N2-01 reads "You went to bed in the brothers room with Leo".
    def test_a_name_in_the_cited_record_counts(self):
        self.assertEqual(self.memory(1, 2, "daniel", 2, "I lay awake in the dark with Leo, listening and starving, "
                                     "knowing the responsibility is mine alone.", "rejected: S4 Leo"), "kept")

    # 4. Seed 1, mind 1, Mara's intent: "came back with nothing" is part of what she means to ask, not an event.
    def test_coming_back_in_an_intent_is_not_an_event(self):
        rec, r = self.checked(1, 1, "mara")
        intent = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", rec["answer"].strip()))["intent"]
        self.assertEqual((intent, rec["intent_verdict"]),
                         ("I am going to ask Daniel why he went out into the night and came back with nothing.",
                          "rejected: S8 mara come back: no such event"))
        self.assertEqual(r["intent_verdict"], "kept")

    # The narrowed rules still catch what they are for, on the same input: seed 1, night 1, Elena. Leo did not go out
    # and found nothing; he did not take the can (Daniel did, and confessed). S8 now warns and keeps
    # (reports/checks_to_warnings.md): what it catches is the warning's reason.
    def test_false_finds_thefts_and_events_in_intents_are_still_caught(self):
        rec, shown, c, carried = self.inputs(1, 1, "elena")
        leo = next(i for i, t in shown.items() if "Leo" in t)

        def verdict(meaning):
            warnings = []
            v = self.mind.check_memory({"ids": [leo], "meaning": meaning}, "elena", shown, c, carried, warnings)
            return v, warnings

        def warned(reason, text):
            return "kept", [{"of": "memory", "text": text, "reason": reason}]
        for text, reason in [("Leo found food at the neighbour's house.", "S8 leo find: no such event"),
                             ("Leo found nothing there.", "S8 leo find: no such event"),
                             ("Leo took the can.", "S8 leo take: no such event"),
                             ("Leo took risks and took the can.", "S8 leo take: no such event")]:
            self.assertEqual(verdict(text), warned(reason, text))

        def intent(text):
            warnings = []
            return self.mind.intent_verdict(text, "elena", shown, c, warnings), warnings
        text = "I will ask Leo why, because Leo took the can."
        self.assertEqual(intent(text), ("kept", [{"of": "intent", "text": text,
                                                  "reason": "S8 leo take: no such event"}]))
        # "came back" has no subject of its own, but the clause before it is no plan: it is still read as Leo's act.
        text = "Leo went out and came back, so I will thank him."
        self.assertEqual(intent(text), ("kept", [{"of": "intent", "text": text, "reason": "S8 leo go out: no such "
                                                  "event; leo come back: no such event"}]))

    # Every other v15 verdict, the six right rejections included, is what v15 gave.
    def test_every_other_v15_verdict_stands(self):
        rejected = []
        for seed in (1, 2, 3):
            for k in (1, 2):
                for pid in self.runs[seed][0][f"mind{k}"]:
                    rec, r = self.checked(seed, k, pid)
                    pairs = [(i, m["verdict"], g["verdict"]) for i, (m, g) in enumerate(zip(rec["memories"],
                                                                                            r["memories"]))]
                    pairs.append(("intent", rec["intent_verdict"], r["intent_verdict"]))
                    for i, was, now in pairs:
                        if (seed, k, pid, i) in self.FIXED:
                            continue
                        self.assertEqual(now, was, (seed, k, pid, i))
                        if was != "kept":
                            rejected.append((seed, k, pid, i, now))
        self.assertEqual(rejected, [(1, 2, "mara", 0, "rejected: S9 a repeat"),
                                    (2, 1, "daniel", 1, "rejected: S5 tonight"),
                                    (2, 2, "daniel", 1, "rejected: S5 tonight"),
                                    (2, 2, "elena", 1, "rejected: S5 tonight"),
                                    (2, 2, "leo", 0, "rejected: S5 yesterday"),
                                    (3, 1, "elena", 0, "rejected: S3 one")])


class WarningFake(FakeClient):
    """The fake model, whose night minds each hold a false theft by Mara (worded apart each night, so S9 lets the
    second through) and a false event in the intent."""
    MEANINGS = ("Mara stole the can.", "Mara stole the can from us all.")
    INTENT = "I will ask Leo why, because Leo took the can."

    def __init__(self, **k):
        super().__init__(**k)
        self.nights = {}

    def mind(self, prompt):
        who = re.match(r"You are (\w+),", prompt).group(1)
        answer = json.loads(super().mind(prompt))
        answer["memories"][0]["meaning"] = self.MEANINGS[self.nights.get(who, 0)]
        self.nights[who] = self.nights.get(who, 0) + 1
        answer["intent"] = self.INTENT
        return json.dumps(answer)


class ChecksToWarningsTest(unittest.TestCase):
    """S4 (a name the cited records do not hold) and S8 (a claim of fact the chronicle does not hold) warn instead of
    rejecting (reports/checks_to_warnings.md): over v15 and v16 they rejected six true memories and no false one. The
    memory or intent is kept, and the run log says what was doubted and why. S2, S3, S5 and S9 still reject."""

    @classmethod
    def setUpClass(cls):
        cls.mind = importlib.import_module("mind")
        cls.chron = importlib.import_module("chronicle")
        cls.v15, cls.v16 = CheckErrorsTest.load("v15"), CheckErrorsTest.load("v16")

    def checked(self, runs, seed, k, pid):
        """(the run's record of this night mind, its answer checked again now)."""
        self.runs = runs
        rec, shown, c, carried = CheckErrorsTest.inputs(self, seed, k, pid)
        return rec, self.mind.check_answer(rec["answer"], pid, shown, c, carried)

    # v16, seed 1, mind 2 (reports/days_v16.md, §6): Leo's "empty-handed" was read as Daniel handing something over,
    # and Daniel's "again" as Elena stopping him twice. Both are true (D2-008: "coming back with nothing"; D2-004:
    # "please do not go out there again"). Each is kept now, and the run log carries its warning.
    def test_v16_empty_handed_and_again_are_kept_with_a_warning(self):
        cases = [("leo", 0, "Daniel thinks grand promises make up for reckless risks, but coming back empty-handed "
                            "solves nothing.", "S8 daniel give: no such event"),
                 ("daniel", 1, "Mom told me not to go out into the dark again and that we will get through this "
                               "together inside.", "S8 elena stop: not twice")]
        results, lines = {}, []
        for pid, i, meaning, reason in cases:
            rec, r = self.checked(self.v16, 1, 2, pid)
            self.assertEqual((rec["memories"][i]["meaning"], rec["memories"][i]["verdict"]),
                             (meaning, "rejected: " + reason))
            self.assertEqual(r["memories"][i]["verdict"], "kept")
            self.assertIn(meaning, [m["meaning"] for m in r["kept"]])
            self.assertEqual(r["warnings"], [{"of": "memory", "text": meaning, "reason": reason}])
            results[pid] = r
            lines.append(f'  night 2, the night mind: warning, {world.NAMES[pid]}\'s memory kept: "{meaning}" '
                         f"({reason})")
        self.assertEqual(self.mind.warning_lines(2, results), lines)

    # The other checks still reject, on v15's real cases: S3 (a number), S5 (a word for when), S9 (a repeat). v15 and
    # v16 hold no S2 rejection, so S2 is shown on v15's real input: Elena cites N1-12, Daniel's walk in the street,
    # which she did not perceive.
    def test_s2_s3_s5_s9_still_reject_their_v15_cases(self):
        cases = [(3, 1, "elena", 0, "rejected: S3 one"),
                 (2, 1, "daniel", 1, "rejected: S5 tonight"),
                 (2, 2, "daniel", 1, "rejected: S5 tonight"),
                 (2, 2, "elena", 1, "rejected: S5 tonight"),
                 (2, 2, "leo", 0, "rejected: S5 yesterday"),
                 (1, 2, "mara", 0, "rejected: S9 a repeat")]
        for seed, k, pid, i, verdict in cases:
            rec, r = self.checked(self.v15, seed, k, pid)
            self.assertEqual((rec["memories"][i]["verdict"], r["memories"][i]["verdict"]), (verdict, verdict))
            self.assertNotIn(rec["memories"][i]["meaning"], [m["meaning"] for m in r["kept"]])
            self.assertNotIn(rec["memories"][i]["meaning"], [w["text"] for w in r["warnings"]])
        self.runs = self.v15
        rec, shown, c, carried = CheckErrorsTest.inputs(self, 1, 1, "elena")
        self.assertNotIn("N1-12", shown)
        self.assertNotIn("elena", c.event("N1-12")["witnesses"])
        warnings = []
        self.assertEqual(self.mind.check_memory({"ids": ["N1-12"], "meaning": "Daniel went out in the dark."},
                                                "elena", shown, c, carried, warnings), "rejected: S2 N1-12")
        self.assertEqual(warnings, [])

    # S4 warns as S8 does; a memory another check rejects carries no warning, as it never reaches a prompt.
    def test_a_name_warns_and_a_rejected_memory_carries_no_warning(self):
        self.runs = self.v15
        rec, shown, c, carried = CheckErrorsTest.inputs(self, 1, 1, "elena")
        nobody = next(i for i, t in shown.items() if "Mara" not in t and "mara" not in
                      {c.event(i)["actor"], c.event(i)["target"], *(c.event(i)["members"] or [])})
        for meaning, verdict, warned in [
                ("Mara never trusted me.", "kept", [{"of": "memory", "text": "Mara never trusted me.",
                                                     "reason": "S4 Mara"}]),
                ("Mara stole the can tonight.", "rejected: S5 tonight", [])]:
            warnings = []
            self.assertEqual(self.mind.check_memory({"ids": [nobody], "meaning": meaning}, "elena", shown, c, carried,
                                                    warnings), verdict)
            self.assertEqual(warnings, warned)

    # A whole run: every night mind's false theft and false intent are kept, and each is a line of the run log.
    def test_the_run_log_carries_every_warning(self):
        dirs = Dirs()
        self.addCleanup(dirs.cleanup)
        (meta, code), out = fake_morning(dirs, client=WarningFake(invalid_every=0))
        self.assertEqual(code, 0, out)
        tr = json.loads(read(os.path.join(dirs.runs, "daniel_ate_it-seed7.transcript.json")))
        n = 0
        for k in (1, 2):
            for pid, r in tr[f"mind{k}"].items():
                name = world.NAMES[pid]
                self.assertEqual([m["verdict"] for m in r["memories"]], ["kept"], (k, pid))
                self.assertEqual(r["intent_verdict"], "kept", (k, pid))
                self.assertIn(f'  night {k}, the night mind: warning, {name}\'s memory kept: '
                              f'"{WarningFake.MEANINGS[k - 1]}" (S8 mara take: no such event)', out)
                self.assertIn(f'  night {k}, the night mind: warning, {name}\'s intent kept: "{WarningFake.INTENT}" '
                              f"(S8 leo take: no such event)", out)
                n += 1
        self.assertGreaterEqual(n, 6)


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


# ---------- the quiet day, stage A (reports/quiet_day_design.md, §1.1, §1.2, §2.1, §2.2, §3, §4, §6.1) ----------
V16_CACHE = os.path.join(HERE, "cache", "v16")
V16_RUNS = os.path.join(HERE, "runs", "v16")


def asked_where(prompt):
    """(who, minute or None at night, option ids, speech option ids) of a decision prompt."""
    who = re.match(r"You are (\w+),", prompt).group(1).lower()
    return (who, now_minute(prompt), re.findall(r"^- (\w+):", block := prompt.split("Your options:")[-1], flags=re.M),
            set(re.findall(r"^- (\w+): \(speech\)", block, flags=re.M)))


def now_minute(prompt):
    """The minute of a day prompt's "Now," line, "Now, minute 54" or "Now, 10:21"; None at night."""
    m = re.search(r"^Now, (?:minute (\d+)|(\d\d):(\d\d)),", prompt, flags=re.M)
    if not m:
        return None
    return int(m.group(1)) if m.group(1) else int(m.group(2)) * 60 + int(m.group(3)) - 7 * 60


def minute_numbers(prompt):
    """Every number a prompt writes after "min", "minute" or "minutes", lists included ("at minutes 03, 06 and 21")."""
    out = []
    for g in re.findall(r"\bmin(?:ute)?s? (\d+(?:(?:, | and )\d+)*)\b", prompt):
        out += [int(x) for x in re.findall(r"\d+", g)]
    return out


class HushFake(FakeClient):
    """The fake model, never broken, silent two times in three when it may: the morning's talk ends, as v16's day 3s
    did, and the quiet day runs."""

    def __init__(self):
        super().__init__(invalid_every=0, max_calls=10 ** 6)
        self.asked = []             # (minute, who) of every day decision

    def generate(self, system, prompt, schema=None):
        text = super().generate(system, prompt, schema)
        if schema is not None:
            return text
        who, minute, options, _ = asked_where(prompt)
        self.asked.append((minute, who))
        ans = json.loads(text)
        if "silent" in options and int(hashlib.sha256(prompt.encode("utf-8")).hexdigest(), 16) % 3:
            ans.update(option="silent", say=None)
        return json.dumps(ans)


class TalkFake(HushFake):
    """Keeps talking from minute `talk_from` on: a speech option it has not yet used, else any speech option, always
    angry with someone. Silent before `talk_from`."""

    def __init__(self, talk_from=0):
        super().__init__()
        self.talk_from = talk_from
        self.used = set()

    def generate(self, system, prompt, schema=None):
        if schema is not None:
            return FakeClient.generate(self, system, prompt, schema)
        self.requests += 1
        who, minute, options, speech = asked_where(prompt)
        self.asked.append((minute, who))
        talk = [o for o in options if o in speech]
        if minute is None or minute < self.talk_from or not talk:
            pick = "silent" if "silent" in options else options[0]
        else:
            fresh = [o for o in talk if (who, o) not in self.used]
            pick = (fresh or talk)[0]
            self.used.add((who, pick))
        return json.dumps({"option": pick, "say": f"Words of {who} {self.requests}." if pick in speech else None,
                           "feeling": "angry", "reason": "Talk.", "suspects": "nobody",
                           "angry_at": "Leo" if who == "daniel" else "Daniel"})


class PolicyFake(HushFake):
    """policy(who, minute, options) -> option or (option, angry_at); silent when it returns None or what it names is
    not offered."""

    def __init__(self, policy):
        super().__init__()
        self.policy = policy

    def generate(self, system, prompt, schema=None):
        if schema is not None:
            return FakeClient.generate(self, system, prompt, schema)
        self.requests += 1
        who, minute, options, speech = asked_where(prompt)
        self.asked.append((minute, who))
        got = self.policy(who, minute, options) or "silent"
        option, angry = got if isinstance(got, tuple) else (got, "nobody")
        if option not in options:
            option = "silent" if "silent" in options else options[0]
        return json.dumps({"option": option, "say": f"Words of {who} at {minute}." if option in speech else None,
                           "feeling": "tense", "reason": "Policy.", "suspects": "nobody", "angry_at": angry})


class RecordingTalkFake(TalkFake):
    """TalkFake that keeps every prompt it is sent, the day's and the night's."""

    def __init__(self, talk_from=0):
        super().__init__(talk_from)
        self.prompts = []

    def generate(self, system, prompt, schema=None):
        self.prompts.append(prompt)
        return super().generate(system, prompt, schema)


class QuietDayTest(unittest.TestCase):
    """Stage A of the quiet day, from day 3 on: the clock, time skipping, fasting and sleep debt with body lines, the
    rest and withdraw routines, triggers Q1 and Q2, and the day budget. Every day-3 test starts from v16 seed 2 as it
    was through night 2 and its night mind, replayed from cache/v16 (copied; never written) with no API call."""
    MODEL = "gemini-3.5-flash-lite"

    def setUp(self):
        self.dirs = Dirs()
        self.quiet = importlib.import_module("quiet")
        self.night = importlib.import_module("night")
        self.chron = importlib.import_module("chronicle")
        self.mind = importlib.import_module("mind")

    def tearDown(self):
        self.dirs.cleanup()

    def v16(self, seed=2, client=None):
        """v16 seed N through night 2 and mind 2 from its own answers, then day 3 set up, answered by `client`."""
        client = client or HushFake()
        name = f"daniel_ate_it-seed{seed}"
        copy = os.path.join(self.dirs.root, f"{self.MODEL}-{name}.json")
        shutil.copyfile(os.path.join(V16_CACHE, f"{self.MODEL}-{name}.json"), copy)
        oracle = Oracle(Cache(copy), self.MODEL, seed, client=client)
        chron = self.chron.Chronicle(seed, "daniel")

        def play(m):
            for t in range(m.turns):
                m.turn(t)
            m.finish()
            chron.add_day(m)
            return m
        day1 = play(Morning(oracle, seed))
        n1 = self.night.Night(day1, oracle, number=1).run()
        chron.add_night(n1)
        mind1 = self.mind.NightMind(n1, chron, oracle).run()
        day2 = play(Morning.next_day(day1, n1, oracle, chronicle=chron))
        n2 = self.night.Night(day2, oracle, number=2, house=chron.house_state()).run()
        chron.add_night(n2)
        mind2 = self.mind.NightMind(n2, chron, oracle).run()
        self.assertEqual((oracle.live, client.requests), (0, 0), "v16 through night 2 comes from its cache")
        day3 = Morning.next_day(day2, n2, oracle, chronicle=chron)
        return type("V16", (), dict(day1=day1, n1=n1, mind1=mind1, day2=day2, n2=n2, mind2=mind2, day3=day3,
                                    chron=chron, oracle=oracle, client=client))

    def played(self, client=None):
        d = self.v16(client=client)
        self.quiet.play(d.day3)
        return d

    # ---------- §1.1, §1.2, §6: the needs at day 3, 07:00 ----------
    def test_fasting_at_day_3_0700_is_section_6s(self):
        d = self.v16()
        # Hours from the last meal to day 3, 07:00 (= 2 × 1440 minutes after day 1, 07:00), × the hunger rate.
        hand = {"daniel": (2 * 1440 + 240) / 60 * 1.15,     # the can, 03:00 of house day 4
                "leo": (2 * 1440 + 720) / 60 * 1.0,         # house day 3, 19:00, the fixed fact
                "mara": (2 * 1440 - 54) / 60 * 0.95,        # day 1, min 54
                "elena": (2 * 1440 - 1440) / 60 * 0.85}     # the given portion, day 2, min 00
        self.assertEqual({k: round(v, 3) for k, v in hand.items()},
                         {"daniel": 59.8, "leo": 60.0, "mara": 44.745, "elena": 20.4})
        q = d.day3.quiet
        for pid, v in hand.items():
            self.assertAlmostEqual(q.fast(d.day3.people[pid], 0), v, places=9, msg=pid)
        # Fasting in days (reports/world_design.md, §4.3.1): F1 from 24, F2 from 72.
        self.assertEqual({pid: self.quiet.fast_stage(q.fast(d.day3.people[pid], 0)) for pid in data.ORDER},
                         {"daniel": 1, "elena": 0, "leo": 1, "mara": 1})
        self.assertEqual([self.quiet.fast_stage(x) for x in (23.99, 24, 71.99, 72)], [0, 1, 1, 2])

    def test_sleep_debt_at_day_3_0700_is_section_6s(self):
        d = self.v16()
        self.assertEqual(d.n1.choices, {q: "lie_awake" for q in data.ORDER})
        self.assertEqual(d.n2.choices, {"daniel": "go_next_door", "elena": "sleep", "leo": "lie_awake",
                                        "mara": "lie_awake"})
        self.assertEqual(world.hunger_level(d.n2.bedtime_hunger["elena"]), 3)     # starving at bedtime: sleep pays 6
        hand = {"daniel": 14 - 3 + 14 - 0, "elena": 14 - 3 + 14 - 6, "leo": 14 - 3 + 14 - 3, "mara": 14 - 3 + 14 - 3}
        self.assertEqual(hand, {"daniel": 25, "elena": 19, "leo": 22, "mara": 22})
        q = d.day3.quiet
        for pid, v in hand.items():
            self.assertAlmostEqual(q.debt(d.day3.people[pid], 0), v, places=9, msg=pid)
        self.assertEqual({pid: self.quiet.debt_stage(q.debt(d.day3.people[pid], 0)) for pid in data.ORDER},
                         {"daniel": 2, "elena": 1, "leo": 1, "mara": 1})
        self.assertEqual([self.quiet.debt_stage(x) for x in (15.99, 16, 23.99, 24)], [0, 1, 1, 2])
        self.assertEqual([self.quiet.night_payback(c, s) for c, s in (("sleep", False), ("sleep", True),
                          ("lie_awake", True), ("watch_door", False), ("go_next_door", False))], [8, 6, 3, 0, 0])

    def test_the_body_line_states_each_stage(self):
        d = self.v16()
        body = {pid: d.day3.inside_lines(d.day3.people[pid])[0] for pid in data.ORDER}
        # Fasting in days (reports/world_design.md, §4.3.1): Daniel, Leo and Mara are past 24 hours (F1). Seed 2's
        # day 3 is 18.4 °C indoors: nobody is cold.
        self.assertEqual(body, {
            "daniel": "Your body: starving; hunger comes in waves; and you have barely slept for nights; your eyes "
                      "close on their own.",
            "elena": "Your body: starving, and you have hardly slept.",
            "leo": "Your body: starving; hunger comes in waves; and you have hardly slept.",
            "mara": "Your body: starving; hunger comes in waves; and you have hardly slept."})
        self.assertEqual(self.quiet.body_line("starving", 2, 0),
                         "Your body: starving, for days now: you feel light and slow, and standing up fast greys your "
                         "sight for a moment.")
        # Day 2 had no needs: its body line is as it was.
        self.assertTrue(all(p.needs is None for p in d.day2.people.values()))

    # ---------- the clock (§3; amendment 3) ----------
    def test_records_show_the_clock_from_minute_90(self):
        self.assertEqual([self.quiet.clock(x) for x in (0, 18, 87, 90, 201, 330, 840)],
                         ["min 00", "min 18", "min 87", "08:30", "10:21", "12:30", "21:00"])
        c = self.chron.Chronicle(1, "daniel")
        for i, minute in enumerate((87, 201), 1):
            c.add({"id": f"D3-{i:03d}", "scene": "D3", "minute": minute, "kind": "say", "actor": "leo",
                   "witnesses": {"mara": "saw"}, "views": {"mara": f"Leo says something {i}."}})
        self.assertEqual(self.mind.records(c, "mara", 3),
                         [("D3-001", "min 87: Leo says something 1."), ("D3-002", "10:21: Leo says something 2.")])

    # ---------- §2.2, §3: the day runs to bedtime, everyone rests, and they get up at different times ----------
    def test_the_quiet_day_runs_to_bedtime_with_a_rest_for_everyone(self):
        d = self.played()
        m, q = d.day3, d.day3.quiet
        spans = m.transcript["quiet"]["spans"]
        self.assertTrue(spans)
        self.assertLessEqual(max(s["end"] for s in spans), 840)
        self.assertEqual(max(s["end"] for s in spans), 840)
        first_up = {}
        for pid in data.ORDER:
            rests = [s for s in spans if s["who"] == pid and s["routine"] == "rest"]
            self.assertTrue(1 <= len(rests) <= 2, (pid, rests))
            for s in rests:
                self.assertEqual(s["room"], self.night.OWN_ROOM[pid])
                self.assertLessEqual(s["end"] - s["start"], 240)
                if s["ended"] == "time":
                    self.assertEqual(s["end"] - s["start"], s["planned"])
                    self.assertIn(s["planned"], range(120, 241, 3))
            for a, b in zip(rests, rests[1:]):
                self.assertGreaterEqual(b["start"] - a["end"], 120)
            first_up[pid] = rests[0]["end"]
        self.assertGreater(len(set(first_up.values())), 1, first_up)
        # Every jump lands on the 3-minute grid, and nothing happens after 21:00. No span is empty: whoever walks into
        # a room where a trigger starts the talk is in the played turns, not in a routine.
        self.assertTrue(all(s["start"] % 3 == 0 and s["end"] % 3 == 0 for s in spans))
        self.assertEqual([s for s in spans if s["end"] == s["start"]], [])
        self.assertEqual({pid: m.people[pid].needs["rests"] for pid in data.ORDER},
                         {pid: sum(1 for s in spans if s["who"] == pid and s["routine"] == "rest") for pid in data.ORDER})
        self.assertTrue(all(rec["minute"] < 840 for rec in m.log))

    def test_rest_lengths_are_seeded_between_2_and_4_hours(self):
        got = {(pid, n): self.quiet.rest_length(2, 3, pid, n) for pid in data.ORDER for n in (1, 2)}
        self.assertEqual(got, {k: self.quiet.rest_length(2, *[3, *k]) for k in got})
        self.assertTrue(all(v in range(120, 241, 3) for v in got.values()), got)
        self.assertGreater(len(set(got.values())), 1)

    def test_a_rest_ends_once_debt_is_below_12(self):
        d = self.v16()
        q, elena = d.day3.quiet, d.day3.people["elena"]
        q.set_debt(elena, 13.0, 300)
        end = q.rest_end(elena, 300, 240)
        self.assertEqual(end, 342)                  # 13 → 12 takes 40 minutes; the next grid minute is 342
        self.assertLess(13 - 1.5 * (end - 300) / 60, 12)
        self.assertEqual(q.rest_end(elena, 300, 30), 330)       # its seeded length comes first

    def test_needs_advance_exactly_across_the_jumps(self):
        d = self.played()
        m, q = d.day3, d.day3.quiet
        start = {"daniel": 25, "elena": 19, "leo": 22, "mara": 22}
        for pid in data.ORDER:
            rest = sum(s["end"] - s["start"] for s in m.transcript["quiet"]["spans"]
                       if s["who"] == pid and s["routine"] == "rest")
            self.assertAlmostEqual(q.debt(m.people[pid], 840), start[pid] + (840 - rest) / 60 - 1.5 * rest / 60,
                                   places=6, msg=pid)
        needs = m.transcript["quiet"]["needs"]
        self.assertEqual(needs["daniel"][0], [0, 59.8, 25.0])
        self.assertEqual(needs["daniel"][-1][0], 840)

    def test_a_routine_breaks_a_run_and_its_move_is_remembered(self):
        """After a span, the played turns do not count the turns before it as "in a row", and a speech act held back
        after three turns is offered again; whoever a routine moves remembers going."""
        d = self.v16()
        m, q = d.day3, d.day3.quiet
        leo = m.people["leo"]
        leo.history = [{"t": t, "kind": "confront", "seq": t + 1} for t in range(3)]
        self.assertNotIn("confront_daniel", [o.id for o in m.options_for(leo)])
        q.arrive(leo, "brothers_room", 30)
        self.assertIn((30, "you went to the brothers room."), leo.memory)
        q.start(leo, "rest", 30)
        q.end(leo, 180, "time")
        q.arrive(leo, "kitchen", 180)
        self.assertEqual(m.pattern(leo), [])
        self.assertIn("confront_daniel", [o.id for o in m.options_for(leo)])

    # ---------- §2.1: withdraw ----------
    def withdraw_case(self, policy, setup=None):
        d = self.v16(client=PolicyFake(policy))
        m, q = d.day3, d.day3.quiet
        self.assertEqual((m.people["leo"].grudges["daniel"].strength, m.people["mara"].grudges["daniel"].strength),
                         (3, 3))
        if setup:
            setup(m)
        q.turn(0)
        q.turn(1)
        return m, q

    def test_leo_withdraws_after_his_say_when_he_falls_silent(self):
        def policy(who, minute, options):
            if who == "leo":
                return ("confront_daniel" if minute == 0 else "silent"), "Daniel"
            if who == "daniel" and minute <= 3:
                return "confront_leo"
            return None
        m, q = self.withdraw_case(policy)
        self.assertEqual([(w["who"], w["minute"], w["room"]) for w in q.withdrawals], [("leo", 6, "brothers_room")])
        self.assertEqual(q.withdrawals[0]["why"], {"chose": "silent", "spoke_at": 0, "grudge_against": ["daniel"]})
        self.assertEqual(m.people["leo"].room, "brothers_room")
        self.assertEqual(q.open["leo"]["routine"], "withdraw")
        # The others in the kitchen saw him go; Mara, silent, had said nothing, so she stays.
        for pid in ("daniel", "elena", "mara"):
            self.assertIn((6, "Leo goes to the brothers room."), m.people[pid].memory, pid)
        self.assertEqual(m.people["mara"].room, "kitchen")

    def test_a_withdraw_into_a_room_with_a_grievance_is_a_meeting(self):
        """Leo walks out to the brothers room, where Mara (who holds 2 against him) already is: the withdraw is a
        routine bringing him into her room, so Q2 asks her at the next turn."""
        def policy(who, minute, options):
            if who == "leo":
                return ("confront_daniel" if minute == 0 else "silent"), "Daniel"
            if who == "daniel" and minute <= 3:
                return "confront_leo"
            return None

        def setup(m):
            m.people["mara"].room = "brothers_room"
            g = m.people["mara"].grudge("leo")
            g.strength, g.last_change = 2, 0        # as a grudge carried into the day: it holds for 15 minutes
        m, q = self.withdraw_case(policy, setup)
        self.assertEqual([(w["who"], w["minute"]) for w in q.withdrawals], [("leo", 6)])
        self.assertEqual([(e["kind"], e["minute"], e["asked"]) for e in q.log if e["fired"]], [("Q2", 6, "mara")])
        self.assertEqual(q.pending["mara"]["kind"], "Q2")
        q.turn(2)
        mara = next(x for x in m.log[-1]["decisions"] if x["person"] == "mara")
        self.assertEqual((mara["mode"], mara.get("quiet")), ("model", "Q2"))

    def test_no_withdraw_without_a_grudge_of_3(self):
        def policy(who, minute, options):
            if who == "leo":
                return "confront_daniel" if minute == 0 else "silent"
            return "confront_leo" if who == "daniel" and minute <= 3 else None

        def setup(m):
            m.people["leo"].grudges["daniel"].strength = 2
        m, q = self.withdraw_case(policy, setup)
        self.assertEqual(q.withdrawals, [])
        self.assertEqual(m.people["leo"].room, "kitchen")

    def test_no_withdraw_when_the_one_held_against_is_not_in_the_room(self):
        def policy(who, minute, options):
            if who == "leo":
                return ("confront_mara" if minute == 0 else "silent"), "Daniel"
            return "confront_leo" if who == "mara" and minute <= 3 else None

        def setup(m):
            m.people["daniel"].room = "back_room"
        m, q = self.withdraw_case(policy, setup)
        self.assertEqual(q.withdrawals, [])

    def test_daniel_and_elena_never_withdraw(self):
        for who, other in (("daniel", "leo"), ("elena", "daniel")):
            def policy(w, minute, options, who=who, other=other):
                if w == who:
                    return ("confront_" + other if minute == 0 else "silent"), world.NAMES[other]
                if w == other and minute <= 3:
                    return "confront_" + who
                return None

            def setup(m, who=who, other=other):
                m.people[who].grudge(other).strength = 3
            m, q = self.withdraw_case(policy, setup)
            self.assertEqual([w for w in q.withdrawals if w["who"] == who], [], who)
            self.assertEqual(m.people[who].room, "kitchen", who)

    def test_every_withdraw_of_the_day_had_every_condition(self):
        d = self.played()
        for w in d.day3.quiet.withdrawals:
            self.assertEqual(w["why"]["chose"], "silent")
            self.assertIsNotNone(w["why"]["spoke_at"])
            self.assertTrue(w["why"]["grudge_against"])
            self.assertNotIn(w["who"], ("daniel", "elena"))

    # ---------- §4 Q2: a grievance meets ----------
    def meeting(self):
        d = self.v16()
        m, q = d.day3, d.day3.quiet
        for p in m.people.values():
            p.room = "back_room"
        m.people["leo"].room, m.people["daniel"].room = "kitchen", "brothers_room"
        q.exchanged[("daniel", "leo")] = 200
        return m, q

    def test_q2_fires_on_an_arrival_after_60_quiet_minutes_and_not_before(self):
        m, q = self.meeting()
        dan = m.people["daniel"]
        self.assertEqual(q.arrive(dan, "kitchen", 257), [])
        self.assertEqual(q.log[-1]["kind"], "Q2")
        self.assertFalse(q.log[-1]["fired"])
        self.assertNotIn("leo", q.pending)
        dan.room = "brothers_room"
        fired = q.arrive(dan, "kitchen", 260)
        self.assertEqual([(f["kind"], f["asked"], f["pair"]) for f in fired], [("Q2", "leo", ["daniel", "leo"])])
        self.assertEqual(q.pending["leo"]["kind"], "Q2")
        self.assertTrue(m.convos.active["kitchen"])

    def test_q2_once_per_pair_per_day(self):
        """reports/multiday.md, fix 3 (it was once per pair in 2 hours): a pair that met this way today is not asked
        again that day, however long after."""
        m, q = self.meeting()
        dan = m.people["daniel"]
        self.assertEqual(len(q.arrive(dan, "kitchen", 260)), 1)
        q.pending.clear()
        got = []
        for minute in (377, 380, 700):
            dan.room = "brothers_room"
            got.append(len(q.arrive(dan, "kitchen", minute)))
        self.assertEqual(got, [0, 0, 0])
        for e in q.log[-3:]:
            self.assertEqual((e["met_today"], e["why"]), (True, "they met this way at 11:20 already today"))

    def test_q2_asks_the_higher_grudge_and_the_one_already_there_on_a_tie(self):
        for dan_holds, asked in ((3, "leo"), (2, "leo")):
            m, q = self.meeting()
            m.people["daniel"].grudge("leo").strength = dan_holds
            self.assertEqual([f["asked"] for f in q.arrive(m.people["daniel"], "kitchen", 300)], [asked])
        m, q = self.meeting()
        m.people["leo"].grudges["daniel"].strength = 1
        m.people["daniel"].grudge("leo").strength = 2
        self.assertEqual([f["asked"] for f in q.arrive(m.people["daniel"], "kitchen", 300)], ["daniel"])
        m, q = self.meeting()
        m.people["leo"].grudges["daniel"].strength = 1
        self.assertEqual(q.arrive(m.people["daniel"], "kitchen", 300), [])

    def test_every_q2_of_the_day_came_after_an_hour_apart(self):
        d = self.played()
        q = d.day3.quiet
        checked = [e for e in q.log if e["kind"] == "Q2"]
        self.assertTrue(checked, "no grievance pair met all day")
        for e in checked:
            apart = e["minute"] - e["last_line"] if e["last_line"] is not None else None
            self.assertEqual(e["fired"], (apart is None or apart >= 60) and not e["met_today"]
                             and not e.get("budget"), e)
        fired = [tuple(e["pair"]) for e in checked if e["fired"]]
        self.assertEqual(len(fired), len(set(fired)), fired)          # once per pair per day

    # ---------- §4 Q1: a need crosses a line with company ----------
    def test_q1_asks_only_with_someone_awake_there_and_once(self):
        d = self.v16()
        m, q = d.day3, d.day3.quiet
        for p in m.people.values():
            p.room = "kitchen"
            q.set_debt(p, 10.0, 0)          # no one's debt crosses a line before 10:27
        mara = m.people["mara"]
        mara.room = "back_room"
        # Mara's fasting reaches 72, light and slow (F2), at 10:25:30: 10:27 on the grid (fasting in days,
        # reports/world_design.md §4.3.1; F1 at 24 asks nobody).
        mara.needs["ate_at"] = self.quiet.absolute(3, 205.5) - 72 / 0.95 * 60
        self.assertEqual(q.tick(204), [])
        cross = q.tick(207)
        self.assertEqual(cross, [("mara", "fast", 2)])
        self.assertEqual(q.ask_q1(cross, 207), [])
        self.assertEqual((q.log[-1]["kind"], q.log[-1]["fired"], q.log[-1]["why"]), ("Q1", False, "alone"))
        # With Elena there, but resting: still alone.
        elena = m.people["elena"]
        elena.room = "back_room"
        q.start(elena, "rest", 207)
        self.assertEqual(q.ask_q1(cross, 207), [])
        q.end(elena, 207, "test")
        self.assertEqual([(f["kind"], f["asked"]) for f in q.ask_q1(cross, 207)], [("Q1", "mara")])
        self.assertEqual(q.ask_q1(cross, 207), [])            # once per person per threshold

    # ---------- §4: the budget ----------
    def test_the_day_budget_holds_when_the_fake_keeps_talking(self):
        """The day's own budget holds; Q5's 8 come on top of it (reports/facts_and_evening.md, fix 5). This day spends
        32 asks before 19:00, so its budget is set to 30 here to see it spent."""
        with mock.patch.object(self.quiet, "DAY_ASKS", 30):
            d = self.played(client=TalkFake())
        m, q = d.day3, d.day3.quiet
        asks = m.transcript["quiet"]["asks"]
        evening = sum(s["asks"] for s in m.transcript["quiet"]["stretches"] if s["trigger"] == "Q5")
        self.assertLessEqual(evening, 8)
        self.assertEqual(asks["day"] - evening, 30)
        self.assertEqual(asks["day"], len([1 for rec in m.log for x in rec["decisions"]
                                           if x["mode"] == "model" or x.get("invalid")]))
        self.assertLessEqual(asks["quiet"], 12)
        self.assertTrue(any(why == "the day's asks are spent" for _, _, what, why in m.convos.log))
        self.assertEqual(max(s["end"] for s in m.transcript["quiet"]["spans"]), 840)

    def test_the_quiet_asks_hold_at_12_and_4_each(self):
        d = self.played(client=TalkFake(talk_from=60))
        m = d.day3
        asks = m.transcript["quiet"]["asks"]
        self.assertLessEqual(asks["day"], 40)
        self.assertLessEqual(asks["quiet"], 12)
        self.assertTrue(all(n <= 4 for n in asks["quiet_by_person"].values()), asks)
        m, q = self.meeting()
        q.quiet_asked = [{"who": "mara"}] * 12
        self.assertEqual(q.arrive(m.people["daniel"], "kitchen", 300), [])
        self.assertEqual(q.log[-1]["budget"], "12 quiet asks today")
        m, q = self.meeting()
        q.quiet_asked = [{"who": "leo"}] * 4
        self.assertEqual(q.arrive(m.people["daniel"], "kitchen", 300), [])
        self.assertEqual(q.log[-1]["budget"], "4 quiet asks of Leo today")

    def test_quiet_mode_asks_the_model_only_through_a_trigger(self):
        d = self.played()
        m, q = d.day3, d.day3.quiet
        stretches = m.transcript["quiet"]["stretches"]
        self.assertTrue(stretches)
        self.assertEqual(stretches[0]["trigger"], "the morning")
        fired = {(e["minute"], e["room"]) for e in q.log if e["fired"]}
        for s in stretches[1:]:
            self.assertIn((s["start"], s["room"]), fired, s)
            # Nobody starts a routine in the room where a trigger has just started the talk.
            self.assertEqual([x for x in m.transcript["quiet"]["spans"]
                              if (x["start"], x["room"]) == (s["start"], s["room"])], [], s)
        for rec in m.log:
            self.assertTrue(any(s["start"] <= rec["minute"] < s["end"] for s in stretches), rec["minute"])

    # ---------- §3: what it records ----------
    def test_each_span_is_a_chronicle_event_with_its_witnesses(self):
        d = self.played()
        m, chron = d.day3, d.chron
        chron.add_day(m)
        spans = m.transcript["quiet"]["spans"]
        routine = [e for e in chron.events if e["kind"] == "routine"]
        self.assertEqual(len(routine), len(spans))
        for e in routine:
            s = next(x for x in spans if (x["who"], x["start"], x["routine"]) == (e["actor"], e["minute"], e["routine"]))
            self.assertEqual((e["scene"], e["room"], e["until"]), ("D3", s["room"], s["end"]))
            self.assertEqual(e["witnesses"][s["who"]], "did")
            self.assertEqual(set(e["witnesses"]), {s["who"]} | set(s["seen_start"]) | set(s["seen_end"])
                             | set(s["seen_leave"]))
            self.assertEqual(set(e["views"]), set(e["witnesses"]))
            # A witness who saw only its end is told when they saw it.
            for q in set(s["seen_end"]) - set(s["seen_start"]) - set(s["seen_leave"]):
                self.assertTrue(e["views"][q].endswith(f"{self.quiet.clock(s['end'])}."), e["views"][q])
        for e in chron.events:
            if e["scene"] in ("D1", "N1", "D2", "N2", "G1", "G2"):
                self.assertEqual(list(e), list(self.chron.KEYS), e["id"])
        for e in (x for x in chron.events if x["kind"] == "need"):
            self.assertEqual(e["witnesses"], {e["actor"]: "did"})
        recs = self.mind.records(chron, "daniel", 3)
        self.assertTrue(any(re.match(r"^(min \d\d|\d\d:\d\d): You lay on your bed in the brothers room from "
                                     r"(min \d\d|\d\d:\d\d) to \d\d:\d\d\.", t) for _, t in recs), recs)

    def test_block_a_and_bedtime_say_the_day_after_the_morning(self):
        d = self.played()
        m, chron = d.day3, d.chron
        chron.add_day(m)
        lines = {pid: self.quiet.gap_line(m, pid) for pid in data.ORDER}
        for pid, line in lines.items():
            self.assertTrue(line.startswith("After the morning: you "), line)
            self.assertRegex(line, r"\(min \d\d to \d\d:\d\d\)")
            self.assertNotRegex(line, r"min \d{3}")
            self.assertIn("lay on your bed", line)
        m.people["elena"].hunger = 0.5
        n3 = self.night.Night(m, d.oracle, number=3, house=chron.house_state()).run()
        self.assertEqual(n3.bedtime_hunger["elena"], 0.5)              # the afternoon was played, not added
        for dec in (x for x in n3.decisions if x["ask"] == "bedtime"):
            self.assertEqual(dec["now"][0], "Now it is night. " + lines[dec["person"]])
        for pid in data.ORDER:
            a = self.night.carry_in_later(m, n3, n3.people[pid])
            self.assertIn("- " + lines[pid], a)
            self.assertNotIn("- " + data.GAP, a)

    def test_the_story_shows_the_quiet_day(self):
        d = self.played()
        text = importlib.import_module("story").render_day2(d.day3)
        self.assertIn("## After the morning", text)
        self.assertIn("lies on his bed in the brothers room", text)

    # ---------- the fixes before the first live run (reports/quiet_day_fixes.md) ----------
    @staticmethod
    def asks_in(m, s):
        """The model's answers asked in a stretch, counted from the turn log: every model decision, and every one that
        fell back after asking (an answer refused because the asks were spent asked nothing)."""
        return sum(1 for rec in m.log if s["start"] <= rec["minute"] < s["end"] for x in rec["decisions"]
                   if x["mode"] == "model" or (x.get("invalid") and "spent" not in x["invalid"]))

    def test_the_morning_stops_at_24_asks_and_a_triggered_stretch_at_8(self):
        """Fix 1, DONE 1: with TalkFake on v16 seed 2, the morning stops at 24 asks, no triggered stretch passes 8, and
        at least 2 triggered stretches happen after the morning."""
        d = self.played(client=TalkFake())
        m = d.day3
        tr = m.transcript["quiet"]
        stretches = tr["stretches"]
        counted = [self.asks_in(m, s) for s in stretches]
        self.assertEqual(stretches[0]["trigger"], "the morning")
        self.assertEqual(counted[0], 24, counted)
        self.assertIn((stretches[0]["end"], "kitchen", "ended", "the morning's 24 asks are spent"), m.convos.log)
        self.assertEqual(tr["morning_end"], stretches[0]["end"])
        self.assertGreaterEqual(len(stretches[1:]), 2, stretches)
        self.assertTrue(all(n <= 8 for n in counted[1:]), counted)
        self.assertEqual([s["asks"] for s in stretches], counted)
        own = sum(n for s, n in zip(stretches, counted) if s["trigger"] in ("Q5", "Q6"))     # their own 8 each
        self.assertLessEqual(tr["asks"]["day"] - own, 40)
        self.assertEqual(tr["asks"]["day"], sum(counted))
        self.assertLessEqual(tr["asks"]["quiet"], 12)

    def test_a_triggered_stretch_ends_as_when_the_budget_is_spent(self):
        d = self.played(client=TalkFake())
        m = d.day3
        for s in m.transcript["quiet"]["stretches"][1:]:
            if s["asks"] == 8:
                self.assertTrue(any(mm == s["end"] and why == "this stretch's 8 asks are spent"
                                    for mm, r, what, why in m.convos.log if what == "ended"), s)
                break
        else:
            self.fail("no triggered stretch reached 8 asks")

    def quiet_mode(self, q, start, stop):
        """Quiet mode from `start`, as quiet.play runs it between stretches, until `stop` or a trigger fires. Returns
        the minute it stopped."""
        minute = start
        while minute < stop:
            if q.step(minute):
                return minute
            nxt = q.next_event(minute)
            q.advance(minute, nxt)
            minute = nxt
        return minute

    def bounce(self):
        """§5 of reports/quiet_day_impl.md: Mara walks out on Daniel at 10:36 (a grudge of 3); Elena comes into the back
        room to lie down at 11:33. Daniel and Leo have had their rests; Mara's next rest is allowed from 11:42."""
        d = self.v16()
        m, q = d.day3, d.day3.quiet
        for r in data.ROOMS:
            m.convos.active[r] = False
        for p in m.people.values():
            p.room = "kitchen"
        for pid in ("daniel", "leo"):
            m.people[pid].needs["rests"] = 2
        m.people["elena"].needs.update(rests=1, last_rest_end=153)
        m.people["mara"].needs.update(rests=1, last_rest_end=162)
        q.tick(216)             # what the needs crossed since 07:00 is behind them
        q.withdraw(m.people["mara"], 216, {"chose": "silent", "spoke_at": 213, "grudge_against": ["daniel"]})
        return m, q

    def test_someone_coming_in_does_not_end_a_withdraw(self):
        """Fix 2, DONE 2: Elena comes into the back room to rest; Mara keeps to it. Her rest falls due at 11:42 and she
        takes it there, and the withdraw lasts to that rest's end."""
        m, q = self.bounce()
        mara = m.people["mara"]
        stop = self.quiet_mode(q, 216, 840)
        mine = [s for s in q.spans if s["who"] == "mara"]
        self.assertIn((273, "Elena comes into the back room."), mara.memory)
        self.assertEqual([(s["routine"], s["room"], s["start"], s["end"], s["ended"]) for s in mine[:2]],
                         [("withdraw", "back_room", 216, 282, "went to rest"),
                          ("rest", "back_room", 282, mine[1]["end"], "time")])
        # Free at her rest's end, she goes to sit in the kitchen, where Daniel is: Q2 asks her, and the talk is played.
        self.assertEqual(len(mine), 2)
        self.assertEqual(stop, mine[1]["end"])
        self.assertEqual((mara.room, q.pending["mara"]["kind"]), ("kitchen", "Q2"))
        self.assertEqual([s for s in q.spans if s["ended"] == "someone came in"], [])
        elena = [s for s in q.spans if s["who"] == "elena" and s["routine"] == "rest"]
        self.assertEqual((elena[0]["start"], elena[0]["room"]), (273, "back_room"))

    def test_a_withdraw_ends_two_hours_after_it_began(self):
        m, q = self.bounce()
        m.people["mara"].needs["rests"] = 2            # no rest of hers falls due today
        stop = self.quiet_mode(q, 216, 840)
        mine = [s for s in q.spans if s["who"] == "mara"]
        self.assertEqual([(s["routine"], s["room"], s["start"], s["end"], s["ended"]) for s in mine],
                         [("withdraw", "back_room", 216, 336, "two hours")])
        # Then she goes to sit in the kitchen, where Daniel is: Q2 asks her.
        self.assertEqual(stop, 336)
        self.assertEqual((m.people["mara"].room, q.pending["mara"]["kind"]), ("kitchen", "Q2"))
        self.assertNotIn("mara", q.withdrawn)

    def test_a_trigger_ask_ends_a_withdraw(self):
        m, q = self.bounce()
        mara = m.people["mara"]
        q.ask(mara, "Q2", 240, "Daniel comes into the back room", "test")
        self.assertNotIn("mara", q.open)
        self.assertEqual((q.spans[-1]["who"], q.spans[-1]["end"], q.spans[-1]["ended"]), ("mara", 240, "asked"))
        self.assertNotIn("mara", q.withdrawn)
        # Asked while resting inside it: woken, and the withdraw is over too.
        m, q = self.bounce()
        mara = m.people["mara"]
        self.quiet_mode(q, 216, 300)
        self.assertEqual(q.open["mara"]["routine"], "rest")
        q.ask(mara, "Q2", 300, "Daniel comes into the back room", "test")
        self.assertNotIn("mara", q.withdrawn)
        self.assertEqual(next(s for s in reversed(q.spans) if s["who"] == "mara")["ended"], "woken")

    def test_someone_coming_in_during_played_turns_does_not_end_a_withdraw(self):
        def policy(who, minute, options):
            if who == "leo":
                return ("confront_daniel" if minute == 0 else "silent"), "Daniel"
            if who == "daniel":
                return "confront_leo" if minute <= 3 else "go_brothers_room"
            return None
        m, q = self.withdraw_case(policy)
        self.assertEqual(q.open["leo"]["routine"], "withdraw")
        q.pending["daniel"] = {"kind": "Q2", "minute": 6, "texts": []}     # Daniel is asked, and goes after him
        q.turn(2)
        self.assertEqual(m.people["daniel"].room, "brothers_room")
        self.assertEqual(q.open["leo"]["routine"], "withdraw")

    def test_prompts_say_the_clock_from_minute_90(self):
        """Fix 3: the "Now" line, memory lines, facts and the lull line say the clock from minute 90 on; below, as
        before."""
        d = self.v16()
        m = d.day3
        leo = m.people["leo"]
        leo.memory += [(54, "Mara sits down."), (201, "Daniel comes into the kitchen.")]
        leo.grudges["daniel"].rise(207, "you were angry with Daniel", kind="angry")
        early = m.prompt_for(leo, 29, m.options_for(leo))
        self.assertRegex(early, r"(?m)^Now, minute 87, you are in the kitchen\.")
        self.assertIn("\n- min 54: Mara sits down.", early)
        late = m.prompt_for(leo, 70, m.options_for(leo), lull=201)
        self.assertRegex(late, r"(?m)^Now, 10:30, you are in the kitchen\.")
        self.assertIn("\n- min 54: Mara sits down.", late)
        self.assertIn("\n- 10:21: Daniel comes into the kitchen.", late)
        self.assertIn("since 10:21.", late)
        self.assertIn("at 10:27", late)
        self.assertEqual([x for x in minute_numbers(late) if x >= 90], [])
        self.assertEqual([data.minutes_words(ms) for ms in ([3], [3, 6], [201], [3, 201, 204])],
                         ["at minute 03", "at minutes 03 and 06", "at 10:21", "at minute 03, and at 10:21 and 10:24"])
        self.assertEqual([data.minutes_list(ms) for ms in ([3, 6], [3, 201], [201, 204])],
                         ["min 03, 06", "min 03, 10:21", "10:21, 10:24"])
        self.assertEqual([data.unstamp(x) for x in ("min 03: a: b", "10:21: c", "tonight: d")],
                         [(3, "a: b"), (201, "c"), (None, "tonight: d")])

    def test_no_prompt_says_a_minute_of_90_or_later(self):
        """Fix 3, DONE 3: day 3 played with TalkFake and night 3 after it: every prompt from minute 90 on says the clock,
        and no prompt says "minute" or "min" with a number of 90 or more."""
        client = RecordingTalkFake(talk_from=60)     # its accusations and confrontations come after 08:30
        d = self.v16(client=client)
        m = d.day3
        self.quiet.play(m)
        d.chron.add_day(m)
        day = list(client.prompts)
        n3 = self.night.Night(m, d.oracle, number=3, house=d.chron.house_state()).run()
        self.assertTrue(n3.decisions)
        night = client.prompts[len(day):]
        late = [p for p in day if now_minute(p) is not None and now_minute(p) >= 90]
        self.assertTrue(late, "no day prompt from minute 90 on")
        for p in late:
            self.assertRegex(p, r"(?m)^Now, \d\d:\d\d, you are in the ")
        for p in day + night:
            self.assertEqual([x for x in minute_numbers(p) if x >= 90], [], p)
        # Block A of the next morning (its Y3/Y4 lists say the clock for acts from minute 90 on).
        for pid in data.ORDER:
            a = "\n".join(self.night.carry_in_later(m, n3, n3.people[pid]))
            self.assertEqual([x for x in minute_numbers(a) if x >= 90], [], a)
        acts = [(a["who"], turn["minute"]) for turn in m.transcript["turns"] for a in turn["acts"]
                if a["option"].startswith(("accuse_", "confront_")) and turn["minute"] >= 90]
        self.assertTrue(acts, "no accusation or confrontation from minute 90 on")
        who, minute = acts[0]
        self.assertIn(self.quiet.clock(minute), "\n".join(self.night.carry_in_later(m, n3, n3.people[who])))

    def test_block_a_reads_the_clock_from_what_they_are_sure_of(self):
        """Fix 3: what someone is sure of from minute 90 on reaches block A as the clock."""
        d = self.played()
        m, chron = d.day3, d.chron
        chron.add_day(m)
        n3 = self.night.Night(m, d.oracle, number=3, house=chron.house_state()).run()
        mara = n3.people["mara"]
        mara.sure += [f"{self.quiet.clock(201)}: you ate one of the portions. 0 left.",
                      f"{self.quiet.clock(204)}: you finished searching the back room: nothing.",
                      f"{self.quiet.clock(54)}: Leo ate one of the portions (you saw it)."]
        a = self.night.carry_in_later(m, n3, n3.people["mara"])
        self.assertIn("- You ate a portion at 10:21.", a)
        self.assertIn("- You searched the back room at 10:24 and found nothing.", a)
        self.assertIn("- Leo ate a portion at minute 54 (you saw it).", a)

    def test_a_record_of_only_a_spans_end_is_stamped_at_its_end(self):
        """Fix 4: a witness who saw only a span's end has its record stamped at the end minute, in time order."""
        d = self.played()
        m, chron = d.day3, d.chron
        chron.add_day(m)
        found = 0
        for e in (x for x in chron.events if x["kind"] == "routine"):
            s = next(x for x in m.transcript["quiet"]["spans"]
                     if (x["who"], x["start"], x["routine"]) == (e["actor"], e["minute"], e["routine"]))
            for q in set(s["seen_end"]) - set(s["seen_start"]) - set(s["seen_leave"]):
                recs = dict(self.mind.records(chron, q, 3))
                self.assertTrue(recs[e["id"]].startswith(self.quiet.clock(s["end"]) + ": "), recs[e["id"]])
                found += 1
            for q in set(s["seen_start"]) | set(s["seen_leave"]):
                recs = dict(self.mind.records(chron, q, 3))
                self.assertTrue(recs[e["id"]].startswith(self.quiet.clock(s["start"]) + ": "), recs[e["id"]])
        self.assertTrue(found, "no witness saw only a span's end")

        def at(text):
            mm = re.match(r"^(?:min (\d+)|(\d\d):(\d\d)): ", text)
            return int(mm.group(1)) if mm.group(1) else int(mm.group(2)) * 60 + int(mm.group(3)) - 420
        for pid in data.ORDER:
            stamps = [at(t) for _, t in self.mind.records(chron, pid, 3) if not t.startswith("tonight: ")]
            self.assertEqual(stamps, sorted(stamps), pid)

    # ---------- a meeting after hours apart, and anger cooling with rest (reports/meeting_fixes.md) ----------
    def apart(self):
        """v17 seed 1's first Q2, rebuilt: the morning's last line between Mara, Daniel and Elena at min 15; Mara and
        Daniel lie down at min 18; Elena gets up at 10:03 and sits in the kitchen; Mara joins her at 10:36; Daniel
        comes in at 10:39."""
        d = self.v16()
        m, q = d.day3, d.day3.quiet
        for r in data.ROOMS:
            m.convos.active[r] = False
        dan, ele, mara, leo = (m.people[x] for x in ("daniel", "elena", "mara", "leo"))
        leo.room = "brothers_room"
        q.start(leo, "rest", 18)
        for a, b in (("daniel", "mara"), ("daniel", "elena"), ("elena", "mara")):
            q.exchanged[(a, b)] = 15
        dan.room, ele.room, mara.room = "brothers_room", "back_room", "back_room"
        for p in (dan, ele, mara):
            q.start(p, "rest", 18)
        q.end(ele, 183, "time")
        q.arrive(ele, "kitchen", 183)
        q.start(ele, "sit", 183)
        q.end(mara, 216, "time")
        q.arrive(mara, "kitchen", 216)
        q.start(mara, "sit", 216)
        q.end(dan, 219, "time")
        q.arrive(dan, "kitchen", 219)
        return m, q

    @staticmethod
    def before_now(prompt):
        lines = prompt.splitlines()
        i = next(i for i, x in enumerate(lines) if x.startswith("Now, "))
        return lines[:i]

    def test_a_meeting_line_says_when_they_last_spoke_what_came_between_and_who_came_in(self):
        """Fix 1: just before "Now", one line for each person present not spoken with for 60 minutes or more."""
        m, q = self.apart()
        mara, dan = m.people["mara"], m.people["daniel"]
        before = self.before_now(m.prompt_for(mara, 73, m.options_for(mara)))
        self.assertEqual(before[-2:], [
            "You last spoke with Daniel at min 15. Since then you lay on your bed until 10:36. Daniel has just come "
            "into the kitchen.",
            "You last spoke with Elena at min 15. Since then you lay on your bed until 10:36."])
        # The one who came in: their own arrival, and a line they spoke within the hour leaves no line.
        q.exchanged[("daniel", "elena")] = 190
        before = self.before_now(m.prompt_for(dan, 73, m.options_for(dan)))
        self.assertEqual(before[-1], "You last spoke with Mara at min 15. Since then you lay on your bed until 10:39. "
                                     "You have just come into the kitchen, where Mara is.")
        self.assertFalse(any(x.startswith("You last spoke with Elena") for x in before))
        # Someone not spoken with all day.
        del q.exchanged[("daniel", "mara")]
        before = self.before_now(m.prompt_for(mara, 73, m.options_for(mara)))
        self.assertIn("You have not spoken with Daniel today. So far today you lay on your bed until 10:36. Daniel has "
                      "just come into the kitchen.", before)

    def test_no_meeting_line_before_minute_90(self):
        m, q = self.apart()
        mara = m.people["mara"]
        q.exchanged = {}
        prompt = m.prompt_for(mara, 29, m.options_for(mara))
        self.assertFalse(any(x.startswith(("You last spoke with", "You have not spoken with"))
                             for x in prompt.splitlines()), prompt)

    def test_a_rest_of_an_hour_cools_a_grudge_of_3_to_2(self):
        """Fix 2: a rest of 60 minutes or more ends, and each grudge at 3 drops to 2; shorter, nothing changes."""
        d = self.v16()
        m, q = d.day3, d.day3.quiet
        leo, mara = m.people["leo"], m.people["mara"]
        self.assertEqual((leo.grudges["daniel"].strength, mara.grudges["daniel"].strength), (3, 3))
        mara.grudge("leo").strength = 2
        leo.room, mara.room = "brothers_room", "back_room"
        q.start(leo, "rest", 30)
        q.start(mara, "rest", 30)
        q.end(leo, 90, "time")
        q.end(mara, 87, "acted")
        self.assertEqual(leo.grudges["daniel"].strength, 2)
        self.assertEqual((mara.grudges["daniel"].strength, mara.grudges["leo"].strength), (3, 2))
        self.assertEqual([(c["minute"], c["who"], c["against"]) for c in q.cooled], [(90, "leo", "daniel")])
        self.assertIn([90, "leo", "daniel"], [[c["minute"], c["who"], c["against"]]
                                               for c in q.transcript()["cooled"]])
        # An answer can raise it again, as before.
        leo.grudges["daniel"].rise(93, "you were angry with Daniel", kind="angry")
        self.assertEqual(leo.grudges["daniel"].strength, 3)
        # The story says it.
        self.assertIn("- 08:30: Leo's grudge against Daniel cools from 3 to 2 (after a rest of an hour or more).",
                      importlib.import_module("story").render_day2(m))

    def test_prompt_headings_say_today_from_minute_90(self):
        """Fix 3: from minute 90 on, "this morning" in the headings is "today"; before, as it was."""
        d = self.v16()
        m = d.day3
        leo = m.people["leo"]
        leo.said_lines.append("min 03, you confronted Daniel.")
        early = m.prompt_for(leo, 29, m.options_for(leo))
        for heading in ("What you are sure of this morning:", "Your own last words this morning:",
                        "What else happened this morning, most recent last:"):
            self.assertIn("\n" + heading + "\n", early)
        late = m.prompt_for(leo, 30, m.options_for(leo))
        for heading in ("What you are sure of today:", "Your own last words today:",
                        "What else happened today, most recent last:"):
            self.assertIn("\n" + heading + "\n", late)
        # Every heading, that is: the house line's "not to be gone to this morning" is not one.
        self.assertEqual([x for x in late.splitlines() if "this morning" in x and x.endswith(":")], [])

    def test_a_rest_under_an_hour_does_not_count_toward_the_two(self):
        """Fix 4: v17 seed 1's Daniel lay down at 12:39 and was up at 13:00; that was not one of his two rests."""
        d = self.v16()
        m, q = d.day3, d.day3.quiet
        dan = m.people["daniel"]
        dan.room = "brothers_room"
        dan.needs["rests"] = 1
        q.start(dan, "rest", 339)
        q.end(dan, 360, "acted")
        self.assertEqual(dan.needs["rests"], 1)
        q.start(dan, "rest", 480)
        q.end(dan, 540, "time")
        self.assertEqual(dan.needs["rests"], 2)

    # ---------- runs past day 3 (reports/multiday.md) ----------
    def test_a_run_goes_on_to_day_5(self):
        """Fix 1: --days 5 plays days 3 to 5 as quiet days, each but the last followed by its night and night mind."""
        runs_dir, cache_dir = os.path.join(self.dirs.root, "runs"), os.path.join(self.dirs.root, "cache")
        os.makedirs(cache_dir)
        name = "daniel_ate_it-seed2"
        shutil.copyfile(os.path.join(V16_CACHE, f"{self.MODEL}-{name}.json"),
                        os.path.join(cache_dir, f"{self.MODEL}-{name}.json"))
        meta, code = run(2, client=HushFake(), runs_dir=runs_dir, cache_dir=cache_dir, quiet=True, days=5)
        self.assertEqual(code, 0, meta)
        tr = json.load(open(os.path.join(runs_dir, f"{name}.transcript.json"), encoding="utf-8"))
        for k in ("day3", "night3", "mind3", "day4", "night4", "mind4", "day5"):
            self.assertIn(k, tr)
        self.assertNotIn("night5", tr)
        for k in ("day3", "day4", "day5"):
            self.assertEqual(max(s["end"] for s in tr[k]["quiet"]["spans"]), 840, k)
            # The day's 40, and Q5's own 8 on top (reports/facts_and_evening.md, fix 5).
            evening = sum(s["asks"] for s in tr[k]["quiet"]["stretches"] if s["trigger"] == "Q5")
            self.assertLessEqual(evening, 8, k)
            self.assertLessEqual(meta[f"{k}_quiet"]["day_asks"] - evening, 40, k)
        self.assertEqual(meta["days"], 5)
        story = open(os.path.join(runs_dir, f"{name}.md"), encoding="utf-8").read()
        for title in ("# The third morning (day 6)", "# The third night", "# The morning of day 7", "# Night 4",
                      "# The morning of day 8"):
            self.assertIn("\n" + title + "\n", story)
        self.assertLess(story.index("# The morning of day 7"), story.index("# Night 4"))

    def test_a_run_stops_after_day_3_by_default(self):
        runs_dir, cache_dir = os.path.join(self.dirs.root, "runs"), os.path.join(self.dirs.root, "cache")
        os.makedirs(cache_dir)
        name = "daniel_ate_it-seed2"
        shutil.copyfile(os.path.join(V16_CACHE, f"{self.MODEL}-{name}.json"),
                        os.path.join(cache_dir, f"{self.MODEL}-{name}.json"))
        meta, code = run(2, client=HushFake(), runs_dir=runs_dir, cache_dir=cache_dir, quiet=True)
        self.assertEqual(code, 0, meta)
        tr = json.load(open(os.path.join(runs_dir, f"{name}.transcript.json"), encoding="utf-8"))
        self.assertEqual(list(tr), ["day1", "night", "mind1", "day2", "night2", "mind2", "day3", "chronicle"])
        self.assertNotIn("days", meta)

    def test_a_day_3_afternoon_act_is_yesterday_and_a_night_event_has_no_clock(self):
        """Fix 2: a quiet day's minutes from 90 on are the day's, not the night's; the night keeps a minute after the
        day's last (21:00), and a night event is never written as a clock time."""
        def policy(who, minute, options):            # at night, Leo is angry with Daniel; by day, nobody acts
            return (options[0], "Daniel") if minute is None and who == "leo" else None
        d = self.v16(client=PolicyFake(policy))
        m, chron = d.day3, d.chron
        self.quiet.play(m)
        chron.add_day(m)
        leo, dan = m.people["leo"], m.people["daniel"]
        leo.grudge("daniel").rise(600, "you were angry with Daniel", kind="angry")       # 17:00, an afternoon answer
        leo.suspicion.target, leo.suspicion.strength = "daniel", 2      # so that a fall at night leaves it standing
        leo.suspected_at = [600]
        dan.guilt_events.append((600, "you let them blame Leo, at 17:00"))
        n3 = self.night.Night(m, d.oracle, number=3, house=chron.house_state()).run()
        nleo = n3.people["leo"]
        self.assertTrue([e for e in nleo.grudges["daniel"].events if e[2] == "angry" and e[0] >= 840],
                        "the night's answers keep a minute after the day")
        line = next(x for x in n3.m.inside_lines(nleo) if x.startswith("Against Daniel"))
        self.assertIn("17:00", line)
        self.assertIn("; and tonight", line)
        for clock in ("08:30", "21:00", "21:"):
            self.assertNotIn(clock, line)
        chron.add_night(n3)
        day4 = Morning.next_day(m, n3, d.oracle, chronicle=chron)
        p4 = day4.people["leo"]
        line = next(x for x in day4.inside_lines(p4) if x.startswith("Against Daniel"))
        self.assertRegex(line, r"yesterday at [^;]*17:00")
        self.assertIn("; and last night", line)
        self.assertNotIn("last night at", line)
        self.assertNotIn("21:00", line)
        self.assertEqual([e[4] for e in p4.grudges["daniel"].events if e[0] == 600], [("D", 3)])
        self.assertTrue(all(e[4] == ("N", 3) for e in p4.grudges["daniel"].events if e[0] >= 840))
        self.assertIn((("D", 3), [600]), p4.suspected_past)
        self.assertEqual([e[2] for e in day4.people["daniel"].guilt_events if e[0] == 600], [("D", 3)])
        self.assertEqual((m.night_minute(), d.day2.night_minute()), (840, 90))

    def test_a_night_suspicion_is_tonight_not_a_clock(self):
        """Fix 2: on a quiet day's night, a suspicion answered at night reads "tonight", never 21:00."""
        d = self.v16()
        m = d.day3
        self.quiet.play(m)
        leo = m.people["leo"]
        leo.knows_culprit = None
        leo.suspicion.target, leo.suspicion.strength = "daniel", 2
        leo.suspected_past, leo.suspected_at = [], [600, 840]
        line = next(x for x in m.inside_lines(leo) if x.startswith("About the can"))
        self.assertIn("you thought Daniel took it, this morning at 17:00, and tonight", line)
        self.assertNotIn("21:00", line)

    # ---------- stage B: further along the street, weakness, dozing (reports/stage_b.md) ----------
    STILL = {"wake:daniel:leo": 0.99, "door:daniel:leo": 0.99, "door:daniel:elena": 0.99, "door:daniel:mara": 0.99,
             "return:daniel:leo": 0.99, "return:daniel:elena": 0.99, "return:daniel:mara": 0.99,
             "doze:leo": 0.99, "doze:elena": 0.99, "doze:mara": 0.99, "doze:daniel": 0.99}

    def night3(self, bed, draws, setup=None, react=None):
        """v16 seed 2's day 3 played (HushFake), then night 3: bed[who] is their bedtime choice (sleep if absent),
        react(who, options) their other night answers; every prompt the night asks is kept."""
        class Nights(HushFake):
            def __init__(self):
                super().__init__()
                self.prompts = []

            def generate(self, system, prompt, schema=None):
                if schema is None and "Now, " not in prompt:        # a night decision
                    self.prompts.append(prompt)
                    self.requests += 1
                    who = re.match(r"You are (\w+),", prompt).group(1).lower()
                    opts = re.findall(r"^- (\w+):", prompt.split("Your options:")[-1], flags=re.M)
                    want = bed.get(who) if "- sleep:" in prompt else (react(who, opts) if react else None)
                    pick = want if want in opts else opts[0]
                    return json.dumps({"option": pick, "say": None, "feeling": "tense", "reason": "Night.",
                                       "suspects": "nobody", "angry_at": "nobody"})
                return super().generate(system, prompt, schema)
        client = Nights()
        d = self.v16(client=client)
        m, chron = d.day3, d.chron
        self.quiet.play(m)
        chron.add_day(m)
        if setup:
            setup(m)
        n3 = self.night.Night(m, d.oracle, draws=draws, number=3, house=chron.house_state()).run()
        return d, m, n3, client

    def test_w5_is_offered_once_someone_knows_next_door_is_empty(self):
        """1: v16 seed 2's Daniel got inside the neighbour's house on night 2 and found nothing. From day 3 he has the
        far street: a fact line, the house line's places, two day options and a bedtime choice. So do Leo and Mara,
        whose neighbour's-house line says he came back with nothing (reports/stage_b_fixes.md, fix 1), and from
        reports/household_knowledge.md Elena too: the whole house knows by morning. On day 2 nobody does."""
        night = self.night
        d = self.v16()
        m = d.day3
        self.assertEqual({q: p.knows_empty for q, p in m.people.items()},
                         {"daniel": True, "elena": True, "leo": True, "mara": True})
        self.assertFalse(any(p.knows_empty for p in d.day2.people.values()))
        dan, elena = m.people["daniel"], m.people["elena"]
        late = m.prompt_for(dan, 70, m.options_for(dan))
        self.assertIn("\n" + night.STREET_UNSEARCHED + "\n", late)
        self.assertIn("Outside, and not to be gone to this morning: the street, the neighbour's house and the houses "
                      "further along the street.", late)
        self.assertIn("\n- propose_far: (speech) say someone should try the houses further along the street tonight\n",
                      late)
        self.assertIn("\n- volunteer_far: (speech) offer to go further along the street tonight yourself\n", late)
        elena = d.day2.people["elena"]
        other = d.day2.prompt_for(elena, 0, d.day2.options_for(elena))
        for x in ("further along", "propose_far", "volunteer_far"):
            self.assertNotIn(x, other)
        d, m, n3, client = self.night3({}, self.STILL)
        beds = {re.match(r"You are (\w+),", p).group(1): p for p in client.prompts if "- sleep:" in p}
        self.assertIn("\n- go_further: wait until the others are asleep, then go out by the front door, past the "
                      "neighbour's house, to the houses further along the street", beds["Daniel"])
        self.assertIn("Outside: the street, the neighbour's house and the houses further along the street.",
                      beds["Daniel"])
        self.assertIn("\n- go_further: ", beds["Elena"])

    def test_far_houses_are_drawn_once_and_a_searched_house_is_empty(self):
        """2: each further house's food is drawn once, when first entered (45% none, 30% 2, 18% 4, 7% 6); a searched
        house is empty afterwards, and the next trip reaches the next house."""
        night = self.night
        self.assertEqual([night.far_house_portions(u) for u in (0.0, 0.449, 0.45, 0.749, 0.75, 0.929, 0.93, 0.999)],
                         [0, 0, 2, 2, 4, 4, 6, 6])
        d, m, n3, _ = self.night3({"daniel": "go_further"}, {**self.STILL, "trip_far:daniel": 0.0, "far_house:0": 0.8})
        g = n3.groups[0]
        self.assertEqual((g["far"], g["street"], g["found"], g["took"]), (True, "clean", 4, 4))
        self.assertEqual(n3.portions, m.portions + 4)
        self.assertEqual(n3.house_state()["far"], {"houses": [4], "us": [0.8], "searched": 1})
        self.assertIn("past the neighbour's house", " ".join(n3.lines["daniel"]))
        self.assertIn("found 4 portions of food", " ".join(n3.lines["daniel"]))
        # The next trip reaches the next house, drawn when first entered; the first is not drawn again.
        n4 = self.night.Night(m, d.oracle, number=4, house=n3.house_state(),
                              draws={**self.STILL, "trip_far:daniel": 0.0, "far_house:1": 0.1}).run()
        self.assertEqual((n4.groups[0]["found"], n4.house_state()["far"]),
                         (0, {"houses": [4, 0], "us": [0.8, 0.1], "searched": 2}))
        # Scared off before getting inside: no house is searched.
        n5 = self.night.Night(m, d.oracle, number=5, house=n3.house_state(),
                              draws={**self.STILL, "trip_far:daniel": 0.5}).run()
        self.assertEqual((n5.groups[0]["street"], n5.groups[0]["found"], n5.house_state()["far"]["searched"]),
                         ("scare_there", None, 1))

    def test_weakness_shifts_the_street_tables(self):
        """3: W2's shifts, on the near and the far tables; a group takes its weakest member's shift at half size, and
        the near table half of that shift (reports/stage_b_fixes.md, fix 2)."""
        night = self.night

        def r(t):
            return tuple(round(x, 4) for x in t)
        self.assertEqual(r(night.street_table(1)), (0.62, 0.14, 0.18, 0.06))
        self.assertEqual(r(night.street_table(1, shift=night.body_shift(2, 0))), (0.60, 0.14, 0.18, 0.08))
        self.assertEqual(r(night.street_table(1, shift=night.body_shift(3, 0))), (0.56, 0.14, 0.19, 0.11))
        self.assertEqual(r(night.street_table(1, shift=night.body_shift(0, 2))), (0.61, 0.14, 0.18, 0.07))
        self.assertEqual(r(night.street_table(1, far=True)), (0.45, 0.17, 0.23, 0.15))
        self.assertEqual(r(night.street_table(2, far=True)), (0.55, 0.15, 0.22, 0.08))
        self.assertEqual(r(night.street_table(1, far=True, shift=night.body_shift(2, 0))), (0.41, 0.17, 0.23, 0.19))
        weakest = night.group_shift([night.body_shift(3, 0), night.body_shift(0, 0)])
        self.assertEqual(r(night.street_table(2, shift=weakest)), (0.67, 0.12, 0.155, 0.055))
        # Night 3 follows a quiet day: Daniel's own shift, from his fasting and debt at bedtime, sets his table.
        d, m, n3, _ = self.night3({"daniel": "go_next_door"}, {**self.STILL, "trip:daniel": 0.6})
        dan = m.people["daniel"]
        shift = night.body_shift(self.quiet.fast_stage(m.quiet.fast(dan, 840)), self.quiet.debt_stage(dan.needs["debt"]))
        self.assertNotEqual(shift, night.body_shift(0, 0))
        g = n3.groups[0]
        self.assertEqual(r(g["table"]), r(night.street_table(1, shift=shift)))
        self.assertEqual(g["street"], night.pick_street(0.6, g["table"]))
        self.assertNotEqual(g["street"], "clean")           # 0.6 is clean on the plain table (under 0.62)
        # Nights 1 and 2 have no needs, so no shift, and their groups are as they were.
        self.assertNotIn("table", d.n2.groups[0])

    def test_an_exhausted_watcher_may_doze_and_then_notices_nothing(self):
        """3: the doze draw, 0.3 + 0.05 × (debt − 24), at most 0.7, for an exhausted watcher or listener."""
        night = self.night
        self.assertEqual([night.doze_chance(x) for x in (23.9, 24, 30, 40)], [0.0, 0.3, 0.6, 0.7])

        def tired(m):
            m.people["elena"].needs["debt"] = 30.0
        bed = {"daniel": "go_next_door", "elena": "watch_door"}
        d, m, n3, _ = self.night3(bed, {**self.STILL, "doze:elena": 0.5, "trip:daniel": 0.1}, setup=tired)
        self.assertEqual(n3.dozed, {"elena"})
        self.assertFalse([x for x in n3.noticing if x["who"] == "elena" and x["noticed"]])
        self.assertIn("You dozed off in the night, and woke by the door at dawn.", " ".join(n3.lines["elena"]))
        self.assertNotIn("daniel", n3.knows["elena"])
        d, m, n3, _ = self.night3(bed, {**self.STILL, "doze:elena": 0.65, "trip:daniel": 0.1}, setup=tired)
        self.assertEqual(n3.dozed, set())
        self.assertIn("daniel", n3.knows["elena"])
        # Not exhausted: no doze, whatever the draw.
        d, m, n3, _ = self.night3(bed, {**self.STILL, "doze:elena": 0.0, "trip:daniel": 0.1})
        self.assertEqual(n3.dozed, set())

    def test_someone_who_does_not_come_back_is_gone_and_each_knows_it_their_way(self):
        """4: Daniel goes further along alone and is lost. Leo saw him go, Elena heard the door, Mara slept. From
        then on he is in no room and never asked; each one's prompts say what they know."""
        bed = {"daniel": "go_further", "leo": "lie_awake", "elena": "lie_awake", "mara": "sleep"}

        def react(who, opts):
            return "let_daniel_go" if who == "leo" else "stay_in_bed"
        d, m, n3, _ = self.night3(bed, {**self.STILL, "trip_far:daniel": 0.99}, react=react)
        self.assertEqual(n3.away, {"daniel"})
        d.chron.add_night(n3)
        day4 = Morning.next_day(m, n3, d.oracle, chronicle=d.chron)
        self.assertIsNone(day4.people["daniel"].room)
        sure = {q: day4.people[q].sure[0] for q in ("leo", "elena", "mara")}
        self.assertIn("Daniel is not here: you saw him go out in the night, and he has not come back.", sure["leo"])
        self.assertIn("Daniel is not here: his bed is empty and he is nowhere in the house. In the night you heard the "
                      "front door; he has not come back.", sure["elena"])
        # Where he went is the house's by morning (reports/household_knowledge.md).
        self.assertIn("Daniel is not here: his bed is empty and he is nowhere in the house. (you saw it)", sure["mara"])
        facts = {q: next(x for x in day4.inside_lines(day4.people[q]) if x.startswith("About Daniel:"))
                 for q in ("leo", "elena", "mara")}
        self.assertEqual(facts, {
            "leo": "About Daniel: you saw him go out last night, and he has not come back.",
            "elena": "About Daniel: last night you heard the front door, and by morning he was gone; he has not come "
                     "back.",
            "mara": "About Daniel: he went further along the street last night and has not come back."})
        self.quiet.play(day4)
        self.assertFalse([x for rec in day4.log for x in rec["decisions"] if x["person"] == "daniel"])
        self.assertTrue(all("daniel" not in rec for rec in day4.transcript["quiet"]["needs"]))

    def test_grudge_lines_say_today_from_minute_90(self):
        """5: on a quiet day from minute 90 on, and at its night, a grudge line's own day reads "today at"."""
        d = self.v16()
        m = d.day3
        leo = m.people["leo"]
        leo.grudges["daniel"].rise(60, "you were angry with Daniel", kind="angry")

        def line(text):
            return next(x for x in text.splitlines() if x.startswith("Against Daniel"))
        self.assertIn("this morning at minute 60", line(m.prompt_for(leo, 29, m.options_for(leo))))
        late = line(m.prompt_for(leo, 30, m.options_for(leo)))
        self.assertIn("today at minute 60", late)
        self.assertNotIn("this morning", late)
        night = line(m.prompt_for(leo, None, [Option("sleep", "go to sleep")], night=["Now it is night."]))
        self.assertIn("today at minute 60", night)

    # ---------- reports/stage_b_fixes.md ----------
    def test_w5_is_known_from_a_neighbour_line_that_came_back_with_nothing(self):
        """Fix 1: whoever's own neighbour's-house line says a trip there came back with nothing knows next door is
        empty, as well as whoever went inside. v16 seed 2, day 3: Leo and Mara (Daniel came back with nothing) are
        offered W5; and Elena, since by morning the whole house knows he came back with nothing
        (reports/household_knowledge.md)."""
        night = self.night
        d = self.v16()
        m = d.day3
        empty = {q for q in data.ORDER if m.neighbour[q].endswith(" and came back with nothing. Outside is dangerous.")}
        self.assertEqual(empty, {"elena", "leo", "mara"})
        self.assertEqual({q: p.knows_empty for q, p in m.people.items()},
                         {"daniel": True, "elena": True, "leo": True, "mara": True})
        for q in ("elena", "leo", "mara"):
            p = m.people[q]
            late = m.prompt_for(p, 70, m.options_for(p))
            self.assertIn("\n" + night.STREET_UNSEARCHED + "\n", late, q)
            self.assertIn("- propose_far:", late, q)
            self.assertIn("- volunteer_far:", late, q)
        d, m, n3, client = self.night3({}, self.STILL)
        beds = {re.match(r"You are (\w+),", p).group(1): p for p in client.prompts if "- sleep:" in p}
        for name in ("Daniel", "Elena", "Leo", "Mara"):
            self.assertIn("\n- go_further: ", beds[name], name)

    def test_weakness_shifts_the_near_table_by_half_of_the_far(self):
        """Fix 2: a walk next door is not as deadly to a weak body as the far street: the near table takes half the
        shift the far one does. The far table is unchanged."""
        night = self.night

        def r(t):
            return tuple(round(x, 4) for x in t)
        self.assertEqual(r(night.street_table(1, shift=night.body_shift(2, 0))), (0.60, 0.14, 0.18, 0.08))
        self.assertEqual(r(night.street_table(1, shift=night.body_shift(3, 0))), (0.56, 0.14, 0.19, 0.11))
        self.assertEqual(r(night.street_table(1, shift=night.body_shift(0, 2))), (0.61, 0.14, 0.18, 0.07))
        self.assertEqual(r(night.street_table(1, shift=night.body_shift(3, 2))), (0.55, 0.14, 0.19, 0.12))
        weakest = night.group_shift([night.body_shift(3, 0), night.body_shift(0, 0)])
        self.assertEqual(r(night.street_table(2, shift=weakest)), (0.67, 0.12, 0.155, 0.055))
        # Far: the full shift, as before.
        self.assertEqual(r(night.street_table(1, far=True, shift=night.body_shift(2, 0))), (0.41, 0.17, 0.23, 0.19))
        self.assertEqual(r(night.street_table(1, far=True, shift=night.body_shift(3, 2))), (0.31, 0.17, 0.25, 0.27))
        self.assertEqual(r(night.street_table(2, far=True, shift=weakest)), (0.49, 0.15, 0.23, 0.13))

    def test_the_suspicion_line_says_today_from_minute_90(self):
        """Fix 3: on a quiet day from minute 90 on, and at its night, the suspicion line's own day reads "today at",
        like the grudge lines."""
        d = self.v16()
        m = d.day3
        mara = m.people["mara"]
        mara.knows_culprit = None
        mara.suspicion.target, mara.suspicion.strength = "leo", 2
        mara.suspected_at = [60]

        def line(text):
            return next(x for x in text.splitlines() if x.startswith("About the can"))
        self.assertIn("this morning at minute 60", line(m.prompt_for(mara, 29, m.options_for(mara))))
        late = line(m.prompt_for(mara, 30, m.options_for(mara)))
        self.assertIn("today at minute 60", late)
        self.assertNotIn("this morning", late)
        night = line(m.prompt_for(mara, None, [Option("sleep", "go to sleep")], night=["Now it is night."]))
        self.assertIn("today at minute 60", night)
        self.assertNotIn("this morning", night)

    # ---------- nothing before day 3 changes ----------
    def test_v16_through_night_2_is_unchanged(self):
        """Seeds 2 and 3, through night 2. Seed 1's Daniel got inside the neighbour's house on night 1 and found it
        empty, so from day 2 he has the far street (stage B, W5): seed 1 replays until his first day-2 prompt, the
        first prompt of anyone who knows next door is empty, and no further (test_v16_seed_1_until_w5)."""
        story = importlib.import_module("story")
        for seed in (2, 3):
            d = self.v16(seed=seed)
            text = (render(d.day1, seed, self.MODEL, f"python morning.py --seed {seed}") + story.render_night(d.n1)
                    + story.render_mind(d.mind1) + story.render_day2(d.day2) + story.render_night(d.n2)
                    + story.render_mind(d.mind2))
            orig = read(os.path.join(V16_RUNS, f"daniel_ate_it-seed{seed}.md"))
            orig = orig[:orig.index("# The third morning (day 6)")]
            if seed == 1:       # S4 and S8 warn since v16 (reports/checks_to_warnings.md): two verdicts read kept
                orig = (orig.replace("**rejected: S8 elena stop: not twice**", "**kept**")
                        .replace("**rejected: S8 daniel give: no such event**", "**kept**"))
            self.assertEqual(text, orig, seed)

    def test_v16_seed_1_until_w5(self):
        """Seed 1 from its own answers: day 1, night 1 and mind 1 are as in v16; the first prompt with no cached answer
        is Daniel's first on day 2, the first of anyone who knows next door is empty."""
        name = "daniel_ate_it-seed1"
        copy = os.path.join(self.dirs.root, f"{self.MODEL}-{name}.json")
        shutil.copyfile(os.path.join(V16_CACHE, f"{self.MODEL}-{name}.json"), copy)
        oracle = Oracle(Cache(copy), self.MODEL, 1, client=None, replay=True)
        missed = []
        real = oracle.ask

        def ask(system, prompt, schema=None):
            try:
                return real(system, prompt, schema)
            except importlib.import_module("gemini").CacheMiss:
                missed.append(prompt)
                raise
        oracle.ask = ask
        chron = self.chron.Chronicle(1, "daniel")
        day1 = Morning(oracle, 1)
        for t in range(day1.turns):
            day1.turn(t)
        day1.finish()
        chron.add_day(day1)
        n1 = self.night.Night(day1, oracle, number=1).run()
        chron.add_night(n1)
        self.mind.NightMind(n1, chron, oracle).run()
        self.assertEqual(missed, [])
        day2 = Morning.next_day(day1, n1, oracle, chronicle=chron)
        self.assertEqual({q: p.knows_empty for q, p in day2.people.items()},
                         {"daniel": True, "elena": True, "leo": True, "mara": True})
        with self.assertRaises(importlib.import_module("gemini").CacheMiss):
            day2.turn(0)
        self.assertTrue(missed[0].startswith("You are Daniel,"), missed[0][:40])
        self.assertRegex(missed[0], r"(?m)^Now, minute 00, ")
        self.assertIn("\n" + self.night.STREET_UNSEARCHED + "\n", missed[0])

    # ---------- what the family is told about outings, and the evening (reports/facts_and_evening.md) ----------
    OUT = "About going out at night: "
    FAR_NIGHT = {"daniel": "go_further", "leo": "lie_awake", "elena": "sleep", "mara": "watch_door"}
    FAR_REST = ("the houses past it have not been searched: nobody knows what is left in them, and they are further "
                "and more dangerous than next door.")

    @staticmethod
    def let_go(who, opts):
        return next((o for o in ("let_daniel_go", "go_anyway", "stay_in_bed") if o in opts), opts[0])

    def far_day4(self, draws):
        """v16 seed 2's night 3 with Daniel going further along: Leo (awake in his room) sees him go, Mara watches the
        door, Elena sleeps through it. Then day 4 is set up."""
        d, m, n3, client = self.night3(self.FAR_NIGHT, {**self.STILL, **draws}, react=self.let_go)
        d.chron.add_night(n3)
        return d, m, n3, Morning.next_day(m, n3, d.oracle, chronicle=d.chron), client

    def test_far_positions_are_heard_as_what_they_are(self):
        """1: on a quiet day, an offer to go further along and saying someone should try there are heard as such, not
        as "says he will not go". A real refusal still is."""
        m = self.v16().day3
        dan, leo = m.people["daniel"], m.people["leo"]
        self.assertEqual(m.line_text(dan, "volunteer_far", None, "I'll go.", leo, option="volunteer_far"),
                         'Daniel offers to go further along the street tonight: "I\'ll go."')
        self.assertEqual(m.line_text(dan, "propose_far", None, "Someone should.", leo, option="propose_far"),
                         'Daniel says someone should try the houses further along the street tonight: '
                         '"Someone should."')
        self.assertEqual(m.line_text(dan, "decline", None, "Not me.", leo, option="refuse_to_go"),
                         'Daniel says he will not go: "Not me."')
        # Played: Daniel offers at min 00, and what Leo has of it says so.
        d = self.v16(client=PolicyFake(lambda who, minute, opts: "volunteer_far" if (who, minute) == ("daniel", 0)
                                       else None))
        self.quiet.play(d.day3)
        heard = [x for _, x in d.day3.people["leo"].memory if x.startswith("Daniel ") and "Words of daniel at 0" in x]
        self.assertEqual(heard, ['Daniel offers to go further along the street tonight: "Words of daniel at 0."'])

    def test_the_street_line_says_how_many_houses_were_searched_as_each_knows_it(self):
        """2: whoever searched a house further along is told when, and that it held nothing; the rest are unsearched.
        The others are told what the house saw (reports/household_knowledge.md): who went further along, when, and
        that they came back with nothing; not what the house held."""
        d, m, n3, day4, _ = self.far_day4({"trip_far:daniel": 0.0, "far_house:0": 0.1})
        g = n3.groups[0]
        self.assertEqual((g["far"], g["street"], g["found"], g["took"]), (True, "clean", 0, 0))
        # W1 (amendment 2): every empty house holds some water (its cistern at least), and he carried some home.
        w = self.night.water_words(g["water"])
        self.assertEqual(day4.street["daniel"], "About the street: you searched one house further along it last night, "
                                                f"and it held no food, and you brought back {w} of water; "
                         + self.FAR_REST)
        seen = ("About the street: Daniel went further along it last night and came back with nothing; nobody knows "
                "what is left in the houses further along, and they are further and more dangerous than next door.")
        for q in ("elena", "leo", "mara"):
            self.assertEqual(day4.street[q], seen.replace("with nothing", "with water"), q)
        mara = day4.people["mara"]
        self.assertIn("\n" + day4.street["mara"] + "\n", day4.prompt_for(mara, 0, day4.options_for(mara)))
        # Scared off before the door: the house sees the same; only Daniel knows he did not get in.
        d, m, n3, day4, _ = self.far_day4({"trip_far:daniel": 0.5})
        self.assertEqual((n3.groups[0]["street"], n3.groups[0]["found"]), ("scare_there", None))
        self.assertEqual(day4.street["leo"], seen)

    def test_every_quiet_prompt_carries_the_outings_line(self):
        """3: on quiet days and their nights, each prompt lists the trips its person knows of (the neighbour's-house
        rule): who, where, which night, and the outcome as they know it; in the trip block, outside the budget."""
        out = self.OUT
        d = self.v16()
        m = d.day3
        nothing = out + "Daniel went to the neighbour's house last night and came back with nothing."
        # Elena slept through it, but the whole house knows by morning (reports/household_knowledge.md).
        expect = {"daniel": out + "you went to the neighbour's house last night, got inside and found no food.",
                  "elena": nothing, "leo": nothing, "mara": nothing}
        lines = {q: [x for x in m.trip_lines(m.people[q]) if x.startswith(out)] for q in data.ORDER}
        self.assertEqual(lines, {q: [x] for q, x in expect.items()})      # in the trip block: outside the 1400
        for q in data.ORDER:
            p = m.people[q]
            for t in (0, 70):
                self.assertIn("\n" + expect[q] + "\n", m.prompt_for(p, t, m.options_for(p)), (q, t))
        for p in d.day2.people.values():                                   # days 1 and 2 are as they were
            self.assertFalse([x for x in d.day2.trip_lines(p) if x.startswith(out)])
        d, m, n3, day4, client = self.far_day4({"trip_far:daniel": 0.0, "far_house:0": 0.1})
        beds = {re.match(r"You are (\w+),", p).group(1): p for p in client.prompts if "- sleep:" in p}
        for q in data.ORDER:
            self.assertIn("\n" + expect[q] + "\n", beds[data.PEOPLE[q]["name"]], q)
        both = (out + "Daniel went to the neighbour's house the night before last and came back with nothing; Daniel "
                      "went further along the street last night and came back with water.")
        w = self.night.water_words(n3.groups[0]["water"])          # W1: the house further along held water
        self.assertEqual({q: [x for x in day4.trip_lines(day4.people[q]) if x.startswith(out)] for q in data.ORDER}, {
            "daniel": [out + "you went to the neighbour's house the night before last, got inside and found no food; "
                             "you went further along the street last night, got inside a house there and found no "
                             f"food, and brought back {w} of water."],
            "elena": [both], "leo": [both], "mara": [both]})

    def test_yesterdays_positions_are_named_as_said_yesterday_about_last_night(self):
        """4: the carried-in line of the trip positions says they were said yesterday, about last night."""
        d = self.v16()
        leo = d.day3.carry["leo"]
        self.assertIn("- What was said yesterday about going out last night, where it was left: Mara said Daniel is "
                      "the one who should go (min 06); you said Daniel is the one who should go (min 06); Daniel said "
                      "he still means to go (min 09); Elena said nobody should go (min 12); then Daniel went to the "
                      "neighbour's house anyway and came back with nothing.", leo)    # its end: ten_days_prep.md
        self.assertFalse([x for x in leo if "About going to the neighbour's house last night" in x])

    # ---------- what the whole house knows by morning (reports/household_knowledge.md) ----------
    def test_a_trip_is_known_to_the_whole_house_by_the_next_morning(self):
        """1: from the morning after a trip, everyone in the house knows who went, where, which night, and what could
        be seen of it: back with nothing, back with food, or not back. Their outings, neighbour's-house and street
        lines follow, and so does knowing next door is empty. What happened out there stays with whoever went."""
        out, night = self.OUT, self.night
        # Elena slept through night 2: by day 3 she knows Daniel went next door and came back with nothing.
        d = self.v16()
        m = d.day3
        elena = m.people["elena"]
        self.assertEqual({q: p.knows_empty for q, p in m.people.items()},
                         {"daniel": True, "elena": True, "leo": True, "mara": True})
        self.assertEqual(m.neighbour["elena"], "About the neighbour's house: Daniel went there last night and came "
                                               "back with nothing. Outside is dangerous.")
        self.assertIn(out + "Daniel went to the neighbour's house last night and came back with nothing.",
                      m.trip_lines(elena))
        text = m.prompt_for(elena, 70, m.options_for(elena))
        for x in ("\n- propose_far: ", "\n- volunteer_far: ", "\n" + night.STREET_UNSEARCHED + "\n"):
            self.assertIn(x, text)
        # Night 3, Daniel further along, back with nothing; Elena slept again. Day 4: she knows both trips, and the
        # street line of everyone but Daniel says only what could be seen.
        far = ("About the street: Daniel went further along it last night and came back with nothing; nobody knows "
               "what is left in the houses further along, and they are further and more dangerous than next door.")
        d, m, n3, day4, _ = self.far_day4({"trip_far:daniel": 0.0, "far_house:0": 0.1})
        self.assertNotIn("daniel", n3.knows["elena"])
        # W1 (amendment 2): the house he got into held water, and the house sees him carry it in.
        both = (out + "Daniel went to the neighbour's house the night before last and came back with nothing; Daniel "
                      "went further along the street last night and came back with water.")
        for q in ("elena", "leo", "mara"):
            self.assertTrue(day4.people[q].knows_empty, q)
            self.assertIn(both, day4.trip_lines(day4.people[q]), q)
            self.assertEqual(day4.street[q], far.replace("with nothing", "with water"), q)
        elena = day4.people["elena"]
        self.assertIn("\n- volunteer_far: ", day4.prompt_for(elena, 0, day4.options_for(elena)))
        self.assertTrue(day4.street["daniel"].startswith("About the street: you searched one house further along it "
                                                         "last night, and it held no food, and you brought back "))
        # Food came home: the house sees food, not what the house held, which only Daniel knows.
        d, m, n3, day4, _ = self.far_day4({"trip_far:daniel": 0.0, "far_house:0": 0.8})
        self.assertEqual(day4.street["elena"], far.replace("came back with nothing", "came back with food and water"))
        self.assertIn(out + "Daniel went to the neighbour's house the night before last and came back with nothing; "
                            "Daniel went further along the street last night and came back with food and water.",
                      day4.trip_lines(day4.people["elena"]))
        self.assertIn("it held 4 portions, all brought back", day4.street["daniel"])
        # Scared off before the door: the house sees him come back with nothing; only he knows he did not get in.
        d, m, n3, day4, _ = self.far_day4({"trip_far:daniel": 0.5})
        self.assertEqual(day4.street["leo"], far)
        self.assertEqual(day4.street["daniel"], "About the street: you went along it last night but did not get inside "
                                                "any house further along; nobody knows what is left in the houses "
                                                "further along, and they are further and more dangerous than next "
                                                "door.")
        # Not back: whoever slept through it knows by morning where he went.
        bed = {"daniel": "go_further", "leo": "lie_awake", "elena": "lie_awake", "mara": "sleep"}
        d, m, n3, _ = self.night3(bed, {**self.STILL, "trip_far:daniel": 0.99},
                                  react=lambda who, opts: "let_daniel_go" if who == "leo" else "stay_in_bed")
        d.chron.add_night(n3)
        day4 = Morning.next_day(m, n3, d.oracle, chronicle=d.chron)
        mara = day4.people["mara"]
        self.assertIn("Daniel is not here: his bed is empty and he is nowhere in the house. (you saw it)", mara.sure[0])
        self.assertIn("About Daniel: he went further along the street last night and has not come back.",
                      day4.inside_lines(mara))
        self.assertIn(out + "Daniel went to the neighbour's house the night before last and came back with nothing; "
                            "Daniel went further along the street last night and has not come back.",
                      day4.trip_lines(mara))

    # ---------- a 10-day run's preparation (reports/ten_days_prep.md) ----------
    @staticmethod
    def heard(*positions):
        """A setup for night3: everyone heard these positions on day 3 (minute, who, kind, target, option)."""
        def setup(m):
            for p in m.people.values():
                p.trip_heard = {who: (minute, kind, target, i, option)
                                for i, (minute, who, kind, target, option) in enumerate(positions)}
        return setup

    def test_yesterdays_positions_end_with_what_happened_that_night(self):
        """1: the carried-in line of yesterday's trip positions ends with what that night came to, as the house knows
        it: who went, where, anyway or not, and what could be seen; or that nobody went out."""
        said = "- What was said yesterday about going out last night, where it was left: "
        offer = (0, "daniel", "volunteer_far", None, "volunteer_far")
        nobody = (15, "elena", "object", None, "nobody_goes")
        # Daniel goes further along although Elena said nobody should go; back with nothing.
        d, m, n3, _ = self.night3({"daniel": "go_further", "leo": "lie_awake"},
                                  {**self.STILL, "trip_far:daniel": 0.0, "far_house:0": 0.1},
                                  setup=self.heard(offer, nobody), react=self.let_go)
        d.chron.add_night(n3)
        day4 = Morning.next_day(m, n3, d.oracle, chronicle=d.chron)
        line = {q: [x for x in day4.carry[q] if x.startswith(said)] for q in data.ORDER}
        # W1 (amendment 2): the house he got into held water, which he carried home.
        self.assertEqual(line["leo"], [said + "Daniel offered to go further along the street (min 00); Elena said "
                                              "nobody should go (min 15); then Daniel went further along anyway and "
                                              "came back with water."])
        self.assertEqual(line["elena"], [said + "Daniel offered to go further along the street (min 00); you said "
                                                "nobody should go (min 15); then Daniel went further along anyway "
                                                "and came back with water."])
        self.assertEqual(line["daniel"], [said + "you offered to go further along the street (min 00); Elena said "
                                                 "nobody should go (min 15); then you went further along anyway and "
                                                 "came back with water."])
        # Nobody objected: no "anyway". Food came home: "with food".
        d, m, n3, _ = self.night3({"daniel": "go_further"}, {**self.STILL, "trip_far:daniel": 0.0, "far_house:0": 0.8},
                                  setup=self.heard(offer), react=self.let_go)
        day4 = Morning.next_day(m, n3, d.oracle, chronicle=d.chron)
        self.assertIn(said + "Daniel offered to go further along the street (min 00); then Daniel went further along "
                             "and came back with food and water.", day4.carry["mara"])
        # Nobody went out.
        d, m, n3, _ = self.night3({}, self.STILL, setup=self.heard(offer, nobody))
        day4 = Morning.next_day(m, n3, d.oracle, chronicle=d.chron)
        self.assertIn(said + "Daniel offered to go further along the street (min 00); Elena said nobody should go "
                             "(min 15); then nobody went out.", day4.carry["leo"])

    def test_a_third_fasting_stage_at_168(self):
        """Fasting in days (reports/world_design.md, §4.3.1, replacing reports/ten_days_prep.md's third stage at 144):
        F3, thin and weak, at 168 (7 days); its body line states what effort costs; a Q1 crossing like the others; the
        street shift of "very weak"."""
        quiet, night = self.quiet, self.night
        self.assertEqual([quiet.fast_stage(x) for x in (71.99, 72, 167.99, 168, 300)], [1, 2, 2, 3, 3])
        self.assertEqual(quiet.body_line("starving", 3, 0), "Your body: starving, for days now: you are thin and weak; "
                                                            "stairs and carrying things tire you fast.")
        self.assertEqual(night.body_shift(3, 0), night.SHIFTS["very weak"])
        self.assertEqual(tuple(round(x, 4) for x in night.body_shift(4, 0)), (-0.20, 0.0, 0.04, 0.16))
        # Leo last ate so long ago that he crosses 168 at 12:00 of day 3, in a quiet stretch: a Q1 check like others.
        d = self.v16()
        m = d.day3
        leo = m.people["leo"]
        leo.needs["ate_at"] = 2 * 1440 + 300 - 168 * 60
        self.quiet.play(m)
        crossed = [e for e in m.quiet.need_events if (e["who"], e["need"], e["stage"]) == ("leo", "fast", 3)]
        self.assertEqual([e["minute"] for e in crossed], [300])
        self.assertEqual(crossed[0]["view"], "You had grown thin and weak: stairs and carrying things tired you fast.")
        q1 = [e for e in m.quiet.log if e["kind"] == "Q1" and (e["who"], e["need"], e["stage"]) == ("leo", "fast", 3)]
        self.assertEqual([e["minute"] for e in q1], [300])
        self.assertTrue(m.inside_lines(leo)[0].startswith("Your body: starving, for days now: you are thin and weak; "
                                                          "stairs and carrying things tire you fast"),
                        m.inside_lines(leo)[0])

    def test_far_offers_read_as_offers_on_every_day(self):
        """2: an offer to go further along reads as an offer on days 1 and 2 too."""
        d = self.v16()
        for m in (d.day1, d.day2, d.day3):
            dan, leo = m.people["daniel"], m.people["leo"]
            self.assertEqual(m.line_text(dan, "volunteer_far", None, "I'll go.", leo, option="volunteer_far"),
                             'Daniel offers to go further along the street tonight: "I\'ll go."', m.day)
            self.assertEqual(m.line_text(dan, "propose_far", None, "Try.", leo, option="propose_far"),
                             'Daniel says someone should try the houses further along the street tonight: "Try."',
                             m.day)

    def q5(self, m):
        return [e for e in m.quiet.log if e["kind"] == "Q5"]

    def test_q5_at_19_asks_whoever_took_a_trip_position_last(self):
        """5: at 19:00, with two or more awake in one room and a trip position taken there today, the one whose trip
        act is most recent is asked; the stretch has 8 asks of its own."""
        def policy(who, minute, opts):          # Daniel offers at min 00; Leo answers it whenever he can
            if (who, minute) == ("daniel", 0):
                return "volunteer_far"
            if who == "leo":
                return next((o for o in ("keep_daniel_home", "nobody_goes") if o in opts), None)

        class Kept(PolicyFake):
            prompts = []

            def generate(self, system, prompt, schema=None):
                self.prompts.append(prompt)
                return super().generate(system, prompt, schema)
        d = self.v16(client=Kept(policy))
        # Fasting in days: Leo's reaches 72 (F2) at exactly 19:00 on day 3, so its Q1 would take Q5's minute. His last
        # meal two hours earlier keeps it at 17:00.
        d.day3.people["leo"].needs["ate_at"] -= 120
        self.quiet.play(d.day3)
        m = d.day3
        entries = self.q5(m)
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual((e["minute"], e["fired"]), (720, True), e)
        last = {}
        for turn in m.transcript["turns"]:
            for a in turn["acts"]:
                if a["minute"] < 720 and world.act_of(a["option"])[0] in world.TRIP_KINDS:
                    last[a["who"]] = max(last.get(a["who"], (-1, -1)), tuple(a["decided_at"]))
        rooms = [ids for ids in e["awake"].values() if len(ids) >= 2]
        want = max((last[q], q) for ids in rooms for q in ids if q in last)[1]
        self.assertEqual(set(last), {"daniel", "leo"})
        self.assertEqual(e["asked"], want)
        self.assertEqual(want, "leo")           # his nobody_goes at 10:21 is more recent than Daniel's offer at min 00
        self.assertIn((720, self.quiet.EVENING_LINE), m.people["leo"].memory)
        # The one asked at 19:00 is told it is evening, just before "Now" (their own minute's records are not listed).
        at = [p for p in Kept.prompts if p.startswith("You are Leo,") and "\nNow, 19:00, " in p]
        self.assertEqual(len(at), 1)
        self.assertIn("\n" + self.quiet.EVENING_LINE + "\nNow, 19:00, ", at[0])
        st = next(s for s in m.quiet.stretches if s["trigger"] == "Q5")
        self.assertEqual(st["start"], 720)
        self.assertTrue(0 < st["asks"] <= 8, st)
        asked = [x for rec in m.log for x in rec["decisions"] if x.get("quiet") == "Q5"]
        self.assertEqual([(x["person"], x["mode"]) for x in asked], [(want, "model")])

    def test_q5_has_8_asks_on_top_of_the_days_40(self):
        """5: the day's asks spent before 19:00, the evening still has its 8. This day spends 32 by 19:00, so the
        day's budget is set to 30 here to have it spent."""
        with mock.patch.object(self.quiet, "DAY_ASKS", 30):
            d = self.played(client=TalkFake(talk_from=0))
        m = d.day3
        e = self.q5(m)[0]
        self.assertTrue(e["fired"], e)
        st = next(s for s in m.quiet.stretches if s["trigger"] == "Q5")
        before = sum(s["asks"] for s in m.quiet.stretches if s["start"] < 720)
        self.assertEqual(before, 30)
        self.assertTrue(0 < st["asks"] <= 8, st)
        self.assertEqual(m.quiet.asks, 30 + st["asks"])

    def test_no_q5_without_a_trip_position(self):
        """5: nobody took a trip position today: nothing happens at 19:00."""
        d = self.played(client=PolicyFake(lambda who, minute, opts: None))
        m = d.day3
        self.assertFalse([a for turn in m.transcript["turns"] for a in turn["acts"]
                          if world.act_of(a["option"])[0] in world.TRIP_KINDS])
        self.assertEqual([(e["fired"], e["why"]) for e in self.q5(m)], [(False, "no trip position today")])
        self.assertFalse([s for s in m.quiet.stretches if s["trigger"] == "Q5"])


# ---------- W1, the physical layer (reports/world_design.md §1, §2, §3.1, §4.1-§4.3, §5 Q6, §6 W1, §7) ----------
FORBIDS = re.compile(r"impossible|cannot|can't|unable|barely (stand|walk|move)", re.I)


class PhysicalLayerTest(unittest.TestCase):
    """W1: World owns the weather and the water; thirst, cold and fasting in days; rain heard and Q6; the yard and
    the water acts; water in the houses next door and further along, fixed once, carried home. Every day-3 test
    starts from v16 seed 2 as it was through night 2, replayed from cache/v16 with no API call."""
    MODEL = QuietDayTest.MODEL
    STILL = QuietDayTest.STILL
    v16 = QuietDayTest.v16
    played = QuietDayTest.played
    night3 = QuietDayTest.night3

    def setUp(self):
        self.dirs = Dirs()
        self.quiet = importlib.import_module("quiet")
        self.night = importlib.import_module("night")
        self.chron = importlib.import_module("chronicle")
        self.mind = importlib.import_module("mind")
        self.truth = importlib.import_module("truth")
        self.weather = importlib.import_module("weather")
        self.water = importlib.import_module("water")

    def tearDown(self):
        self.dirs.cleanup()

    def at(self, k, minute):
        return self.quiet.absolute(k, minute)

    def rain(self, world, k, spells, **more):
        """Day k's weather forced to these spells, (start, end) as day minutes, and mm each."""
        world.weather.force(k, [(self.at(k, a), self.at(k, b), mm) for a, b, mm in spells], **more)

    def dry(self, world, *days, **more):
        for k in days:
            world.weather.force(k, [], **more)

    def silent(self):
        return PolicyFake(lambda who, minute, opts: None)

    def v16_forced(self, client=None, **days):
        """v16 seed 2 to day 3, with day k's weather forced (days: d3=[(start, end, mm)], ...) before day 3 is set up,
        so that a spell beginning at 07:00 is heard."""
        real = self.quiet.world_of

        def forced(chronicle):
            w = real(chronicle)
            for key, spells in days.items():
                self.rain(w, int(key[1:]), spells)
            return w
        with mock.patch.object(self.quiet, "world_of", forced):
            return self.v16(client=client)

    # ---------- §1.2: World is never read while a prompt is built ----------
    def test_world_cannot_be_read_while_a_prompt_is_built(self):
        w = self.truth.World(2)
        self.assertIsNotNone(w.weather)
        with self.truth.prompting():
            with self.assertRaises(self.truth.TruthLeak):
                w.weather
            with self.assertRaises(self.truth.TruthLeak):
                w.store()
        self.assertIsNotNone(w.store())
        # The guard is on inside every prompt builder: a day prompt, a night prompt and the night mind's.
        d = self.v16()
        m = d.day3
        leo = m.people["leo"]
        self.assertIs(m.quiet.world, d.chron.world)
        real = m.inside_lines

        def leaky(p, today=False):
            m.quiet.world.store()
            return real(p, today)
        with mock.patch.object(m, "inside_lines", leaky):
            with self.assertRaises(self.truth.TruthLeak):
                m.prompt_for(leo, 30, m.options_for(leo))
            with self.assertRaises(self.truth.TruthLeak):
                m.prompt_for(leo, None, [Option("sleep", "go to sleep")], night=["Now it is night."])
        mind = self.mind.NightMind(d.n2, d.chron, d.oracle)
        with mock.patch.object(type(d.n2.m), "inside_lines", lambda self_, p, today=False: [d.chron.world.weather]):
            with self.assertRaises(self.truth.TruthLeak):
                mind.prompt_for(d.n2.m.people["leo"])
        m.prompt_for(leo, 30, m.options_for(leo))           # and without the leak, it builds

    def test_a_ten_day_fake_run_never_reads_world_in_a_prompt(self):
        """The guard is on for the whole run; litres in a prompt are only what an eye sees (multiples of 5); no body
        line forbids an act."""
        (meta, code), out = fake_morning(self.dirs, seed=2, days=10)
        self.assertEqual(code, 0, out[-3000:])
        prompts = cached_prompts(self.dirs)
        self.assertTrue([p for p in prompts if "About water:" in p])
        for p in prompts:
            for n in re.findall(r"(\d+(?:\.\d+)?) litres", p):
                self.assertEqual(float(n) % 5, 0, (n, p[:200]))
            for line in p.splitlines():
                if line.startswith("Your body:"):
                    self.assertIsNone(FORBIDS.search(line), line)

    # ---------- §4.1: the weather ----------
    def test_the_weather_is_seeded_by_string_and_follows_the_kew_normals(self):
        W = self.weather.Weather
        self.assertEqual(W(2).day(5), W(2).day(5))
        self.assertNotEqual([W(2).day(k)["wet"] for k in range(1, 31)], [W(3).day(k)["wet"] for k in range(1, 31)])
        self.assertAlmostEqual(self.weather.wet_chance(1), (8.4 / 30 + 10.9 / 31) / 2, delta=0.02)
        days = [W(s).day(k) for s in range(1, 401) for k in range(1, 11)]
        wet = [x for x in days if x["wet"]]
        self.assertAlmostEqual(len(wet) / len(days), 0.32, delta=0.04)
        self.assertAlmostEqual(sum(x["mm"] for x in wet) / len(wet), 6.2, delta=0.6)
        pairs = [(W(s).day(k)["wet"], W(s).day(k + 1)["wet"]) for s in range(1, 401) for k in range(1, 10)]
        ww = [b for a, b in pairs if a]
        self.assertAlmostEqual(sum(ww) / len(ww), 0.5, delta=0.06)
        for x in days:
            self.assertGreater(x["tmax"], x["tmin"])
            self.assertAlmostEqual(x["indoor"], (x["tmax"] + x["tmin"]) / 2 + 4, places=9)
            self.assertAlmostEqual(sum(mm for _, _, mm in x["spells"]), x["mm"] if x["wet"] else 0, places=9)
            for a, b, _ in x["spells"]:
                self.assertTrue(a % 3 == 0 and b % 3 == 0 and 120 <= b - a <= 360, (a, b))

    # ---------- §4.2: the water ----------
    def test_the_store_at_day_3_0700_is_105_5_litres_of_tap_water(self):
        d = self.v16()
        w = d.day3.quiet.world
        s = w.store()
        hand = 196.5 - 24 * (2 * 1440 + 2580) / 1440           # filled on house day 1; dry from house day 2, 12:00
        self.assertAlmostEqual(hand, 105.5, places=9)
        self.assertAlmostEqual(s["tap"], 105.5, places=6)
        self.assertEqual((s["rain"], w.level, w.bin_out), (0, "as_before", False))
        self.assertEqual({q: w.deficit[q] for q in data.ORDER}, {q: 0.0 for q in data.ORDER})
        self.assertIsNone(w.places["neighbour"])            # night 2 took no water, and nobody knows of it

    def test_each_level_uses_its_litres_a_day(self):
        for level, litres in (("as_before", 24), ("careful", 10), ("rationed", 5)):
            w = self.truth.World(2)
            self.dry(w, *range(1, 11))
            w.advance_to(self.at(3, 0), data.ORDER)
            w.set_level(level, self.at(3, 0), "elena")
            before = w.store()["tap"]
            w.advance_to(self.at(4, 0), data.ORDER)
            self.assertAlmostEqual(before - w.store()["tap"], litres, places=6, msg=level)
            self.assertEqual(w.deficit, {q: 0.0 for q in data.ORDER})

    def test_thirst_grows_only_without_water_and_its_stages_are_2_5_8_10_percent(self):
        self.assertEqual([self.water.thirst_stage(x, 100) for x in (1.99, 2, 4.99, 5, 7.99, 8, 9.99, 10, 20)],
                         [0, 1, 1, 2, 2, 3, 3, 4, 4])
        w = self.truth.World(2)
        self.dry(w, *range(1, 11))
        w.advance_to(self.at(3, 0), data.ORDER)
        w.tap = 0.0
        w.advance_to(self.at(4, 0), data.ORDER)
        self.assertAlmostEqual(w.deficit["leo"], 1.2, places=6)
        # Leo, 70 kg: 2% is 1.4 litres, at 1.2 a day: 1680 minutes after the water ran out.
        self.assertEqual(w.thirst_stage("leo"), 0)
        w.advance_to(self.at(3, 0) + 1680, data.ORDER)
        self.assertEqual(w.thirst_stage("leo"), 1)
        # Water comes in: the thirsty drink what they lack at once.
        w.receive(10.0)
        w.advance_to(self.at(3, 0) + 1681, data.ORDER)
        self.assertEqual(w.deficit, {q: 0.0 for q in data.ORDER})
        self.assertLess(w.store()["tap"], 10.0 - 4 * 1.4 + 0.1)

    def test_the_about_water_line_says_what_an_eye_sees(self):
        d = self.v16()
        m = d.day3
        line = next(x for x in m.inside_lines(m.people["mara"]) if x.startswith("About water:"))
        self.assertEqual(line, "About water: the bath holds about 60 litres and the pans, kettle, bottles and buckets "
                               "in the kitchen about 45 litres: tap water stored before the taps ran dry. It is also "
                               "used to flush the toilet and to wash.")
        self.assertFalse([x for x in d.day2.inside_lines(d.day2.people["mara"]) if x.startswith("About water:")])
        self.assertEqual(self.water.describe({"tap": 0.0, "rain": 0.0}, "careful", "since 10:21", None, False),
                         "About water: the bath and the pans are empty: no stored tap water is left. Since 10:21, none "
                         "of it goes on the toilet or on washing.")
        self.assertEqual(self.water.describe({"tap": 30.0, "rain": 87.0}, "rationed", "since yesterday", "you", True),
                         "About water: the bath is empty and the pans, kettle, bottles and buckets in the kitchen hold "
                         "about 30 litres: tap water stored before the taps ran dry. Since yesterday, you share it out "
                         "by the cup: five cups each a day. The bin under the drainpipe in the yard holds about 90 "
                         "litres of rain water.")

    # ---------- §4.3: the body ----------
    def test_fasting_stages_are_in_days(self):
        q = self.quiet
        self.assertEqual([q.fast_stage(x) for x in (23.99, 24, 71.99, 72, 167.99, 168, 335.99, 336, 671.99, 672)],
                         [0, 1, 1, 2, 2, 3, 3, 4, 4, 5])
        self.assertEqual(q.body_line("starving", 3, 0),
                         "Your body: starving, for days now: you are thin and weak; stairs and carrying things tire "
                         "you fast.")
        self.assertEqual(q.body_line("starving", 2, 1, thirst=1, cold=True),
                         "Your body: starving, for days now: you feel light and slow, and standing up fast greys your "
                         "sight for a moment; you are thirsty, and your mouth is dry; you feel cold, even indoors; and "
                         "you have hardly slept.")
        # The street shifts follow: light and slow (F2) is "weak", F3 "very weak", F4 and on "barely standing".
        n = self.night
        self.assertEqual(n.body_shift(1, 0), (0.0, 0.0, 0.0, 0.0))
        self.assertEqual(n.body_shift(2, 0), n.SHIFTS["weak"])
        self.assertEqual(n.body_shift(3, 0), n.SHIFTS["very weak"])
        self.assertEqual(n.body_shift(4, 0), n.SHIFTS["barely standing"])
        self.assertEqual(n.body_shift(5, 0), n.SHIFTS["barely standing"])

    def test_no_body_line_forbids_an_act(self):
        for fast in range(6):
            for debt in range(3):
                for thirst in range(5):
                    for cold in (False, True, "wet"):
                        line = self.quiet.body_line("starving", fast, debt, thirst=thirst, cold=cold)
                        self.assertIsNone(FORBIDS.search(line), line)
        self.assertFalse([v for v in self.quiet.NEED_VIEWS.values() if FORBIDS.search(v)])

    def test_cold_at_f2_under_18_indoors_and_wet_after_the_yard(self):
        d = self.v16()
        m, q = d.day3, d.day3.quiet
        w = q.world
        self.dry(w, 3, indoor=17.0)
        leo, elena = m.people["leo"], m.people["elena"]
        leo.needs["ate_at"] = self.at(3, 0) - 80 * 60          # 80 hours: F2
        elena.needs["ate_at"] = self.at(3, 0) - 30 * 60        # F1
        q.tick(3)
        self.assertIs(leo.needs["cold"], True)
        self.assertIs(elena.needs["cold"], False)
        self.dry(w, 3, indoor=19.0)
        q.tick(6)
        self.assertIs(leo.needs["cold"], False)
        w.wet_until["elena"] = self.at(3, 6) + 120
        q.tick(9)
        self.assertEqual(elena.needs["cold"], "wet")
        self.assertIn("you are wet and cold", m.inside_lines(elena)[0])
        q.tick(126)
        self.assertIs(elena.needs["cold"], False)

    # ---------- §3.1, §4.1, §5: rain heard, and Q6 ----------
    def test_rain_in_a_quiet_stretch_reaches_everyone_awake_and_q6_plays_their_room(self):
        d = self.v16(client=self.silent())
        m, q = d.day3, d.day3.quiet
        self.rain(q.world, 3, [(300, 420, 6.0)])
        self.quiet.play(m)
        q6 = [e for e in q.log if e["kind"] == "Q6"]
        self.assertEqual(len(q6), 1, q6)
        e = q6[0]
        self.assertEqual((e["minute"], e["fired"]), (300, True), e)
        awake = [p for ids in e["awake"].values() for p in ids]
        self.assertTrue(awake)
        for pid in data.ORDER:
            heard = (300, self.quiet.RAIN_HEARD) in m.people[pid].memory
            self.assertEqual(heard, pid in awake, pid)
        room = max(e["awake"], key=lambda r: (len(e["awake"][r]), -list(data.ROOMS).index(r)))
        self.assertEqual(e["room"], room)
        self.assertEqual(sorted(e["asked"]), sorted(e["awake"][room]))
        st = next(s for s in q.stretches if s["trigger"] == "Q6")
        self.assertTrue(0 < st["asks"] <= 8, st)
        rain = [x for x in q.items() if x["kind"] == "rain"]
        self.assertEqual([(x["minute"], x["witnesses"]) for x in rain], [(300, {p: "heard" for p in awake})])
        asked = [x for rec in m.log for x in rec["decisions"] if x.get("quiet") == "Q6"]
        self.assertEqual(sorted(x["person"] for x in asked), sorted(e["asked"]))

    def test_q6_once_a_day_and_rain_in_played_turns_is_a_trigger(self):
        d = self.v16_forced(client=self.silent(), d3=[(0, 120, 2.0), (300, 420, 2.0), (600, 720, 2.0)])
        m, q = d.day3, d.day3.quiet
        self.quiet.play(m)
        q6 = [e for e in q.log if e["kind"] == "Q6"]
        self.assertEqual([(e["minute"], e["fired"]) for e in q6], [(0, False), (300, True), (600, False)])
        self.assertEqual(q6[0]["why"], "the house was already talking")
        self.assertEqual(q6[2]["why"], "Q6 has fired today already")
        first = [x for rec in m.log if rec["minute"] == 0 for x in rec["decisions"]]
        self.assertTrue(first)
        for x in first:
            self.assertIn(self.quiet.RAIN_TRIGGER, x["triggers"], x)

    # reports/v22_fixes.md, rule 2
    def test_you_meant_to_is_shown_only_until_the_first_speech_act_of_the_day(self):
        class Recording(PolicyFake):
            prompts = []

            def generate(self, system, prompt, schema=None):
                if schema is None:
                    self.prompts.append(prompt)
                return super().generate(system, prompt, schema)
        rec = Recording(lambda who, minute, opts: "reassure_all" if "reassure_all" in opts else None)
        rec.prompts = []
        d = self.v16(client=rec)
        m = d.day3
        mara = m.people["mara"]
        meant = '- You meant to: "'
        self.assertTrue([x for x in d.day3.carry["mara"] if x.startswith(meant)], "the premise: the night mind left an intent")
        self.quiet.play(m)
        hers = [x for x in rec.prompts if x.startswith("You are Mara,") and "Your options:" in x and "Now it is night" not in x]
        self.assertGreaterEqual(len(hers), 3)
        self.assertIn(meant, hers[0])                       # before she has spoken
        for later in hers[1:]:
            self.assertNotIn(meant, later)
            self.assertIn("- How it left you:", later)      # the rest of the block stays
            self.assertIn("What yesterday left in you (your own thoughts, last night):", later)
        # The bedtime prompt follows the same rule: she spoke today.
        night = m.prompt_for(mara, None, [Option("sleep", "go to sleep")], night=["Now it is night."])
        self.assertNotIn(meant, night)
        mara.said_lines = []
        self.assertIn(meant, m.prompt_for(mara, None, [Option("sleep", "go to sleep")], night=["Now it is night."]))
        # It is each person's own: Leo spoke too, and with his spoken lines cleared his intent is back, hers still gone.
        leo = m.people["leo"]
        self.assertTrue(leo.said_lines)
        leo.said_lines = []
        mara.said_lines = ["19:03, you reassured everyone."]
        self.assertIn(meant, m.prompt_for(leo, 3, m.options_for(leo)))
        self.assertNotIn(meant, m.prompt_for(mara, 3, m.options_for(mara)))
        # Days 1 and 2 are as they were: the intent stays after a spoken line (v16's cache answers them).
        spoke = [p for p in d.day2.people.values() if p.said_lines and [x for x in d.day2.carry[p.id] if x.startswith(meant)]]
        self.assertTrue(spoke, "the premise: someone spoke on day 2 and carried an intent")
        for p in spoke:
            self.assertIn(meant, d.day2.prompt_for(p, 9, d.day2.options_for(p)), p.id)

    # reports/v22_fixes.md, rule 3
    def test_q6_is_skipped_when_nobody_in_its_room_is_offered_a_rain_action(self):
        def run(bin_out, rain=True):
            d = self.v16(client=self.silent())
            m, q = d.day3, d.day3.quiet
            if rain:
                self.rain(q.world, 3, [(300, 420, 6.0)])
            else:
                self.dry(q.world, 3)
            if bin_out:
                q.world.put_bin_out("daniel", self.at(3, 0))
            self.quiet.play(m)
            return m, q
        m, q = run(True)
        q6 = [e for e in q.log if e["kind"] == "Q6"]
        self.assertEqual(len(q6), 1, q6)
        e = q6[0]
        self.assertEqual((e["minute"], e["fired"], e["asked"], e["why"]), (300, False, [], "Q6 skipped: no rain action"), e)
        self.assertFalse([s for s in q.stretches if s["trigger"] == "Q6"], q.stretches)
        self.assertFalse([x for rec in m.log for x in rec["decisions"] if x.get("quiet") == "Q6"])
        # The onset is written as before: remembered by everyone awake, and in the record of the day.
        awake = [p for ids in e["awake"].values() for p in ids]
        self.assertTrue(awake)
        for pid in data.ORDER:
            self.assertEqual((300, self.quiet.RAIN_HEARD) in m.people[pid].memory, pid in awake, pid)
        self.assertEqual([(x["minute"], sorted(x["witnesses"])) for x in q.items() if x["kind"] == "rain"],
                         [(300, sorted(awake))])
        # No asks are spent on it (the same day without the rain asks as many), and it does not use up the day's Q6.
        self.assertFalse(q.q6_done)
        _, dry = run(True, rain=False)
        self.assertEqual(q.asks, dry.asks)
        # With the bin not out, as before: Q6 fires and plays the room.
        m2, q2 = run(False)
        self.assertEqual([(e["fired"], e["why"]) for e in q2.log if e["kind"] == "Q6"], [(True, None)])
        self.assertTrue([s for s in q2.stretches if s["trigger"] == "Q6"])
        self.assertGreater(q2.asks, q.asks)

    def test_a_prompt_while_it_rains_says_so(self):
        d = self.v16()
        m, q = d.day3, d.day3.quiet
        self.rain(q.world, 3, [(30, 150, 3.0)])
        q.tick(33)
        leo = m.people["leo"]
        self.assertIn("\n- Rain is falling: you hear it on the roof and against the boards.\n",
                      m.prompt_for(leo, 11, m.options_for(leo)))
        q.tick(153)
        self.assertNotIn("Rain is falling", m.prompt_for(leo, 51, m.options_for(leo)))

    # ---------- the yard (amendment 3) and the water acts ----------
    def test_the_back_door_and_the_yard_from_day_3_only(self):
        d = self.v16()
        yard = ("the counter, the dry taps and the back door to the yard; the yard behind the kitchen, small and "
                "walled, with the drainpipe and the bin;")
        p3 = d.day3.prompt_for(d.day3.people["leo"], 30, d.day3.options_for(d.day3.people["leo"]))
        self.assertIn(yard, p3)
        self.assertNotIn("stove", p3)
        for m in (d.day1, d.day2):
            p = m.prompt_for(m.people["leo"], 5, m.options_for(m.people["leo"]))
            self.assertNotIn("yard", p)
        night = d.day3.prompt_for(d.day3.people["leo"], None, [Option("sleep", "go to sleep")], night=["Now."])
        self.assertIn(yard, night)

    def test_collect_rain_sets_the_bin_under_the_drainpipe_and_it_fills_by_catchment(self):
        def policy(who, minute, opts):
            return "collect_rain" if "collect_rain" in opts else None
        d = self.v16(client=PolicyFake(policy))
        m, q = d.day3, d.day3.quiet
        w = q.world
        self.rain(w, 3, [(300, 420, 6.0)])
        self.quiet.play(m)
        acts = [a for turn in m.transcript["turns"] for a in turn["acts"] if a["option"] == "collect_rain"]
        self.assertEqual(len(acts), 1, acts)
        a = acts[0]
        who = a["who"]
        self.assertEqual(a["minute"], 300)           # Q6: whoever is awake hears it begin and is asked
        self.assertTrue(w.bin_out)
        self.assertAlmostEqual(w.caught, self.water.CATCH * 6.0 / 120 * (420 - a["minute"]), places=6)
        self.assertEqual(self.water.CATCH, 25 * 0.85)
        self.assertEqual(w.wet_until[who], self.at(3, a["minute"]) + 120)
        for q_ in a["audience"]:
            self.assertIn((a["minute"], f"{data.PEOPLE[who]['name']} goes out the back door into the rain and sets "
                                        f"the bin under the drainpipe in the yard."), m.people[q_].memory)
        self.assertNotIn("collect_rain", [o.id for o in m.options_for(m.people[who])])
        d.chron.add_day(m)
        self.assertEqual([e["actor"] for e in d.chron.events if e["kind"] == "collect_rain"], [who])

    def test_save_and_ration_water_set_the_level_from_when_they_are_said(self):
        def policy(who, minute, opts):
            if who == "elena" and "save_water" in opts and minute == 0:
                return "save_water"
            if who == "leo" and "ration_water" in opts and minute == 3:
                return "ration_water"
        d = self.v16(client=PolicyFake(policy))
        m, q = d.day3, d.day3.quiet
        w = q.world
        q.turn(0)
        self.assertEqual((w.level, w.level_since), ("careful", self.at(3, 0)))
        mara = m.people["mara"]
        self.assertNotIn("save_water", [o.id for o in m.options_for(mara)])
        self.assertIn("ration_water", [o.id for o in m.options_for(mara)])
        q.turn(1)
        self.assertEqual((w.level, w.holder), ("rationed", "leo"))
        line = next(x for x in m.inside_lines(mara) if x.startswith("About water:"))
        self.assertIn("Since min 03, Leo shares it out by the cup: five cups each a day.", line)
        self.assertNotIn("ration_water", [o.id for o in m.options_for(mara)])
        heard = [t for mm, t in mara.memory if mm == 3]
        self.assertTrue(any("the water must be shared out by the cup" in t for t in heard), heard)

    # ---------- water next door and further along (amendment 2) ----------
    def neighbour_water(self, seed, place="neighbour"):
        bath = 150.0 if random.Random(f"{seed}:world:water:{place}:bath").random() < 0.5 else 0.0
        bottles = 1.5 * random.Random(f"{seed}:world:water:{place}:bottles").randint(0, 4)
        return {"bath": bath, "cistern": 6.0, "bottles": bottles}

    def test_the_neighbours_water_is_fixed_when_first_needed_and_carried_home(self):
        bed = {"daniel": "go_next_door", "leo": "lie_awake"}
        d, m, n3, _ = self.night3(bed, {**self.STILL, "trip:daniel": 0.1})
        w = m.quiet.world
        g = n3.groups[0]
        self.assertEqual(g["street"], "clean")
        want = self.neighbour_water(2)
        self.assertEqual(w.places["neighbour"]["held"], want)
        self.assertEqual(w.fixed["neighbour_water"]["value"], want)
        total = sum(want.values())
        take = min(total, self.water.CARRY)
        self.assertEqual(g["water"], take)
        self.assertAlmostEqual(w.places["neighbour"]["left"], total - take, places=9)
        words = self.night.water_words(take)
        self.assertIn(f"and put {words} of water in the kitchen.", " ".join(n3.lines["daniel"]))
        d.chron.add_night(n3)
        day4 = Morning.next_day(m, n3, d.oracle, chronicle=d.chron)
        dan, leo = day4.people["daniel"], day4.people["leo"]
        self.assertIn(f"The water you brought back is in the kitchen: {words}.", dan.sure[0])
        self.assertIn(f"In the kitchen there is water that was not there last night: {words}. So someone brought water "
                      f"into the house in the night.", leo.sure[0])
        self.assertIn(f"brought back {words} of water", day4.neighbour["daniel"])
        self.assertAlmostEqual(day4.quiet.world.received[-1][1], take, places=9)
        self.assertIn("came back with water", day4.neighbour["leo"])
        self.assertIn("came back with water", day4.outings["leo"])

    def test_a_house_further_along_holds_water_fixed_once(self):
        d, m, n3, _ = self.night3({"daniel": "go_further"}, {**self.STILL, "trip_far:daniel": 0.1})
        w = m.quiet.world
        g = n3.groups[0]
        self.assertEqual(g["street"], "clean")
        held = w.places["far"][0]["held"]
        self.assertEqual(held, self.neighbour_water(2, "far:0"))
        self.assertEqual(g["water"], min(sum(held.values()), self.water.CARRY))
        self.assertEqual(w.fixed["far_house_0_water"]["value"], held)

    def test_nights_1_and_2_took_no_water(self):
        d = self.v16()
        self.assertEqual([g.get("water") for g in d.n2.groups], [None])
        self.assertIsNone(d.day3.quiet.world.places["neighbour"])
        self.assertNotIn("water", d.day3.neighbour["leo"])

    # ---------- the night ----------
    def test_the_bedtime_rain_option_and_rain_masking_the_front_door(self):
        def setup(m):
            self.rain(m.quiet.world, 3, [(780, 1260, 4.0)])        # 20:00 to 04:00
            m.quiet.tick(840)
        bed = {"daniel": "go_next_door", "elena": "rain_out"}
        d, m, n3, client = self.night3(bed, {**self.STILL, "door:daniel:elena": 0.2, "trip:daniel": 0.1},
                                       setup=setup)
        w = m.quiet.world
        self.assertEqual(n3.choices["elena"], "rain_out")
        self.assertTrue(w.bin_out)
        self.assertTrue(n3.rainy)
        elena_bed = next(p for p in client.prompts if p.startswith("You are Elena,") and "- sleep:" in p)
        self.assertIn("It is raining: you hear it on the roof.", elena_bed)
        self.assertIn("- rain_out: set the bin under the drainpipe in the yard to catch the rain, then go to sleep",
                      elena_bed)
        door = [x for x in n3.noticing if x["who"] == "elena" and x["how"] == "front door"]
        self.assertEqual([(x["under"], x["noticed"]) for x in door],
                         [(round(self.night.wake_door("elena") * self.night.RAIN_MASK, 4), False)])
        self.assertEqual(self.quiet.night_payback("rain_out", True), 6)

        def dry(m):
            self.dry(m.quiet.world, 3, 4)
        d, m, n3, client = self.night3({"daniel": "go_next_door", "elena": "sleep"},
                                       {**self.STILL, "door:daniel:elena": 0.2, "trip:daniel": 0.1}, setup=dry)
        self.assertFalse(n3.rainy)
        door = [x for x in n3.noticing if x["who"] == "elena" and x["how"] == "front door"]
        self.assertEqual([x["noticed"] for x in door], [True])
        elena_bed = next(p for p in client.prompts if p.startswith("You are Elena,") and "- sleep:" in p)
        self.assertNotIn("rain_out", elena_bed)

    # ---------- the run prints what DONE 3 asks ----------
    def test_a_run_prints_the_weather_the_water_the_stages_and_every_q6(self):
        (meta, code), out = fake_morning(self.dirs, seed=2, days=4)
        self.assertEqual(code, 0, out[-2000:])
        for k in range(1, 5):
            self.assertRegex(out, rf"\n  weather day {k}: (dry|wet, [\d.]+ mm)")
        for k in (3, 4):
            self.assertRegex(out, rf"\n  day {k} 07:00 water: tap [\d.]+ L")
            self.assertRegex(out, rf"\n  day {k} 21:00 stages: Daniel F\d T\d")
        self.assertIn("q6_fired", meta["day3_quiet"])

    # ---------- rules added while building (reports/w1_impl.md) ----------
    def test_w1_lines_sit_outside_the_budget_and_cut_no_memory_line(self):
        d = self.v16()
        m = d.day3
        leo = m.people["leo"]
        leo.memory += [(0, f"filler line number {i} " + "about nothing much at all " * 12) for i in range(200)]
        self.rain(m.quiet.world, 3, [(0, 120, 2.0)])
        m.quiet.sense(30)
        self.assertIsNotNone(leo.rain_since)
        with_w1 = m.prompt_for(leo, 10, m.options_for(leo))
        water_seen, leo.water, leo.rain_since = leo.water, None, None
        plain = m.prompt_for(leo, 10, m.options_for(leo))
        leo.water = water_seen

        def kept(prompt):
            lines = prompt.split("\n")
            return lines[lines.index("What else happened this morning, most recent last:"):
                         next(i for i, x in enumerate(lines) if x.startswith("Now, "))]
        self.assertIn("About water:", with_w1)
        self.assertIn("- Rain is falling:", with_w1)
        self.assertIn("- (earlier things, left out here)", kept(plain))
        self.assertEqual(kept(with_w1), kept(plain))

    def test_q1_asks_when_thirst_reaches_badly_thirsty(self):
        d = self.v16()
        m, q = d.day3, d.day3.quiet
        w = q.world
        for p in m.people.values():
            p.room = "kitchen"
        w.tap = 0.0
        w.deficit["leo"] = 0.05 * self.water.MASS["leo"] - 0.01         # 0.01 litres short of 5%: T1
        q.tick(3)
        self.assertEqual(m.people["leo"].needs["thirst_stage"], 1)
        cross = q.tick(30)                                             # 1.2 a day: 0.025 litres in 30 minutes
        self.assertIn(("leo", "thirst", 2), cross)
        fired = q.ask_q1(cross, 30)
        self.assertEqual([(f["kind"], f["asked"], f["need"], f["stage"]) for f in fired if f["asked"] == "leo"],
                         [("Q1", "leo", "thirst", 2)])
        self.assertIn("you are badly thirsty", m.inside_lines(m.people["leo"])[0])

    def test_the_chronicle_keeps_the_water_fixed_once(self):
        d, m, n3, _ = self.night3({"daniel": "go_next_door"}, {**self.STILL, "trip:daniel": 0.1})
        d.chron.add_night(n3)
        f = d.chron.fixed["neighbour_water"]
        self.assertEqual((f["value"], f["scene"]), (self.neighbour_water(2), "N3"))

    def test_the_story_shows_rain_and_q6(self):
        story = importlib.import_module("story")
        d = self.v16(client=self.silent())
        m = d.day3
        self.rain(m.quiet.world, 3, [(300, 420, 6.0)])
        self.quiet.play(m)
        text = story.render_day2(m)
        self.assertIn("- 12:00: rain begins (heard by ", text)
        self.assertIn("- 12:00: **Q6**, rain began: ", text)

    # ---------- W1 fixes (reports/w1_fixes.md) ----------
    def test_eating_on_a_quiet_day_resets_fasting_at_that_minute(self):
        """Fix 1: eat, eat_given and share reset the eater's fasting at the minute they eat; their next body line
        follows. Daniel, Leo and Mara are at F1 at 07:00 on day 3; someone gets Leo F2 first (80 hours)."""
        quiet = self.quiet

        def case(policy, food_due=None):
            d = self.v16(client=PolicyFake(policy))
            m = d.day3
            m.portions = 3
            m.people["leo"].needs["ate_at"] = self.at(3, 0) - 80 * 60
            m.quiet.tick(0)
            self.assertEqual(m.people["leo"].needs["fast_stage"], 2)
            if food_due:
                with mock.patch.object(type(m), "food_due", lambda self_, p, t: p.id == food_due and t == 0):
                    m.quiet.turn(0)
            else:
                m.quiet.turn(0)
            return m

        def fasting_words(line):
            return any(w for k, w in quiet.FAST_WORDS.items() if w.lstrip(",; ") in line)

        # eat: Leo eats at min 00.
        m = case(lambda who, minute, opts: "eat" if who == "leo" and minute == 0 else None)
        leo = m.people["leo"]
        self.assertIn("eat", [a["option"] for a in m.transcript["turns"][0]["acts"] if a["who"] == "leo"])
        self.assertEqual(leo.needs["ate_at"], self.at(3, 0))
        self.assertEqual(leo.needs["fast_stage"], 0)
        self.assertAlmostEqual(m.quiet.fast(leo, 3), 3 / 60 * 1.0, places=9)
        self.assertFalse(fasting_words(m.inside_lines(leo)[0]), m.inside_lines(leo)[0])
        # share: Mara shares out the shelf at min 00; everyone in the kitchen with her has their part.
        m = case(lambda who, minute, opts: "share" if who == "mara" and minute == 0 else None)
        acts = [a for a in m.transcript["turns"][0]["acts"] if a["option"] == "share"]
        self.assertEqual([a["who"] for a in acts], ["mara"])
        eaters = ["mara"] + acts[0]["audience"]
        for q in eaters:
            self.assertEqual(m.people[q].needs["ate_at"], self.at(3, 0), q)
            self.assertEqual(m.people[q].needs["fast_stage"], 0, q)
            self.assertFalse(fasting_words(m.inside_lines(m.people[q])[0]), q)
        # eat_given: at a food moment Elena hands Leo a portion, and he eats it.
        def given(who, minute, opts):
            if who == "elena" and "give_leo" in opts:
                return "give_leo"
            if who == "leo" and "eat_given" in opts:
                return "eat_given"
        m = case(given, food_due="elena")
        leo = m.people["leo"]
        self.assertIn("eat_given", [a["option"] for a in m.transcript["turns"][0]["acts"] if a["who"] == "leo"])
        self.assertEqual((leo.needs["ate_at"], leo.needs["fast_stage"]), (self.at(3, 0), 0))
        # The next morning counts from that meal, as before (the chronicle's eat events).
        self.assertEqual(self.quiet.last_meals(self.chron.Chronicle(2, "daniel"), "daniel")["leo"], self.quiet.BEFORE_DAY_1)

    def test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food(self):
        """Fix 2: a trip next door that brought water and no food: everyone knows next door is empty of food, so the
        far options stay; every line says what came home, the block C line of an older night included."""
        memory = importlib.import_module("memory")
        bed = {"daniel": "go_next_door", "leo": "lie_awake"}
        d, m, n3, _ = self.night3(bed, {**self.STILL, "trip:daniel": 0.1})
        g = n3.groups[0]
        self.assertEqual((g["street"], g["took"]), ("clean", 0))
        self.assertGreater(g["water"], 0)
        self.assertEqual(g["outcome"], "back with water")
        d.chron.add_night(n3)
        day4 = Morning.next_day(m, n3, d.oracle, chronicle=d.chron)
        self.assertEqual({q: p.knows_empty for q, p in day4.people.items()}, {q: True for q in data.ORDER})
        for q in data.ORDER:
            p = day4.people[q]
            self.assertIn("\n- volunteer_far: ", day4.prompt_for(p, 0, day4.options_for(p)), q)
        self.assertIn("came back with water", day4.neighbour["elena"])
        self.assertIn(f"brought back {self.night.water_words(g['water'])} of water", day4.neighbour["daniel"])
        street = [e for e in d.chron.events if e["scene"] == "N3" and e["kind"] == "street"]
        self.assertEqual([e["outcome"] for e in street], ["back with water"])
        went = [e for e in d.chron.events if e["scene"] == "N3" and e["kind"] == "went_out"]
        line = memory.person_line(d.chron, "leo", "daniel", "went_out", None, went, 8)      # seen from day 5
        self.assertEqual(line, "The night before last, Daniel went out to the neighbour's house and came back with "
                               "water.")
        # Food and water: the outcome says both.
        self.assertEqual(self.night.outcome_class("clean", 2, 10.0), "back with food and water")
        self.assertEqual(self.night.outcome_class("scare_back", 0, 10.0), "back shaken, with water")
        self.assertEqual(self.night.outcome_class("scare_back", 0), "back shaken, with nothing")

    def test_block_c_names_where_a_trip_went(self):
        """Block C's went_out line: "went out to the neighbour's house" for a trip next door, "went further along the
        street" for a far one, with the outcome as before; for whoever went, and for whoever heard it."""
        memory = importlib.import_module("memory")

        def line(bed, draws, pid):
            d, m, n3, _ = self.night3(bed, {**self.STILL, **draws})
            d.chron.add_night(n3)
            went = [e for e in d.chron.events if e["scene"] == "N3" and e["kind"] == "went_out"]
            return memory.person_line(d.chron, pid, "daniel", "went_out", None, went, 8)      # seen from day 5
        far = line({"daniel": "go_further", "leo": "lie_awake"}, {"trip_far:daniel": 0.1, "far_house:0": 0.1}, "leo")
        self.assertEqual(far, "The night before last, Daniel went further along the street and came back with water.")
        self.assertEqual(line({"daniel": "go_further"}, {"trip_far:daniel": 0.1, "far_house:0": 0.1}, "daniel"),
                         "The night before last, you went further along the street and came back with water.")
        near = line({"daniel": "go_next_door", "leo": "lie_awake"}, {"trip:daniel": 0.1}, "leo")
        self.assertEqual(near, "The night before last, Daniel went out to the neighbour's house and came back with "
                               "water.")


class KnockTest(unittest.TestCase):
    """W2a, the knock (reports/w2_design.md, §7.2): the street drawn and planned in code, a visit to the family's door
    by day, the door scene (Q7) with five door options, the stranger's lines from a pool, and the day cap. Every day-3
    test starts from v16 seed 2 through night 2, replayed from cache/v16 with no API call."""
    MODEL = QuietDayTest.MODEL
    v16 = QuietDayTest.v16

    def setUp(self):
        self.dirs = Dirs()
        self.quiet = importlib.import_module("quiet")
        self.night = importlib.import_module("night")
        self.chron = importlib.import_module("chronicle")
        self.mind = importlib.import_module("mind")
        self.truth = importlib.import_module("truth")

    def tearDown(self):
        self.dirs.cleanup()

    def need(self, name):
        """A module W2a adds: the test fails, rather than errs, until it is built."""
        self.assertIsNotNone(importlib.util.find_spec(name), f"{name}.py is not built")
        return importlib.import_module(name)

    def at(self, k, minute):
        return self.quiet.absolute(k, minute)

    def door_day(self, client=None, visits=()):
        """v16 seed 2 to day 3, the street's own visits taken away and its asks stopped, then a visit by each of its
        first households at these (day minute, purpose)."""
        street = self.need("street")
        d = self.v16(client=client or PolicyFake(lambda who, minute, opts: None))
        q = d.day3.quiet
        st = getattr(q.world, "street", None)
        self.assertIsNotNone(st, "World.street is not built")
        st["factor"] = 0.0
        st["visits"] = [v for v in st["visits"] if v["state"] == "done"]
        hids = sorted(st["households"], key=lambda h: st["households"][h]["home"])
        made = [street.make_visit(st, hids[i], self.at(3, mm), purpose) for i, (mm, purpose) in enumerate(visits)]
        return d, q, made

    @staticmethod
    def door_lines(prompt):
        return [x for x in prompt.split("\n") if x.startswith(("- Someone is knocking", "- You hear knocking",
                                                                 "- Someone is at the front door",
                                                                 "- The front door is open"))
                or re.match(r"^- (A|An|Earlier).* voice at the front door", x)
                or re.match(r"^- door_\w+: ", x)]

    # ---------- T1: the street is drawn by string ----------
    def test_t1_the_street_is_drawn_by_string_and_adding_a_house_changes_no_other_draw(self):
        street = self.need("street")
        a = street.generate(2)
        self.assertEqual(a, street.generate(2))
        self.assertNotEqual(a["households"], street.generate(3)["households"])
        status = [h["status"] for h in a["houses"].values()]
        self.assertEqual((len(status), status.count("occupied"), status.count("empty")), (30, 20, 8))
        self.assertEqual((a["houses"][9]["status"], a["houses"][7]["status"]), ("family", "neighbour"))
        self.assertEqual(len(a["households"]), 20)
        for h in a["households"].values():
            self.assertTrue(any(m["role"] == "adult" for m in h["drawn"]["members"]), h["id"])
            self.assertIn(h["drawn"]["disposition"], ("helper", "guarded", "opportunist", "violent"))
        # Independent of order: the houses listed the other way round give the same households.
        s = street.load("street")
        rev = dict(s, houses=list(reversed(s["houses"])))
        self.assertEqual(street.generate(2, street=rev)["households"], a["households"])
        # Adding a house changes no other house's draw: every household of a house occupied in both is drawn the same.
        more = dict(s, houses=s["houses"] + [{"n": 31, "side": "odd", "x": 120.0}])
        c = street.generate(2, street=more)
        both = [h for h in a["households"] if h in c["households"]]
        self.assertGreaterEqual(len(both), 15)
        for h in both:
            self.assertEqual(c["households"][h]["drawn"], a["households"][h]["drawn"], h)
        # Every value comes from the one draw argument, each by a string of its own that starts with the seed.
        seen = []

        def draw(x):
            seen.append(x)
            return random.Random(x).random()
        self.assertEqual(street.generate(2, draw=draw), a)
        self.assertTrue(seen)
        self.assertTrue(all(x.startswith("2:street:") for x in seen), seen[:3])
        self.assertEqual(len(seen), len(set(seen)))

    # ---------- T2: stocks are conserved ----------
    def test_t2_stocks_are_conserved_across_every_exchange_and_every_door_give(self):
        street = self.need("street")
        st = street.generate(2)
        hs = sorted(st["households"], key=lambda h: st["households"][h]["home"])
        a, b = st["households"][hs[0]], st["households"][hs[1]]
        a["water"], b["water"], b["food"] = 0.0, 60.0, 30.0
        before = a["water"] + b["water"]
        deed = street.resolve(st, {"by": a["id"], "to": b["home"], "good": "water"}, 300)
        self.assertAlmostEqual(a["water"] + b["water"], before, places=9)
        self.assertIn(deed["kind"], ("gave", "refused"))
        self.assertAlmostEqual(a["water"], deed["qty"], places=9)
        # A search moves what an empty house holds into the household, all of it, once.
        empty = next(n for n, h in st["houses"].items() if h["status"] == "empty")
        held = street.contents(st, empty)
        food0, water0 = a["food"] * len(a["drawn"]["members"]), a["water"]
        street.search(st, a["id"], empty, 300)
        self.assertAlmostEqual(a["water"] - water0, held["water"], places=9)
        self.assertAlmostEqual(a["food"] * len(a["drawn"]["members"]) - food0, held["food"], places=9)
        self.assertEqual(st["houses"][empty]["state"], "searched")
        self.assertEqual(street.contents(st, empty), {"water": 0.0, "food": 0.0})
        # Over eight days of plans, what the street holds changes only by what it used and what it found.
        st = street.generate(2)
        t0 = street.totals(st)
        street.advance(st, self.at(10, 0), wet=lambda minute: False)
        t1 = street.totals(st)
        for good in ("water", "food"):
            self.assertAlmostEqual(t0[good] - st["used"][good] + st["found"][good], t1[good], places=6)
        for move in st["ledger"]:
            self.assertGreaterEqual(move["qty"], 0)
        # A door_give: World's stored water falls by exactly what the visitor's household gains, min(3 L, the store).
        policy = lambda who, minute, opts: ("door_give" if "door_give" in opts else
                                            "door_call" if "door_call" in opts else None)
        d, q, (v,) = self.door_day(PolicyFake(policy), [(30, "ask_water")])
        w = q.world
        self.quiet.play(d.day3)
        sc = q.door_scenes[0]
        self.assertEqual(sc["outcome"], "given", sc)
        g = sc["give"]
        self.assertAlmostEqual(g["world_before"] - g["world_after"], g["qty"], places=9)
        self.assertAlmostEqual(g["household_after"] - g["household_before"], g["qty"], places=9)
        self.assertAlmostEqual(g["qty"], min(3.0, g["world_before"]), places=9)
        self.assertEqual([(x[1]) for x in w.given], [g["qty"]])

    # ---------- T3: no prompt builder reads the street ----------
    def test_t3_a_prompt_builder_that_reads_world_street_raises_truthleak(self):
        w = self.truth.World(2)
        self.assertIsNotNone(getattr(w, "street", None), "World.street is not built")
        with self.truth.prompting():
            with self.assertRaises(self.truth.TruthLeak):
                w.street
        d = self.v16()
        m = d.day3
        leo = m.people["leo"]
        real = m.inside_lines

        def leaky(p, today=False):
            m.quiet.world.street["households"]
            return real(p, today)
        with mock.patch.object(m, "inside_lines", leaky):
            with self.assertRaises(self.truth.TruthLeak):
                m.prompt_for(leo, 30, m.options_for(leo))
        # The copy World makes to look ahead does not carry the street (it stays cheap).
        self.assertIsNone(m.quiet.world.ahead().__dict__.get("street"))

    # ---------- T4: days 1 and 2 as before; nobody comes to no. 9 before day 3 ----------
    def test_t4_days_1_and_2_replay_and_the_street_makes_no_visit_before_day_3(self):
        d = self.v16()          # days 1 and 2, nights 1 and 2, minds 1 and 2: all from cache/v16 (asserted there)
        st = getattr(d.day3.quiet.world, "street", None)
        self.assertIsNotNone(st, "World.street is not built")
        parts = [x for x in st["log"] if x["what"] == "part"]
        self.assertTrue(parts, "the street has not been advanced to day 3")
        self.assertEqual(parts[0]["at"], self.quiet.absolute(1, -420))        # played day 1, 00:00
        self.assertGreaterEqual(len(parts), 9)
        self.assertTrue([x for x in st["log"] if x["what"] == "plan"])
        self.assertFalse([v for v in st["visits"] if v["at"] < self.at(3, -420)], "a visit to no. 9 before day 3")
        self.assertFalse([x for x in st["deeds"] if x["to"] == 9 and x["at"] < self.at(3, -420)])
        # The replay of v16 seed 2 to day 10 asks nothing new until day 3, min 00.
        copy = os.path.join(self.dirs.root, f"{self.MODEL}-daniel_ate_it-seed2.json")
        shutil.copyfile(os.path.join(V16_CACHE, f"{self.MODEL}-daniel_ate_it-seed2.json"), copy)
        missed = []
        real = gemini.Oracle.ask

        def ask(oracle, system, prompt, schema=None):
            try:
                return real(oracle, system, prompt, schema)
            except gemini.CacheMiss:
                missed.append(prompt)
                raise
        with mock.patch.object(gemini.Oracle, "ask", ask):
            (meta, code), _ = quiet_run(2, replay=True, days=10, config_path=CONFIG, runs_dir=self.dirs.runs,
                                        cache_dir=self.dirs.root)
        self.assertEqual(code, 3)
        self.assertEqual(len(missed), 1)
        self.assertIn("\nNow, minute 00, you are in the kitchen.", missed[0])
        self.assertIn("Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions", missed[0])

    # ---------- T5: the door lines sit inside the budget ----------
    def test_t5_the_block_is_the_same_with_and_without_a_door_and_the_door_lines_are_under_140_tokens(self):
        policy = lambda who, minute, opts: "door_call" if "door_call" in opts and minute == 30 else None
        d, q, (v,) = self.door_day(PolicyFake(policy), [(30, "ask_water")])
        m = d.day3
        for t in range(0, 12):
            q.turn(t)
        kitchen = [p for p in m.people.values() if p.room == "kitchen" and getattr(p, "door", None)]
        self.assertTrue(kitchen, "nobody in the kitchen has the door scene")
        p = kitchen[0]
        p.memory += [(0, f"filler line number {i} " + "about nothing much at all " * 12) for i in range(200)]
        with_door = m.prompt_for(p, 11, m.options_for(p))
        b1 = m.last_block
        lines = self.door_lines(with_door)
        self.assertTrue([x for x in lines if "voice at the front door says" in x], with_door[-1500:])
        self.assertTrue([x for x in lines if x.startswith("- door_")])
        house = next(x for x in with_door.split("\n") if x.startswith("The house:"))
        seen, p.door = p.door, None
        plain = m.prompt_for(p, 11, m.options_for(p))
        b0 = m.last_block
        p.door = seen
        self.assertEqual(b1, b0)
        plain_house = next(x for x in plain.split("\n") if x.startswith("The house:"))
        extra = estimate_tokens("\n".join(lines)) + (len(house) - len(plain_house)) / 3.6
        self.assertLessEqual(extra, 140, (extra, lines))
        self.assertIn("- (earlier things, left out here)", with_door)

    # ---------- T6: when a knock comes, and who hears it ----------
    def test_t6_a_knock_comes_by_day_once_a_day_never_into_the_bathroom_and_wakes_by_the_draw(self):
        street = self.need("street")
        for seed in range(1, 11):
            for v in street.schedule(seed, days=10):
                k = (v["at"] + 420) // 1440 + 1
                minute = v["at"] - self.at(k, 0)
                self.assertTrue(30 <= minute <= 630 and minute % 3 == 0, (seed, v))
                self.assertGreaterEqual(k, 3, (seed, v))
        # At most one a day: a second visit the same day is deferred to the next part, and logged.
        d, q, (v1, v2) = self.door_day(None, [(180, "ask_food"), (240, "ask_water")])     # people are awake then
        self.quiet.play(d.day3)
        q7 = [e for e in q.log if e["kind"] == "Q7"]
        self.assertEqual(sum(e["fired"] for e in q7), 1, q7)
        later = [e for e in q7 if e["visit"] == v2["id"]]
        self.assertEqual([e["why"] for e in later], ["a knock has come today already"])
        self.assertGreaterEqual(v2["at"], self.at(4, 30))
        self.assertEqual(v2["deferrals"][0]["why"], "a knock has come today already")
        # Deferred when 52 asks are spent: the day cannot give it 6 beyond the evening's 8 (reports/door_memory_impl.md;
        # W2a deferred it from 52 on, test_morning.DoorAfterTest has the rule's edges).
        d, q, (v,) = self.door_day(None, [(120, "ask_food")])
        q.asks = 52
        q.tick(120)
        self.assertFalse(q.hear_knock(120, played=False))
        self.assertEqual(v["deferrals"][-1]["why"], "the day cannot give a knock 6 asks beyond the evening's 8")
        # Never into the bathroom; a resting person wakes by the draw; the kitchen hears the words.
        d, q, (v,) = self.door_day(None, [(120, "ask_food")])
        m = d.day3
        q.tick(120)
        for p in m.people.values():
            q.end(p, 120, "test")
        el, mara, leo, dan = (m.people[x] for x in ("elena", "mara", "leo", "daniel"))
        el.room, mara.room, leo.room, dan.room = "kitchen", "bathroom", "brothers_room", "back_room"
        q.start(leo, "rest", 120, planned=180, until=300)
        fired = q.hear_knock(120, played=False)
        self.assertTrue(fired)
        sc = q.door
        self.assertEqual(sc["heard"].get("elena"), "words")
        self.assertNotIn("mara", sc["heard"])
        self.assertIsNone(mara.door)
        self.assertEqual(sc["heard"].get("daniel"), "heard")
        woke = street.wakes(q.world.street, v, 1, "leo", data.PEOPLE["leo"]["traits"]["anxious"])
        self.assertEqual("leo" in sc["heard"], woke)
        self.assertEqual(q.resting("leo"), not woke)
        self.assertAlmostEqual(street.wake_chance(0.25), 0.3, places=9)
        self.assertAlmostEqual(street.wake_chance(0.95), 0.58, places=9)
        self.assertEqual(street.wake_chance(5.0), 0.9)

    # ---------- T7: the door options ----------
    def test_t7_the_door_options_exist_only_in_a_scene_in_the_kitchen(self):
        def ids(m, p):
            return [o.id for o in m.options_for(p) if o.id.startswith("door_")]
        d, q, (v,) = self.door_day(None, [(120, "ask_water")])
        m = d.day3
        el, leo = m.people["elena"], m.people["leo"]
        el.room = "kitchen"
        self.assertEqual(ids(m, el), [])
        q.tick(120)
        for p in m.people.values():
            q.end(p, 120, "test")
            p.room = "kitchen"
        leo.room = "back_room"
        self.assertTrue(q.hear_knock(120, played=False))
        # The stranger says what they need through the door with the knock (reports/door_heard_impl.md), so water to
        # give puts door_give in from the first turn; with no water it is not offered.
        self.assertEqual(ids(m, el), ["door_look", "door_call", "door_open", "door_give", "door_refuse"])
        self.assertEqual(ids(m, leo), [])
        q.door_act(el, "door_call", 120, "Who is it?")
        q.door_after(120)
        q.door_before(123)
        self.assertEqual(ids(m, el), ["door_look", "door_call", "door_open", "door_give", "door_refuse"])
        tap, rain = q.world.tap, q.world.rain
        q.world.tap = q.world.rain = 0.0
        q.door_before(123)
        self.assertNotIn("door_give", ids(m, el))
        q.world.tap, q.world.rain = tap, rain
        # door_open only while the door is shut.
        q.door_act(el, "door_open", 123, None)
        q.door_after(123)
        q.door_before(126)
        self.assertEqual(q.door["door"], "open")
        self.assertNotIn("door_open", ids(m, el))
        self.assertNotIn("door_look", ids(m, el))
        self.assertIn("door_give", ids(m, el))
        # A visit for food: nothing in the house is offered at the door (W2a gives water only).
        d, q, (v,) = self.door_day(None, [(120, "ask_food")])
        m = d.day3
        q.tick(120)
        for p in m.people.values():
            q.end(p, 120, "test")
            p.room = "kitchen"
        q.hear_knock(120, played=False)
        el = m.people["elena"]
        q.door_act(el, "door_call", 120, "Who is it?")
        q.door_after(120)
        q.door_before(123)
        self.assertNotIn("door_give", ids(m, el))

    # ---------- T8: the cost ----------
    def test_t8_a_visit_asks_at_most_18_at_the_door_and_a_day_at_most_56(self):
        # reports/door_heard_impl.md: the Q7 reserve of 6 is replaced by everyone at the door asked each turn, up to 18
        # door asks a visit; the stretch's own cap (18) still holds everyone else's asks.
        d, q, (v,) = self.door_day(TalkFake(), [(300, "ask_water")])
        m = d.day3
        self.quiet.play(m)
        q7 = [s for s in q.stretches if s["trigger"] == "Q7"]
        knocks = [e for e in q.log if e["kind"] == "Q7" and e["fired"]]
        self.assertEqual(len(knocks), 1, q.log[-5:])
        for sc in q.door_scenes:
            self.assertLessEqual(sc["door_asks"], 18, sc)
        for s in q7:
            self.assertLessEqual(s["asks"], 2 * 18 - 1, s)
        self.assertLessEqual(q.asks, 56)
        # The day cap holds whatever stretch is under way, reserved or not.
        q.cap, q.reserved, q.asks = None, True, 55
        self.assertFalse(q.spent())
        q.asks = 56
        self.assertTrue(q.spent())
        self.assertEqual(self.quiet.DAY_MAX, 56)
        self.assertEqual(self.quiet.DOOR_ASKS, 18)

    # ---------- T9: the stranger's lines ----------
    def test_t9_every_strangers_line_is_short_plain_and_of_the_familys_world(self):
        path = os.path.join(HERE, "streetdata", "lines.json")
        self.assertTrue(os.path.exists(path), "streetdata/lines.json is not written")
        pool = json.loads(read(path))
        slots = ("voice_ask_water", "voice_ask_food", "open_ask_water", "open_ask_food", "insist_water",
                 "insist_food", "again_water", "again_food", "given", "refused_polite", "refused_flat")
        self.assertEqual(sorted(pool["slots"]), sorted(slots))
        absent = re.compile(r"\b(radio|police|army|soldiers?|phone|mobile|electricity|power|cars?|shops?|church|"
                            r"hospital|television|tv|internet|council|government|news|candles?|stove|gas|monday|"
                            r"tuesday|wednesday|thursday|friday|saturday|sunday|number|street|neighbour\w*|"
                            r"should|must|have to|ought|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
                            r"gun|knife|kill)\b", re.I)
        for slot in slots:
            lines = pool["slots"][slot]
            plain = [x for x in lines if not x.get("with")]
            self.assertGreaterEqual(len(plain), 8, slot)
            self.assertEqual(len({x["text"] for x in lines}), len(lines), slot)
            for x in lines:
                text = x["text"]
                self.assertLessEqual(len(text.split()), 25, text)
                self.assertIsNone(re.search(r"\d", text), text)
                self.assertIsNone(absent.search(text), text)
                self.assertIn(x.get("with"), (None, "child", "girl", "boy", "others", "heard_voices"), text)
                if "water" in slot:
                    self.assertNotRegex(text.lower(), r"\b(eat|food|bread|tin)\b", text)
                if "food" in slot:
                    self.assertNotRegex(text.lower(), r"\b(water|drink|thirst\w*)\b", text)
                if not x.get("with"):
                    self.assertNotRegex(text.lower(), r"\b(we|us|our|child|kids?|little one|baby|son|daughter|"
                                                      r"husband|wife|mother|mum|father|dad)\b", text)



class KnockFixTest(unittest.TestCase):
    """reports/w2a_fixes.md: the street sees no. 9's yard from the houses that overlook it, the approach factor back to
    1.0, a Q7 stretch that ends when nobody in its room perceives the door, and lines that say only what the visiting
    household is. Day-3 tests start from v16 seed 2 through night 2, replayed from cache/v16 with no API call."""
    MODEL = QuietDayTest.MODEL
    v16 = QuietDayTest.v16
    setUp, tearDown, need, at = KnockTest.setUp, KnockTest.tearDown, KnockTest.need, KnockTest.at
    door_day, door_lines = KnockTest.door_day, staticmethod(KnockTest.door_lines)

    # ---------- 1: the yard seen ----------
    def test_f1_a_bin_in_no_9s_yard_is_seen_by_day_from_the_houses_that_overlook_it(self):
        street = self.need("street")
        over = street.load("street").get("overlook", {}).get("9")
        self.assertTrue(over, "street.json does not say which houses overlook no. 9's yard")
        pop = street.load("population")
        self.assertIn("yard", pop, "population.json has no belief value for a seen yard")
        prior, seen = pop["priors"]["surplus"], pop["yard"]["has_surplus"]
        self.assertGreater(seen, prior)
        dry = lambda minute: False

        def street_with(bin_at=None, people=()):
            st = street.generate(2)
            return st, (lambda: {"bin_out_at": bin_at, "people": list(people)})

        def beliefs(st):
            return {h["home"]: (h["occupied"][9], h["surplus"][9]) for h in st["households"].values()}
        st, yard = street_with(self.at(6, 0))                         # the bin out at 07:00 on day 6
        occ = [n for n in over if st["houses"][n]["status"] == "occupied"]
        self.assertTrue(occ, "the premise: someone lives in a house that overlooks no. 9's yard")
        far = [h for h in st["households"].values() if h["home"] not in over]
        street.advance(st, self.at(6, 0), dry, yard=yard)
        before = beliefs(st)
        for n in occ:
            self.assertEqual(before[n][1], prior, n)
        street.advance(st, self.at(6, 300), dry, yard=yard)            # 12:00: the morning's daylight showed it
        after = beliefs(st)
        for n in occ:
            self.assertEqual(after[n], (1.0, seen), n)
            self.assertTrue([x for x in st["log"] if x["what"] == "saw_yard" and x["house"] == n and x["bin"]], n)
        for h in far:
            self.assertEqual(after[h["home"]], before[h["home"]], h["home"])
        # Only by day: a bin put out at 19:00 is not seen at midnight or at 06:00, and is seen by 12:00 the next day.
        st, yard = street_with(self.at(6, 720))
        street.advance(st, self.at(7, -60), dry, yard=yard)
        self.assertEqual({n: beliefs(st)[n][1] for n in occ}, {n: prior for n in occ})
        street.advance(st, self.at(7, 300), dry, yard=yard)
        self.assertEqual({n: beliefs(st)[n] for n in occ}, {n: (1.0, seen) for n in occ})
        # Out of sight range nothing is seen, whatever is there.
        self.assertFalse(street.sees({"metres": pop["sight"]["range_m"] + 1}, True))
        self.assertTrue(street.sees({"metres": pop["sight"]["range_m"]}, True))
        self.assertFalse(street.sees({"metres": 5.0}, False))
        # Someone in the yard by day, with no bin: no. 9 is occupied; its water is not judged from that.
        st, yard = street_with(None, [self.at(6, 180)])
        for h in st["households"].values():
            h["occupied"][9] = 0.5
        street.advance(st, self.at(6, 300), dry, yard=yard)
        for n in occ:
            self.assertEqual(beliefs(st)[n], (1.0, prior), n)
        # In the run: the bin set out from the kitchen on day 3 reaches the street through World, by 12:00.
        d = self.v16()
        m, q = d.day3, d.day3.quiet
        self.assertIsNone(getattr(q.world, "bin_out_at", None))
        q.tick(30)
        q.collect_rain(m.people["leo"], 30)
        self.assertEqual(q.world.bin_out_at, self.at(3, 30))
        self.assertEqual(q.world.yard_people, [self.at(3, 30)])
        q.tick(303)
        got = beliefs(q.world.street)
        for n in [n for n in over if q.world.street["houses"][n]["status"] == "occupied"]:
            self.assertEqual(got[n], (1.0, seen), n)

    # ---------- 2: the reasoned rate ----------
    def test_f2_the_approach_factor_is_back_to_1(self):
        street = self.need("street")
        self.assertEqual(street.load("population")["approach"]["factor"], 1.0)
        self.assertEqual(street.generate(2)["factor"], 1.0)

    # ---------- 3: the door stretch ends when nobody in its room perceives the door ----------
    def test_f3_a_q7_stretch_ends_and_frees_its_reserve_when_nobody_in_its_room_perceives_the_door(self):
        class Recording(PolicyFake):
            pass

        def policy(who, minute, opts):
            if minute is None or minute < 180:
                return None
            if "door_call" in opts:
                return next((o for o in ("go_back_room", "go_brothers_room") if o in opts), None)
            return next((o for o in opts if o.startswith("confront_")), None)
        rec = Recording(policy)
        rec.prompts = []
        real = rec.generate

        def generate(system, prompt, schema=None):
            if schema is None:
                rec.prompts.append((now_minute(prompt), prompt))
            return real(system, prompt, schema)
        rec.generate = generate
        d, q, (v,) = self.door_day(rec, [(180, "ask_water")])
        self.quiet.play(d.day3)
        q7 = [s for s in q.stretches if s["trigger"] == "Q7"]
        self.assertTrue(q7, q.log[-6:])
        self.assertEqual(q7[0]["start"], 180)
        # The family walked away from the door at 10:00; at 10:03 nobody in the kitchen perceives it: the stretch ends.
        self.assertEqual(q7[0]["end"], 183, q7)
        for s in q7:
            asked = [(mm, p) for mm, p in rec.prompts if mm is not None and s["start"] <= mm < s["end"]]
            self.assertTrue(asked, s)
            for mm, p in asked:
                self.assertTrue(self.door_lines(p), f"a Q7 ask without the door in it, at {mm}:\n{p[-800:]}")
        sc = q.door_scenes[0]
        self.assertLessEqual(sc["door_asks"], 18)          # was 6 (reports/door_heard_impl.md)
        self.assertEqual(sc["outcome"], "ignored")
        self.assertIsNone(q.door)
        self.assertFalse(q.reserved)

    # ---------- 4: the stranger says only what their household is ----------
    def test_f4_a_strangers_line_says_only_what_its_household_is(self):
        street = self.need("street")
        pool = street.lines()
        voices = [x for xs in pool.values() for x in xs if "heard voices" in x["text"].lower()]
        self.assertTrue(voices)
        for x in voices:
            self.assertEqual(x.get("with"), "heard_voices", x["text"])
        seen = set()
        for seed in range(1, 11):
            st = street.generate(seed)
            for hid, hh in st["households"].items():
                kids = {m["sex"] for m in hh["drawn"]["members"] if m["role"] == "child"}
                for n in range(1, 6):
                    for slot in pool:
                        text = street.line(st, {"household": hid, "n": n}, slot)
                        seen.add(text)
                        self.assertNotIn("heard voices", text.lower(), (seed, hid))
                        if re.search(r"\b(girl|her|she)\b", text, re.I):
                            self.assertIn("f", kids, (seed, hid, text))
                        if re.search(r"\b(boy|him|he)\b", text, re.I):
                            self.assertIn("m", kids, (seed, hid, text))
                        if re.search(r"\b(little one|child)\b", text, re.I):
                            self.assertTrue(kids, (seed, hid, text))
        self.assertGreater(len(seen), 60)


class DoorRecording(PolicyFake):
    """PolicyFake that keeps (who, minute, prompt) of every day decision."""

    def __init__(self, policy):
        super().__init__(policy)
        self.prompts = []

    def generate(self, system, prompt, schema=None):
        if schema is None:
            self.prompts.append((asked_where(prompt)[0], now_minute(prompt), prompt))
        return super().generate(system, prompt, schema)


class DoorHeardTest(unittest.TestCase):
    """reports/door_heard_impl.md (from reports/probe_door.md): the visitor speaks through the shut door in the minute
    of each knock; each one's record of the visit holds only what they perceived of it; a parting line that refers to
    asking only after an ask; and every turn the visitor is at the door, everyone awake who perceives it is asked, up to
    18 door asks a visit. Day-3 tests start from v16 seed 2 through night 2, replayed from cache/v16 with no API call."""
    MODEL = QuietDayTest.MODEL
    v16 = QuietDayTest.v16
    setUp, tearDown, need, at = KnockTest.setUp, KnockTest.tearDown, KnockTest.need, KnockTest.at
    door_day = KnockTest.door_day
    # What a parting line says that only makes sense after the visitor has asked for something (reports/probe_door.md
    # §2: "I'm sorry I asked", "No, I understand", and the two that answer an ask: "Thanks for nothing", "find it").
    ASK_REF = re.compile(r"\b(ask|asked|asking)\b|no, i understand|thanks for nothing|find it somewhere", re.I)

    def scene(self, client=None, household=None, purpose="ask_water", minute=120,
              rooms=(("elena", "kitchen"), ("mara", "kitchen"), ("leo", "kitchen"), ("daniel", "bathroom"))):
        """Day 3 at `minute`: everyone's routine ended, each put in a room, and one visit due now (by `household`, or
        the first household of seed 2's street with no child)."""
        street = self.need("street")
        d, q, _ = self.door_day(client)
        st = q.world.street
        hid = household or next(h for h in sorted(st["households"], key=lambda h: st["households"][h]["home"])
                                if not street.has_child(st["households"][h]))
        v = street.make_visit(st, hid, self.at(3, minute), purpose)
        m = d.day3
        q.tick(minute)
        for p in m.people.values():
            q.end(p, minute, "test")
        for pid, room in rooms:
            m.people[pid].room = room
        return d, q, v

    def visit_turns(self, q, minute, turns=12, between=None):
        """The knock at `minute` as play() makes it in quiet time: Q7's stretch, then played turns until the visitor
        has gone (or `turns`). between(t): called before each turn."""
        self.assertTrue(q.hear_knock(minute, played=False), "the knock was not heard")
        stretch = {"start": minute, "end": None, "room": "kitchen", "trigger": "Q7"}
        q.begin(stretch, self.quiet.DOOR_ASKS, "the door's asks are spent", reserved=True)
        t = minute // data.MINUTES_PER_TURN
        for t in range(t, t + turns):
            if q.door is None:
                break
            if between:
                between(t)
            q.turn(t)
        return stretch

    @staticmethod
    def heard_need(p, good="water"):
        """Whether p heard the visitor say what they need, from p's own memory: a line through the door naming it."""
        words = r"water|drink|cup" if good == "water" else r"food|eat|bread|hungry"
        return any(re.search(r'voice at the front door says?: ".*\b(' + words + r')\b', x, re.I) for _, x in p.memory)

    # ---------- (a) the visitor speaks first ----------
    def test_a_the_visitors_first_line_is_in_the_prompt_of_everyone_who_heard_the_knock_in_words(self):
        rec = DoorRecording(lambda who, minute, opts: None)
        d, q, v = self.scene(rec, rooms=(("elena", "kitchen"), ("mara", "kitchen"), ("leo", "kitchen"),
                                         ("daniel", "back_room")))
        m = d.day3
        self.visit_turns(q, 120, turns=1)
        sc = q.door or q.door_scenes[-1]
        words = sorted(pid for pid, how in sc["heard"].items() if how == "words")
        self.assertEqual(words, ["elena", "leo", "mara"], sc["heard"])          # the premise: the kitchen hears words
        self.assertEqual(sc["heard"].get("daniel"), "heard")
        self.assertTrue(sc["said"], "the visitor said nothing at the knock")
        said_at, text = sc["said"][0]
        self.assertEqual(said_at, 120)
        pool = [x["text"] for x in self.need("street").lines()["voice_ask_water"]]
        self.assertIn(text, pool)
        for pid in words:
            got = [p for who, mm, p in rec.prompts if who == pid and mm == 120]
            self.assertTrue(got, f"{pid} was not asked at the knock minute")
            prompt = got[0]
            self.assertIn(f'voice at the front door says: "{text}"', prompt)
            self.assertLess(prompt.index("- Someone is knocking at the front door."), prompt.index(text))
            self.assertIn(text, " ".join(x for _, x in m.people[pid].memory))
        # Whoever heard only knocking did not hear the words.
        self.assertNotIn(text, " ".join(x for _, x in m.people["daniel"].memory))
        self.assertFalse([p for who, mm, p in rec.prompts if who == "daniel" and text in p])

    # ---------- (b) a visitor with a child names the child and their age ----------
    def test_b_a_child_visitors_first_line_names_the_child_and_their_age(self):
        street = self.need("street")
        d, q, v0 = self.scene(None)
        v0["state"] = "done"                     # only the visits below come to the door
        st = q.world.street
        kids_of = {h: sorted((m for m in hh["drawn"]["members"] if m["role"] == "child"), key=lambda m: m["id"])
                   for h, hh in st["households"].items()}
        homes = sorted((h for h in kids_of if kids_of[h]), key=lambda h: st["households"][h]["home"])
        self.assertGreaterEqual(len(homes), 3, "the premise: households with a child on seed 2's street")
        firsts = []
        for i, hid in enumerate(homes):
            for purpose in ("ask_water", "ask_food"):
                q.door, q.q7_done = None, False
                minute = 120 + 6 * (2 * i + (purpose == "ask_food"))
                q.tick(minute)
                for p in q.m.people.values():
                    q.end(p, minute, "test")
                    p.room = "kitchen"
                v = street.make_visit(st, hid, self.at(3, minute), purpose)
                self.assertTrue(q.hear_knock(minute, played=False), (hid, purpose))
                sc = q.door
                self.assertTrue(sc["said"], f"the visitor from {hid} said nothing at the knock")
                said_at, text = sc["said"][0]
                self.assertEqual(said_at, minute)
                for kid in kids_of[hid]:
                    self.assertRegex(text, r"\b" + ("girl" if kid["sex"] == "f" else "boy") + r"s?\b", (hid, text))
                    self.assertRegex(text, r"\b" + street.AGE_WORDS[kid["age"]] + r"\b", (hid, kid, text))
                good = r"water|drink" if purpose == "ask_water" else r"food|eat"
                self.assertRegex(text.lower(), good, text)
                self.assertNotIn("{", text)
                firsts.append(text)
        self.assertGreater(len(set(firsts)), 3, firsts)

    # ---------- (c) each one's record holds only what they perceived ----------
    def records_hold_only_what_each_perceived(self, m, sc):
        """Every line of the visit each person has (their summary, for block A; their sure lines): the need only if
        they heard words saying it; the visitor's face only if they saw it."""
        checked = 0
        for pid in data.ORDER:
            p = m.people[pid]
            lines = ([sc["summary"][pid]] if pid in sc["summary"] else []) + \
                [x for x in p.sure if "knocked at the front door" in x]
            looked = any(a[1] == pid and a[2] == "door_look" for a in sc["acts"])
            for line in lines:
                checked += 1
                if not self.heard_need(p):
                    self.assertNotRegex(line, r"\basked\b|\bwater\b", (pid, line))
                if not looked and sc["door"] != "open":
                    self.assertNotIn(sc["who"], line, (pid, line))
        return checked

    def test_c_a_record_states_the_need_and_the_visitor_only_as_that_person_perceived_them(self):
        # Elena sends the person away in the knock's minute; Mara looks; Leo only listens; Daniel, in the back room,
        # hears only knocking.
        def policy(who, minute, opts):
            return {("elena", 120): "door_refuse", ("mara", 120): "door_look"}.get((who, minute))
        d, q, v = self.scene(DoorRecording(policy), rooms=(("elena", "kitchen"), ("mara", "kitchen"),
                                                           ("leo", "kitchen"), ("daniel", "back_room")))
        m = d.day3
        self.visit_turns(q, 120, turns=4)
        self.assertIsNone(q.door, "the visit has not ended")
        sc = q.door_scenes[-1]
        self.assertEqual(sc["outcome"], "refused", sc["acts"])
        self.assertEqual(sc["heard"].get("daniel"), "heard")
        self.assertGreaterEqual(self.records_hold_only_what_each_perceived(m, sc), 4)
        self.assertEqual(sc["summary"]["daniel"], "At 09:00 you heard knocking at the front of the house.")
        # Whoever heard the ask through the door has it in their line: Elena heard it and sent the person away.
        self.assertTrue(self.heard_need(m.people["elena"]))
        self.assertIn("who asked for water", sc["summary"]["elena"])
        # Leo heard the voice and did not look: he has the voice, not the face. Mara looked: she has the face.
        self.assertNotIn(sc["who"], sc["summary"]["leo"])
        self.assertIn(sc["voice"].split("'")[0].lower(), sc["summary"]["leo"].lower())
        self.assertIn(sc["who"], sc["summary"]["mara"])
        # Daniel heard only knocking, then came into the kitchen at 09:03 and looked: he saw the person and heard
        # them speak, but never heard what they wanted.
        def policy(who, minute, opts):
            return {("elena", 123): "door_refuse", ("daniel", 123): "door_look"}.get((who, minute))
        d, q, v = self.scene(DoorRecording(policy), rooms=(("elena", "kitchen"), ("mara", "kitchen"),
                                                           ("leo", "kitchen"), ("daniel", "back_room")))
        m = d.day3

        def between(t):
            if t == 41:
                m.people["daniel"].room = "kitchen"
        self.visit_turns(q, 120, turns=4, between=between)
        self.assertIsNone(q.door, "the visit has not ended")
        sc = q.door_scenes[-1]
        self.assertEqual(sc["outcome"], "refused", sc["acts"])
        self.assertIn(["daniel", "door_look"], [[a[1], a[2]] for a in sc["acts"]], "the premise: Daniel looked")
        self.assertFalse(self.heard_need(m.people["daniel"]), "the premise: Daniel heard no ask")
        self.assertIn(sc["who"], sc["summary"]["daniel"])
        self.records_hold_only_what_each_perceived(m, sc)

    def test_c2_someone_who_heard_the_ask_and_then_only_a_later_knock_keeps_the_ask_in_their_record(self):
        # Mara hears the visitor's first line in the kitchen at 09:00, goes to the back room, and hears the second knock
        # at 09:09 only as knocking through the wall (found in reports/door_heard_impl.md, the fake probe's scene 3).
        def policy(who, minute, opts):
            return "go_back_room" if (who, minute) == ("mara", 120) else "door_look"
        d, q, v = self.scene(DoorRecording(policy))
        m = d.day3
        self.visit_turns(q, 120)
        self.assertIsNone(q.door, "the visit has not ended")
        sc = q.door_scenes[-1]
        self.assertEqual(sc["knocks"], [120, 129])
        self.assertEqual(sc["heard"].get("mara"), "heard", "the premise: Mara heard the second knock only as knocking")
        self.assertTrue(self.heard_need(m.people["mara"]), "the premise: Mara heard the ask")
        self.assertIn("asked for water", sc["summary"]["mara"])
        self.assertTrue([x for x in m.people["mara"].sure if "knocked at the front door" in x])
        self.records_hold_only_what_each_perceived(m, sc)

    # ---------- (d) a parting line that refers to asking only after an ask ----------
    def test_d_no_parting_line_that_refers_to_asking_without_an_ask(self):
        street = self.need("street")
        hit = set()
        for seed in range(1, 11):
            st = street.generate(seed)
            for hid in st["households"]:
                for n in range(1, 6):
                    for slot in ("refused_polite", "refused_flat"):
                        text = street.line(st, {"household": hid, "n": n}, slot)
                        self.assertNotRegex(text, self.ASK_REF, (seed, hid, n, slot))
                        asked = street.line(st, {"household": hid, "n": n, "asked": True}, slot)
                        if self.ASK_REF.search(asked):
                            hit.add(asked)
        self.assertTrue(hit, "after an ask, the lines that refer to it are still said")
        # In a scene, the refusal comes after the visitor's ask through the door, and the visit says so.
        policy = lambda who, minute, opts: "door_refuse" if who == "elena" and minute == 120 else None
        d, q, v = self.scene(DoorRecording(policy))
        self.visit_turns(q, 120, turns=4)
        sc = q.door_scenes[-1]
        self.assertEqual(sc["outcome"], "refused")
        self.assertTrue(v.get("asked"), "the visit does not record that its ask was said")
        self.assertEqual([mm for mm, _ in sc["said"]], [120, 123])

    # ---------- (e) every turn at the door, everyone who perceives it is asked, up to 18 ----------
    def test_e_a_visitor_who_stays_6_turns_is_answered_after_the_second_knock_and_no_visit_asks_more_than_18(self):
        rec = DoorRecording(lambda who, minute, opts: "door_look")
        d, q, v = self.scene(rec)
        m = d.day3
        self.visit_turns(q, 120)
        self.assertIsNone(q.door, "the visit has not ended")
        sc = q.door_scenes[-1]
        self.assertEqual(sc["outcome"], "ignored")
        self.assertEqual(sc["knocks"], [120, 129])
        self.assertEqual(sc["end"], 138)
        # The door asks: the model asked of the three at the door (Daniel, in the bathroom, does not perceive it).
        decided = [(rec_["minute"], dd["person"]) for rec_ in m.log for dd in rec_["decisions"]
                   if 120 <= rec_["minute"] < 138 and dd["mode"] == "model" and dd["person"] != "daniel"]
        after = sorted(x for x in decided if x[0] >= 129)
        self.assertEqual(after, sorted((mm, pid) for mm in (129, 132, 135) for pid in ("elena", "leo", "mara")),
                         decided)
        self.assertEqual(len(decided), 18)
        self.assertEqual(sc["door_asks"], 18)
        self.assertEqual(self.quiet.DOOR_ASKS, 18)
        # Four in the room for six turns would be 24: the visit stops at 18.
        rec = DoorRecording(lambda who, minute, opts: "door_look")
        d, q, v = self.scene(rec, rooms=tuple((pid, "kitchen") for pid in data.ORDER))
        m = d.day3
        self.visit_turns(q, 120)
        sc = q.door_scenes[-1]
        decided = [x for x in m.log if 120 <= x["minute"] < sc["end"] for dd in x["decisions"] if dd["mode"] == "model"]
        self.assertEqual(len(decided), 18)
        self.assertEqual(sc["door_asks"], 18)


class SayingPolicy(PolicyFake):
    """PolicyFake whose every answer has words, as the live answers at the door had (runs/probe_door2/scene1.json:
    Mara's door_give said "Mom, we have to give her some, we have enough stored.")."""

    def generate(self, system, prompt, schema=None):
        text = super().generate(system, prompt, schema)
        if schema is not None:
            return text
        got = json.loads(text)
        if got["option"] != "silent" and not got["say"]:
            got["say"] = f"Words of {asked_where(prompt)[0]} at {now_minute(prompt)}."
        return json.dumps(got)


class DoorMemoryTest(unittest.TestCase):
    """reports/door_memory_impl.md (from reports/door_after_facts.md §3 and §4): when one sends the visitor away and
    another gives anyway, each one's summary of the visit keeps both acts, in the order done, each only if they
    perceived it; the actor's own line of an act at the door says what they did; block C has a key for a refusal.
    Day-3 tests start from v16 seed 2 through night 2, replayed from cache/v16 with no API call."""
    MODEL = QuietDayTest.MODEL
    v16 = QuietDayTest.v16
    setUp, tearDown, need, at = KnockTest.setUp, KnockTest.tearDown, KnockTest.need, KnockTest.at
    door_day, scene, visit_turns = KnockTest.door_day, DoorHeardTest.scene, DoorHeardTest.visit_turns
    handmade = DaysTest.handmade
    # probe_door2's scene 1: h13 at the door at 09:42, Daniel in the brothers' room (reports/door_after_facts.md §2).
    ROOMS = (("elena", "kitchen"), ("mara", "kitchen"), ("leo", "kitchen"), ("daniel", "brothers_room"))
    KNOCK = 162
    HEAD = "At 09:42 someone knocked at the front door: "

    def scene1(self, acts):
        """Scene 1 with `acts` {who: option} at the knock's minute; returns (morning, quiet, the ended visit)."""
        policy = lambda who, minute, opts: acts.get(who) if minute == self.KNOCK else None
        d, q, v = self.scene(SayingPolicy(policy), household="h13", minute=self.KNOCK, rooms=self.ROOMS)
        self.visit_turns(q, self.KNOCK, turns=4)
        self.assertIsNone(q.door, "the visit has not ended")
        sc = q.door_scenes[-1]
        self.assertEqual(sc["voice"], "A woman's voice", "the premise: h13's envoy is a woman")
        done = [[a[1], a[2]] for a in sc["acts"] if a[0] == self.KNOCK]
        want = [[w, o] for w, o in acts.items() if o.startswith("door_")]
        self.assertEqual(sorted(done), sorted(want), "the premise: the acts at the knock's minute")
        return d.day3, q, sc

    # ---------- (a) a refusal and a give anyway: each summary keeps both ----------
    def test_a_a_give_over_a_refusal_is_in_each_summary_with_the_refusal_in_the_order_done(self):
        m, q, sc = self.scene1({"elena": "door_refuse", "mara": "door_give", "leo": "save_water"})
        self.assertEqual([a[1] for a in sc["acts"]], ["elena", "mara"], "the premise: Elena acted first (§5)")
        tail = "to go away, and {g} her about three litres of the stored water anyway."
        self.assertEqual(sc["summary"]["elena"], self.HEAD + "you told a woman, who asked for water, "
                         + tail.format(g="Mara handed"))
        self.assertEqual(sc["summary"]["leo"], self.HEAD + "Elena told a woman, who asked for water, "
                         + tail.format(g="Mara handed"))
        self.assertEqual(sc["summary"]["mara"], self.HEAD + "Elena told a woman, who asked for water, "
                         + tail.format(g="you handed"))
        # Daniel, awake in the brothers' room here, heard only knocking: neither act is in his line. (In scene 1 he
        # did not hear the knock and has no line: runs/door_after/trace.py full 1.)
        self.assertEqual(sc["summary"]["daniel"], "At 09:42 you heard knocking at the front of the house.")
        # The sure line is the summary's, and day 4's block A holds it (night.py carry_in_later).
        self.assertIn("09:45: at 09:42 someone knocked at the front door: you told a woman", " ".join(
            m.people["elena"].sure))

    def test_a2_the_give_first_then_the_refusal_and_each_act_only_if_perceived(self):
        # Called directly, in this order: Mara gives, then Elena sends the person away; Leo is in the back room for
        # both, so he perceived neither and keeps the outcome's line.
        d, q, v = self.scene(None, household="h13", minute=self.KNOCK,
                             rooms=(("elena", "kitchen"), ("mara", "kitchen"), ("leo", "kitchen"),
                                    ("daniel", "brothers_room")))
        m = d.day3
        self.assertTrue(q.hear_knock(self.KNOCK, played=False))
        m.people["leo"].room = "back_room"
        q.door_act(m.people["mara"], "door_give", self.KNOCK, "Here.")
        q.door_act(m.people["elena"], "door_refuse", self.KNOCK, "Go.")
        q.door_end(self.KNOCK + 3)
        sc = q.door_scenes[-1]
        self.assertEqual(sc["summary"]["elena"], self.HEAD + "Mara handed a woman, who asked for water, about three "
                         "litres of the stored water, and then you told her to go away.")
        self.assertEqual(sc["summary"]["mara"], self.HEAD + "you handed a woman, who asked for water, about three "
                         "litres of the stored water, and then Elena told her to go away.")
        self.assertEqual(sc["summary"]["leo"], self.HEAD + "Mara handed a woman, who asked for water, about three "
                         "litres of the stored water.")

    def test_a3_whoever_perceived_only_the_refusal_has_only_the_refusal(self):
        # Mara gives while Leo is in the back room; Leo comes back and hears Elena send the person away.
        d, q, v = self.scene(None, household="h13", minute=self.KNOCK, rooms=self.ROOMS)
        m = d.day3
        self.assertTrue(q.hear_knock(self.KNOCK, played=False))
        m.people["leo"].room = "back_room"
        q.door_act(m.people["mara"], "door_give", self.KNOCK, "Here.")
        m.people["leo"].room = "kitchen"
        q.door_act(m.people["elena"], "door_refuse", self.KNOCK, "Go.")
        q.door_end(self.KNOCK + 3)
        sc = q.door_scenes[-1]
        self.assertEqual(sc["summary"]["leo"], self.HEAD + "Elena told a woman, who asked for water, to go away.")

    # ---------- (b) a give alone and a refusal alone keep their wording ----------
    def test_b_a_give_alone_and_a_refusal_alone_keep_their_summaries(self):
        m, q, sc = self.scene1({"mara": "door_give", "leo": "save_water"})
        gave = "a woman, who asked for water, about three litres of the stored water."
        self.assertEqual(sc["summary"]["elena"], self.HEAD + "Mara handed " + gave)
        self.assertEqual(sc["summary"]["leo"], self.HEAD + "Mara handed " + gave)
        self.assertEqual(sc["summary"]["mara"], self.HEAD + "you handed " + gave)
        m, q, sc = self.scene1({"elena": "door_refuse", "leo": "save_water"})
        self.assertEqual(sc["summary"]["elena"], self.HEAD + "you told a woman, who asked for water, to go away.")
        self.assertEqual(sc["summary"]["leo"], self.HEAD + "Elena told a woman, who asked for water, to go away.")
        self.assertEqual(sc["summary"]["mara"], self.HEAD + "Elena told a woman, who asked for water, to go away.")

    # ---------- (c) the actor's own line of an act at the door ----------
    def test_c_maras_own_line_and_her_chronicle_view_of_her_give_say_she_handed_water_out(self):
        m, q, sc = self.scene1({"elena": "door_refuse", "mara": "door_give", "leo": "save_water"})
        words = next(a[3] for a in sc["acts"] if a[2] == "door_give")
        self.assertTrue(words, "the premise: Mara spoke as she gave")
        mine = [x for mm, x in m.people["mara"].memory if mm == self.KNOCK]
        self.assertIn("you handed water out at the front door. You felt tense.", mine)
        self.assertNotIn("you said. You felt tense.", mine)
        chron = self.chron.Chronicle(2, m.culprit)
        chron.add_day(m)
        e = next(e for e in chron.events if e["kind"] == "door_give")
        self.assertEqual(e["witnesses"]["mara"], "did")
        self.assertEqual(e["views"]["mara"], f'you handed water out at the front door, saying: "{words}" You felt '
                                             f'tense.')
        # Elena's own refusal keeps its words too (it was in the table already).
        e = next(e for e in chron.events if e["kind"] == "door_refuse")
        self.assertTrue(e["views"]["elena"].startswith("you told the person at the door to go away, saying: "))

    # ---------- (d) block C: a refusal at the door ----------
    def test_d_block_c_keeps_a_refusal_at_the_door_when_it_is_the_heaviest(self):
        M = importlib.import_module("memory")
        self.assertEqual(M.WEIGHT.get("door_refuse"), 3)
        self.assertEqual({k: M.WEIGHT[k] for k in ("door_give", "door_open")}, {"door_give": 4, "door_open": 3})
        everyone = {p: "saw" for p in data.ORDER}
        c = self.handmade([
            {"id": "D1-001", "scene": "D1", "minute": 3, "kind": "door_refuse", "option": "door_refuse",
             "actor": "elena", "witnesses": everyone | {"elena": "did"}},
            {"id": "D1-002", "scene": "D1", "minute": 6, "kind": "confront", "option": "confront_leo",
             "actor": "elena", "target": "leo", "witnesses": everyone | {"elena": "did"}},
        ])
        self.assertIn("Two days ago, Elena told someone at the front door to go away.",
                      [x["line"] for x in M.block_c(c, "leo", 6)])
        mine = [x for x in M.block_c(c, "elena", 6) if x["self"]]
        self.assertEqual([x["line"] for x in mine], ["Two days ago, you told someone at the front door to go away."])
        self.assertEqual(mine[0]["ids"], ["D1-001"])


class DoorAfterTest(unittest.TestCase):
    """reports/door_memory_impl.md, the door's stretch and the knock's budget (from reports/door_after_facts.md §1.2):
    once a visit ends, its Q7 stretch closes by the end of the 2nd turn after the visit's last turn, so the door's 18 do
    not pay for the rest of the morning's talk; and a knock comes only if the day can give it 6 asks beyond what the
    evening (Q5) is still owed."""
    MODEL = QuietDayTest.MODEL
    v16 = QuietDayTest.v16
    setUp, tearDown, need, at = KnockTest.setUp, KnockTest.tearDown, KnockTest.need, KnockTest.at
    door_day = KnockTest.door_day

    def noon_scene1(self):
        """runs/door_after/trace.py noon 1, in this process: probe_door2's scene 1 (v16 seed 2 to day 3, its visitor at
        09:42, the knock minute's asks answered from cache/probe_door2/scene1.json, every later ask by the fake model),
        played to 12:00. Nothing is written in the repository."""
        spec_ = importlib.util.spec_from_file_location(
            "probe_door2_probe", os.path.join(HERE, "runs", "probe_door2", "probe.py"))
        probe = importlib.util.module_from_spec(spec_)
        spec_.loader.exec_module(probe)
        path = os.path.join(self.dirs.root, "scene1.json")
        shutil.copyfile(os.path.join(HERE, "cache", "probe_door2", "scene1.json"), path)
        m, oracle = probe.day3(path, FakeClient(invalid_every=0, max_calls=10 ** 6))
        self.assertEqual(oracle.live, 0)
        probe.visitor(m, next(v for v in probe.VISITORS if v["scene"] == 1), 162)
        real = self.quiet.Quiet.hear_knock

        class Noon(Exception):
            pass

        def hear_knock(q, minute, played):
            if minute >= 300:
                raise Noon(minute)
            return real(q, minute, played)
        with mock.patch.object(self.quiet.Quiet, "hear_knock", hear_knock):
            with self.assertRaises(Noon):
                self.quiet.play(m)
        return m, oracle

    # ---------- (a) the Q7 stretch closes 2 turns after the visit ----------
    def test_a_after_a_visit_its_stretch_asks_for_2_turns_at_most_and_the_10_00_q2_is_not_refused_for_the_budget(self):
        m, oracle = self.noon_scene1()
        q = m.quiet
        self.assertGreaterEqual(oracle.from_cache, 3, "the premise: 09:42's asks are probe_door2's live answers")
        sc = q.door_scenes[0]
        self.assertEqual((sc["start"], sc["end"], sc["outcome"]), (162, 165, "given"))
        last_turn = sc["end"] - data.MINUTES_PER_TURN               # 09:42: the last turn with the visitor there
        latest = last_turn + 3 * data.MINUTES_PER_TURN              # the end of the 2nd turn after it: 09:51
        q7 = [s for s in q.stretches if s["trigger"] == "Q7"]
        self.assertEqual(len(q7), 1, q.stretches)
        self.assertLessEqual(q7[0]["end"], latest, q7[0])
        # No ask of the stretch after that: nobody is asked from 09:51 until another trigger starts the talk.
        nxt = min([s["start"] for s in q.stretches if s["start"] > q7[0]["start"]] + [300])
        asked = [(r["minute"], d["person"]) for r in m.log for d in r["decisions"]
                 if latest <= r["minute"] < nxt and d["mode"] == "model"]
        self.assertEqual(asked, [], q7)
        # The quiet triggers from the visit to noon are not refused for the day's 40, and the grudge meeting the facts
        # found refused at 10:00 (reports/door_after_facts.md §1.2) is played. (With the stretch over at 09:51, the
        # house's next minutes move: the first Q2 check is at 09:51, not 10:00.)
        q2 = [e for e in q.log if e["kind"] == "Q2" and sc["end"] <= e["minute"] < 300]
        self.assertTrue(q2, "the premise: Q2 is checked between the visit and noon")
        for e in q2 + [e for e in q.log if e["kind"] == "Q1" and sc["end"] <= e["minute"] < 300]:
            self.assertNotIn("asks are spent", str(e.get("why")), e)
        self.assertTrue([e for e in q2 if e["fired"]], [(e["minute"], e["fired"], e["why"]) for e in q2])

    # ---------- (b) a knock needs 6 asks beyond the evening's ----------
    def test_b_a_knock_is_deferred_unless_the_day_can_give_it_6_asks_beyond_the_evenings_owed_asks(self):
        def knock_with(asks, evening_done=False):
            d, q, (v,) = self.door_day(None, [(120, "ask_food")])
            m = d.day3
            q.tick(120)
            for p in m.people.values():
                q.end(p, 120, "test")
                p.room = "kitchen"
            q.asks, q.evening_done = asks, evening_done
            return q, v, q.hear_knock(120, played=False)
        day, evening = self.quiet.DAY_MAX, self.quiet.EVENING_ASKS
        self.assertEqual((day, evening, self.quiet.DOOR_ASKS), (56, 8, 18))
        # Before 19:00 the evening is owed its 8: 56 - 8 - 6 = 42 is the most a knock may find spent.
        q, v, fired = knock_with(day - evening - 6)
        self.assertTrue(fired, "with 42 spent, the day can give the knock 6 beyond the evening's 8")
        q, v, fired = knock_with(day - evening - 5)
        self.assertFalse(fired, "with 43 spent, the knock would take from the evening's 8")
        self.assertTrue(v["deferrals"], v)
        self.assertIn("6 asks", v["deferrals"][-1]["why"])
        self.assertIn("evening", v["deferrals"][-1]["why"])
        # Once Q5 has had its turn the evening is owed nothing: 50 spent leaves 6.
        q, v, fired = knock_with(day - 6, evening_done=True)
        self.assertTrue(fired, "after the evening, 50 spent leaves the knock 6")
        q, v, fired = knock_with(day - 5, evening_done=True)
        self.assertFalse(fired, "after the evening, 51 spent leaves the knock 5")
        self.assertNotIn("evening", v["deferrals"][-1]["why"])


class RefuseTalkFake(TalkFake):
    """TalkFake that refuses at the door whenever it is offered door_refuse: a visit ends in its first turn."""

    def generate(self, system, prompt, schema=None):
        if schema is None and "door_refuse" in asked_where(prompt)[2]:
            self.requests += 1
            return json.dumps({"option": "door_refuse", "say": "Go away.", "feeling": "tense", "reason": "Refuse.",
                               "suspects": "nobody", "angry_at": "nobody"})
        return super().generate(system, prompt, schema)


class BudgetFixTest(unittest.TestCase):
    """reports/budget_fix_impl.md (from reports/door_memory_impl.md §5.2): a reserved stretch's asks (Q5, Q6, Q7) count
    toward the day's 56 only, not the ordinary 40; an ordinary trigger is refused if the day's asks and the evening's
    still-owed 8 would reach 56; a knock inside a running stretch gives it the door's 18 only until 2 turns after the
    visit. Day-3 tests start from v16 seed 2 through night 2, replayed from cache/v16 with no API call."""
    MODEL = QuietDayTest.MODEL
    v16 = QuietDayTest.v16
    setUp, tearDown, need, at = KnockTest.setUp, KnockTest.tearDown, KnockTest.need, KnockTest.at
    door_day = KnockTest.door_day
    meeting = QuietDayTest.meeting

    # ---------- (a) the ordinary 40 and the evening's owed asks ----------
    def test_a_a_q2_before_the_evening_counts_only_ordinary_asks_against_40_and_leaves_the_evening_its_8(self):
        self.assertEqual((self.quiet.DAY_ASKS, self.quiet.DAY_MAX, self.quiet.EVENING_ASKS), (40, 56, 8))

        def q2_with(ordinary, reserved):
            m, q = self.meeting()
            q.asks, q.reserved_asks = ordinary + reserved, reserved
            self.assertFalse(q.evening_done)
            return q, q.arrive(m.people["daniel"], "kitchen", 260)        # 11:20, before 19:00
        # 35 ordinary and 9 reserved: 44 spent, and 44 + the evening's 8 = 52 leaves room. Q2 fires.
        q, fired = q2_with(35, 9)
        self.assertEqual([(f["kind"], f["asked"]) for f in fired], [("Q2", "leo")], q.log[-1])
        # 35 ordinary and 14 reserved: 49 spent, and 49 + 8 = 57 would reach 56. Refused, naming the evening's asks.
        q, fired = q2_with(35, 14)
        self.assertEqual(fired, [])
        why = q.log[-1]["why"]
        self.assertEqual((q.log[-1]["kind"], q.log[-1]["budget"]), ("Q2", why))
        self.assertIn("the evening's 8", why)
        self.assertIn("56", why)
        # The ordinary 40 still holds for ordinary asks, and says so.
        q, fired = q2_with(40, 0)
        self.assertEqual(fired, [])
        self.assertEqual(q.log[-1]["why"], "the day's 40 asks are spent")

    # ---------- (b) a knock inside a running stretch ----------
    def test_b_a_knock_inside_a_running_stretch_gives_it_18_until_2_turns_after_the_visit(self):
        def knock_in_q2(stretch_asks):
            """v16 seed 2's day 3, its Q2 stretch from 10:27; a knock at 10:30, inside it; the house refuses at once, so
            the visit's last turn is 10:30. seen[minute]: (asks, cap, reserved, reserved asks) after that minute's
            turn."""
            d, q, (v,) = self.door_day(RefuseTalkFake(), [(210, "ask_food")])
            seen = {}
            with mock.patch.object(self.quiet, "STRETCH_ASKS", stretch_asks):
                self.quiet.play(d.day3, told=lambda t: seen.setdefault(
                    t * data.MINUTES_PER_TURN, (q.asks, q.cap, q.reserved, getattr(q, "reserved_asks", None))))
            s = next(s for s in q.stretches if s["start"] == 207)
            sc = q.door_scenes[0]
            self.assertEqual((s["trigger"], sc["start"], sc["end"], sc["played"], sc["outcome"]),
                             ("Q2", 210, 213, True, "refused"), "the premise")
            return q, s, seen
        own = self.quiet.STRETCH_ASKS
        # The stretch's own cap is 24 + 8 = 32; the knock adds the door's 18, as now. The visit's last turn is 10:30;
        # the 2 turns after it are 10:33 and 10:36; from the end of 10:36 (seen at 10:39) the cap is back.
        q, s, seen = knock_in_q2(own)
        self.assertEqual(seen[207][1], 24 + own, seen)
        self.assertEqual(seen[210][1:3], (24 + own + 18, True), seen)
        self.assertEqual(seen[216][1:3], (24 + own + 18, True), seen)
        # Asks made while the door's 18 are on (10:30 to 10:36) are reserved ones.
        self.assertEqual(seen[216][3], seen[216][0] - seen[207][0], seen)
        # The asks made by 10:36 (40) are more than its own 32: the cap goes back to them, and the talk ends there.
        self.assertGreater(seen[216][0], 24 + own)
        self.assertEqual((s["end"], s["asks"]), (219, seen[216][0] - 24), s)
        # With a stretch whose own cap is higher than the asks made (patched to 20: 24 + 20 = 44), the cap goes back to
        # exactly its own, and it is no longer reserved: the stretch goes on, on its own asks.
        q, s, seen = knock_in_q2(20)
        self.assertEqual(seen[216][1:3], (24 + 20 + 18, True), seen)
        self.assertLess(seen[216][0], 24 + 20)
        self.assertEqual(seen[219][1:3], (24 + 20, False), seen)
        self.assertGreater(s["end"], 219, s)
        self.assertLessEqual(s["asks"], 20, s)


if __name__ == "__main__":
    unittest.main()
