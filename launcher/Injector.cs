using System.Diagnostics;
using System.Runtime.ConstrainedExecution;
using System.Runtime.InteropServices;
using System.Security;
using System.Text;
using launcher;

public static class Injector
{
    public static Process Launch(string diablo2Folder, string flexFolder, string arguments)
    {
        Kernel32.SetErrorMode(Kernel32.ErrorModes.SEM_NOGPFAULTERRORBOX);
        PrepareFlex(diablo2Folder, flexFolder);
        
        var python = Path.Combine(diablo2Folder, "Python3", "python313.dll");
        var flexlib = Path.Combine(flexFolder, "flexlib.dll");
        
        EnableDebugPrivilege();

        var game = Path.Combine(diablo2Folder, "Game.exe");
        ProcessStartInfo startInfo = new ProcessStartInfo(game)
        {
            Arguments = arguments,
            UseShellExecute = false,
            WorkingDirectory = Path.GetDirectoryName(game),
        };
        var process = new Process
        {
            StartInfo = startInfo
        };
        process = Kernel32.StartSuspended(process, startInfo);
        Kernel32.Resume(process);
        process.WaitForInputIdle();
        Kernel32.LoadRemoteLibrary(process, python);
        Kernel32.LoadRemoteLibrary(process, flexlib);
        return process;
    }

    private static void PrepareFlex(string diablo2Folder, string flexFolder)
    {
        string[] folders = { "resources", "scripts" };

        if (!Directory.Exists(Path.Combine(diablo2Folder, "Python3")))
        {
            CopyDirectory(Path.Combine(flexFolder, "Python3"), Path.Combine(diablo2Folder, "Python3"));
        }
        
        foreach (string folder in folders)
        {
            string targetPath = Path.Combine(diablo2Folder, folder);
            string sourcePath = Path.Combine(flexFolder, folder);

            if (Directory.Exists(targetPath))
            {
                try
                {
                    Directory.Delete(targetPath, true);
                }
                catch (Exception ex)
                {
                    MessageBox.Show(@$"Failed to delete {targetPath}: {ex.Message}");
                }
            }

            if (Directory.Exists(sourcePath))
            {
                CopyDirectory(sourcePath, targetPath);
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

    [DllImport("advapi32.dll", SetLastError = true)]
    static extern bool AdjustTokenPrivileges(IntPtr TokenHandle, bool DisableAllPrivileges,
        ref TOKEN_PRIVILEGES NewState, int BufferLength, IntPtr PreviousState, IntPtr ReturnLength);

    [DllImport("advapi32.dll", SetLastError = true)]
    static extern bool LookupPrivilegeValue(string lpSystemName, string lpName, ref LUID lpLuid);

    [DllImport("kernel32.dll", ExactSpelling = true)]
    static extern IntPtr GetCurrentProcess();

    [DllImport("advapi32.dll", SetLastError = true)]
    static extern bool OpenProcessToken(IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);

    const int TOKEN_ADJUST_PRIVILEGES = 0x20;
    const int TOKEN_QUERY = 0x8;
    const string SE_DEBUG_NAME = "SeDebugPrivilege";
    const int SE_PRIVILEGE_ENABLED = 0x2;

    [StructLayout(LayoutKind.Sequential)]
    struct TOKEN_PRIVILEGES
    {
        public int PrivilegeCount;
        public LUID Luid;
        public int Attributes;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct LUID
    {
        public uint LowPart;
        public int HighPart;
    }

    static void EnableDebugPrivilege()
    {
        IntPtr hToken;
        if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, out hToken))
        {
            MessageBox.Show("OpenProcessToken failed.");
            return;
        }

        TOKEN_PRIVILEGES tkp;
        tkp.PrivilegeCount = 1;
        tkp.Luid = new LUID();
        if (!LookupPrivilegeValue(null, SE_DEBUG_NAME, ref tkp.Luid))
        {
            MessageBox.Show("LookupPrivilegeValue failed.");
            return;
        }

        tkp.Attributes = SE_PRIVILEGE_ENABLED;

        if (!AdjustTokenPrivileges(hToken, false, ref tkp, 0, IntPtr.Zero, IntPtr.Zero))
        {
            MessageBox.Show("AdjustTokenPrivileges failed.");
        }
    }
}