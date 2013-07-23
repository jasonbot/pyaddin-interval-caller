Interval-Callable ArcGIS Extension
==================================

This library extends your `Extension` classes in ArcGIS Add-Ins (in Python) to have a `onTimer()` event, which is called at configurable intervals.

Installing
----------

Install locally on your machine using setup.py:

    C:\gitprojects\pyaddin-interval-caller> C:\Python27\ArcGIS10.2\Python setup.py install

Or copy the `tickextension` folder into your Add-In's `Install\` folder.

Using this Dingus
-----------------

Make an python add-in with at least one extension class. Import `tickextension` near the top of your `Whatever_addin.py` file. If you opted for the copy-into-`Install\` option over using `setup.py`,  you'll do it like this:

    import imp
    import os
    tickextension_info = imp.find_module('tickextension', os.path.dirname(__file__))
    tickextension = imp.load_module('tickextension')

If you did the setup.py it's just `import tickextension` like always.

Then make these changes to your extension class:

 - Inherit from `tickextension.TickExtension`.
 - Add a `onTimer(self):` event. No arguments.
 - If you have a `startup` method, add a `super` call if it so the `TickExtension`'s `startup` is also called.
 - Set a `self.interval` attribute. It will be a float which is the interval, in seconds, in which the `onTimer` method is called.

Here is a visual example of what you'll need to do:

    import imp
    import os
    tickextension_info = imp.find_module('tickextension', os.path.dirname(__file__))
    tickextension = imp.load_module('tickextension')
    
    import arcpy
    import pythonaddins

    class MyNewAndShinyExtensionClass(tickextension.TickExtension):
        def __init__(self):
            self.interval = 0.5 # Call every half second
        def startup(self):
            super(self.__class__, self).startup()
        def onInterval(self):
            print "Tick"

The timer will turn itself off automatically when the extension is disabled. To turn it off manually, `del self.interval`. No interval set = no interval calls. If you wish to start it up again, set `self.interval` to a valid interval again and call `self.startTimer()`.

Be careful, try to follow the simple built-in enabled/disabled workflow if you can. If the interval ticker sticks around after the extension is deactivated, it will never be garbage collected and will hang the program.

How It Works
------------

Win32. Injecting a `WM_TIMER` event into Arc{Map,Globe,Scene}'s event loop. Check out the `CallQueue` class in `call_later.py` for all the gory, pedantic, confusing details. You could also take that class to do other horrible timer-based ugliness in Python in `Arc*.exe` for your own amusement/profit.

License
-------

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
