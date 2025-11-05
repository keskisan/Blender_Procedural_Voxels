import bpy
import bmesh
import random
import mathutils
import math

import numpy as np
from mathutils import Vector
import mathutils.noise

###########################
#Drawing voxels
###########################

def calculate_smooth_array(voxel_contents_array, smooth_value_array):
     #populate a new array with the average off all the voxel smooth types according to the voxel array number(type)
    vertex_smooth_count = np.zeros((len(voxel_contents_array) + 1, len(voxel_contents_array[1]) + 1, len(voxel_contents_array[1][1]) + 1))
    vertex_smooth_array = np.full((len(voxel_contents_array) + 1, len(voxel_contents_array[1]) + 1, len(voxel_contents_array[1][1]) + 1), -1000.55) #less than -100 considered empty
    for x in range(len(voxel_contents_array)):
        for y in range(len(voxel_contents_array[x])):
            for z in range(len(voxel_contents_array[x][y])):
                if voxel_contents_array[x][y][z] > 0: ###lllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll
                    #if vox_array[x][y][z] >= len(smooth_array): #vallue can be set to anything even outside array
                      #  smoothfactor = 0
                    #else:
                       # smoothfactor = smooth_array[int(vox_array[x][y][z])] 
                    smoothfactor = smooth_value_array[x][y][z]
                    
                    if vertex_smooth_array[x][y][z] < -100:
                        vertex_smooth_array[x][y][z] = smoothfactor
                    else:
                       vertex_smooth_array[x][y][z] = vertex_smooth_array[x][y][z] +  smoothfactor
                    vertex_smooth_count[x][y][z] += 1
                        
                    if vertex_smooth_array[x + 1][y][z] < -100:
                        vertex_smooth_array[x + 1][y][z] =  smoothfactor
                    else:
                        vertex_smooth_array[x + 1][y][z] = vertex_smooth_array[x + 1][y][z] +  smoothfactor
                    vertex_smooth_count[x + 1][y][z] += 1 
                          
                    if vertex_smooth_array[x][y + 1][z] < -100:
                        vertex_smooth_array[x][y + 1][z] =  smoothfactor
                    else:
                        vertex_smooth_array[x][y + 1][z] = vertex_smooth_array[x][y + 1][z] +  smoothfactor 
                    vertex_smooth_count[x][y + 1][z] += 1
                    
                    if vertex_smooth_array[x + 1][y + 1][z] < -100:
                        vertex_smooth_array[x + 1][y + 1][z] =  smoothfactor
                    else:
                        vertex_smooth_array[x + 1][y + 1][z] = vertex_smooth_array[x + 1][y + 1][z] + smoothfactor
                    vertex_smooth_count[x + 1][y + 1][z] += 1
                        
                        
                    if vertex_smooth_array[x][y][z + 1] < -100:
                        vertex_smooth_array[x][y][z + 1] =  smoothfactor
                    else:
                        vertex_smooth_array[x][y][z + 1] = vertex_smooth_array[x][y][z + 1] +  smoothfactor
                    vertex_smooth_count[x][y][z + 1] += 1
                        
                    if vertex_smooth_array[x + 1][y][z + 1] < -100:
                        vertex_smooth_array[x + 1][y][z + 1] = smoothfactor
                    else:
                        vertex_smooth_array[x + 1][y][z + 1] = vertex_smooth_array[x + 1][y][z + 1] + smoothfactor 
                    vertex_smooth_count[x + 1][y][z + 1] += 1
                     
                    if vertex_smooth_array[x][y + 1][z + 1] < -100:
                        vertex_smooth_array[x][y + 1][z + 1] = smoothfactor
                    else:
                        vertex_smooth_array[x][y + 1][z + 1] = vertex_smooth_array[x][y + 1][z + 1] + smoothfactor
                    vertex_smooth_count[x][y + 1][z + 1] += 1
                    
                    if vertex_smooth_array[x + 1][y + 1][z + 1] < -100:
                        vertex_smooth_array[x + 1][y + 1][z + 1] = smoothfactor
                    else:
                        vertex_smooth_array[x + 1][y + 1][z + 1] = vertex_smooth_array[x + 1][y + 1][z + 1] + smoothfactor
                    vertex_smooth_count[x + 1][y + 1][z + 1] += 1
                    
    for x in range(len(vertex_smooth_array)):
        for y in range(len(vertex_smooth_array[x])):
            for z in range(len(vertex_smooth_array[x][y])):                
                vertex_smooth_array[x][y][z] = vertex_smooth_array[x][y][z]/vertex_smooth_count[x][y][z]
                
    return vertex_smooth_array


def get_vertex_array_offset(vertex_smooth_array, x, y, z):
    #calculate offsets
    x_offset = 0
    if x > 0:
        if vertex_smooth_array[x - 1][y][z] > -100:
            x_offset -= vertex_smooth_array[x - 1][y][z]
    if x < len(vertex_smooth_array) - 1:
        if vertex_smooth_array[x + 1][y][z] > -100:
            x_offset += vertex_smooth_array[x + 1][y][z]
      
    y_offset = 0      
    if y > 0:
        if vertex_smooth_array[x][y - 1][z] > -100:
            y_offset -= vertex_smooth_array[x][y - 1][z]
    if y < len(vertex_smooth_array[1]) - 1:
        if vertex_smooth_array[x][y + 1][z] > -100:
            y_offset += vertex_smooth_array[x][y + 1][z]
            
    z_offset = 0      
    if z > 0:
        if vertex_smooth_array[x][y][z - 1] > -100:
            z_offset -= vertex_smooth_array[x][y][z - 1]
    if z < len(vertex_smooth_array[1][1]) - 1:
        if vertex_smooth_array[x][y][z + 1] > -100:
            z_offset += vertex_smooth_array[x][y][z + 1]
            
    #return final position
    return (x + x_offset, y + y_offset, z + z_offset)
 
 
def AddFace(vertex_smooth_array, pos_x, pos_y, pox_z, vert_coords, face_vert_indices, FaceCoordinates):
    vert_coords.append(get_vertex_array_offset(vertex_smooth_array, FaceCoordinates[0][0] + pos_x, FaceCoordinates[0][1] + pos_y, FaceCoordinates[0][2] + pox_z))
    vert_coords.append(get_vertex_array_offset(vertex_smooth_array, FaceCoordinates[1][0] + pos_x, FaceCoordinates[1][1] + pos_y, FaceCoordinates[1][2] + pox_z)) 
    vert_coords.append(get_vertex_array_offset(vertex_smooth_array, FaceCoordinates[2][0] + pos_x, FaceCoordinates[2][1] + pos_y, FaceCoordinates[2][2] + pox_z)) 
    vert_coords.append(get_vertex_array_offset(vertex_smooth_array, FaceCoordinates[3][0] + pos_x, FaceCoordinates[3][1] + pos_y, FaceCoordinates[3][2] + pox_z))
    
    length = len(vert_coords)
    
    face_vert_indices.append ((length - 4, length - 3, length - 2, length - 1)) 
    
def getUVCoords(X, Y, uvParams):
    """
    X, Y position of tile
    width, height total tiles to texture
    buffer stops bleed
    """
    buffer = uvParams["buffer"]
    Xvalue = 1 / uvParams["width"]
    Yvalue = 1 / uvParams["height"]
    startX = X * Xvalue
    startY = Y * Yvalue
    #bottom left, bottom right, top right, top left
    return ((startX + buffer, startY + buffer), (startX + Xvalue - buffer, startY + buffer), (startX + Xvalue - buffer, startY + Yvalue - buffer), (startX + buffer, startY + Yvalue - buffer))

 #-x, x, -y, y, -z, z #bottom, side, top 
    
#all params beyond uvFunction just used to potentailly modify uvs by uvFunction
def AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, facepos): #vertices I want always last 4
    face_array = uvFunction(uvFunctionParams, vert_coords, voxel_contents_array, face_array, x, y, z, facepos)#this is where faces uvs are modified
    bl, br, tr, tl = getUVCoords(face_array[x][y][z][facepos][0], face_array[x][y][z][facepos][1], uvParams) #X, Y  f
    uv_coords.append(br)
    uv_coords.append(tr)
    uv_coords.append(tl)
    uv_coords.append(bl)
    


def generate_square_voxels(vertex_smooth_array, voxel_contents_array, face_array, uvParams, uvFunction, uvFunctionParams):
    XPosCoordinates = ((1, 1, 0), (1, 1, 1), (1, 0, 1), (1, 0, 0))
    XNegCoordinates = ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))
    YPosCoordinates = ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))
    YNegCoordinates = ((1, 0, 0), (1, 0, 1), (0, 0, 1), (0, 0, 0))
    ZNegCoordinates = ((0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0))
    ZPosCoordinates = ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))
    
    vert_coords = []
    face_vert_indices = []
    
    uv_coords = []
    
    for x in range(len(voxel_contents_array)):
        for y in range(len(voxel_contents_array[x])):
            for z in range(len(voxel_contents_array[x][y])):
                if voxel_contents_array[x][y][z] > 0: #0 is empty space
                    
                    #add faces x axis
                    if x > 0:
                        if voxel_contents_array[x - 1][y][z] <= 0:
                            AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, XNegCoordinates)
                            AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, 0) #-x, x, -y, y, -z, z
                    else:
                        AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, XNegCoordinates)  
                        AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, 0)
                    if (x + 1) < len(voxel_contents_array):
                        if voxel_contents_array[x + 1][y][z] <= 0:
                            AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, XPosCoordinates)
                            AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z,1)
                    else:
                        AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, XPosCoordinates)
                        AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, 1)
                        
                    #add faces z axis
                    if y > 0:
                        if voxel_contents_array[x][y - 1][z] <= 0:
                            AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, YNegCoordinates)
                            AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, 2)
                    else:
                        AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, YNegCoordinates)
                        AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, 2)
                    if (y + 1) < len(voxel_contents_array[x]):
                        if voxel_contents_array[x][y + 1][z] <= 0:  
                            AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, YPosCoordinates)
                            AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, 3) 
                    else:
                        AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, YPosCoordinates)
                        AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, 3)
                   
                   #add faces y axis
                    if z > 0:
                        if voxel_contents_array[x][y][z - 1] <= 0:
                            AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, ZNegCoordinates)
                            AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, 4)
                    else:
                        AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, ZNegCoordinates)
                        AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, 4)
                    if (z + 1) < len(voxel_contents_array[x][y]):
                        if voxel_contents_array[x][y][z + 1] <= 0:
                            AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, ZPosCoordinates)
                            AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, 5)
                    else:
                        AddFace(vertex_smooth_array, x, y, z, vert_coords, face_vert_indices, ZPosCoordinates)
                        AddUVs(uv_coords, face_array, uvParams, uvFunction, uvFunctionParams, vert_coords, voxel_contents_array, x, y, z, 5)

    return (vert_coords, face_vert_indices, uv_coords)


def GenerateVoxels(voxel_contents_array, smooth_value_array, face_array, uvParams, uvFunction, uvFunctionParams): 
    vertex_smooth_array = calculate_smooth_array(voxel_contents_array, smooth_value_array)   
    
    verts, faces, uvs = generate_square_voxels(vertex_smooth_array, voxel_contents_array, face_array, uvParams, uvFunction, uvFunctionParams) 
    
    edges = []

    mesh_data = bpy.data.meshes.new("cube_data")
    mesh_data.from_pydata(verts, edges, faces)
    validMesh = mesh_data.validate()
    print("Mesh is valid (False is valid): " + str(validMesh))
    mesh_obj = bpy.data.objects.new("cube_object", mesh_data)
    
    uv_layer = mesh_obj.data.uv_layers.new(name='UVlayer')
    for loop in mesh_obj.data.loops:
        uv_layer.data[loop.index].uv = uvs[loop.index]
    
    bpy.context.collection.objects.link(mesh_obj)
          
    #merge faces into single object
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.editmode_toggle()
    

 
    
#################################
#offsetFunctions functions
#################################
from mathutils import Vector
import mathutils.noise

def get_displaced_position(
    position: Vector,
    noise_type: str = 'PERLIN_NEW',
    scale: float = 1.0,
    amplitude: float = 0.2,
    axis_mask: tuple = (True, True, True),
    seed_offset: Vector = Vector((0.0, 0.0, 0.0))
) -> Vector:
    """
    Calculates a noise-based offset for a single position vector and returns
    the new, displaced position.

    Args:
        position (Vector): The input 3D coordinate to displace.
        noise_type (str): The type of noise to use (e.g., 'PERLIN_NEW', 'CELLNOISE').
        scale (float): The scale of the noise pattern. Larger values mean finer detail.
        amplitude (float): The maximum strength of the displacement.
        axis_mask (tuple): A tuple of 3 booleans (X, Y, Z) to enable/disable
                           displacement on each axis.
        seed_offset (Vector): A vector to shift the noise field, acting as a seed.

    Returns:
        Vector: The new, displaced position vector (original position + noise offset).
    """
    # 1. Calculate the position in the noise field
    noise_input = (position * scale) + seed_offset
    
    # 2. Get a 3D noise vector (values are typically in the range -1.0 to 1.0)
    noise_vector = mathutils.noise.noise_vector(noise_input, noise_basis=noise_type)
    
    # 3. Apply the axis mask and amplitude to create the final offset
    mask_vector = Vector(axis_mask)
    final_offset = Vector((
        noise_vector.x * mask_vector.x,
        noise_vector.y * mask_vector.y,
        noise_vector.z * mask_vector.z
    )) * amplitude
    
    # 4. Return the original position with the offset applied
    return position + final_offset


#################################
#Fillvoxels Functions
#################################


def create_gradient_array(
    direction: Vector,
    min_val: float,
    max_val: float,
    dims: tuple,
    distort_func: callable = None,
    distort_parmeters: dict = None
) -> np.ndarray:
    """
    Creates a 3D NumPy array filled with a linear gradient.

    Args:
        direction (Vector): A mathutils.Vector defining the gradient's orientation.
        min_val (float): The minimum value of the gradient.
        max_val (float): The maximum value of the gradient.
        x (int): The width of the array.
        y (int): The height of the array.
        z (int): The depth of the array.

    Returns:
        np.ndarray: A (z, y, x) shaped array with the gradient.
    """
    # Normalize the direction vector to ensure correct projection
    direction.normalize()

    # Create a grid of coordinates.
    indices = np.indices(dims, dtype=np.float32)

    # Calculate the dot product of each coordinate with the direction vector.
    # This projects each point onto the direction vector, creating the gradient.

    if distort_func:
        modified_coords = np.zeros((3, dims[0], dims[1], dims[2]))
        for x in range(dims[0]):
            for y in range(dims[1]):
                for z in range(dims[2]):
                    new_pos = get_displaced_position(
                        position=Vector((indices[0][x][y][z], indices[1][x][y][z], indices[2][x][y][z])),
                        noise_type=distort_parmeters["NOISE"],
                        scale=distort_parmeters["SCALE"],
                        amplitude=distort_parmeters["AMPLITUDE"],
                        axis_mask=distort_parmeters["AXIS_MASK"]
                    )
                    modified_coords[0][x][y][z] = new_pos[0]
                    modified_coords[1][x][y][z] = new_pos[1] 
                    modified_coords[2][x][y][z] = new_pos[2] 
                    
                      
        gradient = (
        modified_coords[0] * direction.x +
        modified_coords[1] * direction.y +
        modified_coords[2] * direction.z
        )
    else:
        gradient = (
        indices[0] * direction.x +
        indices[1] * direction.y +
        indices[2] * direction.z
        )
    
    
    # Normalize the gradient to the range [0, 1]
    grad_min = gradient.min()
    grad_max = gradient.max()
    
    # Avoid division by zero if the gradient is flat
    if grad_max - grad_min != 0:
        gradient = (gradient - grad_min) / (grad_max - grad_min)
    else:
        gradient.fill(0.5) # If flat, just use a mid-value

    # Scale the normalized gradient to the desired [min_val, max_val] range
    gradient = gradient * (max_val - min_val) + min_val

    return gradient



def create_noise_array(
    dims: tuple,
    noise_type: str = 'PERLIN_NEW',
    offset: Vector = Vector((0.0, 0.0, 0.0)),
    scale: Vector = Vector((1.0, 1.0, 1.0)),
    distort_func: callable = None,
    distort_parmeters: dict = None
) -> np.ndarray:
    """
    Creates a 3D NumPy array filled with procedural noise from Blender.

    Note: This function can be slow for large dimensions as it iterates
    through each cell individually.

    Args:
        x (int): The width of the array.
        y (int): The height of the array.
        z (int): The depth of thearray.
        noise_type (str): The type of noise to generate. e.g., 'PERLIN_NEW',
                          'VORONOI_F1', 'CELLNOISE'.
        offset (Vector): A vector to shift the noise field.
        scale (Vector): A vector to scale the noise frequency. Larger values
                        result in finer, more detailed noise.

    Returns:
        np.ndarray: A (z, y, x) shaped array with the noise values.
    """
    noise_array = np.zeros(dims, dtype=np.float32)
    
    # Iterate through each point in the grid
    for x in range(dims[0]):
        for y in range(dims[1]):
            for z in range(dims[2]):
                # Calculate the coordinate to sample in the noise space
                if distort_func:
                    new_pos = get_displaced_position(
                        position=Vector((x, y, z)),
                        noise_type=distort_parmeters["NOISE"],
                        scale=distort_parmeters["SCALE"],
                        amplitude=distort_parmeters["AMPLITUDE"],
                        axis_mask=distort_parmeters["AXIS_MASK"]
                    )
                    coord = mathutils.Vector((
                        new_pos[0] * scale.x + offset.x,
                        new_pos[1] * scale.y + offset.y,
                        new_pos[2] * scale.z + offset.z
                    ))
                else:
                    coord = mathutils.Vector((
                        x * scale.x + offset.x,
                        y * scale.y + offset.y,
                        z * scale.z + offset.z
                    ))
                
                # Get the noise value and store it
                noise_val = mathutils.noise.noise(coord, noise_basis=noise_type)
                noise_array[x, y, z] = noise_val
                
    return noise_array




def create_gradient_array_with_profile(
    dimensions: tuple[int, int, int],
    direction: Vector,
    profile_dict: dict,
    min_val: float,
    max_val: float,
    distort_func=None,
    distort_parmeters=None
) -> np.ndarray:
    """
    Creates a 3D float array with a gradient perpendicular to 'direction',
    where the gradient's value distribution is controlled by 'profile_dict'.

    Args:
        dimensions (tuple[int, int, int]): The (X, Y, Z) dimensions of the array.
        direction (Vector): The normal vector of the gradient.
        profile_dict (dict): Maps normalized distance [0, 1] to normalized value [0, 1].
        min_val (float): The minimum value in the final array.
        max_val (float): The maximum value in the final array.

    Returns:
        np.ndarray: The created float array of shape (Z, Y, X).
    """
    X, Y, Z = dimensions
    
    if direction.length == 0:
        print("Error: Direction vector cannot be zero. Using (0, 0, 1).")
        direction = Vector((0.0, 0.0, 1.0))
    direction.normalize()

    # --- 1. Create Normalized Distance Grid [0.0 to 1.0] ---

    # Generate coordinate indices (shape: 3, Z, Y, X)
    indices = np.indices((X, Y, Z), dtype=np.float32)
    # Reorder to (X, Y, Z) for easier vector math: indices[2] is X, [1] is Y, [0] is Z
    
    # Project coordinates onto the normalized direction vector
    # This gives the scalar distance of each voxel along the direction axis.
    if distort_func:
        modified_indices = np.zeros((3, dims[0], dims[1], dims[2]))
        for x in range(dims[0]):
            for y in range(dims[1]):
                for z in range(dims[2]):
                    new_pos = get_displaced_position(
                        position=Vector((indices[0][x][y][z], indices[1][x][y][z], indices[2][x][y][z])),
                        noise_type=distort_parmeters["NOISE"],
                        scale=distort_parmeters["SCALE"],
                        amplitude=distort_parmeters["AMPLITUDE"],
                        axis_mask=distort_parmeters["AXIS_MASK"]
                    )
                    modified_indices[0][x][y][z] = new_pos[0]
                    modified_indices[1][x][y][z] = new_pos[1] 
                    modified_indices[2][x][y][z] = new_pos[2] 
                    
                      
        distance_grid = (
        modified_indices[0] * direction.x +
        modified_indices[1] * direction.y +
        modified_indices[2] * direction.z
        )
    else:
        distance_grid = (
            indices[0] * direction.x +
            indices[1] * direction.y +
            indices[2] * direction.z
        )

    # Normalize the projected distances to the range [0.0, 1.0]
    min_dist = distance_grid.min()
    max_dist = distance_grid.max()
    dist_range = max_dist - min_dist
    
    if dist_range < 1e-6:
        # If the range is zero (e.g., 1x1x1 array), return a uniform array
        return np.full((X, Y, Z), min_val + (max_val - min_val) * (profile_dict.get(0.0, 0.0) if profile_dict else 0.5), dtype=np.float32)

    normalized_distance = (distance_grid - min_dist) / dist_range

    # --- 2. Prepare Profile Data for Interpolation ---
    
    # Start with the user-provided profile points
    profile_points = profile_dict.copy()
    
    # Apply default boundary conditions if not present (as required)
    if 0.0 not in profile_points:
        profile_points[0.0] = 0.0
    if 1.0 not in profile_points:
        profile_points[1.0] = 1.0
        
    # Sort the dictionary keys to ensure proper interpolation order
    sorted_keys = sorted(profile_points.keys())
    
    # Extract the sorted normalized distances (x-coordinates for interpolation)
    x_interp = np.array(sorted_keys, dtype=np.float32)
    
    # Extract the sorted normalized values (y-coordinates for interpolation)
    y_interp = np.array([profile_points[k] for k in sorted_keys], dtype=np.float32)

    # --- 3. Interpolate Values ---
    
    # Use np.interp to look up the normalized value for every point in the grid.
    # It linearly interpolates between the provided (x_interp, y_interp) points.
    # The output is a normalized value array [0.0 to 1.0].
    normalized_value_array = np.interp(
        normalized_distance, 
        x_interp, 
        y_interp
    ).astype(np.float32)
    
    # --- 4. Scale to Final Range [min_val to max_val] ---
    
    value_range = max_val - min_val
    final_array = min_val + normalized_value_array * value_range

    return final_array


def create_layered_array(
    dims: tuple,
    direction: Vector,
    min_val: float,
    max_val: float,
    min_layer_thickness: float,
    max_layer_thickness: float,
    distort_func: callable = None,
    distort_parmeters: dict = None
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Creates a 3D NumPy array filled with layers of random value and thickness.
    The layers are oriented perpendicular to the provided direction vector.

    Args:
        direction (Vector): The normal vector of the layers.
        min_val (float): The minimum random value for a layer.
        max_val (float): The maximum random value for a layer.
        min_layer_thickness (float): The minimum thickness of a layer.
        max_layer_thickness (float): The maximum thickness of a layer.
        x (int): The width of the array.
        y (int): The height of the array.
        z (int): The depth of the array.

    Returns:
        np.ndarray: A (z, y, x) shaped array filled with the layered data.
    """
    # --- 1. Input Validation ---
    if direction.length == 0:
        print("Error: Direction vector cannot be zero.")
        return np.zeros(dims, dtype=np.float32)
    direction.normalize()

    if min_layer_thickness <= 0 or max_layer_thickness <= 0:
        print("Error: Layer thickness must be positive.")
        min_layer_thickness = max(0.001, min_layer_thickness)
        max_layer_thickness = max(0.001, max_layer_thickness)

    # --- 2. Project Coordinates onto the Direction Vector ---
    # Create a grid of coordinates. Shape is (3, z, y, x).
    # indices[0]=z, indices[1]=y, indices[2]=x
    indices = np.indices(dims, dtype=np.float32)

    # Calculate the dot product to find the projected distance of each point.
    # This creates a 3D grid containing a smooth gradient along the direction.
    if distort_func:
        modified_coords = np.zeros((3, dims[0], dims[1], dims[2]))
        for x in range(dims[0]):
            for y in range(dims[1]):
                for z in range(dims[2]):
                    new_pos = get_displaced_position(
                        position=Vector((indices[0][x][y][z], indices[1][x][y][z], indices[2][x][y][z])),
                        noise_type=distort_parmeters["NOISE"],
                        scale=distort_parmeters["SCALE"],
                        amplitude=distort_parmeters["AMPLITUDE"],
                        axis_mask=distort_parmeters["AXIS_MASK"]
                    )
                    modified_coords[0][x][y][z] = new_pos[0]
                    modified_coords[1][x][y][z] = new_pos[1] 
                    modified_coords[2][x][y][z] = new_pos[2] 
                    
                      
        distance_grid = (
        modified_coords[0] * direction.x +
        modified_coords[1] * direction.y +
        modified_coords[2] * direction.z
        )
    else:
        distance_grid = (
        indices[0] * direction.x +
        indices[1] * direction.y +
        indices[2] * direction.z
        )
    

    # --- 3. Define Layer Boundaries and Values ---
    min_dist = distance_grid.min()
    max_dist = distance_grid.max()

    boundaries = []
    layer_values = []
    layer_ids = []
    layer_smooth_values = []
    
    current_distance = min_dist
    current_layer_id = 0

    # Step through the entire distance range, creating layers
    while current_distance < max_dist:
        # Assign values for the upcoming layer
        layer_values.append(np.random.uniform(min_val, max_val))
        layer_ids.append(current_layer_id)
        layer_smooth_values.append(np.random.uniform(-0.4, 0.6))

        current_layer_id += 1

        # Determine a random thickness and define the next boundary
        thickness = np.random.uniform(min_layer_thickness, max_layer_thickness)
        current_distance += thickness
        boundaries.append(current_distance)

    # --- 4. Assign Layer Values to the Grid ---
    # np.digitize is a highly optimized way to find which "bin" or layer
    # each point in our distance_grid falls into.
    # It returns an array of indices corresponding to the layer number.
    indices = np.digitize(distance_grid, bins=boundaries)

     # Convert lists to NumPy arrays for fast indexing
    all_layer_values = np.array(layer_values, dtype=np.float32)
    all_layer_ids = np.array(layer_ids, dtype=np.int32)
    all_layer_smooth = np.array(layer_smooth_values, dtype=np.float32)

    # Use "fancy indexing" to populate the final arrays from the layer data
    result_array = all_layer_values[indices]
    contents_array = all_layer_ids[indices]
    smooth_value_array = all_layer_smooth[indices]
    print(smooth_value_array)
    return result_array, contents_array, smooth_value_array






def create_projected_noise_array(
    dims: tuple,
    noise_type: str,
    direction: Vector,
    scale: Vector = Vector((1.0, 1.0, 0.0)),
    offset: Vector = Vector((0.0, 0.0, 0.0)),
    third_axis_distortion_amount = 0.01,
    distort_func=None,
    distort_parmeters=None
) -> np.ndarray:
    """
    Creates a 3D NumPy array filled with a 2D noise pattern projected
    along a direction vector.

    Note: This function can be slow for large dimensions because Blender's
    noise function is not vectorized and must be called for each cell.

    Args:
        x (int): The width of the array.
        y (int): The height of the array.
        z (int): The depth of the array.
        noise_type (str): The type of noise, e.g., 'PERLIN_NEW', 'VORONOI_F1'.
        direction (Vector): The 3D vector along which the 2D noise is projected.
        scale (Vector): Scales the noise frequency. Only the X and Y components
                        are used for the 2D noise plane.
        offset (Vector): Shifts the noise field. Only the X and Y components
                         are used.

    Returns:
        np.ndarray: A (z, y, x) shaped array with the projected noise values.
    """
    # --- 1. Input Validation and Basis Setup ---
    if direction.length == 0:
        print("Error: Direction vector cannot have zero length. Using default Z-axis.")
        direction = Vector((0.0, 0.0, 1.0))
    direction.normalize()

    # Create two orthonormal vectors (u_vec, v_vec) that form a 2D plane
    # with the 'direction' vector as its normal.
    temp_vec = Vector((0.0, 0.0, 1.0))
    if abs(direction.dot(temp_vec)) > 0.99:
        # If the direction is too close to the Z-axis, use the X-axis instead
        temp_vec = Vector((1.0, 0.0, 0.0))

    u_vec = direction.cross(temp_vec).normalized()
    v_vec = direction.cross(u_vec).normalized()

    # --- 2. Create and Project 3D Coordinates ---
    # Create a grid of 3D coordinates.
    indices = np.indices(dims, dtype=np.float32)
    # Reorder from (3, z, y, x) with (z,y,x) values to (z, y, x, 3) with (x,y,z) vectors
    coords_3d = np.stack((indices[0], indices[1], indices[2]), axis=-1)

    # Project the 3D coordinates onto the 2D plane's basis vectors (u_vec, v_vec)
    # to get the 2D coordinates for noise sampling.
    coords_u = np.dot(coords_3d, u_vec)
    coords_v = np.dot(coords_3d, v_vec)
    coords_w = np.dot(coords_3d, direction)

    # --- 3. Apply Scale and Offset ---
    coords_u = coords_u * scale.x + offset.x
    coords_v = coords_v * scale.y + offset.y
    coords_w = coords_w * scale.y + offset.y
    
    # --- 4. Sample Noise ---
    print(f"Generating projected '{noise_type}' noise for (dims) array...")
    result_array = np.zeros(dims, dtype=np.float32)

    # Iterate through each cell to sample the noise
    for x in range(dims[0]):
        for y in range(dims[1]):
            for z in range(dims[2]):
                # Get the pre-calculated 2D coordinate for this 3D position
                u = coords_u[x, y, z]
                v = coords_v[x, y, z]
                w = coords_w[x, y, z]
                
                if distort_func:
                    new_pos = get_displaced_position(
                        position=Vector((u, v, w)),
                        noise_type=distort_parmeters["NOISE"],
                        scale=distort_parmeters["SCALE"],
                        amplitude=distort_parmeters["AMPLITUDE"],
                        axis_mask=distort_parmeters["AXIS_MASK"]
                    )
                    noise_val = mathutils.noise.noise(Vector((new_pos[0], new_pos[1], new_pos[2]*third_axis_distortion_amount)), noise_basis=noise_type)
                    result_array[x, y, z] = noise_val
                else:
                    # Sample the noise using a 2D vector
                    noise_val = mathutils.noise.noise(Vector((u, v, 0.0)), noise_basis=noise_type)
                    result_array[x, y, z] = noise_val
    
    print("Noise generation complete.")
    return result_array



def create_projected_image_array_numpy(
    dims: tuple,
    image: bpy.types.Image,
    direction: Vector,
    scale: Vector = Vector((1.0, 1.0, 0.0)),
    offset: Vector = Vector((0.0, 0.0, 0.0)),
    interpolation: str = 'linear',
    tile: bool = True,
    distort_func=None,
    distort_parmeters=None
) -> np.ndarray:
    """
    Creates a 3D NumPy array by projecting a 2D image along a direction vector,
    using only NumPy for interpolation. (Corrected Version)

    Args:
        x (int): The width of the array.
        y (int): The height of the array.
        z (int): The depth of the array.
        image (bpy.types.Image): The Blender image datablock to project.
        direction (Vector): The 3D vector along which the image is projected.
        scale (Vector): Scales the image size on the projection plane.
        offset (Vector): Shifts the image on the projection plane.
        interpolation (str): 'linear' for smooth sampling or 'nearest' for sharp.
        tile (bool): If True, the image repeats. If False, areas outside are black.

    Returns:
        np.ndarray: A (z, y, x) shaped array with the projected image data.
    """
    # --- 1. Input Validation and Data Preparation ---
    if not image or not image.has_data:
        print("Error: Invalid image. Returning a black array.")
        return np.zeros(dims, dtype=np.float32)
    direction.normalize()

    img_w, img_h = image.size
    img_pixels = np.array(image.pixels)
    image_data = img_pixels[::4].reshape((img_h, img_w))
    

    # --- 2. Define the Projection Plane ---
    temp_vec = Vector((0.0, 0.0, 1.0))
    if abs(direction.dot(temp_vec)) > 0.99:
        temp_vec = Vector((1.0, 0.0, 0.0))
    u_vec = direction.cross(temp_vec).normalized()
    v_vec = direction.cross(u_vec).normalized()
    w_vec = direction.normalized()

    # --- 3. Generate and Project Coordinates ---
    indices = np.indices(dims, dtype=np.float32)
    coords_3d = np.stack((indices[0], indices[1], indices[2]), axis=-1)
    
    coords_u = np.dot(coords_3d, u_vec)
    coords_v = np.dot(coords_3d, v_vec)
    coords_w = np.dot(coords_3d, w_vec)
    
    # --- [BUG FIX] Normalize the projected coordinates to a [0, 1] range ---
    # This ensures that the projection fits the image regardless of direction.
    u_min, u_max = coords_u.min(), coords_u.max()
    v_min, v_max = coords_v.min(), coords_v.max()

    # Avoid division by zero if the projection is flat (e.g., a perfect line)
    if (u_max - u_min) > 1e-6:
        coords_u = (coords_u - u_min) / (u_max - u_min)
    if (v_max - v_min) > 1e-6:
        coords_v = (coords_v - v_min) / (v_max - v_min)
    # --- [END FIX] ---

    # Apply scale and offset to the now-normalized [0, 1] coordinates
    coords_u = coords_u * scale.x + offset.x
    coords_v = coords_v * scale.y + offset.y
    coords_w = coords_w * scale.y + offset.y
    
    # --- 4. Sample the Image Using NumPy ---
    # Map normalized coordinates to image pixel coordinates (order is Y, X)
    if distort_func:
        new_coords_v = np.zeros_like(coords_v)
        new_coords_u = np.zeros_like(coords_u)
        for x in range(dims[0]):
            for y in range(dims[1]):
                for z in range(dims[2]):
                    # Get the pre-calculated 2D coordinate for this 3D position
                    u = coords_u[x, y, z]
                    v = coords_v[x, y, z]
                    w = coords_w[x, y, z]
                    
                    new_pos = get_displaced_position(
                        position=Vector((u, v, w)),
                        noise_type=distort_parmeters["NOISE"],
                        scale=distort_parmeters["SCALE"],
                        amplitude=distort_parmeters["AMPLITUDE"],
                        axis_mask=distort_parmeters["AXIS_MASK"]
                    )
                    new_coords_v[x, y, z]=new_pos[1]
                    new_coords_u[x, y, z]=new_pos[0]
                   
        pixel_coords_y = new_coords_v * (img_h - 1)
        pixel_coords_x = new_coords_u * (img_w - 1)
    else:
        pixel_coords_y = coords_v * (img_h - 1)
        pixel_coords_x = coords_u * (img_w - 1)
        

    if tile:
        pixel_coords_y %= (img_h - 1)
        pixel_coords_x %= (img_w - 1)

    print(f"Projecting image '{image.name}' with NumPy '{interpolation}' interpolation...")

    if interpolation == 'nearest':
        iy = np.round(pixel_coords_y).astype(int)
        ix = np.round(pixel_coords_x).astype(int)
        np.clip(iy, 0, img_h - 1, out=iy)
        np.clip(ix, 0, img_w - 1, out=ix)
        result_array = image_data[iy, ix]
    else: # Default to 'linear'
        y0, x0 = np.floor(pixel_coords_y).astype(int), np.floor(pixel_coords_x).astype(int)
        y1, x1 = y0 + 1, x0 + 1
        np.clip(y0, 0, img_h - 1, out=y0)
        np.clip(x0, 0, img_w - 1, out=x0)
        np.clip(y1, 0, img_h - 1, out=y1)
        np.clip(x1, 0, img_w - 1, out=x1)
        val_y0x0, val_y0x1 = image_data[y0, x0], image_data[y0, x1]
        val_y1x0, val_y1x1 = image_data[y1, x0], image_data[y1, x1]
        wy, wx = pixel_coords_y - y0, pixel_coords_x - x0
        interp_y0 = (1 - wx) * val_y0x0 + wx * val_y0x1
        interp_y1 = (1 - wx) * val_y1x0 + wx * val_y1x1
        result_array = (1 - wy) * interp_y0 + wy * interp_y1

    print("Image projection complete.")
    return result_array



#Makes an object into a voxel 
def cast_upward_ray_to_backface(
    dimensions: tuple[int, int, int],
    direction: Vector = Vector((0.0, 0.0, 1.0)),
    record_distance: bool = False,
    distort_func=None,
    distort_parmeters=None
) -> np.ndarray:
    """
    Casts a ray upwards from every (x, y, z) position in a grid and records 
    the distance to the back of the nearest face, or 1.0, or -1.0 if no hit.

    Args:
        dimensions (tuple[int, int, int]): The (X, Y, Z) dimensions of the grid.
        record_distance (bool): If True, record the actual distance; otherwise, record 1.0.
        target_object_name (str, optional): The name of the object to cast rays against. 
                                            If None, uses the active object.

    Returns:
        np.ndarray: A float array of shape (Z, Y, X) with distances, 1.0, or -1.0.
    """
    X, Y, Z = dimensions
    
    # Initialize the result array, shape (Z, Y, X) for easier indexing with Z as height
    result_array = np.full((X, Y, Z), -1.0, dtype=np.float32)
    
    direction.normalize()

    # --- Iterate and Ray Cast ---
    # The grid iterates over X, Y, Z coordinates
    for x in range(X):
        for y in range(Y):
            for z in range(Z):
                if distort_func:
                    new_pos = get_displaced_position(
                        position=Vector((x, y, z)),
                        noise_type=distort_parmeters["NOISE"],
                        scale=distort_parmeters["SCALE"],
                        amplitude=distort_parmeters["AMPLITUDE"],
                        axis_mask=distort_parmeters["AXIS_MASK"]
                    )
                    hit, loc, norm, idx, obj, mw = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, new_pos, direction)
                    if hit:
                        if norm.dot(direction) > 0:
                            if record_distance:
                                result_array[x][y][z] = (Vector(new_pos) - loc).length
                            else:
                                result_array[x][y][z] = 1.0
                else:
                    hit, loc, norm, idx, obj, mw = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, (x, y, z), direction)
                    if hit:
                        if norm.dot(direction) > 0:
                            if record_distance:
                                result_array[x][y][z] = (Vector((x, y, z)) - loc).length
                            else:
                                result_array[x][y][z] = 1.0
    return result_array




#################################
#Merge functions
#################################

def merge_arrays_by_distance(
    array_a: np.ndarray,
    array_b: np.ndarray,
    position: Vector,
    min_distance: float,
    max_distance: float,
    array_a_smooth: np.ndarray = None,
    array_b_smooth: np.ndarray = None,
    array_a_contents: np.ndarray = None,
    array_b_contents: np.ndarray = None
) -> tuple:
    """
    Merges two 3D float arrays based on their distance from a central point.
    Optionally merges corresponding smooth (float) and contents (int) arrays.

    Args:
        array_a (np.ndarray): The "inner" primary array (float).
        array_b (np.ndarray): The "outer" primary array (float).
        position (Vector): The center point for the distance calculation.
        min_distance (float): Radius for 100% array_a.
        max_distance (float): Radius for 100% array_b.
        array_a_smooth (np.ndarray, optional): "Inner" smooth array (float).
        array_b_smooth (np.ndarray, optional): "Outer" smooth array (float).
        array_a_contents (np.ndarray, optional): "Inner" contents array (int).
        array_b_contents (np.ndarray, optional): "Outer" contents array (int).

    Returns:
        A tuple containing the merged arrays:
        (merged_array, merged_smooth_array, merged_contents_array)
        
        Optional arrays will be None if they were not provided.
    """
    # --- 1. Input Validation ---
    if array_a.shape != array_b.shape:
        print("Error: Input arrays array_a and array_b must have the same shape.")
        return None, None, None
        
    if min_distance >= max_distance:
        print("Warning: min_distance should be less than max_distance. Swapping them.")
        min_distance, max_distance = max_distance, min_distance

    # Check which optional merges to perform
    do_merge_smooth = (array_a_smooth is not None) and (array_b_smooth is not None)
    do_merge_contents = (array_a_contents is not None) and (array_b_contents is not None)

    # Validate shapes for optional arrays
    if do_merge_smooth:
        if array_a_smooth.shape != array_a.shape or array_b_smooth.shape != array_a.shape:
            print("Error: Smooth arrays must match the shape of the main arrays.")
            do_merge_smooth = False
            
    if do_merge_contents:
        if array_a_contents.shape != array_a.shape or array_b_contents.shape != array_a.shape:
            print("Error: Contents arrays must match the shape of the main arrays.")
            do_merge_contents = False

    # --- 2. Calculate Distance Grid and Alpha Grid ---
    z, y, x = array_a.shape
    indices = np.indices((z, y, x), dtype=np.float32)
    coords = np.stack((indices[2], indices[1], indices[0]), axis=-1)
    pos_np = np.array([position.x, position.y, position.z])
    distance_grid = np.linalg.norm(coords - pos_np, axis=-1)

    blend_range = max_distance - min_distance
    if blend_range < 1e-6:
        alpha_grid = (distance_grid > min_distance).astype(np.float32)
    else:
        alpha_grid = (distance_grid - min_distance) / blend_range
    np.clip(alpha_grid, 0.0, 1.0, out=alpha_grid)

    # --- 3. Perform Merges ---
    
    # Primary merge (float interpolation)
    merged_array = (1.0 - alpha_grid) * array_a + alpha_grid * array_b
    
    # Optional smooth merge (float interpolation)
    merged_smooth_array = None
    if do_merge_smooth:
        merged_smooth_array = (1.0 - alpha_grid) * array_a_smooth + alpha_grid * array_b_smooth
        
    # Optional contents merge (int threshold)
    merged_contents_array = None
    if do_merge_contents:
        # Use array_a_contents where alpha < 0.5, otherwise use array_b_contents
        merged_contents_array = np.where(
            alpha_grid < 0.5, 
            array_a_contents, 
            array_b_contents
        )
    
    return merged_array, merged_smooth_array, merged_contents_array




def merge_arrays_by_switch(
    array_a: np.ndarray,
    array_b: np.ndarray,
    array_a_smooth: np.ndarray,
    array_b_smooth: np.ndarray,
    array_a_contents: np.ndarray,
    array_b_contents: np.ndarray,
    switch: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Combines two sets of (main, smooth, contents) arrays based on a threshold 
    (switch) applied to array_a.

    If array_a[i, j, k] < switch, the result comes from the 'a' arrays.
    Otherwise, the result comes from the 'b' arrays.

    Args:
        array_a (np.ndarray, float): The primary control array.
        array_b (np.ndarray, float): The alternate primary array.
        array_a_smooth (np.ndarray, float): The 'a' smooth array.
        array_b_smooth (np.ndarray, float): The 'b' smooth array.
        array_a_contents (np.ndarray, int): The 'a' contents array.
        array_b_contents (np.ndarray, int): The 'b' contents array.
        switch (float): The threshold value.

    Returns:
        tuple: (merged_main_array, merged_smooth_array, merged_contents_array)
    """
    
    # --- 1. Create the Boolean Mask ---
    # This mask determines which elements should come from the 'a' set.
    # True means array_a < switch (take from 'a' set).
    # False means array_a >= switch (take from 'b' set).
    mask = array_a < switch

    # --- 2. Perform Merges ---
    # np.where(condition, x, y): If condition is True, return x, else return y.

    # Merge 1: Main Array (float)
    merged_main = np.where(mask, array_a, array_b).astype(np.float32)
    
    # Merge 2: Smooth Array (float)
    merged_smooth = np.where(mask, array_a_smooth, array_b_smooth).astype(np.float32)
    
    # Merge 3: Contents Array (int)
    merged_contents = np.where(mask, array_a_contents, array_b_contents).astype(np.int32)
    
    return merged_main, merged_smooth, merged_contents



def combine_arrays_by_comparison(
    array_a: np.ndarray,
    array_b: np.ndarray,
    array_a_smooth: np.ndarray,
    array_b_smooth: np.ndarray,
    array_a_contents: np.ndarray,
    array_b_contents: np.ndarray,
    is_greater_than: bool
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Combines two sets of arrays based on a comparison between array_a and array_b.

    If is_greater_than is True:
        If array_a[i] > array_b[i], the result comes from the 'a' arrays.
        Else, the result comes from the 'b' arrays.
    
    If is_greater_than is False:
        If array_a[i] < array_b[i], the result comes from the 'a' arrays.
        Else, the result comes from the 'b' arrays.

    Args:
        array_a (np.ndarray, float): The primary control array.
        array_b (np.ndarray, float): The secondary control array.
        array_a_smooth (np.ndarray, float): The 'a' smooth array.
        array_b_smooth (np.ndarray, float): The 'b' smooth array.
        array_a_contents (np.ndarray, int): The 'a' contents array.
        array_b_contents (np.ndarray, int): The 'b' contents array.
        is_greater_than (bool): True for '>' comparison, False for '<' comparison.

    Returns:
        tuple: (merged_main_array, merged_smooth_array, merged_contents_array)
    """
    
    # --- 1. Create the Boolean Mask ---
    
    if is_greater_than:
        # Mask is True where array_a is greater than array_b
        # True means: take from 'a' set
        mask = array_a > array_b
    else:
        # Mask is True where array_a is less than array_b
        # True means: take from 'a' set
        mask = array_a < array_b

    # --- 2. Perform Merges using np.where ---
    # np.where(condition, x, y): If condition (mask) is True, return x ('a' array), else return y ('b' array).

    # Merge 1: Main Array (float)
    merged_main = np.where(mask, array_a, array_b).astype(np.float32)
    
    # Merge 2: Smooth Array (float)
    merged_smooth = np.where(mask, array_a_smooth, array_b_smooth).astype(np.float32)
    
    # Merge 3: Contents Array (int)
    merged_contents = np.where(mask, array_a_contents, array_b_contents).astype(np.int32)
    
    return merged_main, merged_smooth, merged_contents


#################################
#Convenversion functions
#################################
def threshold_array(data: np.ndarray, cutoff: float) -> np.ndarray:
    """
    Converts a float array to a binary int array based on a cutoff value.

    Args:
        data (np.ndarray): The input float array.
        cutoff (float): The threshold value.

    Returns:
        np.ndarray: An integer array where values above the cutoff are 1,
                    and all others are 0.
    """
    # NumPy's broadcasting makes this a fast, one-line operation
    return (data > cutoff).astype(np.int8)

def clamp_array(land: np.ndarray) -> np.ndarray:
    """
    Clamps all values in a NumPy array to the range [0.0, 1.0].

    This function modifies the array in-place for memory efficiency.

    Args:
        land (np.ndarray): The 3D input array of floats.

    Returns:
        np.ndarray: The same array, with its values clamped.
    """
    np.clip(land, 0.0, 1.0, out=land)
    return land

def threshold_array_float(data: np.ndarray, cutoff: float) -> np.ndarray:
    """
    Converts a float array to a binary int array based on a cutoff value.

    Args:
        data (np.ndarray): The input float array.
        cutoff (float): The threshold value.

    Returns:
        np.ndarray: An integer array where values above the cutoff are 1,
                    and all others are 0.
    """
    # NumPy's broadcasting makes this a fast, one-line operation
    return (data > cutoff).astype(np.float32)


#################################
#Remap functions
#################################


def remap_array_values(
    data_array: np.ndarray,
    remap_dict: dict
) -> np.ndarray:
    """
    Replaces values in a NumPy array based on a dictionary mapping.

    Args:
        data_array (np.ndarray): The input NumPy array (e.g., of type int).
        remap_dict (dict): A dictionary where keys are the old values (int) 
                           and values are the new replacement values (int).

    Returns:
        np.ndarray: A new array with the values replaced according to the map.
    """
    if not remap_dict:
        return data_array.copy()

    # 1. Get the unique keys (old values) and values (new values) from the dictionary
    old_values = np.array(list(remap_dict.keys()), dtype=data_array.dtype)
    new_values = np.array(list(remap_dict.values()), dtype=data_array.dtype)
    
    # Create a copy of the input array to modify and return
    remapped_array = data_array.copy()

    # 2. Use np.isin to find the locations of all old values
    # This is often faster than iterating or using multiple np.where calls.
    
    # The dictionary keys are the values to look for
    for old_val, new_val in remap_dict.items():
        # Find all locations where the array matches the old value
        mask = (remapped_array == old_val)
        
        # Apply the replacement value using the mask
        remapped_array[mask] = new_val

    return remapped_array


import numpy as np

def remap_float_array_by_int_id(
    int_id_array: np.ndarray,
    float_data_array: np.ndarray,
    remap_dict: dict
) -> np.ndarray:
    """
    Replaces values in a float array based on the IDs in a corresponding 
    integer array, using a dictionary mapping.

    Args:
        int_id_array (np.ndarray): The input array containing integer IDs. 
                                   (e.g., contents_array)
        float_data_array (np.ndarray): The input float array whose values will 
                                       be modified. (e.g., smooth_value_array)
        remap_dict (dict): A dictionary where keys are the IDs (int) to look for, 
                           and values are the new float values to use for replacement.

    Returns:
        np.ndarray: A new float array with the values replaced according to the map.
    """
    # 1. Create a copy of the float array to modify and return
    remapped_float_array = float_data_array.copy()

    # 2. Iterate through the dictionary to find and replace values
    for target_id, new_float_value in remap_dict.items():
        # Ensure the target ID is an integer
        if not isinstance(target_id, int):
            print(f"Warning: Key '{target_id}' is not an integer. Skipping.")
            continue
            
        # 3. Create a boolean mask where the int_id_array matches the target_id
        mask = (int_id_array == target_id)
        
        # 4. Apply the new float value to the float array at all masked positions
        remapped_float_array[mask] = new_float_value

    return remapped_float_array

#################################
#Generate content values and smooth values from existing data
#################################


import numpy as np
#use float values
def create_stepped_arrays(
    voxel_array: np.ndarray,
    start_value: float,
    step_value: float
) -> tuple[np.ndarray, np.ndarray]:
    """
    Discretizes a 3D array into integer IDs based on steps and creates a
    corresponding array of random values based on those IDs.

    Args:
        data (np.ndarray): The input 3D array of floats.
        start_value (float): The threshold for the first step (ID 1).
        step_value (float): The size of each subsequent step.

    Returns:
        A tuple of (id_array, smooth_array):
        - id_array (np.ndarray, int): Array of integer IDs.
        - smooth_array (np.ndarray, float): Array of corresponding random values.
    """
    if step_value <= 0:
        print("Error: step_value must be greater than 0.")
        return None, None

    # --- 1. Create the ID Array ---
    
    # This formula calculates the ID for each voxel in a single operation.
    # 1. Shift data so that 'start_value' becomes 0.
    # 2. Scale by 'step_value'.
    # 3. Apply floor + 1 (e.g., 0.0-0.9 -> 1, 1.0-1.9 -> 2).
    # 4. Use np.maximum to clamp all values < 1 (i.e., data < start_value) to 0.
    
    id_array = np.floor((voxel_array - start_value) / step_value) + 1
    id_array = np.maximum(id_array, 0).astype(np.int32)

    # --- 2. Create the Smooth Value Array ---
    
    # We create a lookup table (LUT) where the index is the ID.
    # First, find the highest ID we need to generate a value for.
    max_id = id_array.max()
    num_ids = max_id + 1
    
    # Create a 1D array of random values, one for each possible ID.
    random_lut = np.random.uniform(-0.5, 0.5, size=num_ids)
    
    # Use NumPy's "fancy indexing" to build the 3D smooth_array.
    # Each voxel in id_array looks up its corresponding random value in the LUT.
    smooth_array = random_lut[id_array]
    
    return id_array, smooth_array




def _manhattan_distance_transform_3d_numpy(solid_mask: np.ndarray) -> np.ndarray:
    """
    Calculates the 3D Manhattan distance ($L_1$) from each True voxel in
    solid_mask to the nearest False voxel, using only NumPy.
    
    This is a pure NumPy replacement for scipy.ndimage.distance_transform_edt.
    """
    z_dim, y_dim, x_dim = solid_mask.shape
    
    # 1. Initialize field
    # Set solid voxels (True) to infinity, empty voxels (False) to 0.
    field = np.where(solid_mask, np.inf, 0)
    
    # 2. Pass 1: Forward (top-left-front to bottom-right-back)
    # We pad with infinity to avoid complex boundary checks
    padded_field = np.pad(field, 1, mode='constant', constant_values=np.inf)
    
    for z in range(z_dim):
        for y in range(y_dim):
            for x in range(x_dim):
                # Compare to neighbors that have already been processed in this pass
                # (z-1, y, x), (z, y-1, x), (z, y, x-1)
                # We add 1 to the indices because of the padding
                min_neighbor = min(
                    padded_field[z, y+1, x+1],    # (z-1) neighbor
                    padded_field[z+1, y, x+1],    # (y-1) neighbor
                    padded_field[z+1, y+1, x]     # (x-1) neighbor
                )
                
                # The new value is the minimum of its current value or a neighbor + 1
                padded_field[z+1, y+1, x+1] = min(
                    padded_field[z+1, y+1, x+1], 
                    min_neighbor + 1
                )
    
    # 3. Pass 2: Backward (bottom-right-back to top-left-front)
    for z in range(z_dim - 1, -1, -1):
        for y in range(y_dim - 1, -1, -1):
            for x in range(x_dim - 1, -1, -1):
                # Compare to neighbors that have already been processed in this pass
                # (z+1, y, x), (z, y+1, x), (z, y, x+1)
                min_neighbor = min(
                    padded_field[z+2, y+1, x+1],  # (z+1) neighbor
                    padded_field[z+1, y+2, x+1],  # (y+1) neighbor
                    padded_field[z+1, y+1, x+2]   # (x+1) neighbor
                )
                
                padded_field[z+1, y+1, x+1] = min(
                    padded_field[z+1, y+1, x+1],
                    min_neighbor + 1
                )

    # 4. Unpad the final result
    return padded_field[1:-1, 1:-1, 1:-1]



#use proximity
def create_surface_layers_numpy(
    voxel_array: np.ndarray,
    cutoff: float,
    direction: Vector,
    layer_deform: float,
    layer_thickness: float = 0.05
) -> tuple[np.ndarray, np.ndarray]:
    """
    Creates integer layer IDs and smooth values, using a pure NumPy
    distance transform (Manhattan $L_1$ distance).
    
    Args:
        ... [Args are identical to the previous version] ...

    Returns:
        ... [Return values are identical to the previous version] ...
    """
    
    # --- 1. Initialization and Input Validation ---
    z_dim, y_dim, x_dim = voxel_array.shape
    deform = np.clip(layer_deform, 0.0, 1.0)
    
    if direction.length == 0:
        direction = Vector((0.0, 0.0, 1.0))
    direction = Vector((direction[2], direction[1], direction[0]))
    direction.normalize()
    
    if layer_thickness <= 0:
        layer_thickness = 0.05

    solid_mask = (voxel_array >= cutoff)
    
    if not np.any(solid_mask) or np.all(solid_mask):
        print("Warning: Voxel array is fully solid or fully empty.")
        if not np.any(solid_mask):
            return np.zeros_like(voxel_array, dtype=int), np.zeros_like(voxel_array, dtype=float)
        
    
    # --- 2. Field Calculation Functions ---
    
    def get_planar_field():
        """Calculates a normalized [0, 1] planar gradient field."""
        indices = np.indices((z_dim, y_dim, x_dim), dtype=np.float32)
        coords = np.stack((indices[2], indices[1], indices[0]), axis=-1)
        np_dir = np.array([direction.x, direction.y, direction.z])
        field = np.dot(coords, np_dir)
        
        f_min, f_max = field.min(), field.max()
        f_range = f_max - f_min
        if f_range < 1e-6:
            return np.full_like(field, 0.5)
        return (field - f_min) / f_range

    def get_distance_field():
        """Calculates a normalized [0, 1] surface distance field (Manhattan)."""
        # --- MODIFICATION ---
        # Call the new pure-NumPy function instead of SciPy
        field = _manhattan_distance_transform_3d_numpy(solid_mask)
        # --- END MODIFICATION ---
        
        f_min, f_max = field.min(), field.max()
        f_range = f_max - f_min
        if f_range < 1e-6:
            return np.full_like(field, 0.0)
        return (field - f_min) / f_range

    # --- 3. Blend Fields ---
    
    if deform == 0.0:
        final_field = get_planar_field()
    elif deform == 1.0:
        final_field = get_distance_field()
    else:
        planar_field = get_planar_field()
        distance_field = get_distance_field()
        final_field = (1.0 - deform) * planar_field + deform * distance_field

    # --- 4. Discretize into Layers (ID Array) ---
    id_array = np.floor(final_field / layer_thickness).astype(np.int32) + 1
    id_array[~solid_mask] = 0

    # --- 5. Create Smooth Value Array (LUT) ---
    max_id = id_array.max()
    num_ids = max_id + 1
    random_lut = np.random.uniform(-0.5, 0.5, size=num_ids)
    layer_smooth_array = random_lut[id_array]

    return id_array, layer_smooth_array

#################################
#Face functions
#################################
def AssignContentsToFaces(contents_array, faces_array):
    """
    The rows in the texture map correlate to the contents, row 1 content 1 etc
    The columns to the faces, top, middle, bottom and rest is special to be assigned by other functions
    """
    for x in range(len(contents_array)):
        for y in range(len(contents_array[0])):
            for z in range(len(contents_array[0][0])):
                #-X 
                faces_array[x][y][z][0][0] = 1 #X middle
                faces_array[x][y][z][0][1] = contents_array[x][y][z] #YContent
                #X
                faces_array[x][y][z][1][0] = 1
                faces_array[x][y][z][1][1] = contents_array[x][y][z] #YContent
                #-Y
                faces_array[x][y][z][2][0] = 1
                faces_array[x][y][z][2][1] = contents_array[x][y][z] #YContent
                #Y
                faces_array[x][y][z][3][0] = 1
                faces_array[x][y][z][3][1] = contents_array[x][y][z] #YContent
                
                faces_array[x][y][z][4][0] = 2
                faces_array[x][y][z][4][1] = contents_array[x][y][z] #YContent
                
                faces_array[x][y][z][5][0] = 0
                faces_array[x][y][z][5][1] = contents_array[x][y][z] #YContent
                    
    return faces_array   



#Assign new uvs for faces thats distorted into new positions. Mostly edges becoming surfaces
def calculate_face_normal(v1: Vector, v2: Vector, v3: Vector, v4: Vector) -> Vector:
    """
    Calculates the face normal vector for a 3D quad defined by four vertices.
    It uses the cross product of two adjacent edges (v2-v1 and v3-v1).
    """
    # Create two edge vectors that share a vertex (v1)
    edge_a = v3 - v1 #this needed to take all 4 vectors since its 2 triangles not necesarily planar
    edge_b = v4 - v2
    
    # The normal is the cross product of the two edges
    normal = edge_a.cross(edge_b)
    
    # Normalizing the normal is usually necessary for direction comparisons
    if normal.length > 1e-6:
        return normal.normalized()
    else:
        # Handle degenerate face (return a zero vector or a default, e.g., Z-axis)
        return Vector((0.0, 0.0, 0.0))

def update_uv_if_facing_direction(
    v1: Vector, v2: Vector, v3: Vector, v4: Vector,
    direction: Vector,
    cutoff: float,
    uv_array: np.ndarray,
    x: int, y: int, z: int,
    facepos: int,
    uv_x: int, uv_y: int
) -> np.ndarray:
    """
    Calculates the dot product of the face normal and a direction vector.
    If the dot product exceeds the cutoff, it overwrites the UV coordinates
    for that specific face in the uv_array.

    Args:
        v1, v2, v3, v4 (Vector): Coordinates of the face vertices.
        direction (Vector): The direction vector to compare against.
        cutoff (float): The threshold for the dot product (e.g., 0.5).
        uv_array (np.ndarray): The UV array with dimensions (X, Y, Z, 6, 2).
                               The last two dimensions are [U, V].
        x, y, z (int): The coordinates of the voxel containing the face.
        facepos (int): The index of the face (0-5) to update.
        uv_x (int): The new U (first) coordinate value.
        uv_y (int): The new V (second) coordinate value.

    Returns:
        np.ndarray: The modified uv_array.
    """
    
    # 1. Calculate the Face Normal
    face_normal = calculate_face_normal(v1, v2, v3, v4)
    
    # 2. Normalize the Direction Vector
    if direction.length > 1e-6:
        normalized_direction = direction.normalized()
    else:
        # Avoid division by zero if direction is (0, 0, 0)
        return uv_array 

    # 3. Calculate the Dot Product
    # Dot product of two normalized vectors equals the cosine of the angle between them.
    dot_product = face_normal.dot(normalized_direction)
    
    # 4. Check the Cutoff and Update UVs
    if dot_product > cutoff:
        # Check bounds before accessing the array
        if 0 <= x < uv_array.shape[0] and \
           0 <= y < uv_array.shape[1] and \
           0 <= z < uv_array.shape[2] and \
           0 <= facepos < 6:
               
            # The indices for the specific UV pair: [x, y, z, facepos, (U/V)]
            # Overwrite the U coordinate
            uv_array[x, y, z, facepos, 0] = uv_x
            
            # Overwrite the V coordinate
            uv_array[x, y, z, facepos, 1] = uv_y

    return uv_array


#move tiles around to make more sense and aesthetics
def check_and_update_face_uvs(
    voxel_contents_array: np.ndarray,
    face_array: np.ndarray,
    x: int, y: int, z: int,
    face_index: int,
    uv_set_above_only: tuple[int, int],
    uv_set_below_infront_only: tuple[int, int],
    uv_set_both: tuple[int, int]
) -> np.ndarray:
    """
    Modifies the UV coordinates for a specific face of a voxel based on 
    the presence of surrounding solid voxels relative to that face.

    Args:
        voxel_contents_array (np.ndarray): The (X, Y, Z) array of int8, where > 0 is solid.
        face_array (np.ndarray): The (X, Y, Z, 6, 2) array of UV coordinates (int).
        x, y, z (int): Coordinates of the voxel to check.
        face_index (int): The index of the face being checked (0: -x, 1: x, 2: -y, 3: y, 4: -z, 5: z).
        uv_set_above_only (tuple[int, int]): New (U, V) if only 'Above' is solid.
        uv_set_below_infront_only (tuple[int, int]): New (U, V) if only 'Below-Infront' is solid.
        uv_set_both (tuple[int, int]): New (U, V) if both 'Above' and 'Below-Infront' are solid.

    Returns:
        np.ndarray: The modified face_array.
    """
    
    X, Y, Z = voxel_contents_array.shape

    # --- 1. Define Neighbor Check Vectors ---
    
    # Check A: 'Above' (Voxel at (x, y, z+1))
    check_a_vec = np.array([0, 0, 1]) 
    
    # Check B: 'Below-Infront' (Voxel at (x + V_infront + V_down))
    # 'Infront' vectors (normal direction of the face):
    infront_vecs = np.array([
        [-1, 0, 0], # 0: -x face
        [ 1, 0, 0], # 1:  x face
        [ 0,-1, 0], # 2: -y face
        [ 0, 1, 0], # 3:  y face
        [ 0, 0,-1], # 4: -z face
        [ 0, 0, 1]  # 5:  z face
    ])
    
    # 'Down' vector (one unit below)
    down_vec = np.array([0, 0, -1])

    # --- 2. Calculate Neighbor Coordinates and Check Bounds ---
    
    def is_solid(cx, cy, cz):
        # Check if coordinates are within bounds and if voxel is solid (> 0)
        if 0 <= cx < X and 0 <= cy < Y and 0 <= cz < Z:
            return voxel_contents_array[cx, cy, cz] > 0
        return False
        
    # Check A: Above (x, y, z+1)
    check_a_coords = (x + check_a_vec[0], y + check_a_vec[1], z + check_a_vec[2])
    is_a_solid = is_solid(*check_a_coords)
    
    # Check B: Below-Infront (Voxel at position + Infront_Vector + Down_Vector)
    # The new position is calculated by summing the components of the base position 
    # and the two offset vectors.
    infront_offset = infront_vecs[face_index]
    
    check_b_coords = (
        x + infront_offset[0] + down_vec[0],
        y + infront_offset[1] + down_vec[1],
        z + infront_offset[2] + down_vec[2]
    )
    is_b_solid = is_solid(*check_b_coords)

    # --- 3. Apply Update Logic (Same conditions as before) ---
    
    new_uv = None
    
    if is_a_solid and not is_b_solid:
        # Condition 1: Voxel ABOVE but NOT Below-Infront
        new_uv = uv_set_above_only
    elif not is_a_solid and is_b_solid:
        # Condition 2: Voxel NOT Above but IS Below-Infront
        new_uv = uv_set_below_infront_only
    elif is_a_solid and is_b_solid:
        # Condition 3: Voxel BOTH Above AND Below-Infront
        new_uv = uv_set_both
        
    # --- 4. Overwrite UV Coordinates if a Condition Met ---
    if new_uv:
        # Write to the array at the current voxel's x, y, z and the specified face_index
        if 0 <= x < face_array.shape[0] and \
           0 <= y < face_array.shape[1] and \
           0 <= z < face_array.shape[2] and \
           0 <= face_index < 6:
               
            face_array[x, y, z, face_index, 0] = new_uv[0] # U coord
            face_array[x, y, z, face_index, 1] = new_uv[1] # V coord

    return face_array

#################################
#Call functions
#################################
random.seed(402) #make results reproducable
np.random.seed(4800)


if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

#Define a offset function
"""parmeters = {
    "NOISE": 'VORONOI_F2F1', #
    "SCALE": 0.1, # Larger scale = more detail
    "AMPLITUDE": 2.2, #strength
    "AXIS_MASK": (True, True, True) 
}
func = get_displaced_position"""
#func=None
#parmeters=None


# Define the dimensions of our grid
dims = (70, 65, 40) # (x, y, z)

# --- Step 1: Create a base shape using a gradient ---
"""grad_dir = Vector((-0.1, 0.0, -1.0))

#Create a gradient voxels
Array1 = create_gradient_array(
    direction=grad_dir,
    min_val=-1.0,
    max_val=1.0,
    dims=dims,
    distort_func=func, #"SCALE": 0.15, "AMPLITUDE": 6.0,
    distort_parmeters=parmeters
)"""


"""gradient = {
        0.0: 1.0,
        0.25: 0.6,
        0.3: 0.0,
        0.5: 1.0,
        0.75: 0.2,
        1.0: 1.0,
    }
    
land_array = create_gradient_array_with_profile(
    dimensions=dims,
    direction=Vector((0.0, 0.0, 1.0)),
    profile_dict=gradient,
    min_val=-1.0,
    max_val=2.2,
    distort_func=func, #"SCALE": 0.1, "AMPLITUDE": 2.2,
    distort_parmeters=parmeters
)"""


"""parmeters = {
    "NOISE": 'VORONOI_F2F1', #
    "SCALE": 0.5, # Larger scale = more detail
    "AMPLITUDE": 7.5, #strength
    "AXIS_MASK": (True, False, False) 
}
func = get_displaced_position"""

"""Array2 = create_noise_array(
    dims=dims,
    noise_type='PERLIN_NEW',
    offset = Vector((3.0, 2.0, 0.0)),
    scale=Vector((0.03, 0.03, 0.03)), # Larger scale = more detail
    distort_func=func, #"SCALE": 0.3, "AMPLITUDE": 4.5,
    distort_parmeters=parmeters
)"""


#contentsArray2, smooth_value_array2 = create_surface_layers_numpy(Array2, 0.3, Vector((0.1, 0.2, 1.0)), 0.8, 0.09 )

"""layer_direction = Vector((1.0, 0.0, 0.5))
# --- 2. Generate the Layered Data ---
voxelsArray, contentsArray, smooth_value_array = create_layered_array(
    dims=dims,
    direction=layer_direction,
    min_val=-0.3,
    max_val=1.0,
    min_layer_thickness=2.0,
    max_layer_thickness=5.0,
    distort_func=func, #"SCALE": 0.1, "AMPLITUDE": 2.2,
    distort_parmeters=parmeters   
)"""


"""projection_dir = Vector((0.0, 1.0, 1.0)) #z y x
# --- 2. Generate the Projected Noise Data ---
voxelsArray = create_projected_noise_array(
    dims=dims,
    noise_type='VORONOI_F1',
    direction=projection_dir,
    scale=Vector((0.08, 0.18, 0.0)),  # Make the cells larger
    offset=Vector((123.4, 567.8, 0.0)), # Shift the pattern
    third_axis_distortion_amount = 0.1,
    distort_func=func, #"SCALE": 0.4, "AMPLITUDE": 0.2,
    distort_parmeters=parmeters
)"""

"""image_name = "testing.png"
try:
    my_image = bpy.data.images[image_name]
except KeyError:
    print(f"Error: Image '{image_name}' not found.")
    my_image = None

if my_image:
    proj_dir = Vector((1.0, 1.0, 0.0))
    
    # Call the new NumPy-only function
    voxelsArray = create_projected_image_array_numpy(
        dims=dims,
        image=my_image,
        direction=proj_dir,
        scale=Vector((1.0, 1.0, 0)),
        # You can still choose the interpolation method
        interpolation='linear', # or 'nearest'
        distort_func=func, #"SCALE": 0.7, "AMPLITUDE": 0.03,
        distort_parmeters=parmeters
    )"""
    

"""land_array, smooth_value_array, contentsArray = merge_arrays_by_distance(
    array_a=Array1,
    array_b=Array2,
    position=Vector((0.0, 0.0, 11.0)),
    min_distance=30.0,
    max_distance=40.0,
    array_a_smooth=smooth_value_array1,
    array_b_smooth=smooth_value_array2,
    array_a_contents=contentsArray1,
    array_b_contents=contentsArray2
)"""

"""land_array, smooth_value_array, contentsArray = merge_arrays_by_switch(
    array_a=Array1,
    array_b=Array2,
    array_a_smooth=smooth_value_array1,
    array_b_smooth=smooth_value_array2,
    array_a_contents=contentsArray1,
    array_b_contents=contentsArray2,
    switch=0.5
)"""

"""land_array, smooth_value_array, contentsArray = combine_arrays_by_comparison(
    array_a=Array1,
    array_b=Array2,
    array_a_smooth=smooth_value_array1,
    array_b_smooth=smooth_value_array2,
    array_a_contents=contentsArray1,
    array_b_contents=contentsArray2,
    is_greater_than=True
)"""




"""land_array = cast_upward_ray_to_backface(
    dimensions=dims,
    direction=Vector((0.0, 1.0, 0.0)),
    record_distance=True,
    #distort_func=func, #"SCALE": 0.15, "AMPLITUDE": 6.0,
    #distort_parmeters=parmeters
)
contentsArray, smooth_value_array = create_stepped_arrays(voxel_array=land_array, start_value=0.0, step_value=3)"""
#contentsArray, smooth_value_array = create_surface_layers_numpy(voxel_array=land_array, cutoff=0.3, direction=Vector((0.1, 0.2, 1.0)), layer_deform=0.8, layer_thickness=0.09 )



image_name = "heightmap.png"
try:
    my_image = bpy.data.images[image_name]
except KeyError:
    print(f"Error: Image '{image_name}' not found.")
    my_image = None

if my_image:
    proj_dir = Vector((0.0, 0.0, 1.0))
    
    # Call the new NumPy-only function
    projected_image_array = create_projected_image_array_numpy(
        dims=dims,
        image=my_image,
        direction=proj_dir,
        scale=Vector((1.3, 1.3, 0)),
        # You can still choose the interpolation method
        interpolation='linear', # or 'nearest'
        #distort_func=func, #"SCALE": 0.7, "AMPLITUDE": 0.03,
        #distort_parmeters=parmeters
    )
    
    
gradient = {
        0.0: 1.0,
        0.25: 0.5,
        0.3: .250,
        0.5: 0.120,
        0.75: 0.05,
        1.0: 0.0,
    }
    
gradient_array = create_gradient_array_with_profile(
    dimensions=dims,
    direction=Vector((0.0, 0.0, 1.0)),
    profile_dict=gradient,
    min_val=-1.0,
    max_val=2.2,
    #distort_func=func, #"SCALE": 0.1, "AMPLITUDE": 2.2,
    #distort_parmeters=parmeters
)    
    
    
Array1 = projected_image_array + gradient_array * 0.4
contentsArray1, smooth_value_array1 = create_surface_layers_numpy(voxel_array=Array1, cutoff=0.3, direction=Vector((0.1, 0.2, 1.0)), layer_deform=0.8, layer_thickness=0.09 )



proj_dir = Vector((0.0, 0.0, 1.0))

projected_noise_array = create_projected_noise_array(
    dims=dims,
    noise_type='VORONOI_F1',
    direction=proj_dir,
    scale=Vector((0.08, 0.18, 0.0)),  # Make the cells larger
    offset=Vector((123.4, 567.8, 0.0)), # Shift the pattern
    third_axis_distortion_amount = 0.1,
    #distort_func=func, #"SCALE": 0.4, "AMPLITUDE": 0.2,
    #distort_parmeters=parmeters
)


gradient = {
        0.0: 1.0,
        0.1: 0.5,
        0.25: 0.20,
        0.4: 0.40,
        0.6: 0.2,
        0.75: 0.0,
        1.0: 0.0,
    }
    
gradient_array_with_profile = create_gradient_array_with_profile(
    dimensions=dims,
    direction=Vector((0.0, 0.3, 1.0)),
    profile_dict=gradient,
    min_val=-1.0,
    max_val=2.2,
    #distort_func=func, #"SCALE": 0.1, "AMPLITUDE": 2.2,
    #distort_parmeters=parmeters
)    


Array2 = projected_noise_array + gradient_array_with_profile
contentsArray2, smooth_value_array2 = create_surface_layers_numpy(voxel_array=Array2, cutoff=0.3, direction=Vector((0.1, 0.2, 1.0)), layer_deform=0.8, layer_thickness=0.07 )

land_array, smooth_value_array, contentsArray = merge_arrays_by_distance(
    array_a=Array1,
    array_b=Array2,
    position=Vector((20.0, 26.0, 40.0)),
    min_distance=20.0,
    max_distance=25.0,
    array_a_smooth=smooth_value_array1,
    array_b_smooth=smooth_value_array2,
    array_a_contents=contentsArray1,
    array_b_contents=contentsArray2
)




"""remapping = {
        1: 5,
        2: 6,
        3: 7
}
remapped_contentsArray = remap_array_values(contentsArray, remapping)"""
remapping = {
        0: 0.25,
        1: -0.25,
        2: 0.5,
        3: 0.45,
        4: -0.5,
        5: -0.25,
        6: 0.35,
        7: 0.11,
        8: -0.25,
        9: 0.0,
        10: -0.12,
        11: -0.22,
        12: 0.45,
        13: -0.23,
        14: 0.0,
        15: -0.26,
        16: 0.5,
        17: -0.5,
        18: 0.45,
        19: 0.45,

    }
    

remapped_smooth_value_array = remap_float_array_by_int_id(contentsArray, smooth_value_array, remapping)  

uvParams = {
    "width" : 6, 
    "height": 10, 
    "buffer": 0.0005
    }



#x, y, z, 6, 2 index of uv cords array for each face on each voxel
face_array = np.zeros((dims[0], dims[1], dims[2], 6, 2), dtype=int) #-x, x, -y, y, -z, z
face_array =  AssignContentsToFaces(contentsArray, face_array)


#make int array from float array
final_binary_data = threshold_array(land_array, cutoff=0.3)

def modify_face_UVS(uvFunctionParams, vert_coords, voxel_contents_array, face_array, x, y, z, facepos):
    """
    uvFunctionParams: parramaters passed in
    vert_coords: last 4 coords of last face
    voxel_contents_array: the whole voxel array
    face_array: the whole voxal faces array
    x, y, z: position coordinates
    facepos: indicate direction of face or position in array
    """
    coord1 = Vector(vert_coords[len(vert_coords) - 1])
    coord2 = Vector(vert_coords[len(vert_coords) - 2])
    coord3 = Vector(vert_coords[len(vert_coords) - 3])
    coord4 = Vector(vert_coords[len(vert_coords) - 4])
    if facepos <= 3: #sides only, not top or bottom #-x, x, -y, y, -z, z      
        face_array = check_and_update_face_uvs(
            voxel_contents_array=voxel_contents_array,
            face_array=face_array,
            x=x, y=y, z=z,
            face_index=facepos,
            uv_set_above_only=[3, face_array[x][y][z][facepos][1]], #existing row 3 column
            uv_set_below_infront_only=[5, face_array[x][y][z][facepos][1]], #existing row 5 column
            uv_set_both=[4, face_array[x][y][z][facepos][1]] #existing row 4 column
            )
            
    face_array = update_uv_if_facing_direction(
        v1=coord1, v2=coord2, v3=coord3, v4=coord4,
        direction=Vector((0.0, 0.0, -1.0)),
        cutoff=0.5,
        uv_array=face_array,
        x=x, y=y, z=z,
        facepos=facepos,
        uv_x=0, uv_y=face_array[x][y][z][facepos][1] #existing row o column
    )

    return face_array

uvFunction = modify_face_UVS
uvFunctionParams = {
    "Placeholder" : 6, 
}


GenerateVoxels(final_binary_data, remapped_smooth_value_array, face_array, uvParams, uvFunction, uvFunctionParams)



#Desert Scape
"""
#Define a offset function
parmeters = {
    "NOISE": 'BLENDER', #  [‘BLENDER’, ‘PERLIN_ORIGINAL’, ‘PERLIN_NEW’, ‘VORONOI_F1’, ‘VORONOI_F2’, ‘VORONOI_F3’, ‘VORONOI_F4’, ‘VORONOI_F2F1’, ‘VORONOI_CRACKLE’, ‘CELLNOISE’].
    "SCALE": 0.1, # Larger scale = more detail
    "AMPLITUDE": 0.9, #strength
    "AXIS_MASK": (False, True, True) 
}
func = get_displaced_position

gradient = {
        0.0: 1.0,
        0.25: 0.5,
        0.3: 0.3,
        0.5: 0.3,
        0.75: 0.75,
        1.0: 0.0,
    }
    
gradient_array = create_gradient_array_with_profile(
    dimensions=dims,
    direction=Vector((0.0, 0.0, 1.0)),
    profile_dict=gradient,
    min_val=-1.0,
    max_val=2.2,
    distort_func=func, #"SCALE": 0.1, "AMPLITUDE": 2.2,
    distort_parmeters=parmeters
)


parmeters = {
    "NOISE": 'VORONOI_F2F1', #  [‘BLENDER’, ‘PERLIN_ORIGINAL’, ‘PERLIN_NEW’, ‘VORONOI_F1’, ‘VORONOI_F2’, ‘VORONOI_F3’, ‘VORONOI_F4’, ‘VORONOI_F2F1’, ‘VORONOI_CRACKLE’, ‘CELLNOISE’].
    "SCALE": 0.2, # Larger scale = more detail
    "AMPLITUDE": 0.1, #strength
    "AXIS_MASK": (True, False, True) 
}
func = get_displaced_position

image_name = "dots.png"
try:
    my_image = bpy.data.images[image_name]
except KeyError:
    print(f"Error: Image '{image_name}' not found.")
    my_image = None

if my_image: #specifically load image in uv editor or elsewhere when reopen scene else it qont error just all black
    proj_dir = Vector((0.0, 0.0, 1.0))
    
    # Call the new NumPy-only function
    projected_image_array = create_projected_image_array_numpy(
        dims=dims,
        image=my_image,
        direction=proj_dir,
        scale=Vector((1.0, 1.0, 0)),
        # You can still choose the interpolation method
        interpolation='linear', # or 'nearest'
        distort_func=func, #"SCALE": 0.7, "AMPLITUDE": 0.03,
        distort_parmeters=parmeters
    )


parmeters = {
    "NOISE": 'VORONOI_F2F1', #  [‘BLENDER’, ‘PERLIN_ORIGINAL’, ‘PERLIN_NEW’, ‘VORONOI_F1’, ‘VORONOI_F2’, ‘VORONOI_F3’, ‘VORONOI_F4’, ‘VORONOI_F2F1’, ‘VORONOI_CRACKLE’, ‘CELLNOISE’].
    "SCALE": 0.12, # Larger scale = more detail
    "AMPLITUDE": 1.2, #strength
    "AXIS_MASK": (True, False, True) 
}
func = get_displaced_position

layer_direction = Vector((0.0, 0.0, 1.0))
layerdArray, contentsArray, smooth_value_array = create_layered_array(
    dims=dims,
    direction=layer_direction,
    min_val=-0.5,
    max_val=0.5,
    min_layer_thickness=2.0,
    max_layer_thickness=5.0,
    distort_func=func, #"SCALE": 0.1, "AMPLITUDE": 2.2,
    distort_parmeters=parmeters   
    )
    
land_array = gradient_array * 0.2 + projected_image_array * 0.7 + layerdArray * 0.2
"""

#Forest Scape
"""
parmeters = {
    "NOISE": 'VORONOI_F3', #[‘BLENDER’, ‘PERLIN_ORIGINAL’, ‘PERLIN_NEW’, ‘VORONOI_F1’, ‘VORONOI_F2’, ‘VORONOI_F3’, ‘VORONOI_F4’, ‘VORONOI_F2F1’, ‘VORONOI_CRACKLE’, ‘CELLNOISE’].
    "SCALE": 0.1, # Larger scale = more detail
    "AMPLITUDE": 2.2, #strength
    "AXIS_MASK": (True, True, True) 
}
func = get_displaced_position

grad_dir = Vector((-0.1, 0.0, -1.0))

#Create a gradient voxels
GradienArray = create_gradient_array(
    direction=grad_dir,
    min_val=-2.0,
    max_val=2.0,
    dims=dims,
    distort_func=func, #"SCALE": 0.15, "AMPLITUDE": 6.0,
    distort_parmeters=parmeters
)


parmeters = {
    "NOISE": 'VORONOI_F2F1', #
    "SCALE": 0.7, # Larger scale = more detail
    "AMPLITUDE": 1.5, #strength
    "AXIS_MASK": (True, True, False) 
}
func = get_displaced_position

NoiseArray = create_noise_array(
    dims=dims,
    noise_type='BLENDER',
    offset = Vector((3.0, 1.7, 3.0)),
    scale=Vector((0.03, 0.03, 0.03)), # Larger scale = more detail
    distort_func=func, #"SCALE": 0.3, "AMPLITUDE": 4.5,
    distort_parmeters=parmeters
)


parmeters = {
    "NOISE": 'PERLIN_ORIGINAL', #  [‘BLENDER’, ‘PERLIN_ORIGINAL’, ‘PERLIN_NEW’, ‘VORONOI_F1’, ‘VORONOI_F2’, ‘VORONOI_F3’, ‘VORONOI_F4’, ‘VORONOI_F2F1’, ‘VORONOI_CRACKLE’, ‘CELLNOISE’].
    "SCALE": 0.05, # Larger scale = more detail
    "AMPLITUDE": 15.0, #strength
    "AXIS_MASK": (True, False, True) 
}
func = get_displaced_position

layer_direction = Vector((0.0, 0.0, 1.0))
layerdArray, contentsArray, smooth_value_array = create_layered_array(
    dims=dims,
    direction=layer_direction,
    min_val=-0.24,
    max_val=0.24,
    min_layer_thickness=2.0,
    max_layer_thickness=5.0,
    distort_func=func, #"SCALE": 0.1, "AMPLITUDE": 2.2,
    distort_parmeters=parmeters   
    )
    
land_array = GradienArray * 1.1 + NoiseArray * 3.1 + layerdArray * 1.2
#contentsArray, smooth_value_array = create_stepped_arrays(voxel_array=land_array, start_value=0.0, step_value=1)
"""

#land exp
"""parmeters = {
    "NOISE": 'VORONOI_F2F1', #
    "SCALE": 0.1, # Larger scale = more detail
    "AMPLITUDE": 2.2, #strength
    "AXIS_MASK": (True, True, True) 
}
func = get_displaced_position

grad_dir = Vector((-0.0, 0.5, -1.0))

#Create a gradient voxels
Array1 = create_gradient_array(
    direction=grad_dir,
    min_val=-1.0,
    max_val=1.0,
    dims=dims,
    distort_func=func, #"SCALE": 0.15, "AMPLITUDE": 6.0,
    distort_parmeters=parmeters
)

parmeters = {
    "NOISE": 'BLENDER', #
    "SCALE": 0.3, # Larger scale = more detail
    "AMPLITUDE": 3.2, #strength
    "AXIS_MASK": (True, True, False) 
}
func = get_displaced_position

Array2 = create_noise_array(
    dims=dims,
    noise_type='PERLIN_NEW',
    offset = Vector((3.0, 2.0, 0.0)),
    scale=Vector((0.08, 0.08, 0.03)), # Larger scale = more detail
    distort_func=func, #"SCALE": 0.3, "AMPLITUDE": 4.5,
    distort_parmeters=parmeters
)

parmeters = {
    "NOISE": 'BLENDER', #
    "SCALE": 0.1, # Larger scale = more detail
    "AMPLITUDE": 8.2, #strength
    "AXIS_MASK": (True, True, False) 
}
func = get_displaced_position

layer_direction = Vector((0.0, 1.0, 1.0)) #z y x
voxelsArray, contentsArray1, smooth_value_array1 = create_layered_array(
    dims=dims,
    direction=layer_direction,
    min_val=-0.3,
    max_val=1.0,
    min_layer_thickness=2.0,
    max_layer_thickness=5.0,
    distort_func=func, #"SCALE": 0.1, "AMPLITUDE": 2.2,
    distort_parmeters=parmeters   
)





Array3 = Array1 * 0.6 + Array2 * 0.6 + voxelsArray







Array4 = cast_upward_ray_to_backface(
    dimensions=dims,
    direction=Vector((0.0, 1.0, 0.0)),
    record_distance=True,
    #distort_func=func, #"SCALE": 0.15, "AMPLITUDE": 6.0,
    #distort_parmeters=parmeters
)

Array4 = Array4 * 4

contentsArray2, smooth_value_array2 = create_surface_layers_numpy(voxel_array=Array4, cutoff=0.3, direction=Vector((0.1, 0.2, 1.0)), layer_deform=0.8, layer_thickness=0.09 )


    
land_array, smooth_value_array, contentsArray = combine_arrays_by_comparison(
    array_a=Array3,
    array_b=Array4,
    array_a_smooth=smooth_value_array1,
    array_b_smooth=smooth_value_array2,
    array_a_contents=contentsArray1,
    array_b_contents=contentsArray2,
    is_greater_than=False
)"""





