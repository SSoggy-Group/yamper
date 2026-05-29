// Quick OpenSCAD wrapper for yamper_v11_back_cover_with_pisugar_power_slot.stl
// Uses the STL from cad/stl. The full mesh source is one folder up.
module yamper_v11_back_cover_with_pisugar_power_slot() {
    import(file = "../../stl/yamper_v11_back_cover_with_pisugar_power_slot.stl", convexity = 10);
}

yamper_v11_back_cover_with_pisugar_power_slot();
