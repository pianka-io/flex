using System;
using System.IO;
using System.Text.Json;

namespace launcher
{
    public class Settings
    {
        public bool IsInstalled { get; set; } = false;
        public string InstalledVersion { get; set; } = "0.0.0";
        public string LauncherVersion { get; set; } = "0.0.6";
        public string InstallPath { get; set; } = "";
        public string CommandLineArguments { get; set; } = "-3dfx";
        
        private static readonly string FilePath = Path.Combine(
            Path.GetDirectoryName(System.Diagnostics.Process.GetCurrentProcess().MainModule!.FileName)!,
            "settings.json"
        );

        public static Settings Load()
        {
            try
            {
                if (File.Exists(FilePath))
                {
                    var json = File.ReadAllText(FilePath);
                    return JsonSerializer.Deserialize<Settings>(json, new JsonSerializerOptions
                    {
                        PropertyNameCaseInsensitive = true
                    }) ?? new Settings();
                }
            }
            catch
            {
                // ignore and fall back to defaults
            }

            var defaults = new Settings();
            Save(defaults);
            return defaults;
        }

        public static void Save(Settings settings)
        {
            var dir = Path.GetDirectoryName(FilePath)!;
            Directory.CreateDirectory(dir);

            var json = JsonSerializer.Serialize(settings, new JsonSerializerOptions
            {
                WriteIndented = true
            });

            File.WriteAllText(FilePath, json);
        }
    }
}