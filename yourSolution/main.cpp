#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

using namespace std;

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/

int main()
{
    int surface_n; // the number of points used to draw the surface of Mars.
    cin >> surface_n; cin.ignore();
    for (int i = 0; i < surface_n; i++) {
        int land_x; // X coordinate of a surface point. (0 to 6999)
        int land_y; // Y coordinate of a surface point. By linking all the points together in a sequential fashion, you form the surface of Mars.
        cin >> land_x >> land_y; cin.ignore();
    }

    // game loop
    while (1) {
        int x;
        int y;
        int h_speed; // the horizontal speed (in m/s), can be negative.
        int v_speed; // the vertical speed (in m/s), can be negative.
        int fuel; // the quantity of remaining fuel in liters.
        int rotate; // the rotation angle in degrees (-90 to 90).
        int power; // the thrust power (0 to 4).
        cin >> x >> y >> h_speed >> v_speed >> fuel >> rotate >> power; cin.ignore();

        // Write an action using cout. DON'T FORGET THE "<< endl"
        // To debug: cerr << "Debug messages..." << endl;


        // rotate power. rotate is the desired rotation angle. power is the desired thrust power.
        cout << "-20 3" << endl;

		// Write the number of drawing commands that will follow
		cout << "0" << endl;

		// All the numbers must be integers
		// The color must respect the format '#RRGGBB' (not case sensitive)

		// Draw a line from point A to point B with a width of W and a color of C.
		// cout << "LINE Ax Ay Bx By W C" << endl;

		// Draw a circle centered on point A with a radius of R and a color of C.
		// cout << "CIRCLE Ax Ay R C" << endl;

		// Draw a point at point A with a width of W and a color of C.
		// cout << "POINT Ax Ay W C" << endl;

		// I strongly recommend you to create a object that will handle the drawing commands.
		// One that stores the commands and then prints them all at once for example.
    }
}