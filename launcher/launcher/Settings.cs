using System;
using System.IO;
using System.Text.Json;

namespace launcher
{
    public class Settings
    {
        public bool IsInstalled { get; set; } = false;
        public string InstalledVersion { get; set; } = "0.0.0";
        public string LauncherVersion { get; set; } = "0.0.1";
        public string InstallPath { get; set; } = "";

        private static readonly string FilePath = Path.Combine(AppContext.BaseDirectory, "settings.json");

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
            var json = JsonSerializer.Serialize(settings, new JsonSerializerOptions
            {
                WriteIndented = true
            });

            File.WriteAllText(FilePath, json);
        }
    }
}