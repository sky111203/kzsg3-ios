#ifndef __APPDELEGATE_H__
#define __APPDELEGATE_H__

#include "cocos2d.h"

class AppDelegate : private cocos2d::Application
{
public:
    AppDelegate();
    ~AppDelegate();

    /**
    @brief  Implement Director and Scene init code here.
    @return true    Initialize success, app continue.
    @return false   Initialize failed, app terminate.
    */
    virtual bool applicationDidFinishLaunching();

    /**
    @brief  The function be called when the application enter background
    */
    virtual void applicationDidEnterBackground();

    /**
    @brief  The function be called when the application enter foreground
    */
    virtual void applicationWillEnterForeground();
};

#endif
