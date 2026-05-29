// Quick OpenSCAD wrapper for yamper_v11_round_inmp441_mic_retainer.stl
// Uses the STL from cad/stl. The full mesh source is one folder up.
module yamper_v11_round_inmp441_mic_retainer() {
    import(file = "../../stl/yamper_v11_round_inmp441_mic_retainer.stl", convexity = 10);
}

yamper_v11_round_inmp441_mic_retainer();
