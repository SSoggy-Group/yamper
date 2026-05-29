/*
Yamper V11 mesh source for yamper_v11_pisugar_slot_blank_cap_optional.stl
Units: millimeters

This source keeps the restored V11 STL geometry as a plain OpenSCAD polyhedron.
It is not a new redesign. It exists so the CAD source, STL, and STEP exports stay together.
*/

module yamper_v11_pisugar_slot_blank_cap_optional() {
    pts = [
        [-14, -6, 2],
        [-14, 6, 2],
        [-14, -6, 0],
        [14, -6, 0],
        [-14, 6, 0],
        [14, 6, 2],
        [14, -6, 2],
        [14, 6, 0],
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
    ];

    polyhedron(points = pts, faces = tris, convexity = 10);
}

yamper_v11_pisugar_slot_blank_cap_optional();
