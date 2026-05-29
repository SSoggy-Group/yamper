// Quick OpenSCAD wrapper for yamper_v11_button_washer_optional.stl
// Uses the STL from cad/stl. The full mesh source is one folder up.
module yamper_v11_button_washer_optional() {
    import(file = "../../stl/yamper_v11_button_washer_optional.stl", convexity = 10);
}

yamper_v11_button_washer_optional();
