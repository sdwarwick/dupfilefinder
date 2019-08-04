#! /usr/bin/python

import argparse
import os
import sys
import stat
import hashlib
import time

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter)

# parser.add_argument("command", choices=["file", "site"], help=help_text)  # required command
parser.add_argument( "path", nargs="+",
                    default=None, type=str, help="filePath")
parser.add_argument("--verbose", "-v", dest="verbose", default=False,
                    help="verbose" , action='store_true')
p = parser.parse_args()

#print("command line:", p, file=sys.stderr)

if p.path is None:
    print("No path defined", file=sys.stderr)
    exit()

filesBySize = {}
totalInputFiles = 0

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

for thisMapValue in p.path:
    if p.verbose:
        print ('Scanning directory "%s"....' % thisMapValue)

    for root, dirs, files in os.walk(thisMapValue):
        #print ('Scanning directory "%s"....' % root)
        totalInputFiles += len(files)
        walker(root,files)

duplicateList = []

if p.verbose:
    print ('Finding potential dupes...')
potentialDupes = []
potentialCount = 0
sizeList = list(filesBySize.keys())
sizeList.sort()
for size in sizeList:
    sameSizeFiles = filesBySize[size]

    if len(sameSizeFiles) is 1:
        continue
    if p.verbose:
        print ('Short Test %d files of size %d' % (len(sameSizeFiles), size))

    sameSizeFileHashMap = {}
    for fileName in sameSizeFiles:
        if not os.path.isfile(fileName):
            continue

        aFile = open(fileName, 'rb')
        hashValue = hashlib.sha3_256(aFile.read(1024)).digest()
        if hashValue in sameSizeFileHashMap.keys():
            sameSizeFileHashMap[hashValue].append(fileName)
        else:
            sameSizeFileHashMap[hashValue] = [fileName]
        aFile.close()

    for hashKey in sameSizeFileHashMap.keys():
        fileList = sameSizeFileHashMap.get(hashKey)
        if len(fileList) <= 1:
            continue
        if size < 1024:
            if p.verbose:
                print("Short file duplicate found: %s" % fileList[0])

            duplicateList.append( (size,fileList) )  # add file list tagged with size of file
            continue

        # queueing for long file test
        potentialDupes.append(fileList)
        potentialCount = potentialCount + len(fileList)

del filesBySize

if p.verbose:
    print ('Found %d sets of potential dupes...' % potentialCount)
    print ('Scanning for long file dupes...')


for aSet in potentialDupes:
    sameSizeFileHashMap = {}

    size = os.path.getsize(aSet[0])

    for fileName in aSet:
        if p.verbose:
            print ('Scanning file "%s"...' % fileName)
        aFile = open(fileName, 'rb')
        hasher =  hashlib.sha3_256()
        while True:
            r = aFile.read(4096)  # unclear why so small
            if not len(r):
                break
            hasher.update(r)
        aFile.close()
        hashValue = hasher.digest()

        if hashValue in sameSizeFileHashMap.keys():
            sameSizeFileHashMap[hashValue].append(fileName)
        else:
            sameSizeFileHashMap[hashValue] = [fileName]

    for hashKey in sameSizeFileHashMap.keys():
        fileList = sameSizeFileHashMap.get(hashKey)
        if len(fileList) <=1:
            continue
        duplicateList.append( (size,fileList))

# largest duplicate files first
duplicateList.sort( key = lambda v: v[0],reverse=True)

foundDupes = 0
for taggedFileList in duplicateList:
    fileSize = taggedFileList[0]
    fileList = taggedFileList[1]
    timeMap = {}
    for fileName in fileList:
        timeMap[os.path.getmtime(fileName)] = fileName
    orderedTimesList = list(timeMap.keys())
    orderedTimesList.sort()

    first = orderedTimesList[0]
    rest = orderedTimesList[1:]
    foundDupes += len(rest)

    print ('\n\nOriginal is %10d bytes Mod Date: %s -- %s' % (fileSize,time.strftime("%m/%d/%Y %H:%M:%S",time.gmtime(first)),timeMap[first]))

    for t in rest:
        print ('    Able to Delete %s -- %s' % (time.strftime("%m/%d/%Y %H:%M:%S",time.gmtime(t)),timeMap[t]))
        #os.remove(f) - Dont do this!!!
print ( "total Dupes: ", foundDupes)
print ( "total Input Files: ", totalInputFiles)
