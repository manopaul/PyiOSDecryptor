###########################################
# Script created by Mano 'dash4rk' Paul   #
# twitter: @manopaul 				      #
# PLEASE USE IT ONLY FOR 'LEGIT' PURPOSES #
###########################################

#!/usr/bin/env python
import os, subprocess, shutil, zipfile, fnmatch, re, sys

#Get the name of the directory where the App is located and change to that directory
dirPath = raw_input("Specify the directory where the App is : ")
os.chdir(dirPath)

#Get the name of the App to reverse
appName = raw_input("Input the name of the App you wish to reverse : ")

#Make the Backup and Reversing directory
appFolderPath = os.getcwd() + "/" + os.path.splitext(appName)[0] 
if not os.path.exists(appFolderPath):
    os.mkdir(appFolderPath)
    
backupDirPath = appFolderPath + "/Backup"
if not os.path.exists(backupDirPath):
    os.mkdir(backupDirPath)
    print("Created Backup Directory")
else:
    print("Backup directory already exists. Did not create it again")

reversingDirPath = appFolderPath + "/Reversing"
if not os.path.exists(reversingDirPath):
    os.mkdir(reversingDirPath)
    print("Created reversing directory")
else:
    print("Reversing directory already exists. Did not create it again")

appPath = dirPath + "/" + appName
print(appPath)
#copy the App to Backup directory first
if os.path.isfile(appPath):
    shutil.copy2(appPath, backupDirPath)
    print("Successfully copied the App to the backup directory")
else:
    print("No file with .ipa extension to copy")

#Rename the App name with .zip extension
if(os.path.isfile(appPath) & appName.endswith('.ipa')):
    appNameWithoutExt = os.path.splitext(appName)[0]
    renamedZipName = appNameWithoutExt + ".zip"
    os.rename(appName, renamedZipName)
    print("Successfully renamed the App (.ipa) to .zip extension")
else:
    print("No file with .ipa extension to rename")

appNameWithoutExt = os.path.splitext(appName)[0]
with zipfile.ZipFile(appNameWithoutExt + ".zip", "r") as z:
    z.extractall(reversingDirPath)
    print("Extracted App Payload and Metadata into Reversing Directory")

payLoadDirPath = reversingDirPath + "/Payload"
filelist = [f for f in os.listdir(payLoadDirPath) if f.endswith('.app')]
#Get executable name with the .app
appExe = [os.path.splitext(x)[0] for x in filelist]

appExePath = payLoadDirPath + "/" + ''.join(filelist) + "/" + ''.join(appExe)

classInfo = subprocess.check_output(["class-dump-z", appExePath])
print(classInfo)

MachOHeaderInfo = subprocess.check_output(["otool", "-vh", appExePath])
print("Mach-O Header Information (otool -vh)")
print("----------------------")
print(MachOHeaderInfo)
print("----------------------")

print("Crypt Info (oTool -l | grep crypt)")
print("----------------------")
from subprocess import Popen, PIPE
proc1 = Popen(["otool", "-l", appExePath], stdout=PIPE)
proc2 = Popen(["grep", "crypt"], stdin=proc1.stdout, stdout=PIPE)
proc1.stdout.close()  # Allow proc1 to receive a SIGPIPE if proc2 exits.
cryptInfo = proc2.communicate()[0]
print(cryptInfo)
print("----------------------")

print "Now, to decrypt the App, open the app in a hex editor (e.g., OxED, HexEdit, etc.) "
print "and overwrite the cryptids from 1's to 0's"
while True:
    isCryptIdOverwritten = raw_input("Did you overwrite the cryptid? ('y' or 'n') : ")
    if isCryptIdOverwritten in ['yes', 'y']:
        break

print("Verifying that CryptId(s) are overwritten")
print("----------------------")
from subprocess import Popen, PIPE
proc1 = Popen(["otool", "-l", appExePath], stdout=PIPE)
proc2 = Popen(["grep", "crypt"], stdin=proc1.stdout, stdout=PIPE)
proc1.stdout.close()  # Allow proc1 to receive a SIGPIPE if proc2 exits.
cryptInfo = proc2.communicate()[0]
print(cryptInfo)
print("----------------------")

while True:
    isCryptIdOverwritten = raw_input("Are the crytid(s) overwritten ('y' or 'n') : ")
    if isCryptIdOverwritten in ['yes', 'y']:
        break


print "Now, it is time to build the memory dump command "
print "Connect to the remote device (iPhone, iPad), using ssh "
print "Run the app on the device and attach gdb to the process (pid) "
print "Find the base address using info sharedlibrary command "
print "Once you dump the memory, quit gdb and transfer the dumped bin file (e.g., scp) "
print "back to the local device (MacBook Pro, iMac) "

p_fileName = raw_input("Specify the name of the file to dump memory to (e.g., AppName_memDump.bin) : ")
p_baseAddr = raw_input("Specify the base address from gdb -p pid (in hex format) : ")
p_cryptOffset = raw_input("Specify the crypt offset (in decimal format) : ")
p_cryptSize = raw_input("Specify the crypt size (in decimal format) : ")

def dec2hex(dec1):
	return hex(dec1)
	
def add_2hexs(hex1, hex2):
    return hex(int(hex1, 16) + int(hex2, 16))
        
def buildDumpMemCmd(filename, baseAddr, cryptOffset, cryptSize):
	_startAddr = add_2hexs(baseAddr, dec2hex(int(cryptOffset))) 
	_endingAddr = add_2hexs(_startAddr, dec2hex(int(cryptSize)))
	return 'dump memory ' + str(filename) + ' '  +  str(_startAddr) + ' ' + str(_endingAddr)

print buildDumpMemCmd(p_fileName, p_baseAddr, p_cryptOffset, p_cryptSize)

while True:
    isMemoryDumped = raw_input("Did you dump and transfer the memory? : ")
    if isMemoryDumped in ['yes', 'y']:
        break

print "Next, we need to find the virtual memory address (vmaddr) "
print "by using otool -l Appname and looking at Load Command 1 "

while True:
    shouldIContinue = raw_input("Shall we continue? : ")
    if shouldIContinue in ['yes', 'y']:
        break
        
oToolResult = subprocess.check_output(["otool", "-l", appExePath])
print("Load Commands Information (oTool -l)")
print("----------------------")
print(oToolResult)
print("----------------------")

	
p_vmAddr = raw_input("Specify the VM address (from otool -l AppName - load command 1) in hex: ")
p_memDumpFile = raw_input("Specify the Memory Dump file) : ")

appToPatch = open(appExePath, "r+b") 
vmaddr = int(p_vmAddr, 16)
memDumpBin = open(p_memDumpFile, "rb")
hexOffset = vmaddr + int(p_cryptOffset) #p_cryptOffset comes from buildDumpMemCmd
print hexOffset

print "Patching app " + str(appToPatch) + " from " + str(hexOffset) + " using " + str(memDumpBin) 
appToPatch.seek(hexOffset)
appToPatch.write(memDumpBin.read())
appToPatch.close()
print "App has been patched."

print "Once the app is patched, try to dump the class information again "
while True:
    isAppPatched = raw_input("Is the App Patched? : ")
    if shouldIContinue in ['yes', 'y']:
        break

classInfo = subprocess.check_output(["class-dump-z", appExePath])
print(classInfo)

print "dash4rk has bitten - 'w00t'"
