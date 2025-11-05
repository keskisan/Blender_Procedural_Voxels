This script does procedural voxel generation. It is used by calling functions and passing variables between them. It was specifically designed to be modular

The workflow is relatively straight forward. A voxel array of dimensions x, y, z is created of type float. These can be created by one of the functions or in what ever other way. These can also be added, divided or have any other mathematical function applied to them. In its final form it is to be called land_array

Two more arrays are needed, one of type int which describes the contents of the voxels.  Its will be used to map the texture which are tiles of soil or sand or moss or rock or what ever. The other is of type float and describes how smooth that part of the voxel object is. Best values are between -0.25 for rough and 0.45 for smooth. These two arrays can be generated which ever way, but is usually generated from the land_array using one of the relevant functions. create_layered_array function can generate all three arrays at once.  In their final form these are called contentsArray and smooth_value_array

These three arrays are sufficient to generate voxels.
