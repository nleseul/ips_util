# ips-util

## Summary

This is a Python package for manipulating binary patches encoded in the International Patching System (IPS) format, as documented [here](http://fileformats.archiveteam.org/wiki/IPS_(binary_patch_format)) and [here](http://old.smwiki.net/wiki/IPS_file_format). IPS is a format that historically has been widely used for the distribution of ROM hacks for classic game consoles; as far as I know it remains a standard format today, despite its known limitations, and tools for using it are still helpful.

While the ips-util package does provide a command-line interface for creating and applying patches analagous to the GUI provided by [Lunar IPS](https://fusoya.eludevisibility.org/lips/) and similar tools, I created it mainly to assist in writing Python scripts that generate ROM hacks and output IPS patches. Thus it may not be as full-featured as other programs... but given how bare-bones the IPS format is, I'm not sure how "full-featured" such a tool could really be. 

I've included a suite of tests to verify that ips-util handles the known pitfalls of the IPS format as best I can, but there may still be some edge cases I haven't thought of. I also haven't put too much thought into optimizing the creation of patches from a source and target file... the results seem pretty good based on limited testing, but I know that [Flips](https://github.com/Alcaro/Flips), for example, still has some optimizations I haven't bothered to implement. I'm not too worried about it; we don't live in a world where the difference between a 2Kb and a 3Kb patch matters to anyone that much anymore. 

## Command line usage

The package provides a command-line interface which can be accessed independently of the Python shell (although `python -m ips_util` will still work if you really want it...). 

To create a patch, using existing source and target binary files:

```bash
> ips_util create "Super Mario World.smc" "Super Mario World [1337357_h4x_3v4r].smc" -o 1337_p47ch.ips
```

To apply a patch to a binary file:

```bash
> ips_util apply 1337_p47ch.ips "Super Mario World.smc" -o w00t.smc
```

Note that in both cases, if an output file is not specified using the `-o` flag, the result will be written to stdout, for use in whatever complicated `bash` shenanigans you Linux kids get up to these days. 

You can also dump the contents of a patch, to preview it or to debug your patch creation scripts:

```bash
> ips_util trace 1337_p47ch.ips
```

(However, for the moment, a proper visual tool like [ips-peek](https://github.com/vector-man/IPS-Peek) is probably better in every way for that purpose.)

## Usage in scripts

Very simple:

```python
from ips_util import Patch

def this_is_my_patch():
  patch = Patch()
  
  patch.add_record(0x1234, 0xff)              # Max out some stat
  patch.add_rle_record(0x5678, b'\xea', 0x10) # NOP out a bunch of code
  
  with open('gavroche.ips', 'w+b') as f:
    f.write(patch.encode())
```

Or:

```python
from ips_util import Patch

def dude_wheres_my_patch():
  patch = Patch.load('gavroche.ips')
  
  with open('some_data.smc', 'rb') as f_in:
    with open('some_patched_data.smc', 'w+b') as f_out:
      f_out.write(patch.apply(f_in.read()))
```
