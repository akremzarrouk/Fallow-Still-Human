namespace Fallow.Core.Model
{
    /// <summary>
    /// How evidence and feeling build up. Every increase closes part of the gap
    /// that is left rather than adding a flat amount, so the tenth reminder that
    /// someone let you down moves you far less than the first did, and nobody
    /// ever arrives at complete certainty.
    ///
    /// Beliefs, ledger strength and emotions all accumulate this way. One shape
    /// used everywhere means a trace reads the same wherever you look.
    /// </summary>
    public static class Accumulate
    {
        /// <summary>
        /// The most anyone is ever sure of anything. Held below one on purpose:
        /// a character who reached certainty could never be argued out of it.
        /// </summary>
        public const double Certainty = 0.995;

        /// <summary>
        /// Moves a 0..1 quantity by a fraction of the room it has left. Positive
        /// deltas move toward certainty, negative deltas eat into what is there.
        /// </summary>
        public static double Toward(double current, double delta)
        {
            var next = delta >= 0.0
                ? current + delta * (1.0 - current)
                : current + delta * current;

            if (next < 0.0) return 0.0;
            if (next > Certainty) return Certainty;
            return next;
        }

        /// <summary>
        /// Turns an unbounded amount of pushing into a feeling on a 0 to 1 scale.
        ///
        /// Feelings need a scale with a top, because "how strongly do you feel
        /// this" is a proportion and not a quantity of rules. But the pushing
        /// that produces one has no natural ceiling: a person can be touched in
        /// four places at once, and each of those weights can be large. Adding
        /// them and clamping would make everybody who is very upset equally
        /// upset, which is exactly the information worth keeping.
        ///
        /// So the total is squashed rather than cut off. The curve is strictly
        /// increasing, so the order of two feelings is never lost however hard
        /// either is pushed, and it never quite arrives at one, for the same
        /// reason certainty never does.
        /// </summary>
        public static double Saturate(double total)
        {
            if (total <= 0.0) return 0.0;
            var v = 1.0 - System.Math.Exp(-total);
            return v > Certainty ? Certainty : v;
        }

        /// <summary>
        /// Leaves a quantity alone up to the knee and bends it below one beyond.
        ///
        /// Written for urgency, after S1.1 found wants pinned at the ceiling in both
        /// worlds of a counterfactual, so that something which pushed them could
        /// not move them at all. Most wants live well below the top of the scale
        /// and must keep exactly the values they have, because every cost and
        /// every fit was written against those values. Only the part above the
        /// knee is compressed. The curve is continuous at the knee, has the same
        /// slope there, is strictly increasing, and never reaches one, so a want
        /// with more reasons behind it is always a little stronger than one with
        /// fewer, however strong both are.
        ///
        /// A knee at or above one switches it off.
        /// </summary>
        public static double Knee(double value, double knee)
        {
            if (knee >= 1.0 || value <= knee) return value;
            var room = 1.0 - knee;
            return knee + room * (1.0 - System.Math.Exp(-(value - knee) / room));
        }

        /// <summary>
        /// Two reasons to want the same thing, each closing part of the room the
        /// other left. The same curve as Toward, without the certainty cap, which
        /// belongs to belief: capping urgency there would pin strong wants at the
        /// ceiling again and undo the knee.
        /// </summary>
        public static double Combine(double a, double b)
        {
            // Inputs at or above one only arise when no knee is in use. Then the
            // old ceiling applies, so a rule set that never asked for a knee
            // behaves exactly as it did before there was one.
            if (a >= 1.0 || b >= 1.0) return Toward(a, b);

            if (a <= 0.0) return b < 0.0 ? 0.0 : b;
            if (b <= 0.0) return a;
            return a + b * (1.0 - a);
        }

        /// <summary>Holds a value inside 0..1 without the accumulation curve.</summary>
        public static double Clamp01(double v) => v < 0.0 ? 0.0 : v > 1.0 ? 1.0 : v;
    }
}
