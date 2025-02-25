# Simple Text Editor

Simple Text Editor implementation in Python using tkinter for the GUI and implemented using a Gap Buffer for efficient insertions/deletions in the editing of a text file. Loading and Saving files is also implemented.

Gap buffers work by moving the gap to the edit location so that insert and delete operations clustered nearby are more efficient. Text is stored in a "buffer"; in this case a python list in two segments. The segments are separated by the "gap". Operations at different locations in the text could cause a lot of copying to occur (to move the gap), which is inefficient, so the use of a gap buffer assumes copying occuring rarely compared to the gains found in the cheaper operations.
