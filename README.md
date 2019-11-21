# PyPiGFX

PyPiGFX is inspired by [Pigfx](https://github.com/fbergama/pigfx), which is a video output device for single board computers and other microcomputers that have no display of their own. Computers can use PiGFX as a display target by simply connecting a serial cable to the Pi; it's a *really* great idea.

The difference between this project and PiGFX, is that PyPiGFX is specially designed as a graphical output device, for those types of microcomputers. It's also written in Python; hence PyPiGFX.

# In more detail

In principle, PyPiGFX works as a high-level accelerated graphics device somewhat similar to a modern 3D accelerator for a PC. In the old days of the PC you had unfettered access to the video ram, could toggle registers and generally get in to a load of trouble! PyPiGFX doesn't try to do that, instead, PyPiGFX offers a command based interface to the Pi GPU; specifically it listens on a local interface for incoming commands which are remapped to libSDL functions which are run on the local GPU framebuffer and then transferred to the Pi HDMI output.

Although there are mechanisms to transfer data back and forth from microcomputer to Pi, the main intended workflow would be to load all of the assets up into the Pi memory, then use the equivalent of the SDL vram-to-vram commands so that we're not relying on the local memory of the microcomputer to store or transfer assets.

Since most of the load will actually be on the Pi itself, the interface for transferring display commands can be over a relatively modest link:

   * I2C
   * SPI
   * USB/Serial FIFO

# Implementation 

## GPU / Pi side

A stripped-down Linux kernel (with real-time patches applied) runs on the Pi, a single process (*pypigfx* itself) runs in place of init or any other user process. Pypigfx opens either the serial port, i2c or spi bus and listens for incoming commands.

PyPiGFX is implemented in Python, using the PySDL2 package, which relies on libSDL2 to interact with the hardware. A version of libSDL2 later than (??) must be used, as full-screen graphics acceleration was added in that version which did not rely on a running X server.

Without any connection, the HDMI output from the Pi will show a basic Linux text interface, with statistics about the running pypigfx process.

## Client / microcomputer side

The client computer opens up a serial interface to the Pi and starts sending commands. These commands are encoded versions of the libSDL functions. Since we are operating over a relatively slow link, with very modest processors, we don't want to send every single ASCII byte in the call verbatim:


    SDL_BlitSurface(sdl_bitmap, sdl_rect, sdl_window, sdl_rect)
    

Instead, our client library at compile time will turn that into something that looks like:


    fifo_send("0x09", "0x02", "0x00", "0x01", "0x00")


Then only the 12 bytes that are encoded in that call will need to traverse the serial interface; not references to memory locations and not serialized/deserialized and we don't have to convert between big-endian/little-endian objects depending on what client we're using (never mind the fact that we're not going to get even a partial framebuffer copied to/from a tiny little 8-bit micro like a Z80 or 6502!).

At the Pi end, it reads the first set of bytes: `0x09`, look it up, detect that it should have 4 further parameters, turn it into the function call `SDL_BlitSurface()` and run it. The Pi keeps a table of each of those reference codes as it creates new SDL objects, so it knows that `0x02` is an already loaded `SDL_bitmap`, for example.
