// Quick OpenSCAD wrapper for yamper_v11_max98357a_clip.stl
// Uses the STL from cad/stl. The full mesh source is one folder up.
module yamper_v11_max98357a_clip() {
    import(file = "../../stl/yamper_v11_max98357a_clip.stl", convexity = 10);
}

yamper_v11_max98357a_clip();
