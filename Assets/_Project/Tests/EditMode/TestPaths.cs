using System.IO;

namespace Fallow.Tests.Core
{
    /// <summary>
    /// Locates the on-disk data folder for tests. Fallow.Core takes paths as
    /// arguments and never asks Unity where anything lives, so this is the only
    /// place that knows.
    /// </summary>
    public static class TestPaths
    {
        public static string DataRoot =>
            Path.Combine(UnityEngine.Application.dataPath, "_Project", "Data");

        public static string Minds => Path.Combine(DataRoot, "Minds");
        public static string Rules => Path.Combine(DataRoot, "Rules");
        public static string Scenario => Path.Combine(DataRoot, "Scenario");
        public static string Tests => Path.Combine(DataRoot, "Tests");

        public static string ProjectRoot =>
            Directory.GetParent(UnityEngine.Application.dataPath).FullName;

        public static string CoreSources =>
            Path.Combine(UnityEngine.Application.dataPath, "_Project", "Scripts", "Core");
    }
}
