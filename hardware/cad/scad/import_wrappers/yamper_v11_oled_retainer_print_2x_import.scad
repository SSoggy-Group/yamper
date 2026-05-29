// Quick OpenSCAD wrapper for yamper_v11_oled_retainer_print_2x.stl
// Uses the STL from cad/stl. The full mesh source is one folder up.
module yamper_v11_oled_retainer_print_2x() {
    import(file = "../../stl/yamper_v11_oled_retainer_print_2x.stl", convexity = 10);
}

yamper_v11_oled_retainer_print_2x();
