#!/usr/bin/env python

import pcbnew

# TODO how to run this offline too?

class HolePlugin(pcbnew.ActionPlugin):
    def defaults(self):
        """
        """
        self.name = "Edge.Cuts circles to NPTHs."
        self.category = "convert holes"
        self.description = "Convert circles in Edge.Cuts layer to non-plated through-holes."
 
    def Run(self):
        """
        The entry function of the plugin that is executed on user action
        """
        board = pcbnew.GetBoard()

        circles = []
        # get circles drawn on board
        # TODO maybe include some means of filtering out possible circular board outline
        drawing_list = board.DrawingsList()
        for d in drawing_list:
            if d.GetLayerName() == 'Edge.Cuts':
                # to gaurd against random stuff being on edge cuts for some reason
                # causing weird errors
                assert type(d) == pcbnew.DRAWSEGMENT, 'non-DRAWSEGMENT on Edge.Cuts'
                if d.GetShapeStr() == 'Circle':
                    # TODO check these are what i want, and don't need modification
                    # w/ thickness or whatever (check using dxf import)
                    radius = d.GetRadius()

                    

        # TODO also aggregate and bin by optional attributes, like tolerances
        radii = set()
       
        # TODO option to use nearest hole in existing library option / next largest
        # (report error)
        # TODO option to take a set of target hole sizes (for DFM purposes)

        # TODO option to make new hole components and put in project specific library
        # TODO make library if necessary...

        # TODO convert slots / particularly large holes to a series of holes?

        # TODO lock all new holes

    # TODO need to explicitly mark board as modified, or do these calls have that built in?

# just since it is not evident there is still support for an action plugins interface
# no menu in HEAD now
#HolePlugin().register() # Instantiate and register to Pcbnew

h = HolePlugin()
h.Run()

