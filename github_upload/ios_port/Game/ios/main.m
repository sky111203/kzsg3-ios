

#import <UIKit/UIKit.h>

void kzsg3_install_crash_handler(void);

int main(int argc, char *argv[]) {

    NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];
    kzsg3_install_crash_handler();
    int retVal = UIApplicationMain(argc, argv, nil, @"AppController");
    [pool release];
    return retVal;
}
