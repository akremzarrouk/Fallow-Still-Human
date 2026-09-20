using System.Linq;
using Fallow.Core.Model;
using Fallow.Core.Rules;
using Fallow.Core.Sim;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// The two decision architectures the slice can run, on the same content.
    ///
    /// Since the decision-sensitivity experiment the shipped data is the primary
    /// experimental baseline: traits and values as dispositions (S1.5 Model B,
    /// `dispositions: respond`), a walk credited to a want only when its end
    /// could be worth doing (S1.6 M2, `means: end`), and the scripted events of
    /// the lived day carrying the minute they happened (S1.6 M1, `minute: 0`).
    ///
    /// Model A is what the data shipped before that, kept as a comparison: traits
    /// and values as standing wants, walks credited to their want whatever waits
    /// at the end, and those events carrying no minute, so that their memories
    /// never age. Every test written before the change measured Model A, and
    /// selects it here, so that what it says it measured is still what it
    /// measures.
    /// </summary>
    internal static class Baselines
    {
        /// <summary>The shipped content: Model B with both S1.6 fixes.</summary>
        internal static Scenario001Content Primary() => Scenario001Content.Load(TestPaths.DataRoot);

        /// <summary>Model A, as the data shipped it before the change.</summary>
        internal static Scenario001Content ModelA() => ModelA(Primary());

        /// <summary>
        /// Model A on any content: standing wants, walks credited to their want,
        /// and the lived day's scripted events untimed. Nothing else is touched.
        /// </summary>
        internal static Scenario001Content ModelA(Scenario001Content c)
            => Untimed(S15.Deciding(c, d =>
            {
                d.Dispositions = DispositionMode.Standing;
                d.Means = MeansMode.Want;
            }));

        /// <summary>
        /// The inverse of <see cref="S16.Timed"/>: every scripted event of the
        /// lived day (the backstory's events on the morning's day, and the
        /// opening) carries no minute, as the data had it before S1.6's M1 was
        /// shipped. The night is not on the lived day and is not touched.
        /// </summary>
        internal static Scenario001Content Untimed(Scenario001Content c)
        {
            var day = c.Morning.Day;
            WorldEvent At(WorldEvent e, int minute) => new WorldEvent(
                e.Id, e.Day, e.Order, e.Kind, e.ActorId, e.TargetId, e.Act, e.Action, e.Topic, e.Tone,
                e.Directness, e.Valence, e.Intent, e.Summary, e.Witnesses, e.Overhearers,
                e.LedgerEffects, e.BeliefEffects, minute);
            WorldEvent Clear(WorldEvent e) => e != null && e.Day == day && e.Minute >= 0 ? At(e, -1) : e;

            var backstory = new ScenarioScript(
                c.Backstory.Id, c.Backstory.Description, c.Backstory.CharacterIds,
                c.Backstory.Events.Select(Clear).ToList());
            var m = c.Morning;
            var morning = new MorningScenario(
                m.Id, m.Description, m.Day, m.Minutes, m.House, m.Portions, m.StartRooms, m.StartHunger,
                Clear(m.Opening), m.Variants, m.HeldOutVariants);
            return new Scenario001Content(c.Vocabulary, c.Cast, backstory, morning, c.Rules);
        }
    }
}
