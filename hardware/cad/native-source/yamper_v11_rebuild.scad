// Yamper V11 editable OpenSCAD rebuild
// Units: millimeters
$fn = 64;

PART = "all";
// front_shell, back_cover, oled_retainer, speaker_retainer, mic_retainer,
// max98357a_clip, pisugar_plunger, pisugar_slot_cap, button_washer,
// front_test_plate, all

case_w = 104;
case_h = 82.5;
case_d = 52.25;
wall = 3.2;
front_t = 3.2;
back_t = 3.0;
corner_r = 8.5;

oled_visible_w = 23.5;
oled_visible_h = 12.9;
oled_pcb_w = 27.5;
oled_pcb_h = 27.8;

speaker_w = 25;
speaker_h = 35;
button_hole_d = 16.4;

eye_dx = 18;
eye_y = 21;

speaker_x = 0;
speaker_y = -12.5;
grille_w = 31;
grille_h = 25;
grille_slot_w = 1.4;
grille_slot_count = 7;

mic_x = -34;
mic_y = -24;
mic_hole_d = 2;

case_screw_x = 41.5;
case_screw_y = 30.5;

pi_hole_x = 58;
pi_hole_y = 23;

pisugar_slot_x = 27;
pisugar_slot_y = -24;
pisugar_slot_w = 24;
pisugar_slot_h = 8;

module rounded_rect_2d(w, h, r) {
    hull() {
        translate([ w/2-r,  h/2-r]) circle(r=r);
        translate([-w/2+r,  h/2-r]) circle(r=r);
        translate([ w/2-r, -h/2+r]) circle(r=r);
        translate([-w/2+r, -h/2+r]) circle(r=r);
    }
}

module rounded_box(w, h, d, r) {
    linear_extrude(height=d) rounded_rect_2d(w, h, r);
}

module slot_2d(w, h) {
    r = h/2;
    hull() {
        translate([-w/2+r,0]) circle(r=r);
        translate([ w/2-r,0]) circle(r=r);
    }
}

module cyl_cut(x, y, r, z0, z1) {
    translate([x,y,z0]) cylinder(h=z1-z0, r=r);
}

module slot_cut(x, y, w, h, z0, z1) {
    translate([x,y,z0]) linear_extrude(height=z1-z0) slot_2d(w,h);
}

module front_screw_boss(x, y) {
    difference() {
        union() {
            translate([x,y,front_t-0.2]) cylinder(h=case_d-front_t, r=4.2);

            translate([x > 0 ? x+1.4 : x-6.4, y-1.2, front_t-0.2])
                cube([5,2.4,case_d-front_t]);

            translate([x-1.2, y > 0 ? y+1.4 : y-6.4, front_t-0.2])
                cube([2.4,5,case_d-front_t]);
        }
        translate([x,y,case_d-16]) cylinder(h=18, r=1.35);
        translate([x,y,case_d-3]) cylinder(h=5, r=2.05);
    }
}

module oled_cuts() {
    for (x=[-eye_dx, eye_dx])
        translate([x, eye_y, front_t/2])
            cube([oled_visible_w, oled_visible_h, front_t+4], center=true);
}

module speaker_cuts() {
    gap = grille_w / (grille_slot_count*2 - 1);
    for (i=[0:grille_slot_count-1]) {
        x = speaker_x - grille_w/2 + gap + i*2*gap;
        translate([x, speaker_y, front_t/2])
            cube([grille_slot_w, grille_h, front_t+4], center=true);
    }
}

module mic_cuts() {
    for (p=[
        [mic_x,mic_y],
        [mic_x-3,mic_y],
        [mic_x+3,mic_y],
        [mic_x,mic_y-3],
        [mic_x,mic_y+3]
    ])
        cyl_cut(p[0], p[1], mic_hole_d/2, -1, front_t+3);
}

module top_button_cut() {
    translate([0, case_h/2-wall/2, 27])
        rotate([90,0,0])
            cylinder(h=wall+4, r=button_hole_d/2, center=true);
}

module face_frames() {
    for (x=[-eye_dx, eye_dx]) {
        translate([x, eye_y+oled_visible_h/2+2.2, front_t])
            cube([oled_visible_w+5.5,1.4,1.3], center=true);
        translate([x, eye_y-oled_visible_h/2-2.2, front_t])
            cube([oled_visible_w+5.5,1.4,1.3], center=true);
        translate([x-oled_visible_w/2-2.2, eye_y, front_t])
            cube([1.4,oled_visible_h+5.5,1.3], center=true);
        translate([x+oled_visible_w/2+2.2, eye_y, front_t])
            cube([1.4,oled_visible_h+5.5,1.3], center=true);
    }

    translate([speaker_x, speaker_y+grille_h/2+1.9, front_t])
        cube([grille_w+4.5,1.3,1.3], center=true);
    translate([speaker_x, speaker_y-grille_h/2-1.9, front_t])
        cube([grille_w+4.5,1.3,1.3], center=true);
    translate([speaker_x-grille_w/2-1.9, speaker_y, front_t])
        cube([1.3,grille_h+4.5,1.3], center=true);
    translate([speaker_x+grille_w/2+1.9, speaker_y, front_t])
        cube([1.3,grille_h+4.5,1.3], center=true);
}

module front_shell() {
    difference() {
        union() {
            difference() {
                rounded_box(case_w, case_h, case_d, corner_r);
                translate([0,0,front_t])
                    rounded_box(case_w-2*wall, case_h-2*wall, case_d+2, max(1,corner_r-wall));
            }

            for (x=[-case_screw_x, case_screw_x])
                for (y=[-case_screw_y, case_screw_y])
                    front_screw_boss(x,y);

            face_frames();
        }

        oled_cuts();
        speaker_cuts();
        mic_cuts();
        top_button_cut();
    }
}

module back_cover() {
    difference() {
        union() {
            rounded_box(case_w-0.8, case_h-0.8, back_t, corner_r-0.5);

            for (x=[-pi_hole_x/2, pi_hole_x/2])
                for (y=[-pi_hole_y/2, pi_hole_y/2])
                    translate([x,y,back_t-0.1]) cylinder(h=5.6, r=3.5);

            translate([-31,22,back_t]) cube([62,1.8,2]);
            translate([-31,11,back_t]) cube([62,1.8,2]);
            translate([-32,11,back_t]) cube([1.8,13,2]);
            translate([30.2,11,back_t]) cube([1.8,13,2]);
        }

        for (x=[-case_screw_x, case_screw_x])
            for (y=[-case_screw_y, case_screw_y]) {
                cyl_cut(x,y,1.75,-1,back_t+3);
                cyl_cut(x,y,3.3,back_t-1.5,back_t+2);
            }

        for (x=[-pi_hole_x/2, pi_hole_x/2])
            for (y=[-pi_hole_y/2, pi_hole_y/2])
                cyl_cut(x,y,1.25,back_t-0.5,back_t+8);

        slot_cut(pisugar_slot_x,pisugar_slot_y,pisugar_slot_w,pisugar_slot_h,-1,back_t+2);
        slot_cut(pisugar_slot_x,pisugar_slot_y,pisugar_slot_w+8,pisugar_slot_h+5,-1,1.1);
    }
}

module oled_retainer() {
    difference() {
        cube([34,8,2.2], center=true);
        cube([26,3,3], center=true);
    }
}

module speaker_retainer() {
    difference() {
        cube([31,41,2.2], center=true);
        cube([24,34,3], center=true);
    }
}

module mic_retainer() {
    difference() {
        cylinder(h=2.2, r=8);
        translate([0,0,-0.5]) cylinder(h=3.2, r=5.8);
    }
}

module max98357a_clip() {
    union() {
        cube([29,2.2,3], center=true);
        translate([0,10.5,0]) cube([29,2.2,3], center=true);
        translate([-14.5,5.25,0]) cube([2.2,12.5,3], center=true);
    }
}

module pisugar_plunger() {
    union() {
        cube([26,11,2.2], center=true);
        translate([0,0,4.2]) cube([4.2,4.2,6.2], center=true);
    }
}

module pisugar_slot_cap() {
    linear_extrude(height=2) slot_2d(pisugar_slot_w+2,pisugar_slot_h+2);
}

module button_washer() {
    difference() {
        cylinder(h=2, r=11.4);
        translate([0,0,-0.5]) cylinder(h=3, r=button_hole_d/2);
    }
}

module front_test_plate() {
    difference() {
        rounded_box(case_w, case_h, 4, corner_r);
        oled_cuts();
        speaker_cuts();
        mic_cuts();
    }
}

if (PART == "front_shell") front_shell();
else if (PART == "back_cover") back_cover();
else if (PART == "oled_retainer") oled_retainer();
else if (PART == "speaker_retainer") speaker_retainer();
else if (PART == "mic_retainer") mic_retainer();
else if (PART == "max98357a_clip") max98357a_clip();
else if (PART == "pisugar_plunger") pisugar_plunger();
else if (PART == "pisugar_slot_cap") pisugar_slot_cap();
else if (PART == "button_washer") button_washer();
else if (PART == "front_test_plate") front_test_plate();
else if (PART == "all") {
    translate([-140,0,0]) front_shell();
    translate([0,0,0]) back_cover();
    translate([100,40,0]) oled_retainer();
    translate([125,40,0]) speaker_retainer();
    translate([165,40,0]) mic_retainer();
    translate([195,40,0]) max98357a_clip();
    translate([100,-20,0]) pisugar_plunger();
    translate([130,-20,0]) pisugar_slot_cap();
    translate([160,-20,0]) button_washer();
}
