using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Input;
using System.Net.Http;
using System.Text.Json;
using System.IO.Compression;
using System.Windows.Media.Imaging;
using Microsoft.Win32;
using Microsoft.WindowsAPICodePack.Dialogs;

namespace launcher
{
    public partial class MainWindow : Window
    {
        private const string NewsUrl = "https://warnet2025-sanctuary.s3.us-east-2.amazonaws.com/news.json";
        private Settings _settings;
        private bool _diabloNeedsPatch = false;
        private List<string> _diabloPatchFiles = new();
        
        private int _backgroundIndex = 1;
        private readonly int _maxBackgrounds = 1;

        public MainWindow()
        {
            InitializeComponent();
            LoadNewsAsync();
            _settings = Settings.Load();
            
            MainButton.Content = _settings.IsInstalled ? "Play Diablo II" : "Install Diablo II";
            OptionsButton.Visibility = _settings.IsInstalled ? Visibility.Visible : Visibility.Collapsed;

            StartBackgroundRotation();
        }
        
        private async void Window_Loaded(object sender, RoutedEventArgs e)
        {
            await CheckForAndApplyUpdatesAsync("launcher", AppContext.BaseDirectory);
            if (_settings.IsInstalled)
                await CheckForAndApplyUpdatesAsync("diablo", _settings.InstallPath);
            StartUpdateTimer();
            DiabloVersionText.Text = $"Diablo II v{_settings.InstalledVersion}";
            LauncherVersionText.Text = $"Launcher v{_settings.LauncherVersion}";
        }
        
        private void StartUpdateTimer()
        {
            var timer = new System.Windows.Threading.DispatcherTimer
            {
                Interval = TimeSpan.FromMinutes(1)
            };

            timer.Tick += async (s, e) =>
            {
                await CheckForAndApplyUpdatesAsync("launcher", AppContext.BaseDirectory);

                if (_settings.IsInstalled)
                    await CheckForAndApplyUpdatesAsync("diablo", _settings.InstallPath);
            };

            timer.Start();
        }
        
        private BitmapImage LoadResourceImage(string fileName)
        {
            var uri = new Uri($"pack://application:,,,/Resources/{fileName}", UriKind.Absolute);
            return new BitmapImage(uri);
        }

        private void StartBackgroundRotation()
        {
            BackgroundImage.Source = LoadResourceImage("sanctuary1.png");
            
            var timer = new System.Windows.Threading.DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(15)
            };

            timer.Tick += (s, e) =>
            {
                _backgroundIndex++;
                if (_backgroundIndex > _maxBackgrounds)
                    _backgroundIndex = 1;

                var nextImage = LoadResourceImage($"sanctuary{_backgroundIndex}.png");

                PreviousBackgroundImage.Source = BackgroundImage.Source;
                BackgroundImage.Source = nextImage;

                var fadeOut = new System.Windows.Media.Animation.DoubleAnimation(1, 0, TimeSpan.FromSeconds(1));
                var fadeIn = new System.Windows.Media.Animation.DoubleAnimation(0, 1, TimeSpan.FromSeconds(1));

                PreviousBackgroundImage.BeginAnimation(UIElement.OpacityProperty, fadeOut);
                BackgroundImage.BeginAnimation(UIElement.OpacityProperty, fadeIn);
            };

            // timer.Start();
        }
        
        private async Task DownloadAndExtractZipAsync(string url, string extractTo, int index, int total)
        {
            string fileName = Path.GetFileName(new Uri(url).AbsolutePath);
            string tempPath = Path.Combine(Path.GetTempPath(), fileName);

            InstallStatusText.Text = $"Preparing {index}/{total}...";
            InstallStatusText.Visibility = Visibility.Visible;
            InstallProgressBar.Visibility = Visibility.Visible;
            InstallProgressBar.Value = 0;
            InstallProgressBar.Width = MainButton.ActualWidth;
            InstallStatusText.Width = MainButton.ActualWidth;
            MainButton.IsEnabled = false;

            if (!File.Exists(tempPath))
            {
                InstallStatusText.Text = $"Downloading {index}/{total}...";

                using var http = new HttpClient();
                using var response = await http.GetAsync(url, HttpCompletionOption.ResponseHeadersRead);
                response.EnsureSuccessStatusCode();

                var totalBytes = response.Content.Headers.ContentLength ?? -1L;
                var canReportProgress = totalBytes > 0;

                using (var inputStream = await response.Content.ReadAsStreamAsync())
                using (var fileStream = new FileStream(tempPath, FileMode.Create, FileAccess.Write, FileShare.None))
                {
                    var buffer = new byte[81920];
                    long totalRead = 0;
                    int bytesRead;

                    while ((bytesRead = await inputStream.ReadAsync(buffer, 0, buffer.Length)) > 0)
                    {
                        await fileStream.WriteAsync(buffer, 0, bytesRead);
                        totalRead += bytesRead;

                        if (canReportProgress)
                        {
                            double progress = (double)totalRead / totalBytes * 100;
                            InstallProgressBar.Value = progress;
                        }
                    }
                }
            }

            InstallStatusText.Text = $"Extracting {index}/{total}...";
            Directory.CreateDirectory(extractTo);
            ZipFile.ExtractToDirectory(tempPath, extractTo, overwriteFiles: true);
        }
        
        private async void LoadNewsAsync()
        {
            try
            {
                using var http = new HttpClient();
                var json = await http.GetStringAsync($"{NewsUrl}?ts={DateTimeOffset.UtcNow.ToUnixTimeSeconds()}");
                var items = JsonSerializer.Deserialize<List<NewsItem>>(json, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

                NewsList.ItemsSource = items;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Failed to load news.\n" + ex.Message);
            }
        }
        
        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            DragMove();
        }

        private async void MainButton_Click(object sender, RoutedEventArgs e)
        {
            if (!_settings.IsInstalled)
            {
                var dialog = new CommonOpenFileDialog
                {
                    IsFolderPicker = true,
                    Title = "Choose a folder to install Diablo II"
                };

                if (dialog.ShowDialog() != CommonFileDialogResult.Ok)
                    return;

                string selectedPath = dialog.FileName;
                string installDir = Path.Combine(selectedPath, "Diablo II");

                try
                {
                    await DownloadAndExtractZipAsync(
                        $"https://warnet2025-sanctuary.s3.us-east-2.amazonaws.com/diablo2.zip?ts={DateTimeOffset.UtcNow.ToUnixTimeSeconds()}",
                        installDir,
                        1,
                        2
                    );
                    await DownloadAndExtractZipAsync(
                        $"https://warnet2025-sanctuary.s3.us-east-2.amazonaws.com/Python3.zip?ts={DateTimeOffset.UtcNow.ToUnixTimeSeconds()}",
                        Path.Combine(installDir, "Python3"),
                        2,
                        2
                    );
                    SetRegistryKeys();
                    
                    await CheckForAndApplyUpdatesAsync("diablo", installDir);
                    
                    _settings.IsInstalled = true;
                    _settings.InstallPath = installDir;
                    _settings.LauncherVersion = new Settings().LauncherVersion;
                    _settings.InstalledVersion = new Settings().InstalledVersion;
                    Settings.Save(_settings);
                    
                    MainButton.Content = "Play Diablo II";
                    OptionsButton.Visibility = _settings.IsInstalled ? Visibility.Visible : Visibility.Collapsed;
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Installation failed:\n{ex.Message}");
                }
                finally
                {
                    InstallProgressBar.Visibility = Visibility.Collapsed;
                    InstallStatusText.Visibility = Visibility.Collapsed;
                    MainButton.IsEnabled = true;
                }
            }
            else
            {
                if (_diabloNeedsPatch)
                {
                    if (AnyFilesLocked(_settings.InstallPath, _diabloPatchFiles))
                    {
                        MessageBox.Show("Please close Diablo II before patching!");
                    }
                    await CheckForAndApplyUpdatesAsync("diablo", _settings.InstallPath);
                    if (!_diabloNeedsPatch)
                        MainButton.Content = "Play Diablo II";
                    return;
                }
                LaunchGame();
            }
        }

        private void RunInjector(int pid, string dll)
        {
            var injectorPath = Path.Combine(_settings.InstallPath, "injector.exe");
            var injectorInfo = new ProcessStartInfo
            {
                FileName = injectorPath,
                Arguments = $"{pid} \"{dll}\"",
                UseShellExecute = true,
                Verb = "runas", // triggers UAC prompt for admin
                WorkingDirectory = _settings.InstallPath
            };

            Process.Start(injectorInfo);
        }
        
        private void LaunchGame()
        {
            var gamePath = Path.Combine(_settings.InstallPath, "Game.exe");
            if (!File.Exists(gamePath))
                return;

            var startInfo = new ProcessStartInfo(gamePath)
            {
                Arguments = _settings.CommandLineArguments,
                UseShellExecute = false,
                WorkingDirectory = _settings.InstallPath,
            };

            var process = new Process { StartInfo = startInfo };
            process = Kernel32.StartSuspended(process, startInfo);
            Kernel32.Resume(process);
            process.WaitForInputIdle();

            var pid = process.Id;
            var sgD2FreeResDll = Path.Combine(_settings.InstallPath, "SGD2FreeRes.dll");
            var pythonDll = Path.Combine(_settings.InstallPath, "Python3", "python313.dll");
            var flexlibDll = Path.Combine(_settings.InstallPath, "flexlib.dll");
            
            RunInjector(pid, sgD2FreeResDll);
            Thread.Sleep(100);
            RunInjector(pid, pythonDll);
            Thread.Sleep(100);
            RunInjector(pid, flexlibDll);
        }

        private void ShowContextMenu_Click(object sender, RoutedEventArgs e)
        {
            OptionsPopup.IsOpen = true;
        }

        private void Uninstall_Click(object sender, RoutedEventArgs e)
        {
            // Optional: confirm uninstall
            var result = MessageBox.Show("Are you sure you want to uninstall Diablo II?", "Confirm Uninstall", MessageBoxButton.YesNo);
            if (result != MessageBoxResult.Yes)
                return;

            try
            {
                if (Directory.Exists(_settings.InstallPath))
                    Directory.Delete(_settings.InstallPath, recursive: true);

                _settings.IsInstalled = false;
                _settings.InstallPath = null;
                _settings.InstalledVersion = null;
                Settings.Save(_settings);

                MainButton.Content = "Install Diablo II";
                OptionsButton.Visibility = _settings.IsInstalled ? Visibility.Visible : Visibility.Collapsed;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Uninstall failed:\n{ex.Message}");
            }
        }
        
        private void SetRegistryKeys()
        {
            const string keyPath = @"Software\Battle.net\Configuration";
            const string valueName = "Diablo II Battle.net gateways";

            using (var key = Registry.CurrentUser.OpenSubKey(keyPath, writable: true) ??
                             Registry.CurrentUser.CreateSubKey(keyPath, writable: true))
            {
                if (key.GetValue(valueName) == null)
                {
                    byte[] gatewayBytes = new byte[]
                    {
                        0x31, 0x00, 0x30, 0x00, 0x30, 0x00, 0x32, 0x00, 0x00, 0x00,
                        0x30, 0x00, 0x31, 0x00, 0x00, 0x00,
                        0x67, 0x00, 0x61, 0x00, 0x6d, 0x00, 0x65, 0x00, 0x2e, 0x00,
                        0x77, 0x00, 0x61, 0x00, 0x72, 0x00, 0x2e, 0x00, 0x70, 0x00,
                        0x69, 0x00, 0x61, 0x00, 0x6e, 0x00, 0x6b, 0x00, 0x61, 0x00,
                        0x2e, 0x00, 0x69, 0x00, 0x6f, 0x00, 0x00, 0x00,
                        0x36, 0x00, 0x00, 0x00,
                        0x53, 0x00, 0x61, 0x00, 0x6e, 0x00, 0x63, 0x00, 0x74, 0x00,
                        0x75, 0x00, 0x61, 0x00, 0x72, 0x00, 0x79, 0x00, 0x00, 0x00,
                        0x00, 0x00
                    };

                    key.SetValue(valueName, gatewayBytes, RegistryValueKind.Binary);
                }
            }
        }
        
        private void Exit_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }
        
        private void Minimize_Click(object sender, RoutedEventArgs e)
        {
            WindowState = WindowState.Minimized;
        }
        
        private bool IsFileLocked(string path)
        {
            try
            {
                using var stream = new FileStream(path, FileMode.Open, FileAccess.ReadWrite, FileShare.None);
                return false;
            }
            catch (IOException)
            {
                return true;
            }
        }
        
        private bool AnyFilesLocked(string installDir, List<string> files)
        {
            foreach (var file in files)
            {
                var targetPath = Path.Combine(installDir, file);
                if (File.Exists(targetPath) && IsFileLocked(targetPath))
                    return true;
            }
            return false;
        }
        
        private async Task CheckForAndApplyUpdatesAsync(string type, string installDir)
        {
            try
            {
                string baseUrl = "https://warnet2025-sanctuary.s3.us-east-2.amazonaws.com/";
                string versionFile = type == "diablo" ? "version.txt" : "version_launcher.txt";
                string currentVersion = type == "diablo" ? _settings.InstalledVersion : _settings.LauncherVersion;

                using var http = new HttpClient();
                string remoteVersion =
                    (await http.GetStringAsync(
                        $"{baseUrl}{versionFile}?ts={DateTimeOffset.UtcNow.ToUnixTimeSeconds()}")).Trim();

                if (remoteVersion == currentVersion)
                    return;
                
                string listUrl =
                    $"{baseUrl}{type}/{remoteVersion}/filelist.json?ts={DateTimeOffset.UtcNow.ToUnixTimeSeconds()}";
                var fileListJson = await http.GetStringAsync(listUrl);
                var files = JsonSerializer.Deserialize<List<string>>(fileListJson);

                if (type == "diablo")
                {
                    if (AnyFilesLocked(installDir, files))
                    {
                        _diabloNeedsPatch = true;
                        _diabloPatchFiles = files;
                        Dispatcher.Invoke(() => MainButton.Content = "Patch Diablo II");
                        return;
                    }
                    _diabloNeedsPatch = false;
                }

                InstallStatusText.Visibility = Visibility.Visible;
                InstallProgressBar.Visibility = Visibility.Visible;
                InstallProgressBar.Value = 0;
                InstallProgressBar.Maximum = files.Count;
                InstallProgressBar.Width = MainButton.ActualWidth;
                InstallStatusText.Width = MainButton.ActualWidth;
                OptionsButton.Margin = new Thickness(MainButton.ActualWidth, 0, 0, 0);
                MainButton.IsEnabled = false;

                string patchDir = type == "launcher"
                    ? Path.Combine(Path.GetTempPath(), $"{type}_update")
                    : installDir;
                Directory.CreateDirectory(patchDir);

                for (int i = 0; i < files.Count; i++)
                {
                    string file = files[i];
                    string url = $"{baseUrl}{type}/{remoteVersion}/{file}";
                    string targetPath = Path.Combine(patchDir, file);

                    Directory.CreateDirectory(Path.GetDirectoryName(targetPath)!);

                    InstallStatusText.Text = $"Patching {i + 1}/{files.Count}...";
                    var fileBytes = await http.GetByteArrayAsync(url);
                    await File.WriteAllBytesAsync(targetPath, fileBytes);

                    InstallProgressBar.Value = i + 1;
                }

                if (type == "diablo")
                    _settings.InstalledVersion = remoteVersion;
                else
                    _settings.LauncherVersion = remoteVersion;

                Settings.Save(_settings);
                InstallProgressBar.Visibility = Visibility.Collapsed;
                InstallStatusText.Visibility = Visibility.Collapsed;
                MainButton.IsEnabled = true;

                if (type == "launcher")
                {
                    string launcherExe = Process.GetCurrentProcess().MainModule.FileName;
                    string launcherDir = AppContext.BaseDirectory.TrimEnd('\\');
                    string batchPath = Path.Combine(Path.GetTempPath(), "launcher_update.bat");

                    string batch = $@"
                        @echo off
                        timeout /t 1 /nobreak > nul
                        xcopy /E /Y /I ""{patchDir}"" ""{launcherDir}""
                        start """" ""{launcherExe}""
                        del ""%~f0""
                    ";

                    File.WriteAllText(batchPath, batch);

                    Process.Start(new ProcessStartInfo
                    {
                        FileName = batchPath,
                        UseShellExecute = true,
                        CreateNoWindow = true
                    });

                    Environment.Exit(0);
                }
            }
            catch (HttpRequestException e)
            {
                // ignore
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Update failed for {type}: {ex}");
            }
            Dispatcher.Invoke(() =>
            {
                DiabloVersionText.Text = $"Diablo II v{_settings.InstalledVersion}";
                LauncherVersionText.Text = $"Launcher v{_settings.LauncherVersion}";
            });
        }
    }
}