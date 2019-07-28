# Bouncer
My first "large-scale" programming project done in an official programming language (Python). It's a simple physics program that simulates balls bouncing off of rectangles. It was made using PyGame. Originally, my final product didn't have any user interface, but I decided to add one before publishing it to GitHub, so here it is.

INSTRUCTIONS:
Press F to enable the overlay, which shows the underlying geometry that makes the physics work (what distances are used to calculate collisions and such). Hold G while pressing the arrow keys to change the gravity. The first number shown in the top left is the vertical component and the second one is the horizontal component, with positive numbers corresponding to "down" and "left". When using the Spawner (top right with overlay enabled), make sure to enter the values in the input boxes in the correct format. Otherwise, the values of the new spawned objects will stick to their defaults. The space is 900x600 pixels. As stated in the Spawner, left click anywhere on the screen to spawn the object you have selected along with the properties entered, if any (except in the Spawner itself). To delete an object, right click it. Rectangles (aka "grounds") cannot be deleted.

BUGS:
-If a ball is going fast enough, it will slightly phase into any rectangles it bounces off of.
-If a ball is spawned inside of a rectangle, its center will bounce off of the sides of the rectangle from the inside as if it were hollow.
-If a ball is spawned partially inside of a rectangle, it may stick to that side or glitch into/out of it.
-Collisions with multiple rectangles at once are... unfavorable.
