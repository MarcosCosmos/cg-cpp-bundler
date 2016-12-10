#!/usr/bin/python3
import os
import re
import argparse

###define some defaults
DEFAULT_INPUT_FILEPATH = 'main.cpp'
DEFAULT_INCLUDE_GUARD_PREFIX = '__INCLUDE_GUARD_'

###launch the argument parser for a proper cli experience
parser = argparse.ArgumentParser(description='A script for bundling small C++ projects into a single file, to upload to CodinGame by resolving includes, include guards, and accompanying .cpp files')
parser.add_argument(
    '-i',
    '--input',
    help='A path to the file to start reading from (this should typically be the file containing your main() method). Defaults to \'main.cpp\' if omitted'
)
parser.add_argument(
    '-o',
    '--output',
    help='A path to the file to save the bundled code to. The bundler will print the code to standard output if this is omitted'
)
guardArgGroup = parser.add_mutually_exclusive_group()
guardArgGroup.add_argument(
    '-g',
    '--guard-prefix',
    help='Specifies the prefix that is used to detect include-guard macros, defaults to \'__INCLUDE_GUARD_\' if omitted. This can be an empty string ("") if you want all #define,#ifdef, and #ifndef macros to be treated as include guards.'
)
guardArgGroup.add_argument(
    '-ng',
    '--no-guard',
    help='A flag indicating that the script should not try to detect include guards (in case you have macros that might conflict with it, and are using #pragma once). If this flag is set, only #include "" and #pragma once macros will be processed',
    action='store_true'
)
parser.add_argument(
    '-a1',
    '--always-once',
    help='A flag indicating that the script should automatically include any file only once, even when include guards, and the #pragma once macro are missing. Note that this will not effect the behaviour of automatically detected source files, even if that file also appears in a header.',
    action='store_true'
)
parser.add_argument(
    '-ns',
    '--no-source',
    help='A flag indicating that the script should not attempt to detect source files that accompany any header file included in the input',
    action='store_true'
)
arguments = parser.parse_args()
inputFilePath = arguments.input or DEFAULT_INPUT_FILEPATH
outputFilePath = arguments.output
if arguments.no_guard:
    includeGuardPrefix = None
else:
    includeGuardPrefix = arguments.guard_prefix or '__INCLUDE_GUARD_'

alwaysOnce = arguments.always_once
noSource = arguments.no_source
###set some values, etc to use in the processing
definesFound = {}
ifStack=[]

###processing section
def processInclude(line):
    macro = re.search('^#include ".+"', line)
    if macro is not None:
        fileContents = ""
        oldWorkingDirectory = os.getcwd()
        includeFilePath = macro.group(0).split('#include "')[1].split('"')[0]

        if alwaysOnce:
            associatedDefine = ('ALWAYS ONCE: ' + os.path.abspath(includeFilePath))
            if associatedDefine in definesFound:
                return ''
            else:
                definesFound[associatedDefine] = True

        lastDirSepPos = includeFilePath.rfind('/')
        if lastDirSepPos == -1:
            lastDirSepPos = includeFilePath.rfind('\\')
        if lastDirSepPos != -1:
            includePath, includeFileName = includeFilePath[0:lastDirSepPos], includeFilePath[lastDirSepPos+1:]
            os.chdir(includePath)
        else:
            includeFileName = includeFilePath
        with open(includeFileName, 'r') as subFile:
            subFileContents = scan(subFile)
            fileContents += '%s%s' % (subFileContents, '\n' if len(subFileContents) > 0 else '')
        #now get the corresponding .cpp, unless it was for some reason the actual include above, or the cli flag --no-source is set
        if not noSource:
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
                            associatedDefine = ('DETECT SOURCE ONCE:' + os.path.abspath(srcFileName))
                            if not associatedDefine in definesFound:
                                definesFound[associatedDefine] = True
                                subFileContents = scan(subFile)
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
        associatedDefine = 'PRAGMA ONCE:' + os.path.abspath(file.name)
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
        if includeGuardPrefix is not None:
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
            if includeGuardPrefix is not None:
                temp = processDefine(line)
                if temp is not None:
#                fileContents += temp
                    continue

                temp = processUndef(line)
                if temp is not None:
                    fileContents += temp
                    continue
            #don't include anything in this file if we see #pragma once
            temp = processPragmaOnce(line, file)
            if temp is not None:
                if temp == True:
                    return ""
                else:
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
lastDirSepPos = inputFilePath.rfind('/')
if lastDirSepPos == -1:
    lastDirSepPos = inputFilePath.rfind('\\')
if lastDirSepPos != 1:
    inputPath, inputFileName = inputFilePath[0:lastDirSepPos], inputFilePath[lastDirSepPos+1:]
    os.chdir(inputPath)
else:
    inputFileName = inputFilePath
#now scan the file
with open(inputFileName, 'r') as inputFile:
    result = scan(inputFile)

#now jump back to the initial directory
os.chdir(oldWorkingDirectory)
if outputFilePath is not None:
    with open(outputFilePath, 'w') as outFile:
        outFile.write(result)
else:
    print(result)