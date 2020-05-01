:doc:`/index`

Authors
=======

DeepDiff Core Developer:

- Sep Dehpour

    - `Github <https://github.com/seperman>`_
    - `ZepWorks <http://www.zepworks.com>`_
    - `Linkedin <http://www.linkedin.com/in/sepehr>`_
    - `Articles about Deepdiff <https://zepworks.com/tags/deepdiff/>`_

And many thanks to the following people for their contributions to DeepDiff!

- Victor Hahn Castell for major contributions
    - `hahncastell.de <http://hahncastell.de>`_
    - `flexoptix.net <http://www.flexoptix.net>`_
- nfvs for Travis-CI setup script.
- brbsix for initial Py3 porting.
- WangFenjin for Unicode support.
- timoilya for comparing list of sets when ignoring order.
- Bernhard10 for significant digits comparison.
- b-jazz for PEP257 cleanup, Standardize on full names, fixing line endings.
- finnhughes for fixing __slots__
- moloney for Unicode vs. Bytes default
- serv-inc for adding help(deepdiff)
- movermeyer for updating docs
- maxrothman for search in inherited class attributes
- maxrothman for search for types/objects
- MartyHub for exclude regex paths
- sreecodeslayer for DeepSearch match_string
- Brian Maissy (brianmaissy) for weakref fix, enum tests
- Bartosz Borowik (boba-2) for Exclude types fix when ignoring order
- Brian Maissy (brianmaissy) for fixing classes which inherit from classes with slots didn't have all of their slots compared
- Juan Soler (Soleronline) for adding ignore_type_number
- mthaddon for adding timedelta diffing support
- Necrophagos for Hashing of the number 1 vs. True
- Hugo (hugovk) for fixes for Python 3.10 and dropping support for EOL Python 3.4
- Andrey Gavrilin (gaal-dev) for hashing classes.
- gaal-dev for adding exclude_obj_callback
- Ivan Piskunov (van-ess0) for deprecation warning enhancement.
- Nathaniel Brown (nathanielobrown) Adds support for datetime.time
- Michał Karaś (MKaras93) for the pretty view
- Christian Kothe (chkothe) for the basic support for diffing numpy arrays


Back to :doc:`/index`
