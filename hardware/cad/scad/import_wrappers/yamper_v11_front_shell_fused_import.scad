// Quick OpenSCAD wrapper for yamper_v11_front_shell_fused.stl
// Uses the STL from cad/stl. The full mesh source is one folder up.
module yamper_v11_front_shell_fused() {
    import(file = "../../stl/yamper_v11_front_shell_fused.stl", convexity = 10);
}

yamper_v11_front_shell_fused();
