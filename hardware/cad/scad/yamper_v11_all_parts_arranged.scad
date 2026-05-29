/* Yamper V11 arranged OpenSCAD preview. Units are millimeters. */

use <yamper_v11_front_shell_fused.scad>;
use <yamper_v11_back_cover_with_pisugar_power_slot.scad>;
use <yamper_v11_oled_retainer_print_2x.scad>;
use <yamper_v11_3525_speaker_retainer.scad>;
use <yamper_v11_round_inmp441_mic_retainer.scad>;
use <yamper_v11_max98357a_clip.scad>;
use <yamper_v11_pisugar_power_button_plunger_test.scad>;
use <yamper_v11_pisugar_slot_blank_cap_optional.scad>;
use <yamper_v11_button_washer_optional.scad>;

translate([52.075001, 41.625, 0.075]) yamper_v11_front_shell_fused();
translate([171.625, 40.674999, 0.075]) yamper_v11_back_cover_with_pisugar_power_slot();
translate([16.5, 124, 0]) yamper_v11_oled_retainer_print_2x();
translate([64.5, 140.5, 0]) yamper_v11_3525_speaker_retainer();
translate([104.1, 128.1, 1.1]) yamper_v11_round_inmp441_mic_retainer();
translate([140.700001, 122, 0]) yamper_v11_max98357a_clip();
translate([180.200001, 125, 0]) yamper_v11_pisugar_power_button_plunger_test();
translate([221.200001, 126, 0]) yamper_v11_pisugar_slot_blank_cap_optional();
translate([11.4, 188.4, 1]) yamper_v11_button_washer_optional();
