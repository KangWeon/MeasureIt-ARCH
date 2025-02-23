# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# ----------------------------------------------------------
# Author: Antonio Vazquez (antonioya), Kevan Cress
# ----------------------------------------------------------

# ----------------------------------------------
# Define Addon info
# ----------------------------------------------
bl_info = {
    "name": "MeasureIt-ARCH",
    "author": "Kevan Cress, Antonio Vazquez (antonioya)",
    "location": "View3D > Tools Panel /Properties panel",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),      
    "description": "Tools for measuring objects.",
    "category": "3D View"
}

import sys
import os

# ----------------------------------------------
# Import modules
# ----------------------------------------------
if "bpy" in locals():
    import importlib
    #importlib.reload(measureit_arch_geometry)
    #importlib.reload(measureit_arch_annotations)
    #importlib.reload(measureit_arch_baseclass)
    #importlib.reload(measureit_arch_main)
    #importlib.reload(measureit_arch_lines)
    #importlib.reload(measureit_arch_render)
    #importlib.reload(measureit_arch_styles)
    #importlib.reload(measureit_arch_dimensions)
    print("measureit_arch: Reloaded multifiles")
else:
    #from . import measureit_arch_geometry
    #from . import measureit_arch_annotations
    #from . import measureit_arch_baseclass
    #from . import measureit_arch_main
    #from . import measureit_arch_lines
    #from . import measureit_arch_render
    #from . import measureit_arch_styles
    #from . import measureit_arch_dimensions
    print("measureit_arch: Imported multifiles")

import bpy
from bpy.types import (
        PropertyGroup,
        AddonPreferences,
        Scene,
        WindowManager,
        )
from bpy.props import (
        CollectionProperty,
        FloatVectorProperty,
        IntProperty,
        BoolProperty,
        StringProperty,
        FloatProperty,
        EnumProperty,
        )

from . import auto_load
auto_load.init()

# --------------------------------------------------------------
# Register all operators and panels
# --------------------------------------------------------------

# Add-ons Preferences Update Panel

# Define Panel classes for updating
panels = (
        measureit_arch_main.SCENE_PT_MARCH_Settings,
        measureit_arch_main.MeasureitArchMainPanel,
        measureit_arch_render.MeasureitArchRenderPanel
        )

def update_panel(self, context):
    message = "MeasureIt-ARCH: Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass


# Append Precision settings to units panel
def precision_ui(self, context):
    layout = self.layout
    layout.use_property_decorate = False
    layout.use_property_split = True

    
    scene = context.scene
    col = layout.column()
    col.alignment = 'RIGHT'
    col.label(text="MeasureIt-ARCH Precision")
    col = layout.column()
    col.prop(scene, 'measureit_arch_gl_precision', text="Metric Precision")
    col.prop(scene, 'measureit_arch_imperial_precision', text="Imperial Precision")


class Measure_Pref(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    category = StringProperty(
            name="Tab Category",
            description="Choose a name for the category of the panel",
            default="MeasureIt-ARCH",
            update=update_panel
            )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.label(text="Tab Category:")
        col.prop(self, "category", text="")

# Define menu
# noinspection PyUnusedLocal
def register():
    auto_load.register()
    bpy.types.SCENE_PT_unit.append(precision_ui)

    # Define properties
    Scene.measureit_arch_debug_flip_text = BoolProperty(name="Debug Text Flip Vectors",
                                    description="Displys Text Card and View Vectors used to Flip Text",
                                    default=False)

    Scene.measureit_arch_inst_dims = BoolProperty(name="Instance Dimensions",
                                    description="NOTE: Instanced Dimensions text will not adapt to local changes in scale or rotation",
                                    default=False)

    Scene.measureit_arch_eval_mods = BoolProperty(name="Evaluate Modifiers",
                                    description="MeasureIt-ARCH will attempt to evaluate Modifiers before drawing, May make dimensions and linework unstable",
                                    default=False)

    Scene.measureit_arch_is_render_draw = BoolProperty(name="Is Render",
                                        description="Flag to use render size for draw aspect ratio",
                                        default=False)

    Scene.measureit_arch_show_gizmos = BoolProperty(name="Show Gizmos",
                                        description="(EXPERIMENTAL) Display Measureit-ARCH Gizmos",
                                        default=False)
    Scene.measureit_arch_dim_axis = EnumProperty(
                    items=(('X', "X", "X Axis"),
                           ('Y', "Y", "Y Axis"),
                           ('Z', "Z", "Z Axis")),
                    name="Axis",
                    description="Axis")

    Scene.measureit_arch_debug_text = BoolProperty(name="Debug Text",
                                        description="(DEBUG) Draw Debug Info For Text",
                                        default=False)

    Scene.viewPlane= EnumProperty(
                    items=(('99', "None", "No View Plane Selected",'EMPTY_AXIS',0),
                           ('XY', "XY Plane", "Optimize Dimension for XY Plane (Plan)",'AXIS_TOP',1),
                           ('YZ', "YZ Plane", "Optimize Dimension for YZ Plane (Elevation)",'AXIS_FRONT',2),
                           ('XZ', "XZ Plane", "Optimize Dimension for XZ Plane (Elevation)",'AXIS_SIDE',3)),
                    name="View Plane",
                    description="View Plane")   
    
    Scene.measureit_arch_imperial_precision= EnumProperty(
                items=(('1', "1\"", "1 Inch"),
                        ('2', "1/2\"", "1/2 Inch"),
                        ('4', "1/4\"", "1/4 Inch"),
                        ('8', "1/8\"", "1/8th Inch"),
                        ('16', "1/16\"", "1/16th Inch"),
                        ('32', "1/32\"", "1/32th Inch"),
                        ('64', "1/64\"", "1/64th Inch")),
                name="Imperial Precision",
                description="Measurement Precision for Imperial Units")                  
    Scene.measureit_arch_use_depth_clipping = BoolProperty(name="Use Depth Clipping",
                                             description="Lines Behind Objects Won't Be Rendered (Slower)",
                                             default=True)

    Scene.measureit_arch_default_color = FloatVectorProperty(
        name="Default color",
        description="Default Color",
        default=(0.0, 0.0, 0.0, 1.0),
        min=0.1,
        max=1,
        subtype='COLOR',
        size=4)

    Scene.measureit_arch_default_dimension_style = StringProperty(name="Default Style",
                                            description="Dimension Style to Use")   

    Scene.measureit_arch_default_annotation_style = StringProperty(name="Default Style",
                                            description="Annotation Style to Use")  

    Scene.measureit_arch_default_line_style = StringProperty(name="Default Style",
                                            description="Line Style to Use") 

    Scene.measureit_arch_set_annotation_use_style = BoolProperty(name="Set Annotation Style",
                                            description="Set Annotation Style on Creation",
                                            default=False)

    Scene.measureit_arch_set_dimension_use_style = BoolProperty(name="Set Dimension Style",
                                            description="Set Dimension Style on Creation",
                                            default=False)

    Scene.measureit_arch_set_line_use_style = BoolProperty(name="Set Line Style",
                                            description="Set Line Style on Creation",
                                            default=False)                                         

    Scene.measureit_arch_font_size = IntProperty(name="Text Size",
                                            description="Default text size",
                                            default=14, min=10, max=150)
    Scene.measureit_arch_hint_space = FloatProperty(name='Separation', min=0, max=100, default=0.1,
                                               precision=3,
                                               description="Default distance to display measure")
    
    Scene.measureit_arch_gl_ghost = BoolProperty(name="All",
                                            description="Display measures for all objects,"
                                                        " not only selected",
                                            default=True)
                                            
    Scene.measureit_arch_gl_txt = StringProperty(name="Text", maxlen=256,
                                            description="Short description (use | for line break)")
    Scene.measureit_arch_gl_width = IntProperty(name="Lineweight",
                                            description="Default Line Weight",
                                            default=3, min=0, max=20)

    Scene.measureit_arch_gl_precision = IntProperty(name='Precision', min=0, max=5, default=2,
                                               description="Number of decimal precision")
    Scene.measureit_arch_gl_show_d = BoolProperty(name="Show Dimension Text",
                                             description="Display Dimension Text",
                                             default=True)
    Scene.measureit_arch_gl_show_n = BoolProperty(name="ShowName",
                                             description="Display texts",
                                             default=False)
    Scene.measureit_arch_scale = BoolProperty(name="Scale",
                                         description="Use scale factor",
                                         default=False)
    Scene.measureit_arch_scale_factor = FloatProperty(name='Factor', min=0.001, max=9999999,
                                                 default=1.0,
                                                 precision=3,
                                                 description="Scale factor 1:x")
    Scene.measureit_arch_scale_color = FloatVectorProperty(name="Scale color",
                                                      description="Scale Color",
                                                      default=(1, 1, 0, 1.0),
                                                      min=0.1,
                                                      max=1,
                                                      subtype='COLOR',
                                                      size=4)
    Scene.measureit_arch_scale_font = IntProperty(name="Font",
                                             description="Text size",
                                             default=14, min=10, max=150)
    Scene.measureit_arch_scale_pos_x = IntProperty(name="X Position",
                                              description="Margin on the X axis",
                                              default=5,
                                              min=0,
                                              max=100)
    Scene.measureit_arch_scale_pos_y = IntProperty(name="Y Position",
                                              description="Margin on the Y axis",
                                              default=5,
                                              min=0,
                                              max=100)
    Scene.measureit_arch_gl_scaletxt = StringProperty(name="ScaleText", maxlen=48,
                                                 description="Scale title",
                                                 default="Scale:")
    Scene.measureit_arch_scale_precision = IntProperty(name='Precision', min=0, max=5, default=0,
                                                  description="Number of decimal precision")
    Scene.measureit_arch_ovr = BoolProperty(name="Override",
                                       description="Override colors and fonts",
                                       default=False)
    Scene.measureit_arch_ovr_font = IntProperty(name="Font",
                                           description="Override text size",
                                           default=14, min=10, max=150)
    Scene.measureit_arch_ovr_color = FloatVectorProperty(name="Override color",
                                                    description="Override Color",
                                                    default=(1, 0, 0, 1.0),
                                                    min=0.1,
                                                    max=1,
                                                    subtype='COLOR',
                                                    size=4)
    Scene.measureit_arch_ovr_width = IntProperty(name='Override width', min=1, max=10, default=1,
                                            description='override line width')

    Scene.measureit_arch_ovr_font_rotation = IntProperty(name='Rotate', min=0, max=360, default=0,
                                                    description="Text rotation in degrees")

    Scene.measureit_arch_ovr_font_align = EnumProperty(items=(('L', "Left Align", "Use current render"),
                                                         ('C', "Center Align", ""),
                                                         ('R', "Right Align", "")),
                                                  name="Align Font",
                                                  description="Set Font Alignment")

    Scene.measureit_arch_hide_units = BoolProperty(name="hide_units",
                                              description="Do not display unit of measurement on viewport",
                                              default=False)
    Scene.measureit_arch_render = BoolProperty(name="Render",
                                          description="Save an image with measures over"
                                                      " render image",
                                          default=False)

    Scene.measureit_arch_sum = EnumProperty(items=(('99', "-", "Select a group for sum"),
                                              ('0', "A", ""),
                                              ('1', "B", ""),
                                              ('2', "C", ""),
                                              ('3', "D", ""),
                                              ('4', "E", ""),
                                              ('5', "F", ""),
                                              ('6', "G", ""),
                                              ('7', "H", ""),
                                              ('8', "I", ""),
                                              ('9', "J", ""),
                                              ('10', "K", ""),
                                              ('11', "L", ""),
                                              ('12', "M", ""),
                                              ('13', "N", ""),
                                              ('14', "O", ""),
                                              ('15', "P", ""),
                                              ('16', "Q", ""),
                                              ('17', "R", ""),
                                              ('18', "S", ""),
                                              ('19', "T", ""),
                                              ('20', "U", ""),
                                              ('21', "V", ""),
                                              ('22', "W", ""),
                                              ('23', "X", ""),
                                              ('24', "Y", ""),
                                              ('25', "Z", "")),
                                       name="Sum in Group",
                                       description="Add segment length in selected group")

    Scene.measureit_arch_rf = BoolProperty(name="render_frame",
                                      description="Add a frame in render output",
                                      default=False)
    Scene.measureit_arch_rf_color = FloatVectorProperty(name="Fcolor",
                                                   description="Frame Color",
                                                   default=(0.9, 0.9, 0.9, 1.0),
                                                   min=0.1,
                                                   max=1,
                                                   subtype='COLOR',
                                                   size=4)
    Scene.measureit_arch_rf_border = IntProperty(name='fborder ', min=1, max=1000, default=10,
                                            description='Frame space from border')
    Scene.measureit_arch_rf_line = IntProperty(name='fline', min=1, max=10, default=1,
                                          description='Line width for border')

    Scene.measureit_arch_glarrow_a = EnumProperty(items=(('99', "--", "No arrow"),
                                                    ('1', "Line",
                                                     "The point of the arrow are lines"),
                                                    ('2', "Triangle",
                                                     "The point of the arrow is triangle"),
                                                    ('3', "TShape",
                                                     "The point of the arrow is a T")),
                                             name="A end",
                                             description="Add arrows to point A")
    Scene.measureit_arch_glarrow_b = EnumProperty(items=(('99', "--", "No arrow"),
                                                    ('1', "Line",
                                                     "The point of the arrow are lines"),
                                                    ('2', "Triangle",
                                                     "The point of the arrow is triangle"),
                                                    ('3', "TShape",
                                                     "The point of the arrow is a T")),
                                             name="B end",
                                             description="Add arrows to point B")
    Scene.measureit_arch_glarrow_s = IntProperty(name="Size",
                                            description="Arrow size",
                                            default=15, min=6, max=500)

    Scene.measureit_arch_debug = BoolProperty(name="Debug",
                                         description="Display information for debuging"
                                                     " (expand/collapse for enabling or disabling)"
                                                     " this information is only renderered for "
                                                     "selected objects",
                                         default=False)
    Scene.measureit_arch_debug_select = BoolProperty(name="Selected",
                                                description="Display information "
                                                            "only for selected items",
                                                default=False)
    Scene.measureit_arch_debug_vertices = BoolProperty(name="Vertices",
                                                  description="Display vertex index number",
                                                  default=True)
    Scene.measureit_arch_debug_objects = BoolProperty(name="Objects",
                                                 description="Display object scene index number",
                                                 default=False)
    Scene.measureit_arch_debug_vert_loc = BoolProperty(name="Location",
                                                  description="Display vertex location",
                                                  default=False)
    Scene.measureit_arch_debug_object_loc = BoolProperty(name="Location",
                                                    description="Display object location",
                                                    default=False)
    Scene.measureit_arch_debug_edges = BoolProperty(name="Edges",
                                               description="Display edge index number",
                                               default=False)
    Scene.measureit_arch_debug_faces = BoolProperty(name="Faces",
                                               description="Display face index number",
                                               default=False)
    Scene.measureit_arch_debug_normals = BoolProperty(name="Normals",
                                                 description="Display face normal "
                                                             "vector and creation order",
                                                 default=False)
    Scene.measureit_arch_debug_normal_details = BoolProperty(name="Details",
                                                        description="Display face normal details",
                                                        default=True)
    Scene.measureit_arch_debug_font = IntProperty(name="Font",
                                             description="Debug text size",
                                             default=14, min=10, max=150)
    Scene.measureit_arch_debug_vert_color = FloatVectorProperty(name="Debug color",
                                                           description="Debug Color",
                                                           default=(1, 0, 0, 1.0),
                                                           min=0.1,
                                                           max=1,
                                                           subtype='COLOR',
                                                           size=4)
    Scene.measureit_arch_debug_face_color = FloatVectorProperty(name="Debug face color",
                                                           description="Debug face Color",
                                                           default=(0, 1, 0, 1.0),
                                                           min=0.1,
                                                           max=1,
                                                           subtype='COLOR',
                                                           size=4)
    Scene.measureit_arch_debug_norm_color = FloatVectorProperty(name="Debug vector color",
                                                           description="Debug vector Color",
                                                           default=(1.0, 1.0, 0.1, 1.0),
                                                           min=0.1,
                                                           max=1,
                                                           subtype='COLOR',
                                                           size=4)
    Scene.measureit_arch_debug_edge_color = FloatVectorProperty(name="Debug vector color",
                                                           description="Debug vector Color",
                                                           default=(0.1, 1.0, 1.0, 1.0),
                                                           min=0.1,
                                                           max=1,
                                                           subtype='COLOR',
                                                           size=4)
    Scene.measureit_arch_debug_obj_color = FloatVectorProperty(name="Debug vector color",
                                                          description="Debug vector Color",
                                                          default=(1.0, 1.0, 1.0, 1.0),
                                                          min=0.1,
                                                          max=1,
                                                          subtype='COLOR',
                                                          size=4)
    Scene.measureit_arch_debug_normal_size = FloatProperty(name='Len', min=0.001, max=9,
                                                      default=0.5,
                                                      precision=2,
                                                      description="Normal arrow size")
    Scene.measureit_arch_debug_width = IntProperty(name='Debug width', min=1, max=10, default=2,
                                              description='Vector line thickness')
    Scene.measureit_arch_debug_precision = IntProperty(name='Metric Precision', min=0, max=5, default=1,
                                                  description="Number of Decimal Places for Metric Measurements")
    Scene.measureit_arch_debug_vert_loc_toggle = EnumProperty(items=(('1', "Local",
                                                                 "Uses local coordinates"),
                                                                ('2', "Global",
                                                                 "Uses global coordinates")),
                                                         name="Coordinates",
                                                         description="Choose coordinate system")
    Scene.measureit_arch_font_rotation = IntProperty(name='Rotate', min=0, max=360, default=0,
                                                description="Default text rotation in degrees")
    Scene.measureit_arch_font_align = EnumProperty(items=(('L', "Left Align", "Use current render"),
                                                     ('C', "Center Align", ""),
                                                     ('R', "Right Align", "")),
                                              name="Align Font",
                                              description="Set Font Alignment")

    # OpenGL flag
    wm = WindowManager
    # register internal property
    wm.measureit_arch_run_opengl = BoolProperty(default=False)
    
def unregister():
    auto_load.unregister()
    bpy.types.SCENE_PT_unit.remove(precision_ui)
    # Remove properties 
    del Scene.measureit_arch_default_color
    del Scene.measureit_arch_font_size
    del Scene.measureit_arch_hint_space
    del Scene.measureit_arch_gl_ghost
    del Scene.measureit_arch_gl_txt
    del Scene.measureit_arch_gl_precision
    del Scene.measureit_arch_gl_show_d
    del Scene.measureit_arch_gl_show_n
    del Scene.measureit_arch_scale
    del Scene.measureit_arch_scale_factor
    del Scene.measureit_arch_scale_color
    del Scene.measureit_arch_scale_font
    del Scene.measureit_arch_scale_pos_x
    del Scene.measureit_arch_scale_pos_y
    del Scene.measureit_arch_gl_scaletxt
    del Scene.measureit_arch_scale_precision
    del Scene.measureit_arch_ovr
    del Scene.measureit_arch_ovr_font
    del Scene.measureit_arch_ovr_color
    del Scene.measureit_arch_ovr_width
    del Scene.measureit_arch_ovr_font_rotation
    del Scene.measureit_arch_ovr_font_align
    del Scene.measureit_arch_hide_units
    del Scene.measureit_arch_render
    del Scene.measureit_arch_sum
    del Scene.measureit_arch_rf
    del Scene.measureit_arch_rf_color
    del Scene.measureit_arch_rf_border
    del Scene.measureit_arch_rf_line
    del Scene.measureit_arch_glarrow_a
    del Scene.measureit_arch_glarrow_b
    del Scene.measureit_arch_glarrow_s
    del Scene.measureit_arch_debug
    del Scene.measureit_arch_debug_select
    del Scene.measureit_arch_debug_vertices
    del Scene.measureit_arch_debug_objects
    del Scene.measureit_arch_debug_edges
    del Scene.measureit_arch_debug_faces
    del Scene.measureit_arch_debug_normals
    del Scene.measureit_arch_debug_normal_details
    del Scene.measureit_arch_debug_font
    del Scene.measureit_arch_debug_vert_color
    del Scene.measureit_arch_debug_face_color
    del Scene.measureit_arch_debug_norm_color
    del Scene.measureit_arch_debug_edge_color
    del Scene.measureit_arch_debug_obj_color
    del Scene.measureit_arch_debug_normal_size
    del Scene.measureit_arch_debug_width
    del Scene.measureit_arch_debug_precision
    del Scene.measureit_arch_debug_vert_loc
    del Scene.measureit_arch_debug_object_loc
    del Scene.measureit_arch_debug_vert_loc_toggle
    del Scene.measureit_arch_font_rotation
    del Scene.measureit_arch_font_align

    # remove OpenGL data
    measureit_arch_main.ShowHideViewportButton.handle_remove(measureit_arch_main.ShowHideViewportButton, bpy.context)
    wm = bpy.context.window_manager
    p = 'measureit_arch_run_opengl'
    if p in wm:
        del wm[p]

if __name__ == '__main__':
    register()
