# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Random Shapes",
    "author" : "Ben Norris",
    "description" : "Generate Random Shapes",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
from bpy.props import (BoolProperty, StringProperty, IntProperty, FloatProperty, PointerProperty)
from bpy.types import (Panel, Operator, PropertyGroup)
import bmesh
import random
from mathutils import Vector

class RandomShapeProps(PropertyGroup):
    use_generated_object : BoolProperty(name = "Generate Object", description = "Should shapes be generated on a plane", default = False)
    vary_height : BoolProperty(name = "Vary Layer Height", description = "Should all objects be the same height", default = True)
    make_cubes : BoolProperty(name = "Make Only Cubes", description = "Should all objects be Cubes", default = True)
    num_of_layers : IntProperty(name = "Layers", description = "How many layers should be generated", default = 1)
    num_of_cuts : IntProperty(name = "Number of Cuts", description = "How cuts should each layer have", default = 1)
    solidify_thickness : FloatProperty(name  = "Thickness", description = "How thick each layer should be", default = 0.1)
    solidify_thickness_min : FloatProperty(name  = "Min", description = "Minimum Solidify Thickness", default = 0.1)
    solidify_thickness_max : FloatProperty(name  = "Max", description = "Maximum Solidify Thickness", default = 0.9)

def RandomNum():
    return random.uniform(-.9,.9)

def RandVector():
    return (RandomNum(),RandomNum(),RandomNum())

def PickYAxis():
    num = random.randint(0,1)
    if num == 0:
        return True
    else:
        return False

def GenerateShapes():
    #get props
    rand_shape_props = bpy.context.scene.rand_shape_prop
    generate_object = rand_shape_props.use_generated_object
    layers = rand_shape_props.num_of_layers
    cubes = rand_shape_props.make_cubes
    vary_layer_height = rand_shape_props.vary_height
    number_of_cuts = rand_shape_props.num_of_cuts
    solidify_mod_thickness = rand_shape_props.solidify_thickness
    solidify_thickness_min = rand_shape_props.solidify_thickness_min
    solidify_thickness_max = rand_shape_props.solidify_thickness_max

    #create random cube layers 
    for i in range(layers):
        #creates plane otherwise use current selection
        if generate_object:
            bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=(0, 0, i * -solidify_mod_thickness))
        bpy.ops.object.shade_smooth()
        bpy.ops.object.editmode_toggle()

        for i in range(number_of_cuts):
            bpy.ops.mesh.select_all(action='SELECT')
            if cubes: #creates cuts only on x or y axis
                if PickYAxis():
                    #y axis
                    bpy.ops.mesh.bisect(plane_co=(RandomNum(),0,0), plane_no=(1, 0, 0))
                else:
                    #x axis
                    bpy.ops.mesh.bisect(plane_co=(0,RandomNum(),0), plane_no=(0, 1, 0))
            else: #creates random cuts
                bpy.ops.mesh.bisect(plane_co=RandVector(), plane_no=RandVector())
            bpy.ops.mesh.edge_split()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        for obj in bpy.context.selected_objects:
            solidify_mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
            if vary_layer_height:
                solidify_mod.thickness = random.uniform(-solidify_thickness_max, -solidify_thickness_min)
            else:
                solidify_mod.thickness = solidify_mod_thickness
            bevel_mod = obj.modifiers.new(name="Bevel", type='BEVEL')
            bevel_mod.width = 0.005
            bevel_mod.segments = 2
            bevel_mod.limit_method = 'ANGLE'
            subd_mod = obj.modifiers.new(name="Subdivision Surface", type='SUBSURF')
            subd_mod.levels = 2

#operator
class Random_Shape_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.random_shape"
    bl_label = "Random Shape"
    bl_description = "Generate Random Shapes!"

    def execute(self, context):
        #Main Operator Here
        GenerateShapes()
        return{'FINISHED'}

#ui
class RANDOMSHAPE_PT_Panel(bpy.types.Panel):
    bl_idname = "Random_Shape_PT_Panel"
    bl_label = "Random Shape"
    bl_category = "Random Shape"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col1 = layout.column(align=False)
        col1.prop(scene.rand_shape_prop, "use_generated_object")
        col1.prop(scene.rand_shape_prop, "num_of_layers")
        col1.prop(scene.rand_shape_prop, "num_of_cuts")

        col1.prop(scene.rand_shape_prop, "vary_height")
        vary_bool = scene.rand_shape_prop.vary_height
        layout.label(text="Uniform Thickness")
        col2 = layout.column(align=False)
        col2.prop(scene.rand_shape_prop, "solidify_thickness")
        layout.label(text="Random Thickness")
        col3 = layout.column(align=False)
        row1 = col3.row(align=True)
        row1.prop(scene.rand_shape_prop, "solidify_thickness_min")
        row1.prop(scene.rand_shape_prop, "solidify_thickness_max")
        if not vary_bool:
            col2.enabled = True
            col3.enabled = False
        else:
            col2.enabled = False
            col3.enabled = True
        
        col4 = layout.column(align=False)
        col4.prop(scene.rand_shape_prop, "make_cubes")

        col4.separator()
        col4.operator('view3d.random_shape', text="GenerateRandomShapes!")

#blender addon reg, unreg
def register():
    bpy.utils.register_class(Random_Shape_OT_Operator)
    bpy.utils.register_class(RANDOMSHAPE_PT_Panel)
    bpy.utils.register_class(RandomShapeProps)
    bpy.types.Scene.rand_shape_prop = PointerProperty(type=RandomShapeProps)

def unregister():
    bpy.utils.unregister_class(Random_Shape_OT_Operator)
    bpy.utils.unregister_class(RANDOMSHAPE_PT_Panel)
    bpy.utils.unregister_class(RandomShapeProps)
    del bpy.types.Scene.rand_shape_prop 
