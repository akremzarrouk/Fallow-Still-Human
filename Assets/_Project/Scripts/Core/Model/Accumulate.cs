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

        /// <summary>Holds a value inside 0..1 without the accumulation curve.</summary>
        public static double Clamp01(double v) => v < 0.0 ? 0.0 : v > 1.0 ? 1.0 : v;
    }
}
