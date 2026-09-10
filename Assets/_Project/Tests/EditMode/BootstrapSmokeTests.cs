using NUnit.Framework;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// Temporary bootstrap gate: proves the EditMode test loop runs headlessly.
    /// Deleted once the first real Core test exists.
    /// </summary>
    public class BootstrapSmokeTests
    {
        [Test]
        public void TestHarnessRuns()
        {
            Assert.AreEqual(2, 1 + 1);
        }
    }
}
