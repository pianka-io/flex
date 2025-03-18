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
    
    public static void InjectAll(Process process, string flexFolder)
    {
        var python = Path.Combine(flexFolder, "python313_d.dll");
        var flexlib = Path.Combine(flexFolder, "flexlib.dll");
        
        EnableDebugPrivilege();
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
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            WorkingDirectory = Path.GetDirectoryName(fileName),
            CreateNoWindow = false,
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
        try
        {
            IntPtr handle = OpenProcess(0x001F0FFF | 0x0020 | 0x0008 | 0x0010, false, process.Id);
            if (handle == IntPtr.Zero)
                throw new Exception($"OpenProcess failed: {Marshal.GetLastWin32Error()}");

            IntPtr kernel32 = GetModuleHandle("kernel32.dll");
            if (kernel32 == IntPtr.Zero) 
                throw new Exception($"GetModuleHandle(kernel32.dll) failed: {Marshal.GetLastWin32Error()}");

            IntPtr loadLibraryAddr = GetProcAddress(kernel32, "LoadLibraryA");
            if (loadLibraryAddr == IntPtr.Zero) 
                throw new Exception($"GetProcAddress(LoadLibraryA) failed: {Marshal.GetLastWin32Error()}");

            IntPtr allocatedMemory = VirtualAllocEx(handle, IntPtr.Zero, (uint)path.Length + 1, 0x00001000 | 0x00002000, 0x40);
            if (allocatedMemory == IntPtr.Zero) 
                throw new Exception($"VirtualAllocEx failed: {Marshal.GetLastWin32Error()}");

            bool writeSuccess = WriteProcessMemory(handle, allocatedMemory, Encoding.ASCII.GetBytes(path), (uint)path.Length + 1, out _);
            if (!writeSuccess) 
                throw new Exception($"WriteProcessMemory failed: {Marshal.GetLastWin32Error()}");

            IntPtr thread = CreateRemoteThread(handle, IntPtr.Zero, 0, loadLibraryAddr, allocatedMemory, 0, IntPtr.Zero);
            if (thread == IntPtr.Zero) 
                throw new Exception($"CreateRemoteThread failed: {Marshal.GetLastWin32Error()}");
        }
        catch (Exception ex)
        {
            MessageBox.Show($@"Injection failed: {ex.Message}");
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