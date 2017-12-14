## kicad_holes
KiCad script to convert circles in Edge.Cuts layer to non-plated through-holes.

### Installation
```
git clone kicad_holes
./kicad_holes/install.sh
```

### Operation
0. Follow installation instructions above.
1. Backup KiCad board file in question (the .kicad_pcb)
2. Open KiCad board in pcbnew
3. Go to the tools menu and open the scripting console
4. Type `import edges2holes_action`, and hit enter.
5. **Before clicking anything on the board, save the board, close all KiCad windows.** 
   This avoids a segfault that may be caused by selecting one of the deleted Edge.Cuts 
   circles.
6. Reopen KiCad to inspect changes, and for further work.

This script currently saves the footprints in a folder called `<prefix>.pretty`, where 
`<prefix>.kicad_pcb` is the name of the board file.

Circles on Edge.Cuts will be deleted.
