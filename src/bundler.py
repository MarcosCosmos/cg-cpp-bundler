#!/usr/bin/python3
import sys
import os
import re

DEFAULT_INPUT_FILEPATH = 'main.cpp'

definesFound = {}
ifStack=[]

includeGuardPrefix = '__INCLUDE_GUARD_'
def processInclude(line):
    macro = re.search('^#include ".+"', line)
    if macro is not None:
        fileContents = ""
        oldWorkingDirectory = os.getcwd()
        includeFilePath = macro.group(0).split('#include "')[1].split('"')[0]
        lastDirSepPos = includeFilePath.rfind('/')
        if lastDirSepPos == -1:
            lastDirSepPos = includeFilePath.rfind('\\')
        if lastDirSepPos != -1:
            includePath, includeFileName = includeFilePath[0:lastDirSepPos], includeFilePath[lastDirSepPos+1:]
            os.chdir(includePath)
        else:
            includeFileName = includeFilePath
        with open(includeFileName, 'r') as subFile:
            subFileContents = scan(subFile).strip()
            fileContents += '%s%s' % (subFileContents, '\n' if len(subFileContents) > 0 else '')
        #now get the corresponding .cpp, unless it was for some reason the actual include above
        splitFileName = includeFileName.rsplit('.', 1)
        if len(splitFileName) == 2:
            name, ext = splitFileName
            if ext.lower() != 'cpp':
                srcFileName = name + '.cpp'
                if not os.path.isfile(srcFileName):
                    #try a .c file instead
                    srcFileName = name + '.c'

                if os.path.isfile(srcFileName):
                    with open(srcFileName, 'r') as subFile:
                        associatedDefine = (includeGuardPrefix + os.path.abspath(srcFileName))
                        if not associatedDefine in definesFound:
                            definesFound[associatedDefine] = True
                            subFileContents = scan(subFile).strip()
                            fileContents += '%s%s' % (subFileContents, '\n' if len(subFileContents) > 0 else '')
        os.chdir(oldWorkingDirectory)

        fileContents = fileContents.strip()
        return '%s%s' % (fileContents, '\n' if len(fileContents) > 0 else '')
    else:
        return None

def processDefine(line):
    macro = re.search('^#define %s(_|\w|[0-9])+' % includeGuardPrefix, line)
    if macro is not None:
        definedThing = macro.group(0).split('#define %s' % includeGuardPrefix, 1)[1]
        definesFound[definedThing] = True
        return line
    else:
        return None

def processUndef(line):
    macro = re.search('^#undef %s(_|\w|[0-9])+' % includeGuardPrefix, line)
    if macro is not None:
        definedThing = macro.group(0).split('#undef %s' % includeGuardPrefix, 1)[1]
        if definedThing in definesFound:
            del definesFound[definedThing]
        return line
    else:
        return None


def processIf(line):
    macro = re.search('^#if .+', line)
    if macro is not None:
        return True
    else:
        return None

def processIfDef(line):
    macro = re.search('^#ifdef (_|\w|[0-9])+', line)
    if macro is not None:
        targetThing = macro.group(0).split('#ifdef %s' % includeGuardPrefix, 1)
        if len(targetThing) > 1:
            targetThing = targetThing[1]
            return 1 if targetThing in definesFound else 0
        else:
            return 2
    else:
        return None

def processIfNDef(line):
    macro = re.search('^#ifndef (_|\w|[0-9])+', line)
    if macro is not None:
        targetThing = macro.group(0).split('#ifndef %s' % includeGuardPrefix, 1)
        if len(targetThing) > 1:
            targetThing = targetThing[1]
            return 1 if not (targetThing in definesFound) else 0
        else:
            return 2
    else:
        return None

def processEndif(line):
    macro = re.search('^#endif', line)
    if macro is not None:
        return True
    else:
        return None

#if the macro was found, this returns whether or not associated file already has been pragma-onced, otherwise returns None
def processPragmaOnce(line, file):
    macro = re.search('^#pragma once', line)
    if macro is not None:
        associatedDefine = 'PRAGMA:' + includeGuardPrefix + os.path.abspath(file.name)
        if not associatedDefine in definesFound:
            definesFound[associatedDefine] = True
            return False
        else:
            return True
    else:
        return None

def scan(file):
    fileContents = ""
    for line in file.readlines():
        temp = processIf(line)
        if temp is not None:
            ifStack.append(2)
            fileContents += line
            continue

        temp = processEndif(line)
        if temp is not None:
            if len(ifStack) != 0:
                top = ifStack[-1]
                ifStack.pop()
            else:
                top = False
            if top == 2:
                fileContents += line
            continue

        temp = processIfDef(line)

        #handle ifdef and ifndef with the same main thing below this one
        if temp is None:
            temp = processIfNDef(line)

        if temp is not None:
            #ignore any macros in an #if we're not fully handling, other than includes
            #this means that the contents of #ifs cannot take advantage of the size reduction, but won't produce invalid code
            if len(ifStack) == 0 or ifStack[-1] == 1:
                nextIfValue = temp
            else:
                nextIfValue = ifStack[-1]
            if nextIfValue == 2:
                fileContents += line
            ifStack.append(nextIfValue)
            continue
        #only try to deal with macros if not nested in a macro we are skipping.
        if len(ifStack) == 0 or ifStack[-1] == 1:
            #don't include anything in this file if we see #pragma once
            temp = processPragmaOnce(line, file)
            if temp is not None:
                if temp == True:
                    return ""
                else:
                    continue

            temp = processDefine(line)
            if temp is not None:
#                fileContents += temp
                continue

            temp = processUndef(line)
            if temp is not None:
                fileContents += temp
                continue
        #include process includes if we are not ommitting this entire block
        if len(ifStack) == 0 or ifStack[-1] != 0:
            temp = processInclude(line)
            if temp is not None:
                fileContents += temp
                continue

            #if nothing else happened, just add the line to the file
            fileContents += line

    return fileContents.strip()


#process the initial input file path, moving to to the appropriate path if neccessary
oldWorkingDirectory = os.getcwd()
target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT_FILEPATH
lastDirSepPos = target.rfind('/')
if lastDirSepPos == -1:
    lastDirSepPos = target.rfind('\\')
if lastDirSepPos != 1:
    targetPath, target = target[0:lastDirSepPos], target[lastDirSepPos+1:]
    os.chdir(targetPath)

#now scan the file
with open(target, 'r') as targetFile:
    result = scan(targetFile)

#now jump back to the initial directory
os.chdir(oldWorkingDirectory)
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w') as outFile:
        outFile.write(result)
else:
    print(result)