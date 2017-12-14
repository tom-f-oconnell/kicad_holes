#!/usr/bin/env python

import os
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

        # TODO also aggregate and bin by optional attributes, like tolerances
        radii = set()
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
                    r = d.GetRadius()
                    radii.add(r)
                    c = d.GetCenter()
                    circles.append((c.x, c.y, r))

       
        # TODO option to use nearest hole in existing library option / next largest
        # (report error)
        # TODO easiest way to get available footprints (and their radii?)
        # TODO option to take a set of target hole sizes (for DFM purposes)
        # TODO include either global use next largest / next smallest
        # (maybe ignore locked, and say that, to complement this?)
        # or let people check for each hole whether they want to use next up or down

        # TODO option to make new hole components and put in project specific library

        # TODO include field for library to be saved to (maybe mandatory if this option?)
        target_footprint_lib = '.'.join(str(board.GetFileName()).split('.')[-1] \
            + ['.pretty'])
        if not os.path.exists(target_footprint_lib):
            pcbnew.PCB_IO().FootprintLibCreate(target_footprint_lib)

        # make a new footprint for each distinct hole radius we need
        # save to project specific library by default
        for r in radii:
            footprint = pcbnew.MODULE(None)
            # TODO set tags to include non-plated through hole, npth?
            #footprint.SetDescription('{}mm diameter non-plated through hole')
            pad = pcbnew.D_PAD(footprint)

            # other library mounting hole pads seem to have this pad number
            pad.SetName('1')

            # TODO does this change the layers and stuff automatically? pad shape?
            pad.SetAttribute(pcbnew.PAD_ATTRIB_HOLE_NOT_PLATED)
            pad.SetShape(pcbnew.CIRCLE)
            # TODO do i need setsize / setstartend?
            # size seems to equal (r, r) for existing npth library parts

            # all holes in KiCad currently have to reside on one of the (external?)
            # copper layers (F.Cu should be one of these layers. mask the other?)
            pad.SetLayerSet(pcbnew.D_PAD_UnplatedHoleMask())

            # TODO what is attr virtual and why do all library M2s holes have them?
            # TODO are holes alone actually rendered, or do you need the other stuff?

            #pad.SetDrillShape() # huh???
            pad.SetDrillSize(pcbnew.wxSize(r))

            ''' copied from electrode_vertices.py
            # TODO name according to input parameters
            # (would require this function to have knowledge of generating parameters)
            #module_id = os.path.split(filename)[-1][:(-1)*len('.kicad_mod')]
            # what is reference used for exactly?
            #footprint.SetReference(module_id)

            # TODO not clear on why both setpos0 and setposition are called
            # in FootprintWizardBase.py
            footprint.Reference().SetPosition(pcbnew.wxPoint(int(round(0.6 * min(all_xs))), \
                int(round(1.1 * min(all_ys)))))
            footprint.Value().SetPosition(pcbnew.wxPoint(int(round(0.6 * max(all_xs))), \
                int(round(1.1 * min(all_ys)))))

            # aiming for a visible layer that does not translate into manufacture
            comment_layer_id = get_layer_id_by_name('Cmts.User')
            footprint.Reference().SetLayer(comment_layer_id)
            footprint.Value().SetLayer(comment_layer_id)

            fpid = pcbnew.LIB_ID(module_id)
            footprint.SetFPID(fpid)
            '''
            # TODO here or need to do individually?
            footprint.SetLocked(True)

            # TODO name? fpid?
            pcbnew.PCB_IO().FootprintSave(target_footprint_lib, footprint)

            f = pcbnew.PCB_IO().FootprintLoad(target_footprint_lib, fpid)
            for x, y, r_curr in circles:
                if r == r_curr:
                    # TODO what works here? clone? duplicate seems wrong
                    f_new = f.Clone()
                    # TODO duplicate / make new pad. see make_board?
                    pad.SetCenter(pcbnew.wxPoint(c.x, c,y))
                    # TODO everything set right?
                    board.AddNative(f_new)

        # TODO make library if necessary (?) (way to check for existing project specific library?)
        # or clean way to add a library? (rather than manually editing the files to add lines)

        # TODO convert slots / particularly large holes to a series of holes?
        # TODO maybe offer a (np) pilot hole for particularly large holes?

        # TODO lock all new holes

    # TODO need to explicitly mark board as modified, or do these calls have that built in?

# just since it is not evident there is still support for an action plugins interface
# no menu in HEAD now
#HolePlugin().register() # Instantiate and register to Pcbnew

# TODO redraw

h = HolePlugin()
h.Run()

