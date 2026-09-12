// ==========================================
// Compact Filament Archive Swatch (Corrected)
// Designed for 0.4mm nozzle, 0.2mm layer height
// ==========================================

// --- Customizable Parameters ---
brand_text = "Brand";
material_text = "Material";
color_text = "Color";

// Dimensions (Compact archiving size)
card_width = 80;
card_height = 50;
base_thickness = 2.0; // Sufficient for rigidity but saves plastic

// Corner Styles (2D Profile)
right_corner_radius = 3; // Fillets (Right side)
left_chamfer_size = 4;   // Chamfers (Left side)

// Edge Styles (3D Z-Layer Tests)
top_edge_chamfer = 2.0;  // Size of the 45deg slope on top edge (Y-max edge)
bottom_edge_fillet = 2.0; // Radius of the rounding on bottom edge (Y-min edge)

// Layer settings
layer_height = 0.2;

// --- Main Render ---
$fn = 60; // Resolution for curves

difference() {
    // 1. Base Shape (Hybrid: Chamfered Left, Filleted Right)
    hybrid_rect(card_width, card_height, base_thickness, right_corner_radius, left_chamfer_size);

    // 2. Thumb Notch (Ergonomics)
    translate([card_width, card_height/2, -1])
        cylinder(h = base_thickness + 2, r = 8);

    // 3. Concave Dome (Surface Finish)
    // Moved to the left of the opacity steps to clear the text area
    translate([card_width - 66, 9, base_thickness + 6])
        sphere(r = 8);

    // 4. Opacity Steps (Translucency & Flow)
    // FIX: Cuts must start from the desired floor thickness and go UP to the top surface.
    // To leave X mm, we translate to Z = X and cut the rest of the height.
    
    // Step 1: 0.2mm thick floor
    translate([card_width - 15, 5, 0.2])
        cube([10, 8, base_thickness]);
    // Step 2: 0.4mm thick floor
    translate([card_width - 25, 5, 0.4])
        cube([10, 8, base_thickness]);
    // Step 3: 0.6mm thick floor
    translate([card_width - 35, 5, 0.6])
        cube([10, 8, base_thickness]);
    // Step 4: 0.8mm thick floor
    translate([card_width - 45, 5, 0.8])
        cube([10, 8, base_thickness]);
    // Step 5: 1.0mm thick floor
    translate([card_width - 55, 5, 1.0])
        cube([10, 8, base_thickness]);

    // 5. Text Labeling
    // Note: Engraved 0.6mm deep. Since Opacity steps are at Y=5 and Text is higher up, they don't clash.
    // Brand
    translate([4, card_height - 10, base_thickness - 0.6])
        linear_extrude(1)
        text(brand_text, size=5, font="Liberation Sans:style=Bold");
    // Material
    translate([4, card_height - 18, base_thickness - 0.6])
        linear_extrude(1)
        text(material_text, size=5, font="Liberation Sans:style=Bold");
    // Color
    translate([4, card_height - 28, base_thickness - 0.6])
        linear_extrude(1)
        text(color_text, size = len(color_text) > 12 ? 3.5 : 4.5, font="Liberation Sans");

    // 6. Chamfer & Fillet Tests (Original integrated test)
    translate([card_width - 55, 13, base_thickness])
        rotate([45, 0, 0])
        cube([10, 2, 2]);

    // 7. Top Edge Z-Layer Chamfer
    // FIX: Corrected rotation and coordinates. 
    // We define the profile in the Y-Z plane using X and Y in the polygon, then rotate -90 Y to align with World X.
    translate([card_width + 5, 0, 0]) // Start slightly past the end of the card
        rotate([0, -90, 0])           // Rotate so Z-extrusion points along -X
        linear_extrude(card_width + 10)
        polygon([
            [base_thickness, card_height],                      // Top-Back Corner (Z=2, Y=45)
            [base_thickness - top_edge_chamfer, card_height],   // Side Cut limit (Z=0, Y=45)
            [base_thickness, card_height - top_edge_chamfer]    // Top Cut limit (Z=2, Y=43)
        ]);

    // 8. Bottom Edge Z-Layer Fillet
    // Rounds off the edge at Y=0 (as seen from top), specifically the top corner of that edge.
    // Z translation aligns the cutter's void with the top edge.
    translate([-5, 0, base_thickness - bottom_edge_fillet])
        fillet_cutter_x(card_width + 10, bottom_edge_fillet);

}

// --- Modules ---

// Generates a plate with Chamfered Left corners and Filleted Right corners
module hybrid_rect(w, h, d, r, c) {
    linear_extrude(d)
        hull() {
            // Right side: Fillets (Circles)
            translate([w-r, r]) circle(r=r);
            translate([w-r, h-r]) circle(r=r);
            
            // Left side: Chamfers (Polygon)
            polygon([
                [c, 0],       // Bottom chamfer start
                [0, c],       // Bottom chamfer end
                [0, h-c],     // Top chamfer start
                [c, h],       // Top chamfer end
                [w/2, h],     // Middle connector
                [w/2, 0]      // Middle connector
            ]);
        }
}

// Tool to cut a rounded fillet edge along the X axis
module fillet_cutter_x(len, r) {
    difference() {
        // The block that removes the sharp corner
        cube([len, r + 0.1, r + 0.1]); 
        
        // The cylinder that preserves the rounded material inside
        // Adjusted translation to ensure clean difference
        translate([-1, r, 0])
            rotate([0, 90, 0])
            cylinder(h=len+2, r=r);
    }
}

