

#import <UIKit/UIKit.h>

void kzsg3_install_crash_handler(void);

int main(int argc, char *argv[]) {

    NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];

    // ===== 生命标记: main 一进入就写文件 (诊断 pre-main 被杀) =====
    @autoreleasepool {
        NSArray *docs = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
        if (docs.count > 0) {
            NSString *mp = [docs[0] stringByAppendingPathComponent:@"launched_marker.txt"];
            NSString *ts = [NSString stringWithFormat:@"launched %@\n", [NSDate date]];
            [ts writeToFile:mp atomically:YES encoding:NSUTF8StringEncoding error:NULL];
            NSLog(@"[kzsg3] marker written: %@", mp);
        }
        NSLog(@"[kzsg3] main() entered, installing crash handler...");
    }

    kzsg3_install_crash_handler();

    NSLog(@"[kzsg3] calling UIApplicationMain...");
    int retVal = UIApplicationMain(argc, argv, nil, @"AppController");
    NSLog(@"[kzsg3] UIApplicationMain returned %d", retVal);
    [pool release];
    return retVal;
}
