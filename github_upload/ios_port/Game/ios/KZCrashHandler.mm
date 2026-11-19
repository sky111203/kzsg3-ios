// KZCrashHandler.mm — 崩溃信号处理器: 把回溯地址写入 Documents/kzsg3_crash.txt
#import <Foundation/Foundation.h>
#import <execinfo.h>
#import <signal.h>
#import <mach-o/dyld.h>
#import <unistd.h>
#import <stdio.h>

static char g_crash_path[1024];
static struct sigaction g_old[16];

static void kzsg3_handler(int sig, siginfo_t *info, void *ctx)
{
    // Documents/kzsg3_crash.txt
    static const char *names[] = {"SIGSEGV", "SIGBUS", "SIGILL", "SIGFPE", "SIGABRT"};
    const char *nm = (sig == SIGSEGV) ? names[0] : (sig == SIGBUS) ? names[1]
                   : (sig == SIGILL) ? names[2] : (sig == SIGFPE) ? names[3] : names[4];
    FILE *f = fopen(g_crash_path, "a");
    if (!f) {
        // fallback: /tmp
        f = fopen("/tmp/kzsg3_crash.txt", "a");
        if (!f) _exit(66);
    }
    void *addr = (info && info->si_addr) ? info->si_addr : NULL;
    fprintf(f, "== KZSG3 CRASH %s addr=%p\n", nm, addr);
    void *bt[128];
    int n = backtrace(bt, 128);
    // 记录主二进制基址, 方便离线换算 imageOffset
    void *base = (void *)_dyld_get_image_header(0);
    fprintf(f, "base=%p\n", base);
    backtrace_symbols_fd(bt, n, fileno(f));
    // 额外输出纯偏移行, 便于脚本解析
    fprintf(f, "-- offsets (relative to base):\n");
    for (int i = 0; i < n; ++i)
        fprintf(f, "+%llu\n", (unsigned long long)((uintptr_t)bt[i] - (uintptr_t)base));
    fprintf(f, "== end\n");
    fclose(f);
    // 恢复默认处理并重发, 保持系统生成 .ips
    sigaction(sig, &g_old[sig < 16 ? sig : 0], NULL);
    raise(sig);
    _exit(70);
}

void kzsg3_install_crash_handler(void)
{
    // Documents 路径
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    if (paths.count > 0) {
        NSString *dir = paths[0];
        snprintf(g_crash_path, sizeof(g_crash_path), "%s/kzsg3_crash.txt", [dir UTF8String]);
    } else {
        snprintf(g_crash_path, sizeof(g_crash_path), "/tmp/kzsg3_crash.txt");
    }
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_sigaction = kzsg3_handler;
    sa.sa_flags = SA_SIGINFO;
    int sigs[5] = {SIGSEGV, SIGBUS, SIGILL, SIGFPE, SIGABRT};
    for (int i = 0; i < 5; ++i) {
        sigaction(sigs[i], &sa, &g_old[sigs[i]]);
    }
}
