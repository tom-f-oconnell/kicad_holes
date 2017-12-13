#!/usr/bin/env python

import pcbnew

class HolePlugin(pcbnew.ActionPlugin):
    def defaults(self):
		self.name = "Edge.Cuts circles to NPTHs."
        self.category = "convert holes"
        self.description = "Convert circles in Edge.Cuts layer to non-plated through-holes."

    def Run(self):
        # The entry function of the plugin that is executed on user action
        print("Hello World")
        # TODO option to use nearest hole in existing library option / next largest (report error)

        # TODO option to make new hole components and put in project specific library
        # TODO make library if necessary...

        # TODO convert slots / particularly large holes to a series of holes?

        # TODO lock all new holes

SimplePlugin().register() # Instantiate and register to Pcbnew

