using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

namespace launcher;

// Token: 0x02000013 RID: 19
[Flags]
public enum PageAccessProtectionFlags
{
	// Token: 0x040000B1 RID: 177
	NoAccess = 1,
	// Token: 0x040000B2 RID: 178
	ReadOnly = 2,
	// Token: 0x040000B3 RID: 179
	ReadWrite = 4,
	// Token: 0x040000B4 RID: 180
	WriteCopy = 8,
	// Token: 0x040000B5 RID: 181
	Execute = 16,
	// Token: 0x040000B6 RID: 182
	ExecuteRead = 32,
	// Token: 0x040000B7 RID: 183
	ExecuteReadWrite = 64,
	// Token: 0x040000B8 RID: 184
	ExecuteWriteCopy = 128,
	// Token: 0x040000B9 RID: 185
	Guard = 256,
	// Token: 0x040000BA RID: 186
	NoCache = 512,
	// Token: 0x040000BB RID: 187
	WriteCombine = 1024
}

// Token: 0x02000011 RID: 17
[Flags]
public enum ProcessAccessFlags : uint
{
	// Token: 0x04000096 RID: 150
	All = 2035711U,
	// Token: 0x04000097 RID: 151
	Terminate = 1U,
	// Token: 0x04000098 RID: 152
	CreateThread = 2U,
	// Token: 0x04000099 RID: 153
	VMOperation = 8U,
	// Token: 0x0400009A RID: 154
	VMRead = 16U,
	// Token: 0x0400009B RID: 155
	VMWrite = 32U,
	// Token: 0x0400009C RID: 156
	DupHandle = 64U,
	// Token: 0x0400009D RID: 157
	SetInformation = 512U,
	// Token: 0x0400009E RID: 158
	QueryInformation = 1024U,
	// Token: 0x0400009F RID: 159
	Synchronize = 1048576U
}

// Token: 0x02000012 RID: 18
[Flags]
public enum AllocationType
{
	// Token: 0x040000A1 RID: 161
	WriteMatchFlagReset = 1,
	// Token: 0x040000A2 RID: 162
	Commit = 4096,
	// Token: 0x040000A3 RID: 163
	Reserve = 8192,
	// Token: 0x040000A4 RID: 164
	CommitOrReserve = 12288,
	// Token: 0x040000A5 RID: 165
	Decommit = 16384,
	// Token: 0x040000A6 RID: 166
	Release = 32768,
	// Token: 0x040000A7 RID: 167
	Free = 65536,
	// Token: 0x040000A8 RID: 168
	Public = 131072,
	// Token: 0x040000A9 RID: 169
	Mapped = 262144,
	// Token: 0x040000AA RID: 170
	Reset = 524288,
	// Token: 0x040000AB RID: 171
	TopDown = 1048576,
	// Token: 0x040000AC RID: 172
	WriteWatch = 2097152,
	// Token: 0x040000AD RID: 173
	Physical = 4194304,
	// Token: 0x040000AE RID: 174
	SecImage = 16777216,
	// Token: 0x040000AF RID: 175
	Image = 16777216
}

// Token: 0x02000017 RID: 23
[Flags]
public enum LoadLibraryFlags : uint
{
	// Token: 0x040000DF RID: 223
	LoadAsDataFile = 2U,
	// Token: 0x040000E0 RID: 224
	DontResolveReferences = 1U,
	// Token: 0x040000E1 RID: 225
	LoadWithAlteredSeachPath = 8U,
	// Token: 0x040000E2 RID: 226
	IgnoreCodeAuthzLevel = 16U,
	// Token: 0x040000E3 RID: 227
	LoadAsExclusiveDataFile = 64U
}

// Token: 0x02000016 RID: 22
public enum ThreadAccessFlags : uint
{
	// Token: 0x040000D3 RID: 211
	Terminate = 1U,
	// Token: 0x040000D4 RID: 212
	SuspendResume,
	// Token: 0x040000D5 RID: 213
	GetContext = 8U,
	// Token: 0x040000D6 RID: 214
	SetContext = 16U,
	// Token: 0x040000D7 RID: 215
	SetInformation = 32U,
	// Token: 0x040000D8 RID: 216
	QueryInformation = 64U,
	// Token: 0x040000D9 RID: 217
	SetThreadToken = 128U,
	// Token: 0x040000DA RID: 218
	Impersonate = 256U,
	// Token: 0x040000DB RID: 219
	DirectImpersonate = 512U,
	// Token: 0x040000DC RID: 220
	SetLimitedInformation = 1024U,
	// Token: 0x040000DD RID: 221
	QueryLimitedInformation = 2048U
}

// Token: 0x02000014 RID: 20
[Flags]
public enum CreateThreadFlags
{
	// Token: 0x040000BD RID: 189
	RunImmediately = 0,
	// Token: 0x040000BE RID: 190
	CreateSuspended = 4,
	// Token: 0x040000BF RID: 191
	StackSizeParamIsAReservation = 65536,
	// Token: 0x040000C0 RID: 192
	UseNtCreateThreadEx = 8388608
}

// Token: 0x02000015 RID: 21
[Flags]
public enum ProcessCreationFlags : uint
{
	// Token: 0x040000C2 RID: 194
	BreakawayFromJob = 16777216U,
	// Token: 0x040000C3 RID: 195
	DefaultErrorMode = 67108864U,
	// Token: 0x040000C4 RID: 196
	NewConsole = 16U,
	// Token: 0x040000C5 RID: 197
	NewProcessGroup = 512U,
	// Token: 0x040000C6 RID: 198
	NoWindow = 134217728U,
	// Token: 0x040000C7 RID: 199
	ProtectedProcess = 262144U,
	// Token: 0x040000C8 RID: 200
	PreserveCodeAuthzLevel = 33554432U,
	// Token: 0x040000C9 RID: 201
	SeparateWowVdm = 2048U,
	// Token: 0x040000CA RID: 202
	SharedWowVdm = 4096U,
	// Token: 0x040000CB RID: 203
	Suspended = 4U,
	// Token: 0x040000CC RID: 204
	UnicodeEnvironment = 1024U,
	// Token: 0x040000CD RID: 205
	DebugOnlyThisProcess = 2U,
	// Token: 0x040000CE RID: 206
	DebugProcess = 1U,
	// Token: 0x040000CF RID: 207
	DetachedProcess = 8U,
	// Token: 0x040000D0 RID: 208
	ExtendedStartupInfo = 524288U,
	// Token: 0x040000D1 RID: 209
	InheritParentAffinity = 65536U
}

public static class Kernel32
{
	// Token: 0x06000042 RID: 66
	[DllImport("kernel32.dll")]
	public static extern Kernel32.ErrorModes SetErrorMode(Kernel32.ErrorModes uMode);

	// Token: 0x06000043 RID: 67
	[DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
	private static extern bool CreateProcess(string Application, string CommandLine, IntPtr ProcessAttributes, IntPtr ThreadAttributes, bool InheritHandles, uint CreationFlags, IntPtr Environment, string CurrentDirectory, ref Kernel32.StartupInfo StartupInfo, out Kernel32.ProcessInformation ProcessInformation);

	// Token: 0x06000044 RID: 68
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	private static extern uint SuspendThread(IntPtr hThread);

	// Token: 0x06000045 RID: 69
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	private static extern uint ResumeThread(IntPtr hThread);

	// Token: 0x06000046 RID: 70
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	[return: MarshalAs(UnmanagedType.Bool)]
	private static extern bool VirtualProtectEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, PageAccessProtectionFlags flags, out PageAccessProtectionFlags oldFlags);

	// Token: 0x06000047 RID: 71
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	private static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr baseAddress, [Out] byte[] buffer, uint size, out uint numBytesRead);

	// Token: 0x06000048 RID: 72
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	private static extern IntPtr OpenProcess(ProcessAccessFlags dwDesiredAccess, [MarshalAs(UnmanagedType.Bool)] bool bInheritHandle, uint dwProcessId);

	// Token: 0x06000049 RID: 73
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	private static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

	// Token: 0x0600004A RID: 74
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	private static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, AllocationType flAllocationType, PageAccessProtectionFlags flProtect);

	// Token: 0x0600004B RID: 75
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	[return: MarshalAs(UnmanagedType.Bool)]
	private static extern bool VirtualFreeEx(IntPtr hProcess, IntPtr lpAddress, int dwSize, AllocationType dwFreeType);

	// Token: 0x0600004C RID: 76
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	[return: MarshalAs(UnmanagedType.Bool)]
	private static extern bool CloseHandle(IntPtr hObject);

	// Token: 0x0600004D RID: 77
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	private static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out int lpNumberOfBytesWritten);

	// Token: 0x0600004E RID: 78
	[DllImport("kernel32.dll", SetLastError = true)]
	private static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

	// Token: 0x0600004F RID: 79
	[DllImport("kernel32.dll", SetLastError = true)]
	private static extern IntPtr GetModuleHandle(string lpModuleName);

	// Token: 0x06000050 RID: 80
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	private static extern uint WaitForSingleObject(IntPtr hHandle, uint dwMilliseconds);

	// Token: 0x06000051 RID: 81
	[DllImport("kernel32.dll", SetLastError = true)]
	private static extern IntPtr LoadLibraryEx(string lpFileName, IntPtr hFile, LoadLibraryFlags dwFlags);

	// Token: 0x06000052 RID: 82
	[DllImport("kernel32.dll", SetLastError = true)]
	private static extern IntPtr LoadLibrary(string library);

	// Token: 0x06000053 RID: 83
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	[return: MarshalAs(UnmanagedType.Bool)]
	private static extern bool FreeLibrary(IntPtr hHandle);

	// Token: 0x06000054 RID: 84
	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	private static extern IntPtr OpenThread(ThreadAccessFlags flags, bool bInheritHandle, uint threadId);

	// Token: 0x06000055 RID: 85
	[DllImport("user32.dll", SetLastError = true)]
	public static extern IntPtr SetParent(IntPtr hWndChild, IntPtr hWndNewParent);

	// Token: 0x06000056 RID: 86 RVA: 0x00002FC0 File Offset: 0x000011C0
	public static bool LoadRemoteLibrary(Process p, object module)
	{
		IntPtr intPtr = Kernel32.WriteObject(p, module);
		bool result = Kernel32.CallRemoteFunction(p, "kernel32.dll", "LoadLibraryW", intPtr);
		Kernel32.FreeObject(p, intPtr);
		return result;
	}

	// Token: 0x06000057 RID: 87 RVA: 0x00002FF0 File Offset: 0x000011F0
	public static bool UnloadRemoteLibrary(Process p, string module)
	{
		IntPtr intPtr = Kernel32.FindModuleHandle(p, module);
		IntPtr intPtr2 = Kernel32.WriteObject(p, intPtr);
		bool result = Kernel32.CallRemoteFunction(p, "kernel32.dll", "FreeLibrary", intPtr2);
		Kernel32.FreeObject(p, intPtr2);
		return result;
	}

	// Token: 0x06000058 RID: 88 RVA: 0x0000302A File Offset: 0x0000122A
	public static bool CallRemoteFunction(Process p, string module, string function, IntPtr param)
	{
		return Kernel32.CallRemoteFunction(p.Id, module, function, param);
	}

	// Token: 0x06000059 RID: 89 RVA: 0x0000303C File Offset: 0x0000123C
	public static bool CallRemoteFunction(int pid, string module, string function, IntPtr param)
	{
		IntPtr intPtr = Kernel32.LoadLibraryEx(module, LoadLibraryFlags.LoadAsDataFile);
		IntPtr procAddress = Kernel32.GetProcAddress(intPtr, function);
		if (intPtr == IntPtr.Zero || procAddress == IntPtr.Zero)
		{
			return false;
		}
		IntPtr intPtr2 = Kernel32.CreateRemoteThread(pid, procAddress, param, CreateThreadFlags.RunImmediately);
		if (intPtr2 != IntPtr.Zero)
		{
			Kernel32.WaitForSingleObject(intPtr2, uint.MaxValue);
		}
		return intPtr2 != IntPtr.Zero;
	}

	// Token: 0x0600005A RID: 90 RVA: 0x000030A0 File Offset: 0x000012A0
	public static bool ReadProcessMemory(Process p, IntPtr address, ref byte[] buffer)
	{
		IntPtr processHandle = Kernel32.GetProcessHandle(p, ProcessAccessFlags.VMRead);
		PageAccessProtectionFlags flags;
		if (!Kernel32.VirtualProtect(new IntPtr(p.Id), address, (uint)buffer.Length, PageAccessProtectionFlags.ExecuteReadWrite, out flags))
		{
			throw new Win32Exception(Marshal.GetLastWin32Error());
		}
		uint num;
		if (!Kernel32.ReadProcessMemory(processHandle, address, buffer, (uint)buffer.Length, out num))
		{
			throw new Win32Exception(Marshal.GetLastWin32Error());
		}
		PageAccessProtectionFlags pageAccessProtectionFlags;
		if (!Kernel32.VirtualProtect(new IntPtr(p.Id), address, (uint)buffer.Length, flags, out pageAccessProtectionFlags))
		{
			throw new Win32Exception(Marshal.GetLastWin32Error());
		}
		Kernel32.CloseProcessHandle(processHandle);
		return (ulong)num == (ulong)((long)buffer.Length);
	}

	// Token: 0x0600005B RID: 91 RVA: 0x0000312C File Offset: 0x0000132C
	public static IntPtr WriteObject(Process p, object data)
	{
		byte[] rawBytes = Kernel32.GetRawBytes(data);
		IntPtr intPtr = Kernel32.VirtualAlloc(p, IntPtr.Zero, (uint)rawBytes.Length, AllocationType.CommitOrReserve, PageAccessProtectionFlags.ReadWrite);
		Kernel32.WriteProcessMemory(p, intPtr, rawBytes);
		return intPtr;
	}

	// Token: 0x0600005C RID: 92 RVA: 0x0000315F File Offset: 0x0000135F
	public static void FreeObject(Process p, IntPtr address)
	{
		Kernel32.VirtualFree(p, address);
	}

	// Token: 0x0600005D RID: 93 RVA: 0x00003168 File Offset: 0x00001368
	public static IntPtr FindModuleHandle(Process p, string module)
	{
		foreach (object obj in p.Modules)
		{
			ProcessModule processModule = (ProcessModule)obj;
			if (Path.GetFileName(processModule.FileName).ToLowerInvariant() == Path.GetFileName(module).ToLowerInvariant())
			{
				return processModule.BaseAddress;
			}
		}
		return IntPtr.Zero;
	}

	// Token: 0x0600005E RID: 94 RVA: 0x000031EC File Offset: 0x000013EC
	public static IntPtr FindOffset(string moduleName, string function)
	{
		IntPtr intPtr = Kernel32.LoadLibraryEx(moduleName, LoadLibraryFlags.LoadAsDataFile);
		if (intPtr != IntPtr.Zero)
		{
			IntPtr procAddress = Kernel32.GetProcAddress(intPtr, function);
			Kernel32.FreeLibrary(intPtr);
			return (IntPtr)(procAddress.ToInt32() - intPtr.ToInt32());
		}
		return IntPtr.Zero;
	}

	// Token: 0x0600005F RID: 95 RVA: 0x00003238 File Offset: 0x00001438
	[DebuggerHidden]
	public static bool VirtualProtect(IntPtr pid, IntPtr address, uint size, PageAccessProtectionFlags flags, out PageAccessProtectionFlags oldFlags)
	{
		IntPtr processHandle = Kernel32.GetProcessHandle(pid, ProcessAccessFlags.VMOperation);
		bool result = Kernel32.VirtualProtectEx(processHandle, address, size, flags, out oldFlags);
		Kernel32.CloseHandle(processHandle);
		return result;
	}

	// Token: 0x06000060 RID: 96 RVA: 0x0000325F File Offset: 0x0000145F
	[DebuggerHidden]
	public static IntPtr GetProcessHandle(IntPtr pid, ProcessAccessFlags flags)
	{
		flags = ProcessAccessFlags.All;
		IntPtr intPtr = Kernel32.OpenProcess(flags, false, (uint)((int)pid));
		if (intPtr == IntPtr.Zero)
		{
			throw new Win32Exception(Marshal.GetLastWin32Error());
		}
		return intPtr;
	}

	// Token: 0x06000061 RID: 97 RVA: 0x00003286 File Offset: 0x00001486
	[DebuggerHidden]
	public static IntPtr LoadLibraryEx(string module, LoadLibraryFlags flags)
	{
		return Kernel32.LoadLibraryEx(module, IntPtr.Zero, flags);
	}

	// Token: 0x06000062 RID: 98 RVA: 0x00003294 File Offset: 0x00001494
	[DebuggerHidden]
	public static IntPtr GetProcessHandle(Process p, ProcessAccessFlags flags)
	{
		flags = ProcessAccessFlags.All;
		IntPtr intPtr = Kernel32.OpenProcess(flags, false, (uint)p.Id);
		if (intPtr == IntPtr.Zero)
		{
			throw new Win32Exception(Marshal.GetLastWin32Error());
		}
		return intPtr;
	}

	// Token: 0x06000063 RID: 99 RVA: 0x000032BB File Offset: 0x000014BB
	[DebuggerHidden]
	public static void CloseProcessHandle(IntPtr handle)
	{
		if (!Kernel32.CloseHandle(handle))
		{
			throw new Win32Exception(Marshal.GetLastWin32Error());
		}
	}

	// Token: 0x06000064 RID: 100 RVA: 0x000032D0 File Offset: 0x000014D0
	[DebuggerHidden]
	public static IntPtr VirtualAlloc(Process p, IntPtr address, uint size, AllocationType type, PageAccessProtectionFlags flags)
	{
		IntPtr processHandle = Kernel32.GetProcessHandle(p, ProcessAccessFlags.VMOperation);
		IntPtr intPtr = Kernel32.VirtualAllocEx(processHandle, address, size, type, flags);
		if (intPtr == IntPtr.Zero)
		{
			throw new Win32Exception(Marshal.GetLastWin32Error());
		}
		Kernel32.CloseProcessHandle(processHandle);
		return intPtr;
	}

	// Token: 0x06000065 RID: 101 RVA: 0x00003310 File Offset: 0x00001510
	[DebuggerHidden]
	public static void VirtualFree(Process p, IntPtr address)
	{
		IntPtr processHandle = Kernel32.GetProcessHandle(p, ProcessAccessFlags.VMOperation);
		bool flag = Kernel32.VirtualFreeEx(processHandle, address, 0, AllocationType.Release);
		Kernel32.CloseProcessHandle(processHandle);
		if (!flag)
		{
			throw new Win32Exception(Marshal.GetLastWin32Error());
		}
	}

	// Token: 0x06000066 RID: 102 RVA: 0x00003348 File Offset: 0x00001548
	[DebuggerHidden]
	public static int WriteProcessMemory(Process p, IntPtr address, byte[] buffer)
	{
		IntPtr processHandle = Kernel32.GetProcessHandle(p, ProcessAccessFlags.VMOperation | ProcessAccessFlags.VMWrite);
		int result;
		if (!Kernel32.WriteProcessMemory(processHandle, address, buffer, (uint)buffer.Length, out result))
		{
			throw new Win32Exception(Marshal.GetLastWin32Error());
		}
		Kernel32.CloseProcessHandle(processHandle);
		return result;
	}

	// Token: 0x06000067 RID: 103 RVA: 0x0000337D File Offset: 0x0000157D
	[DebuggerHidden]
	public static IntPtr CreateRemoteThread(Process p, IntPtr address, IntPtr param, CreateThreadFlags flags)
	{
		return Kernel32.CreateRemoteThread(p.Id, address, param, flags);
	}

	// Token: 0x06000068 RID: 104 RVA: 0x00003390 File Offset: 0x00001590
	[DebuggerHidden]
	public static IntPtr CreateRemoteThread(int pid, IntPtr address, IntPtr param, CreateThreadFlags flags)
	{
		IntPtr processHandle = Kernel32.GetProcessHandle(new IntPtr(pid), ProcessAccessFlags.CreateThread | ProcessAccessFlags.VMOperation | ProcessAccessFlags.VMRead | ProcessAccessFlags.VMWrite | ProcessAccessFlags.QueryInformation);
		IntPtr intPtr = Kernel32.CreateRemoteThread(processHandle, IntPtr.Zero, 0U, address, param, (uint)flags, IntPtr.Zero);
		if (intPtr == IntPtr.Zero)
		{
			throw new Win32Exception(Marshal.GetLastWin32Error());
		}
		Kernel32.CloseProcessHandle(processHandle);
		return intPtr;
	}

	// Token: 0x06000069 RID: 105 RVA: 0x000033E0 File Offset: 0x000015E0
	[DebuggerHidden]
	public static void SuspendThread(int tid)
	{
		IntPtr intPtr = Kernel32.OpenThread(ThreadAccessFlags.SuspendResume, false, (uint)tid);
		Kernel32.SuspendThread(intPtr);
		Kernel32.CloseHandle(intPtr);
	}

	// Token: 0x0600006A RID: 106 RVA: 0x000033F7 File Offset: 0x000015F7
	[DebuggerHidden]
	public static void ResumeThread(int tid)
	{
		IntPtr intPtr = Kernel32.OpenThread(ThreadAccessFlags.SuspendResume, false, (uint)tid);
		Kernel32.ResumeThread(intPtr);
		Kernel32.CloseHandle(intPtr);
	}

	// Token: 0x0600006B RID: 107 RVA: 0x00003410 File Offset: 0x00001610
	[DebuggerHidden]
	public static byte[] GetRawBytes(object anything)
	{
		if (anything.GetType().Equals(typeof(string)))
		{
			return Encoding.Unicode.GetBytes((string)anything);
		}
		int num = Marshal.SizeOf(anything);
		IntPtr intPtr = Marshal.AllocHGlobal(num);
		Marshal.StructureToPtr(anything, intPtr, false);
		byte[] array = new byte[num];
		Marshal.Copy(intPtr, array, 0, num);
		Marshal.FreeHGlobal(intPtr);
		return array;
	}

	// Token: 0x0600006C RID: 108 RVA: 0x00003474 File Offset: 0x00001674
	public static uint StartProcess(string directory, string application, ProcessCreationFlags flags, params string[] parameters)
	{
		Kernel32.StartupInfo startupInfo = default(Kernel32.StartupInfo);
		Kernel32.ProcessInformation processInformation = default(Kernel32.ProcessInformation);
		if (Kernel32.CreateProcess(application, application + string.Concat(parameters), IntPtr.Zero, IntPtr.Zero, false, (uint)flags, IntPtr.Zero, directory, ref startupInfo, out processInformation))
		{
			return processInformation.ProcessId;
		}
		return uint.MaxValue;
	}

	// Token: 0x0600006D RID: 109 RVA: 0x000034C3 File Offset: 0x000016C3
	public static Process StartSuspended(Process process, ProcessStartInfo startInfo)
	{
		return Process.GetProcessById((int)Kernel32.StartProcess(startInfo.WorkingDirectory, startInfo.FileName, ProcessCreationFlags.Suspended, new string[]
		{
			startInfo.Arguments
		}));
	}

	// Token: 0x0600006E RID: 110 RVA: 0x000034EC File Offset: 0x000016EC
	public static void Suspend(Process process)
	{
		foreach (object obj in process.Threads)
		{
			Kernel32.SuspendThread(new IntPtr(((ProcessThread)obj).Id));
		}
	}

	// Token: 0x0600006F RID: 111 RVA: 0x00003550 File Offset: 0x00001750
	public static void Resume(Process process)
	{
		foreach (object obj in process.Threads)
		{
			Kernel32.ResumeThread(((ProcessThread)obj).Id);
		}
	}

	// Token: 0x06000070 RID: 112 RVA: 0x000035AC File Offset: 0x000017AC
	public static void Suspend(ProcessThread thread)
	{
		Kernel32.SuspendThread(new IntPtr(thread.Id));
	}

	// Token: 0x06000071 RID: 113 RVA: 0x000035BF File Offset: 0x000017BF
	public static void Resume(ProcessThread thread)
	{
		Kernel32.ResumeThread(new IntPtr(thread.Id));
	}

	// Token: 0x0200001D RID: 29
	private struct ProcessInformation
	{
		// Token: 0x040000F3 RID: 243
		public IntPtr Process;

		// Token: 0x040000F4 RID: 244
		public IntPtr Thread;

		// Token: 0x040000F5 RID: 245
		public uint ProcessId;

		// Token: 0x040000F6 RID: 246
		public uint ThreadId;
	}

	// Token: 0x0200001E RID: 30
	private struct StartupInfo
	{
		// Token: 0x040000F7 RID: 247
		public uint CB;

		// Token: 0x040000F8 RID: 248
		public string Reserved;

		// Token: 0x040000F9 RID: 249
		public string Desktop;

		// Token: 0x040000FA RID: 250
		public string Title;

		// Token: 0x040000FB RID: 251
		public uint X;

		// Token: 0x040000FC RID: 252
		public uint Y;

		// Token: 0x040000FD RID: 253
		public uint XSize;

		// Token: 0x040000FE RID: 254
		public uint YSize;

		// Token: 0x040000FF RID: 255
		public uint XCountChars;

		// Token: 0x04000100 RID: 256
		public uint YCountChars;

		// Token: 0x04000101 RID: 257
		public uint FillAttribute;

		// Token: 0x04000102 RID: 258
		public uint Flags;

		// Token: 0x04000103 RID: 259
		public short ShowWindow;

		// Token: 0x04000104 RID: 260
		public short Reserved2;

		// Token: 0x04000105 RID: 261
		public IntPtr lpReserved2;

		// Token: 0x04000106 RID: 262
		public IntPtr StdInput;

		// Token: 0x04000107 RID: 263
		public IntPtr StdOutput;

		// Token: 0x04000108 RID: 264
		public IntPtr StdError;
	}

	// Token: 0x0200001F RID: 31
	[Flags]
	public enum ErrorModes : uint
	{
		// Token: 0x0400010A RID: 266
		SYSTEM_DEFAULT = 0U,
		// Token: 0x0400010B RID: 267
		SEM_FAILCRITICALERRORS = 1U,
		// Token: 0x0400010C RID: 268
		SEM_NOALIGNMENTFAULTEXCEPT = 4U,
		// Token: 0x0400010D RID: 269
		SEM_NOGPFAULTERRORBOX = 2U,
		// Token: 0x0400010E RID: 270
		SEM_NOOPENFILEERRORBOX = 32768U
	}
}