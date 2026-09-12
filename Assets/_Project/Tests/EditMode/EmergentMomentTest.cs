using System;
using System.IO;
using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Sim;
using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// One moment nobody wrote, kept as a test so that it stays true and so that
    /// the chain behind it stays printable.
    ///
    /// Daniel wants to know what happened to the food, so he stands watching his
    /// mother. She reads being watched as a slight. What it mostly leaves her
    /// with is hurt, because she is close to him and holds no pride to speak of;
    /// but it leaves a little shame as well, and shame is the thing that makes a
    /// person want to be out of the room. So she goes.
    ///
    /// Nobody authored a mother made to feel like a suspect in her own kitchen by
    /// a son who is only trying to work out what happened. It comes out of four
    /// rules meeting, and it is the first thing this project has produced that
    /// was not put there.
    /// </summary>
    public class EmergentMomentTest
    {
        [Test]
        public void BeingWatchedByYourSonMakesYouWantToLeaveTheRoom()
        {
            var content = Scenario001Content.Load(TestPaths.DataRoot);
            var run = Scenario001.Run(content, "elena_fed_mara", 1);

            // He does watch her, and it is wanting to know that puts him there.
            var watching = run.Result.Actions.FirstOrDefault(a =>
                a.CharacterId == "daniel" && a.Action.Kind == ActionKind.Observe && a.Action.TargetId == "elena");

            Assert.IsNotNull(watching, "he never watched her in this run");
            StringAssert.StartsWith("find_out", watching.LeadingMotive);

            // She took it as a slight and it left a mark.
            var elena = run.Minds["elena"];
            var slight = elena.Experiences.LastOrDefault(x => x.Meaning == "disrespect" && x.ActorId == "daniel");

            Assert.IsNotNull(slight, "she made nothing of being watched");
            Assert.AreEqual("hurt", slight.DominantEmotion,
                "what it mostly leaves her with is hurt, from somebody she is close to");

            // And it is that shame, not anything from the night, that makes her
            // want to be elsewhere. H1 establishes she came out of the night with none.
            var wanting = run.Result.Decisions
                .Where(d => d.CharacterId == "elena")
                .SelectMany(d => d.Motives)
                .Where(m => m.Name == "avoid_exposure")
                .OrderByDescending(m => m.Urgency)
                .FirstOrDefault();

            Assert.IsNotNull(wanting, "she never wanted to be anywhere else");
            StringAssert.Contains("shame", wanting.Because);
            Assert.Greater(wanting.Urgency, 0.2,
                "it has to be strong enough to be worth calling a want");

            // And it is a passing thing, not a state she is left in. By the end
            // of the morning it has almost gone.
            Assert.Less(elena.Emotions.Intensity("shame"), 0.1,
                "shame from a look should fade, unlike the memory of it");

            var chain = run.Trace.Why(wanting.TraceId);
            TestContext.WriteLine(chain);

            var dir = Path.Combine(TestPaths.ProjectRoot, "Docs", "slices", "S1", "traces");
            Directory.CreateDirectory(dir);
            File.WriteAllText(
                Path.Combine(dir, "a-mother-made-to-feel-like-a-suspect.txt"),
                "Daniel watches Elena. She reads it as a slight, and wants to be out of the room.\n" +
                "Variant elena_fed_mara, seed 1. Nobody authored this.\n\n" + chain);

            // The chain reaches all the way back to something that happened.
            StringAssert.Contains("because", chain);
            StringAssert.Contains("Event", chain);
        }
    }
}
