# Random-Shapes
Generate random shapes in Blender

<h1>Overview</h1>

This is a Blender add-on that creates random shapes.

<h1>Installation</h1>
Download the zip. Open Blender. Edit > Preferences > Add-ons. Click the install button at the top and navigate to the zip.
Random Shapes is in the "n" menu (hot key n when in 3D viewport) under the tab Random Curves.</br>

![screenshot](images/readmeSS.JPG?raw=true)

<b>Cut Settings:</b></br>
* Number of Cuts
  * The number of cuts that are made to the selected object.
* Number of Recursive Cuts
  * The number of recursive cuts that are made to each generated object.
  * After the initial number of cuts are made, each generated object will be cut again by the Number of Cuts. This process is repeated for each of the Number of Recursive Cuts specified. Higher values here can cause generation to take a long time.
* Chance of Recursive Cuts
  * The percent chance that an object will be recursively cut.
* Make Only Cubes
  * When checked only rectangles are generated.
  * When unchecked random polygons are created.
* Cut on:
  * Must include 1 axis.
  * Cuts are made on any included axis.

<b>Finishing Settings:</b></br>
* Use Solidify
  * Adds a solidify modifier to each generated object with the settings below.
* Vary Height
  * When checked the Random Thickness range is used to determine the thickness of each generated object.
  * When unchecked the Uniform Thickness value is used to determine the thickness of each generated object.

* Use Bevel
  * Adds a bevel modifier to each generated with the settings below.
* Bevel Width
  * The bevel width setting applied to each object
* Bevel Segments
  * The bevel segments added to each object.
  
* Use SubD
  * Adds a subdivision surface modifier to each generated object.
* SubD Level
  * The number of subdivision levels added to each object.
  
* Add to a Collection
  * Adds each object to the collection in the name field.
  * If the collection does not exist it will be created.
  * If no collection is specified it adds to "Collection"

* Generate Random Shapes
  * Generates shapes with the settings above.
  
version 1.0.0
