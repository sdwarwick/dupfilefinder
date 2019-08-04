# dupfilefinder
Python 3 duplicate file finder

####Usage:

    dedup.py [-v]  path1 path2 ...

Scans through paths looking for duplicate files.  

Process is:
1. gather all files by size   (```map[size] = [file list]```)
1. read first 1k bytes of same-size files, hash using sha-256
1. gather files with same size and same hash
1. if the files in this gathered group are less than 1k in size, mark as duplicate
1. if the files in the gathered group are more than 1k in size, enqueue for further testing
1. for each file in the group gathered by same size and 1k byte hash,  with files greater than 1k, create new hash based on reading through the entire file.
1. create new groups based on the new full-file hashes. 
1. if hashes are the same, mark as duplicates
1. order by largest file first, mark earliest file as "original" and all others as duplicates
1. report 

#### Skip patterns
* skip files < 100 bytes
* skip thumbnails

#### Discussion

This process efficiently identifies the duplicate files.

Scanned 54917 files, found 32420 duplicate files, time: 20 seconds
