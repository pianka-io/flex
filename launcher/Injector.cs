using System.Diagnostics;
using System.Runtime.ConstrainedExecution;
using System.Runtime.InteropServices;
using System.Security;
using System.Text;

public static class Injector
{
    public static Process Launch(string diablo2Folder, string flexFolder, string arguments)
    {
        PrepareFlex(diablo2Folder, flexFolder);
        var process = StartProcessWithCapture(Path.Combine(diablo2Folder, "Game.exe"), arguments);
        Thread.Sleep(2000);
        InjectAll(process, flexFolder);
        process.WaitForInputIdle();
        return process;
    }

    private static void PrepareFlex(string diablo2Folder, string flexFolder)
    {
        string[] folders = { "resources", "scripts" };

        foreach (string folder in folders)
        {
            string targetPath = Path.Combine(diablo2Folder, folder);
            string sourcePath = Path.Combine(flexFolder, folder);

            if (Directory.Exists(targetPath))
            {
                try
                {
                    Directory.Delete(targetPath, true);
                    Console.WriteLine(@$"Deleted: {targetPath}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine(@$"Failed to delete {targetPath}: {ex.Message}");
                }
            }

            if (Directory.Exists(sourcePath))
            {
                CopyDirectory(sourcePath, targetPath);
                Console.WriteLine(@$"Copied: {sourcePath} → {targetPath}");
            }
            else
            {
                Console.WriteLine(@$"Skipping '{folder}' - does not exist in {flexFolder}");
            }
        }
    }

    private static void CopyDirectory(string sourceDir, string destinationDir)
    {
        Directory.CreateDirectory(destinationDir);

        foreach (string dir in Directory.GetDirectories(sourceDir, "*", SearchOption.AllDirectories))
        {
            string newDir = dir.Replace(sourceDir, destinationDir);
            Directory.CreateDirectory(newDir);
        }

        foreach (string file in Directory.GetFiles(sourceDir, "*", SearchOption.AllDirectories))
        {
            string newFile = file.Replace(sourceDir, destinationDir);
            File.Copy(file, newFile, true);
        }
    }
    
    public static void InjectAll(Process process, string flexFolder)
    {
        var python = Path.Combine(flexFolder, "python313_d.dll");
        var flexlib = Path.Combine(flexFolder, "flexlib.dll");
        
        Inject(process, python);
        Inject(process, flexlib);
    }
    
    public static Process StartProcessWithCapture(string fileName, string arguments)
    {
        ProcessStartInfo startInfo = new ProcessStartInfo
        {
            FileName = fileName,
            Arguments = arguments,
            UseShellExecute = false,
            WorkingDirectory = Path.GetDirectoryName(fileName),
            CreateNoWindow = false,
            RedirectStandardOutput = true
        };

        Process process = new Process { StartInfo = startInfo };
        process.Start();
        return process;
    }
    
    [DllImport("kernel32.dll")]
    public static extern IntPtr OpenProcess(int dwDesiredAccess, bool bInheritHandle, int dwProcessId);

    [DllImport("kernel32.dll", CharSet = CharSet.Auto)]
    public static extern IntPtr GetModuleHandle(string lpModuleName);

    [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
    static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

    [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
    static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress,
        uint dwSize, uint flAllocationType, uint flProtect);

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out UIntPtr lpNumberOfBytesWritten);

    [DllImport("kernel32.dll")]
    static extern IntPtr CreateRemoteThread(IntPtr hProcess,
        IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);

    [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
    static extern bool VirtualFreeEx(IntPtr hProcess, IntPtr lpAddress, int dwSize, uint dwFreeType);

    [DllImport("kernel32.dll", SetLastError = true)]
    [ReliabilityContract(Consistency.WillNotCorruptState, Cer.Success)]
    [SuppressUnmanagedCodeSecurity]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool CloseHandle(IntPtr hObject);

    public static void Inject(Process process, string path)
    {
        string dll = path;
        Process targetProcess = process;
        IntPtr handle = OpenProcess(0x001F0FFF, false, targetProcess.Id);
        IntPtr libraryAddress = GetProcAddress(GetModuleHandle("kernel32.dll"), "LoadLibraryA");
        IntPtr allocatedMemory = VirtualAllocEx(handle, IntPtr.Zero, (uint)dll.Length + 1, 0x00001000, 4);
        Console.WriteLine("Loaded " + path);
        WriteProcessMemory(handle, allocatedMemory, Encoding.Default.GetBytes(dll), (uint)dll.Length + 1, out _);
        CreateRemoteThread(handle, IntPtr.Zero, 0, libraryAddress, allocatedMemory, 0, IntPtr.Zero);
    }
}