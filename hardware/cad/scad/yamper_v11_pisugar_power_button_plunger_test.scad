/*
Yamper V11 mesh source for yamper_v11_pisugar_power_button_plunger_test.stl
Units: millimeters

This source keeps the restored V11 STL geometry as a plain OpenSCAD polyhedron.
It is not a new redesign. It exists so the CAD source, STL, and STEP exports stay together.
*/

module yamper_v11_pisugar_power_button_plunger_test() {
    pts = [
        [-11, -5, 2.2],
        [-11, 5, 2.2],
        [-11, -5, 0],
        [11, -5, 0],
        [-11, 5, 0],
        [11, 5, 2.2],
        [11, -5, 2.2],
        [11, 5, 0],
        [-2, -2, 6.9],
        [-2, 2, 6.9],
        [-2, -2, 1.1],
        [2, -2, 1.1],
        [-2, 2, 1.1],
        [2, 2, 6.9],
        [2, -2, 6.9],
        [2, 2, 1.1],
    ];

    tris = [
        [0, 1, 2],
        [3, 0, 2],
        [2, 1, 4],
        [4, 3, 2],
        [0, 5, 1],
        [6, 0, 3],
        [6, 5, 0],
        [1, 5, 4],
        [7, 3, 4],
        [4, 5, 7],
        [7, 6, 3],
        [5, 6, 7],
        [8, 9, 10],
        [11, 8, 10],
        [10, 9, 12],
        [12, 11, 10],
        [8, 13, 9],
        [14, 8, 11],
        [14, 13, 8],
        [9, 13, 12],
        [15, 11, 12],
        [12, 13, 15],
        [15, 14, 11],
        [13, 14, 15],
    ];

    polyhedron(points = pts, faces = tris, convexity = 10);
}

yamper_v11_pisugar_power_button_plunger_test();
