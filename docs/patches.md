# Patches

Patches must be compressed in `.7z`, `.rar`, or `.zip` format and must be named
according to the following the scheme `<CRC32> - <TITLE>` in order to be
recognised and used by _Emulauncher_:

  * `<CRC32>` must be the clean CRC32 of the ROM the patch can be applied onto.
              _Emulauncher_ obtains the CRC32 of ROMs from `.dat` files; hence
              ROM files not included in a `.dat` file can't be patched.
  * `<TITLE>` is the title of the patch (not the ROM or the game), and it'll
              appear in the patch selection menu. In principle, it can be
              anything you want as long as the characters can be used in a path.
              Use something short, and descriptive such as `English
              translation`, `Increased difficulty hack`, `Colors closer to
              arcade version`...

Inside the compressed files you must put the following files:

  * A `readme.txt` with all the information possible about the patch. Patch
    files are the result of the hard work of dedicated individuals or teams.
    They frequently release the patches with text files explaining the reason
    behind the patch, and the changes achieved in the game. It's a good idea to
    include all that documentation in the `readme.txt` file. It's highly
    recommended to indicate at the very top of the file the full name of the
    ROM, the CRC32, and the date of the patch.

  * As many patch files as required with following naming convention:
    `patch-<X>[-Y]`:
    * `<X>`
      * **For single file ROMS** (e.g. SNES games), it will always be **0**.
      * **For single disc games**, it's the index of the "clean" file this patch
        file must be applied to. Below you can see an exampleFor example, if you
        had a Playstation 1 game composed by just 1 CD containing the files:
        * `track list.cue` → Nothing, because `.cue` files are ignored.
        * `track 01.bin` → 0
        * `track 02.bin` → 1
      * **For multi-disc games**, it's the number of the disc containing the
        file the patch has to be applied onto. Remember we will start counting
        at zero.
    * `[-Y]` **It's only used for multi-disc games**, and is the index of the
       clean file the patch has to be applied onto.

Below you can see a sample structure for a patch that modifies the first file of
the first CD of a Playstation 1 game, and the third file of the second CD.

    0af5c34b - French translation.zip
        ├ readme.txt
        ├ patch-0-0.xdelta
        └ patch-1-2.bps

Notice that each patch file can have a different format (`.xdelta` and `.bps` in
the above example).

    