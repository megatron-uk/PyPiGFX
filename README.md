# PyPiGFX

## Status

   * The Pi / Linux / master side of the application can accept incoming datastream messages via FIFO
   * The master is able to translate a limited number of datastream messages back into libSDL calls and execute them
   * Data is not yet being returned to the client
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

## List of implemented functions

### SDL_Init(flags:int)
   * https://wiki.libsdl.org/SDL_Init
   * Description: Initialises the SDL subsystem and libraries on the host
   * Parameters
     * flags: An OR-ed set of SDL init flags (see https://wiki.libsdl.org/SDL_Init)

Example use:

```
flags = SDL_INIT_VIDEO|SDL_INIT_TIMER;
r = SDL_Init(flags); // Where r is a returned data structure
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

Example use:

```
r = SDL_Quit(); // where r is a returned data structure
```

   * If the call was not run, returns `<status:0,type:,value:>`
   * SDL_Quit returns void, so shall always return `<status:1,type:void,value:null>`

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

## List of planned functions

  * SDL_BlitSurface
  * SDL_CreateRenderer
  * SDL_CreateRGBSurface
  * SDL_DestroyTexture
  * SDL_Drivertype
  * SDL_FillRect
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