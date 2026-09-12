namespace Fallow.Core.Model
{
    /// <summary>
    /// A small deterministic random source, carried explicitly rather than taken
    /// from a global.
    ///
    /// The simulation uses randomness for exactly one thing: choosing between
    /// actions a character has no real preference between. That makes
    /// reproducibility a requirement rather than a convenience, so this is
    /// written out by hand instead of using the platform generator, whose
    /// sequence is not guaranteed to be the same on another runtime.
    ///
    /// splitmix64, which is standard, fast and well distributed.
    /// </summary>
    public sealed class Rng
    {
        ulong _state;

        public ulong Seed { get; }

        public Rng(ulong seed)
        {
            Seed = seed;
            _state = seed;
        }

        /// <summary>A fresh generator for a named purpose, so one stream cannot shift another.</summary>
        public Rng Fork(string purpose)
        {
            ulong h = 1469598103934665603UL;
            foreach (var c in purpose ?? "")
            {
                h ^= c;
                h *= 1099511628211UL;
            }
            return new Rng(Seed ^ h);
        }

        public ulong NextULong()
        {
            _state += 0x9E3779B97F4A7C15UL;
            var z = _state;
            z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
            z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
            return z ^ (z >> 31);
        }

        /// <summary>A number in [0,1).</summary>
        public double NextDouble() => (NextULong() >> 11) * (1.0 / 9007199254740992.0);

        /// <summary>An index in [0,count).</summary>
        public int NextIndex(int count) => count <= 1 ? 0 : (int)(NextULong() % (ulong)count);
    }
}
