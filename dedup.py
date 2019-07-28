#! /usr/bin/python

import os
import sys
import stat
import hashlib

filesBySize = {}

def walker( dirname, fnames):
    # add files in the specified directory to the file list, sorted and skipping small files
    d = os.getcwd()
    os.chdir(dirname)
    try:
        fnames.remove('Thumbs')
    except ValueError:
        pass
    for f in fnames:
        if not os.path.isfile(f):
            continue
        size = os.stat(f)[stat.ST_SIZE]
        if size < 100:
            continue

        if size not in filesBySize.keys():
            filesBySize[size] = []

        filesBySize[size].append(os.path.join(dirname, f))

    os.chdir(d)

for x in sys.argv[1:]:
    print ('Scanning directory "%s"....' % x)
    for root, dirs, files in os.walk(x):
        #print ('Scanning directory "%s"....' % root)
        walker(root,files)

print ('Finding potential dupes...')
potentialDupes = []
potentialCount = 0
trueType = type(True)
sizes = list(filesBySize.keys())
sizes.sort()
for k in sizes:
    inFiles = filesBySize[k]
    outFiles = []
    hashes = {}
    if len(inFiles) is 1: continue
    print ('Testing %d files of size %d...' % (len(inFiles), k))
    for fileName in inFiles:
        if not os.path.isfile(fileName):
            continue
        aFile = open(fileName, 'rb')
        hashValue = hashlib.sha3_256(aFile.read(1024)).digest()
        if hashValue in hashes.keys():
            x = hashes[hashValue]
            if type(x) is not trueType:
                outFiles.append(hashes[hashValue])
                hashes[hashValue] = True
            outFiles.append(fileName)
        else:
            hashes[hashValue] = fileName
        aFile.close()
    if len(outFiles):
        potentialDupes.append(outFiles)
        potentialCount = potentialCount + len(outFiles)
del filesBySize

print ('Found %d sets of potential dupes...' % potentialCount)
print ('Scanning for real dupes...')

# could make this faster by recognizing that we've already validated all dupes for files less than 1024 bytes, don't need to
# check again

dupes = []
for aSet in potentialDupes:
    outFiles = []
    hashes = {}
    for fileName in aSet:
        print ('Scanning file "%s"...' % fileName)
        aFile = open(fileName, 'rb')
        hasher =  hashlib.sha3_256()
        while True:
            r = aFile.read(4096)
            if not len(r):
                break
            hasher.update(r)
        aFile.close()
        hashValue = hasher.digest()
        if hashValue in hashes.keys():
            if not len(outFiles):
                outFiles.append(hashes[hashValue])
            outFiles.append(fileName)
        else:
            hashes[hashValue] = fileName
    if len(outFiles):
        dupes.append(outFiles)

i = 0
for d in dupes:
    print ('\n\nOriginal is %s' % d[0])
    for f in d[1:]:
        i = i + 1
        print ('    Able to Delete %s' % f)
        #os.remove(f)
print ( "total Dupes: ", i)
