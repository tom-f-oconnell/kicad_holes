#!/usr/bin/env python

from __future__ import division
from __future__ import print_function
import os
import pcbnew

from kicad_util import *


# TODO set up to run offline too

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

        # TODO don't add an extra hole in same place -> overwrite

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

                    # TODO make optional
                    # how to do?
                    board.RemoveNative(d)

       
        # TODO option to use nearest hole in existing library option / next largest
        # (report error)
        # TODO easiest way to get available footprints (and their radii?)
        # TODO option to take a set of target hole sizes (for DFM purposes)
        # TODO include either global use next largest / next smallest
        # (maybe ignore locked, and say that, to complement this?)
        # or let people check for each hole whether they want to use next up or down

        # TODO option to make new hole components and put in project specific library

        # TODO include field for library to be saved to (maybe mandatory if this option?)
        # TODO fail gracefully if board filename is empty (board not saved yet)
        target_footprint_lib = '.'.join(str(board.GetFileName()).split('.')[:-1]) \
            + '.pretty'

        if not os.path.exists(target_footprint_lib):
            print('creating project specific footprint library' + \
                ' {}'.format(target_footprint_lib))
            pcbnew.PCB_IO().FootprintLibCreate(target_footprint_lib)
        else:
            print('using footprint library {}'.format(target_footprint_lib))

        # make a new footprint for each distinct hole radius we need
        # save to project specific library by default
        for r in radii:
            r_mm = nm_to_mm(r)
            print('generating footprint for hole of radius {}mm'.format(r_mm))

            footprint = pcbnew.MODULE(None)
            # for non-electronic parts like these
            footprint.SetAttributes(pcbnew.MOD_VIRTUAL)
            footprint.SetLastEditTime()
            footprint.SetKeywords('non-plated through hole NPTH')

            # TODO it looks like the module itself needs to be specified to be on F.Cu?
            # how? (see github for example output)

            # TODO set tags to include non-plated through hole, npth?
            #footprint.SetDescription('{}mm diameter non-plated through hole')
            pad = pcbnew.D_PAD(footprint)

            # other library mounting hole pads seem to have this pad number
            pad.SetName('1')

            # TODO does this change the layers and stuff automatically? pad shape?
            pad.SetAttribute(pcbnew.PAD_ATTRIB_HOLE_NOT_PLATED)
            pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            # TODO do i need setsize / setstartend?
            # size seems to equal (r, r) for existing npth library parts

            # all holes in KiCad currently have to reside on one of the (external?)
            # copper layers (F.Cu should be one of these layers. mask the other?)
            pad.SetLayerSet(pcbnew.D_PAD_UnplatedHoleMask())

            # TODO are holes alone actually rendered, or do you need the other stuff?

            # there seems to be a PAD_DRILL_SHAPE_CIRCLE and PAD_DRILL_SHAPE_OBLONG
            # but when are they ever not circular? oblong = limited routing?
            # would advanced circuits do oblong, for instance?
            #pad.SetDrillShape() # huh???
            # TODO why isn't this a single number? what gens (drill X)?
            # TODO why is x in (size x x) slightly larger than 1.5?
            pad.SetDrillSize(pcbnew.wxSize(r, r))
            footprint.Add(pad)

            footprint_id = 'R{}mm_NPTH'.format(r_mm)
            footprint.SetReference(footprint_id)

            '''
            footprint.Reference().SetPosition(pcbnew.wxPoint()1)
            footprint.Value().SetPosition(pcbnew.wxPoint()1)
            '''

            # aiming for a visible layer that does not translate into manufacture
            comment_layer_id = get_layer_id_by_name('Cmts.User')
            footprint.Reference().SetLayer(comment_layer_id)
            footprint.Value().SetLayer(comment_layer_id)

            # this is the filename, preceeding .kicad_mod
            fpid = pcbnew.LIB_ID(footprint_id)
            footprint.SetFPID(fpid)

            # seems to work to lock all imports by default
            footprint.SetLocked(True)

            print('saving footprint to {}'.format(os.path.join(\
                target_footprint_lib, footprint_id + '.kicad_mod')))
            pcbnew.PCB_IO().FootprintSave(target_footprint_lib, footprint)

            for x, y, r_curr in circles:
                if r == r_curr:
                    f_new = pcbnew.PCB_IO().FootprintLoad(target_footprint_lib, footprint_id)
                    f_new.SetPosition(pcbnew.wxPoint(x, y))
                    board.Add(f_new)

        # TODO convert slots / particularly large holes to a series of holes?
        # TODO maybe offer a (np) pilot hole for particularly large holes?

        # TODO lock all new holes (if not already working to just lock module)

        # TODO redraw / refresh / updateuserinterface?
        # these together didn't work, and might have unmarked as modified
        # (couldn't save directly)
        # actually that seems to be happening anyway
        #pcbnew.UpdateUserInterface()
        #pcbnew.Refresh()

    # TODO need to explicitly mark board as modified, or do these calls have that built in?

# just since it is not evident there is still support for an action plugins interface
# no menu in HEAD now
#HolePlugin().register() # Instantiate and register to Pcbnew

h = HolePlugin()
h.Run()

