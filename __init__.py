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
    "version" : (1, 0, 0),
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
    vary_height : BoolProperty(name = "Vary Layer Height", description = "If checked: Use uniform thickness and all objects are the same height. \nIf unchecked: Random thickness is used between min and max values.", default = True)
    make_cubes : BoolProperty(name = "Make Only Cubes", description = "If checked: Only squares and rectangles are created. \nIf unchecked: Random ngons are created", default = True)
    cuts : IntProperty(name = "Number of Cuts", description = "How cuts should be made", default = 1)
    rec_cuts : IntProperty(name = "Number of Recursive Cuts", description = "How recursive cuts should be made.\nNOTE: This can take a long time with higher values. Be careful.", default = 0)
    rec_chance : IntProperty(name = "Chance of Recursive Cuts", description = "Percent chance of recursive cuts on each piece", default = 100, min = 0, max = 100)
    use_solidify_bool : BoolProperty(name = "Use Solidify", description = "Should a Solidify Modifier be added", default = False)
    solidify_thickness : FloatProperty(name  = "Thickness", description = "Solidify Modifier Thickness", default = 0.1)
    solidify_thickness_min : FloatProperty(name  = "Min", description = "Minimum Solidify Thickness", default = 0.1)
    solidify_thickness_max : FloatProperty(name  = "Max", description = "Maximum Solidify Thickness", default = 0.9)
    use_bevel_bool : BoolProperty(name = "Use Bevel", description = "Should A Bevel Modifier be added", default = False)
    bevel_width_float : FloatProperty(name  = "Bevel Width", description = "Bevel Width", default = 0.002)
    bevel_seg_int : IntProperty(name = "Bevel Segments", description = "How many Bevel Segments", default = 1, min = 1)
    use_subd_bool : BoolProperty(name = "Use Subdivision Mod", description = "Should A Subdivision Surface Modifier be added", default = False)
    sub_d_levels: IntProperty(name = "SubD Levels", description = "How many Subdivision Surface Levels", default = 1, min = 1)

def RandomNum(dim):
    return random.uniform(-dim,dim)

def RandVector(object_center, dim):
    return (RandomNum(dim[0]) + object_center[0],RandomNum(dim[1]) + object_center[1],RandomNum(dim[2]) + object_center[2])

def PickYAxis():
    num = random.randint(0,1)
    if num == 0:
        return True
    else:
        return False

def GenerateShapes():
    #get props
    rand_shape_props = bpy.context.scene.rand_shape_prop
    cubes = rand_shape_props.make_cubes
    vary_layer_height = rand_shape_props.vary_height
    number_of_cuts = rand_shape_props.cuts
    num_of_rec = rand_shape_props.rec_cuts
    chance_of_rec = rand_shape_props.rec_chance
    use_solidify = rand_shape_props.use_solidify_bool
    solidify_mod_thickness = rand_shape_props.solidify_thickness
    solidify_thickness_min = rand_shape_props.solidify_thickness_min
    solidify_thickness_max = rand_shape_props.solidify_thickness_max
    use_bevel = rand_shape_props.use_bevel_bool
    bev_width = rand_shape_props.bevel_width_float
    bevel_seg = rand_shape_props.bevel_seg_int
    use_subd = rand_shape_props.use_subd_bool
    sub_d_lev = rand_shape_props.sub_d_levels

    #creates plane otherwise use current selection
    if bpy.context.active_object == None:
        bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=(0, 0, 0))
    
    #get object location to add to bisect vector for 
    # objects not at world center
    obj = bpy.context.active_object

    objects_to_cut = []
    new_objects = []
    objects_to_cut.append(obj)
    cutting = True

    #num of recs defaults to zero meaning no recursion. add one to make sure we cut selected object atleast once
    for r in range(num_of_rec + 1):
        for ob in objects_to_cut:
            if r > 0: # first loop always cuts otherwise determine if recursive cuts happen
                num = random.randint(0, 100)
                if num in range(0, chance_of_rec):
                    cutting = True
                else:
                    cutting = False
            loc = ob.location
            #get dimension - 10 percent to cut each piece
            #used in RandomNum and RandVector to give random cut values within dimensions of current object
            dim = []
            for value in ob.dimensions:
                tmp = (value / 2) - ((value / 2) * .1)
                dim.append(tmp)
            
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[ob.name].select_set(True)
            bpy.ops.object.shade_smooth()
            bpy.ops.object.editmode_toggle()

            if cutting:
                for i in range(number_of_cuts):
                    bpy.ops.mesh.select_all(action='SELECT')
                    if cubes: #creates cuts only on x or y axis
                        if PickYAxis():
                            #y axis
                            bpy.ops.mesh.bisect(plane_co=(RandomNum(dim[0]) + loc[0],loc[1],0), plane_no=(1, 0, 0))
                            #bpy.ops.mesh.bisect(plane_co=(RandomNum(),0,0), plane_no=(1, 0, 0))
                        else:
                            #x axis
                            bpy.ops.mesh.bisect(plane_co=(loc[0],RandomNum(dim[1]) + loc[1],0), plane_no=(0, 1, 0))
                            #bpy.ops.mesh.bisect(plane_co=(0,RandomNum(),0), plane_no=(0, 1, 0))
                    else: #creates random cuts
                        bpy.ops.mesh.bisect(plane_co=RandVector(loc,dim), plane_no=RandVector((0,0,0), dim))
                    bpy.ops.mesh.edge_split()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                bpy.ops.mesh.separate(type='LOOSE')
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                #add all created objects to new list
                new_objects.extend(bpy.context.selected_objects)
            else:
                bpy.ops.object.editmode_toggle()
                new_objects.append(ob)
        
        #clear list used for this loop and copy in newly created objects
        objects_to_cut.clear()
        objects_to_cut = new_objects.copy()
        new_objects.clear()

    #finishing settings
    if use_bevel or use_subd or use_solidify:
        for obj in objects_to_cut:
            if use_solidify:
                solidify_mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
                if vary_layer_height:
                    solidify_mod.thickness = random.uniform(-solidify_thickness_max, -solidify_thickness_min)
                else:
                    solidify_mod.thickness = solidify_mod_thickness
            if use_bevel:
                bevel_mod = obj.modifiers.new(name="Bevel", type='BEVEL')
                bevel_mod.width = bev_width
                bevel_mod.segments = bevel_seg
                bevel_mod.limit_method = 'ANGLE'
            if use_subd:
                subd_mod = obj.modifiers.new(name="Subdivision Surface", type='SUBSURF')
                subd_mod.levels = sub_d_lev

    

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
        layout.label(text="Cut Settings:")
        box1 = layout.box()
        box1_col1 = box1.column(align=False)
        box1_col1.prop(scene.rand_shape_prop, "cuts")
        box1_col1.prop(scene.rand_shape_prop, "rec_cuts")
        box1_col1.prop(scene.rand_shape_prop, "rec_chance")
        box1_col1.prop(scene.rand_shape_prop, "make_cubes")

        layout.label(text="Finishing Settings:")
        box2 = layout.box()
        box2_col = box2.column(align=False)
        box2_col.prop(scene.rand_shape_prop, "use_solidify_bool")
        use_solid = scene.rand_shape_prop.use_solidify_bool
        if use_solid:
            box2_col.separator()
            box2.label(text="Uniform Thickness")
            box2_col2 = box2.column(align=False)
            box2.label(text="Random Thickness")
            box2_col3 = box2.column(align=False)
            box2_col.prop(scene.rand_shape_prop, "vary_height")
            vary_bool = scene.rand_shape_prop.vary_height
            
            box2_col2.prop(scene.rand_shape_prop, "solidify_thickness")
            box2_row1 = box2_col3.row(align=True)
            box2_row1.prop(scene.rand_shape_prop, "solidify_thickness_min")
            box2_row1.prop(scene.rand_shape_prop, "solidify_thickness_max")
            if not vary_bool:
                box2_col2.enabled = True
                box2_col3.enabled = False
            else:
                box2_col2.enabled = False
                box2_col3.enabled = True
        
        box3 = layout.box()
        box3_col = box3.column(align=False)
        box3_col.prop(scene.rand_shape_prop, "use_bevel_bool")
        use_bevel = scene.rand_shape_prop.use_bevel_bool
        if use_bevel:
            box3_col1 = box3.column(align=False)
            box3_col1.prop(scene.rand_shape_prop, "bevel_width_float")
            box3_col1.prop(scene.rand_shape_prop, "bevel_seg_int")

        box4 = layout.box()
        box4_col = box4.column(align=False)
        box4_col.prop(scene.rand_shape_prop, "use_subd_bool")
        use_sub = scene.rand_shape_prop.use_subd_bool
        if use_sub:
            box4_col1 = box4.column(align=False)
            box4_col1.prop(scene.rand_shape_prop, "sub_d_levels")

        col2 = layout.column(align=False)
        col2.separator()
        col2.operator('view3d.random_shape', text="GenerateRandomShapes!")

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
