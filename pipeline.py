import os
import shutil
import sys

from core.center_layer import generate_planes_from_stl
from core.plane_cut import run_plane_cut
from core.rotate_batch import run_rotate_batch
from core.slicer_runner import run_slicer
from core.gcode_global_transform import run_global_transform
from core.gcode_machine_transform import run_machine_transform
from core.gcode_viewer_transform import run_viewer_transform
from core.merge import run_merge
from core.rrf_converter import convert_to_rrf


# =========================================================
# BASE DIR
# =========================================================

def get_base_dir():

    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.path.abspath(".")


# =========================================================
# CLEAN TEMP
# =========================================================

def clean_temp(temp_dir, log):

    if not os.path.exists(temp_dir):
        return

    try:
        shutil.rmtree(temp_dir)
        log(f"🧹 Temp deleted: {temp_dir}")

    except Exception as e:
        log(f"⚠ Temp delete failed: {e}")


# =========================================================
# MAIN PIPELINE
# =========================================================

def run_pipeline(
    stl_path,
    out_folder,
    layer_height,
    pivot_offset,
    log,
    progress
):

    log("🌸 5-Axis Pipeline Start 🌸")

    pivot_y, pivot_z = pivot_offset

    log(f"Pivot Offset → Y: {pivot_y} mm | Z: {pivot_z} mm")

    # =====================================================
    # TEMP DIR
    # =====================================================

    temp_dir = os.path.join(out_folder, "temp")

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    os.makedirs(temp_dir)

    try:

        # =================================================
        # STEP 0
        # =================================================

        log("Generating planes...")

        planes = generate_planes_from_stl(
            stl_path,
            layer_height
        )

        progress(10)

        # =================================================
        # STEP 1
        # =================================================

        log("Plane cutting...")

        part_files = run_plane_cut(
            stl_path,
            planes,
            temp_dir
        )

        progress(25)

        # =================================================
        # STEP 2
        # =================================================

        log("Rotate batch...")

        flat_files, transform_files = run_rotate_batch(
            part_files,
            planes,
            temp_dir
        )

        progress(40)

        # =================================================
        # STEP 3
        # =================================================

        log("Slicing...")

        gcode_files = run_slicer(
            flat_files,
            temp_dir
        )

        progress(55)

        if not gcode_files:
            log("❌ Slicing failed")
            return

        # =================================================
        # STEP 4
        # =================================================

        log("Global transform...")

        global_gcode_files = run_global_transform(
            gcode_files,
            transform_files,
            temp_dir
        )

        progress(70)

        # =================================================
        # STEP 5
        # =================================================

        log("Machine transform...")

        machine_gcode_files = run_machine_transform(
            global_gcode_files,
            planes,
            temp_dir,
            pivot_offset=pivot_offset
        )

        progress(85)

        # =================================================
        # STEP 6
        # =================================================

        log("Viewer transform...")

        viewer_gcode_files = run_viewer_transform(
            global_gcode_files,
            planes,
            temp_dir
        )

        progress(90)

        # =================================================
        # STEP 7
        # SAVE MERGED FILES INTO TEMP
        # =================================================

        log("Merging...")

        merged_machine, merged_viewer = run_merge(
            machine_gcode_files,
            viewer_gcode_files,
            temp_dir
        )

        # =================================================
        # COPY VIEWER TO FINAL OUTPUT
        # =================================================

        final_viewer = os.path.join(
            out_folder,
            "merged_viewer.gcode"
        )

        shutil.copy(
            merged_viewer,
            final_viewer
        )

        # =================================================
        # STEP 8
        # CONVERT MACHINE -> RRF
        # =================================================

        log("Converting to RRF...")

        final_rrf = os.path.join(
            out_folder,
            "merged_rrf.gcode"
        )

        convert_to_rrf(
            merged_machine,
            final_rrf
        )

        progress(100)

        # =================================================
        # FINAL LOGS
        # =================================================

        log("")
        log("🎉 FINAL OUTPUT")
        log(f"Viewer : {final_viewer}")
        log(f"RRF    : {final_rrf}")

    except Exception as e:

        log(f"❌ ERROR: {e}")

    finally:

        # =================================================
        # CLEAN TEMP
        # =================================================

        clean_temp(temp_dir, log)

    log("DONE ✨")
