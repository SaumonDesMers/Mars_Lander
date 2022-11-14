# Mars Lander
A copy of the Mars Lander puzzle from [Codingame](https://www.codingame.com/training/medium/mars-lander-episode-2), but with drawing features that make debugging more visual.

<br/>

## Dependencies

This project is in python and uses external libraries like ```pillow``` and ```python-tk```.

<br/>

## How does it work
```
python3 mars_lander.py <your program> <input.json>
```


***\<your program\> :*** the command which will execute your program.

```./a.out``` if your program is compiled but ```"python3 main.py"``` if your program requires an interpreter.


***\<input.json\> :*** the JSON file that contains the simulation parameters.

The simulation parameters are the inputs that the game sends you at initialization and at the first turn.

All the tests that Codingame gives as well as the subject example are provided in the ```test``` folder.

> As a good developer, I should encourage you to do your own testing, but since Codingame provides us with ready-made tests, I guess it's not necessary. 🥳

If you still want to do your own test, look at the input files, I think their format is rather straightforward.

<br/>

## The drawing commands

In the original game, the only outputs required are **rotation** and **power**. But this version offers some additional features that allow you to draw in the game area.

Just after the **rotation** and **power** line, you will have to send, on a new line, a ```int N``` representing the number of drawing command you want to send.

Then, on the next N lines you will send one of these commands:

```LINE Ax Ay Bx By W C```: Draw a line from point A to point B with a width of W and a color of C.

```CIRCLE Ax Ay R C```: Draw a circle centered on point A with a radius of R and a color of C.

```POINT Ax Ay W C```: Draw a point at point A with a width of W and a color of C.

All the numbers must be ***integers*** and the color must respect the format ***#RRGGBB*** (not case sensitive).

<br/>

## Compatibility with Codingame

Except for the drawing commands, the auto-generated codes provided by Codingame are compatible with this program.

In the ```yourSolution``` folder, I have written 2 main (in ```python``` and ```cpp```) which are copies of the ones on Codingame but with some extra lines which explain how to send the drawing commands depending on each language.

If you want other languages, copy the code given by Codingame and add the necessary lines to send the drawing commands.
