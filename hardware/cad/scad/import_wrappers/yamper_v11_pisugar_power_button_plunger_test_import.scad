// Quick OpenSCAD wrapper for yamper_v11_pisugar_power_button_plunger_test.stl
// Uses the STL from cad/stl. The full mesh source is one folder up.
module yamper_v11_pisugar_power_button_plunger_test() {
    import(file = "../../stl/yamper_v11_pisugar_power_button_plunger_test.stl", convexity = 10);
}

yamper_v11_pisugar_power_button_plunger_test();
