# PyPiGFX

## Status

   * The Pi / Linux / master side of the application can accept incoming datastream messages via unix FIFO or serial device
   * The master is able to translate a limited number of datastream messages back into libSDL calls and execute them
   * Response codes and data is returned to the client
   * We can dynamically generate a sdl.py wrapper library for a Python based client
   * We are not yet generating a set of .c / .h stub pages that can be used to implement a client natively on a non-Linux system

----

## About PyPiGFX

PyPiGFX is inspired by [Pigfx](https://github.com/fbergama/pigfx), which is a video output device for single board computers and other microcomputers that have no display of their own. Computers can use PiGFX as a display target by simply connecting a serial cable to the Pi; it's a *really* great idea.

The difference between this project and PiGFX, is that PyPiGFX is specially designed as a graphical output device, for those types of microcomputers. It's also written in Python; hence PyPiGFX.

## In more detail

In principle, PyPiGFX works as a high-level accelerated graphics device somewhat similar to a modern 3D accelerator for a PC. In the old days of the PC you had unfettered access to the video ram, could toggle registers and generally get in to a load of trouble! PyPiGFX doesn't try to do that, instead, PyPiGFX offers a command based interface to the Pi GPU; specifically it listens on a local interface for incoming commands which are remapped to libSDL functions which are run on the local GPU framebuffer and then transferred to the Pi HDMI output.

Although there are mechanisms to transfer data back and forth from microcomputer to Pi, the main intended workflow would be to load all of the assets up into the Pi memory, then use the equivalent of the SDL vram-to-vram commands so that we're not relying on the local memory of the microcomputer to store or transfer assets.

Since most of the load will actually be on the Pi itself, the interface for transferring display commands can be over a relatively modest link:

   * I2C
   * SPI
   * USB/Serial FIFO

----

# Implementation 

## GPU / Pi side

A stripped-down Linux kernel (with real-time patches applied) runs on the Pi, a single process (*pypigfx* itself) runs in place of init or any other user process. Pypigfx opens either the serial port, i2c or spi bus and listens for incoming commands.

PyPiGFX is implemented in Python, using the PySDL2 package, which relies on libSDL2 to interact with the hardware. A version of libSDL2 later than (??) must be used, as full-screen graphics acceleration was added in that version which did not rely on a running X server.

Without any connection, the HDMI output from the Pi will show a basic Linux text interface, with statistics about the running pypigfx process.

## Client / microcomputer side

The client computer opens up a serial interface to the Pi and starts sending commands. These commands are encoded versions of the libSDL functions. Since we are operating over a relatively slow link, with very modest processors, we don't want to send every single ASCII byte in the call verbatim:


    SDL_BlitSurface(sdl_bitmap, sdl_rect, sdl_window, sdl_rect)
    

Instead, our client library at compile time will turn that into something that looks like:


    fifo_send("09", "1A", "00", "01", "00")


Then only the 10 bytes that are encoded in that call will need to traverse the serial interface; not references to memory locations and not serialized/deserialized and we don't have to convert between big-endian/little-endian objects depending on what client we're using (never mind the fact that we're not going to get even a partial framebuffer copied to/from a tiny little 8-bit micro like a Z80 or 6502!).

Since we use 2 bytes for each object reference and are using hexadecimal, that means we can keep track of up to 256 unique SDL objects (including the main display object); that's fairly huge - I'm certain we'll run out of memory on the client before that becomes an issue.

At the Pi end, it reads the first set of bytes: `0x09`, look it up, detect that it should have 4 further parameters, turn it into the function call `SDL_BlitSurface()` and run it. The Pi keeps a table of each of those reference codes as it creates new SDL objects, so it knows that `001A` is an already loaded `SDL_bitmap`, for example.

There will be some function calls where literal values are passed over the link; for example in the case of creating new SDL_bitmap or SDL_rect objects, we'll need to supply integers to specify sizes. We should be able to use a 3 byte value scheme for most cases (32768 values) to keep the datastream compact.

----

# API

Most SDL functions, in their native implementation, return either basic types (int, null, etc) or pointers to SDL structures (SDL_Window, SDL_Rect, etc).

Since we don't have a mechanism for passing SDL structures over a serial link, the SDL calls to PyPiGFX return a data structure of the following type:

`<status:,type:,value:>`

Where:

   * status: 0 or 1, indicates whether the call was executed or not by the Pi [0 == failed, 1 == success]
   * type: a textual description of the value being returned - int, string, SDL_Rect, etc
   * value: for basic types such as int or string, the literal value, for SDL_ types, a hexadecimal reference to the object

SDL object references are used in place of actual SDL objects in function calls. So where a call to create a new SDL_Rect returns "01D8", that reference is used in any future SDL call to refer to that specific object and the PyPiGFX process will automatically look up that object from its object store when you use it.

Note that the `<status:,type:,value:>` data structure is not passed back to your code; it is dealt with internally within the SDL functions in the client - your code will receive the `type` and `value` defined in the structure only. The details about the data structure are for debugging/data-monitoring purposes only.

**Note:** This documentation is not intended to teach you how to use SDL, for that, please consult one of the excellent [tutorials](https://wiki.libsdl.org/Tutorials), or one of my previous SDL projects: [sdlRFController, in Python + SDL2](https://github.com/megatron-uk/sdlRFController/tree/master/lib) or [sdlLauncher, in C + SDL1.2](https://github.com/megatron-uk/sdlRFController/tree/master/lib) ... actually, scratch that, don't use sdlLauncher, because the SDL1.2 way of doing things is now how you do it anymore...

## List of implemented functions

   * SDL_Init
   * SDL_Quit
   * SDL_CreateWindow
   * SDL_CreateRenderer
   * SDL_CreateRGBSurface
   * SDL_CreateTextureFromSurface
   * SDL_FillRect
   * SDL_GetDriverName
   * SDL_MapRGB
   * SDL_RenderCopy
   * SDL_RenderPresent

### SDL_Init(flags:int)
   * https://wiki.libsdl.org/SDL_Init
   * Description: Initialises the SDL subsystem and libraries on the host
   * Parameters
     * flags: An OR-ed set of SDL init flags (see https://wiki.libsdl.org/SDL_Init)
   * Returns: 0 on success

Example use:

```
int r;
flags = SDL_INIT_VIDEO|SDL_INIT_TIMER;
r = SDL_Init(flags);
```

   * If the call was not run, returns `<status:0,type:,value:>`
   * On SDL success, returns `<status:1,type:int,value:0>`
   * On SDL error, value shall be a negative integer

----

### SDL_Quit()
   * https://wiki.libsdl.org/SDL_Quit
   * Description: Closes all open SDL resources and windows
   * Parameters
     * None
   * Returns: void/null

Example use:

```
SDL_Quit();
```

   * If the call was not run, returns `<status:0,type:,value:>`
   * SDL_Quit returns void, so shall always return `<status:1,type:void,value:null>`

----

### SDL_CreateRenderer(window:SDL_Window, index:int, flags:int)
   * https://wiki.libsdl.org/SDL_CreateRenderer
   * Description: Returns an instance of a rendering context that can be used to perform drawing operations into a specific SDL_Window.
   * Parameters
     * window: Object ID of the SDL_Window to perform 2D drawing operations on
     * index: See https://wiki.libsdl.org/SDL_CreateRenderer
     * flags: An OR-ed set of SDL_RendererFlags (see https://wiki.libsdl.org/SDL_RendererFlags)
   * Returns SDL_Renderer object ID

Example use:

```
int renderer;
int window;
window = SDL_CreateWindow(title, 0, 0, 320, 240, flags);
renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
```

   * If the call was not run, returns `<status:0,type:,value:>`
   * On SDL success, returns `<status:1,type:SDL_Renderer,value:0ABC>` - where 0ABC is an SDL object ID reference that can be used in any subsequent calls requiring this SDL_Renderer object.
   * On SDL error, returns `<status:1,type:void,value:null>`

----

### SDL_CreateRGBSurface(flags:int, w:int, h:int, d:int, rmask:int, gmask:int, bmask:int, alpha:int)
   * https://wiki.libsdl.org/SDL_CreateRGBSurface
   * Description: Returns a new surface which can have content copied to it or edited, before being rendered to a window.
   * Parameters:
     * flags: Always set to 0, as per the SDL documentation
     * w: width of the surface, in pixels
     * h: height of the surface, in pixels
     * d: colour depth of the surface, in pixels
     * rmask: the value of the red channel to mask
     * gmask: the value of the green channel to mask
     * bmask: the value of the blue channel to mask
     * alpha: the level of alpha transparency for pixels on this surface
   * Returns SDL_Surface object ID

Example use:

```
int surface;
surface = SDL_CreateRGBSurface(0, 640, 480, 24, 0, 0, 0, 255)
```

   * If the call was not run, returns `<status:0,type:,value:>`
   * On SDL success, returns `<status:1,type:SDL_Surface,value:0ABC>` - where 0ABC is an SDL object ID reference that can be used in any subsequent calls requiring this SDL_Surface object.
   * On SDL error, returns `<status:1,type:void,value:null>`

----

### SDL_CreateTextureFromSurface(renderer:SDL_Renderer, surface:SDL_Surface)
   * https://wiki.libsdl.org/SDL_CreateTextureFromSurface
   * Description: Creates a texture suitable for rendering to a render context from an SDL_Surface object
   * Parameters:
     * renderer: An instance of an SDL_Renderer
     * surface: An instance of an SDL_Surface
   * Returns: An SDL_Texture object ID

```
int window;
int renderer;
int surface;
int texture;
window = SDL_CreateWindow("newwindow",0,0,640,480,0);
renderer = SDL_CreateRenderer(window,0,0);
surface = SDL_CreateRGBSurface(0,640,480,24,0,0,0,255);
texture = SDL_CreateTextureFromSurface(renderer, surface);
```

   * If the call was not run, returns `<status:0,type:,value:>`
   * On SDL success, returns `<status:1,type:SDL_Texture,value:0ABC>` - where 0ABC is an SDL object ID reference that can be used in any subsequent calls requiring this SDL_Texture object.
   * On SDL error, returns `<status:1,type:void,value:null>`

----

### SDL_CreateWindow(char* title, x:int, y:int, w:int, h:int, flags:int)
   * https://wiki.libsdl.org/SDL_CreateWindow
   * Description: Opens a new SDL window (fullscreen or otherwise) that we can use to draw in and render
   * Parameters
     * title: A pointer to a string representing the title of the window (if not fullscreen)
     * x: The x position of where the new window will be created (if not fullscreen)
     * y: The y position of where the new window will be created (if not fullscreen)
     * w: Width of the new window, in pixels
     * h: Height of the new window, in pixels
     * flags: An OR-ed set of SDL_WindowFlags (see https://wiki.libsdl.org/SDL_WindowFlags)
   * Returns: SDL_Window object ID

Example use:

```
char *title = "MyWindow";
flags = SDL_WINDOW_FULLSCREEN | SDL_WINDOW_BORDERLESS;
r = SDL_CreateWindow(title, 0, 0, 320, 240, flags); // where r is a returned data structure
```

   * If the call was not run, returns `<status:0,type:,value:>`
   * On SDL success, returns `<status:1,type:SDL_Window,value:0ABC>` - where 0ABC is an SDL object ID reference that can be used in any subsequent calls requiring this SDL_Window object.
   * On SDL error, returns `<status:1,type:void,value:null>`


----

### SDL_GetCurrentVideoDriver()
   * https://wiki.libsdl.org/SDL_GetCurrentVideoDriver
   * Description: Returns a string representing the name of the current Video output driver
   * Parameters:
     * None
   * Returns: String of the current driver

Example use:

```
char *driver;
driver = SDL_GetCurrentVideoDriver();
```

   * If the call was not run, returns `<status:0,type:,value:>`
   * On SDL success, returns `<status:1,type:str,value:rpi>` - where *rpi* is an example of one of the available SDL video drivers, on desktop Linux systems you may find *x11*, or *opengl*.
   * On SDL error, returns `<status:1,type:void,value:null>`

----

### SDL_FillRect(surface:SDL_Surface, rect:[SDL_Rect|None], colour:SDL_Colour)
   * https://wiki.libsdl.org/SDL_FillRect
   * Description: Fills a rectangular region on a SDL_Surface, defined by an optional SDL_Rect structure, with a given SDL_Colour value
   * Parameters:
     * surface: the SDL_Surface into which we want to fill with a new colour
     * rect: either an SDL_Rect instance of the bounding box of the area to colour, *or* blank (*use ,,*) to use the entire SDL_Surface
     * colour: an example of an SDL_Colour as returned by SDL_MapRGB

Example use:

```
int my_colour;
int my_surface;
my_surface = SDL_CreateRGBSurface(0, 320, 240, 24, 0, 0, 0, 255);
my_colour = SDL_MapRGB(my_surface, 255, 0, 0);
SDL_FillRect(my_surface,, my_colour); // Fills the entire SDL_Surface with solid red

``` 

   * If call was not run, returns `<status:0,type:,value:>`
   * On SDL success, returns `<status:1,type:int,value:0>`
   * On SDL error, returns `<status:1,type:void,value:null>`

----

### SDL_MapRGB(surface:SDL_Surface, r:int, g:int, b:int)
   * https://wiki.libsdl.org/SDL_MapRGB
   * Description: Returns a colour value appropriate to the format of a given pixel format associated with a surface (i.e. matches the closest available colour for a given rgb value).
   * Parameters
     * surface: Object ID of the SDL_Surface to retrieve the SDL_PixelFormat structure from.
     * r: Integer value of the red channel (8 bits precision)
     * g: Integer value of the green channel (8 bits precision)
     * b: Integer value of the blue channel (8 bits precision)
   * Returns: Integer representing the closest available RGB colour

Example use:

```
int my_colour;
int my_surface;
my_surface = SDL_CreateRGBSurface(0, 320, 240, 24, 0, 0, 0, 255);
my_colour = SDL_MapRGB(my_surface, 255, 0, 0);
```

   * If call was not run, returns `<status:0,type:,value:>`
   * On SDL success, returns `<status:1,type:int,value:FF0000>` - where FF0000 is the RGB colour value of the closet matching available colour, solid red in this case.
   * On SDL error, returns `<status:1,type:void,value:null>`
   * NOTE: There is a change compared to the libSDL documentation linked above - the original call includes an explicit reference to a SDL_PixelFormat structure, with this implementation the SDL_PixelFormat is derived from the SDL_Surface referred to in the call.

----

### SDL_RenderCopy(renderer:SDL_Renderer, texture:SDL_Texture, [SDL_Rect|None], [SDL_Rect|None])
   * https://wiki.libsdl.org/SDL_RenderCopy
   * Description: Copies all or a partial texture to the output rendering context

----

### SDL_RenderPresent(renderer:SDL_Renderer)
   * https://wiki.libsdl.org/SDL_RenderPresent
   * Description: Updates the output device with any changes since the last call. This updates the screen!

----

## List of planned functions

  * SDL_BlitSurface
  * SDL_DestroyTexture
  * SDL_Drivertype
  * SDL_FreeSurface
  * SDL_GetCurrentDisplayMode
  * SDL_GetNumVideoDisplays
  * SDL_GetWindowDisplayMode
  * SDL_GetWindowSize
  * SDL_LoadBMP
  * SDL_Rect
  * SDL_RenderCopy
  * SDL_RenderDrawLine
  * SDL_RenderPresent
  * SDL_SetRenderDrawColor
  * SDL_ShowCursor

Additional SDL_ttf functions:

  * TTF_CloseFont
  * TTF_Init
  * TTF_OpenFont
  * TTF_Quit
  * TTF_RenderText_Blended
