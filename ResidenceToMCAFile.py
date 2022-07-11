import argparse
import imp
import yaml

from pathlib import Path
from Anvil_Parser import *

def getArgs():
    args = argparse.ArgumentParser("ResidenceToMCAFile.py",description="Read the chunks containing Residence and seperate it out")

    args.add_argument("--input","-i",type=str,help="The file contains all the servers")
    args.add_argument("--output","-o",type=str,default="ResidenceServers/",required=False,help="The output file")
    args.add_argument("--blackList","-b",type=str,default="Bungeecord",required=False,help="Black list inside the input file")
    args.add_argument("--restoreWorld","-rs",type=int,default=1,required=False,help="Need to copy the Restore world. Set to 0 to skip _rs world")

    return args.parse_args()

def getChunkList(worldResidence):
    areas = []
    with open(str(worldResidence).replace("_rs",""),'r') as f:
        data = yaml.load(f,yaml.CLoader)

        for key in data["Residences"].keys():

            area = data["Residences"][key]["Areas"]["main"].split(":")
            
            xmin = min(int(area[0]),int(area[3]))>>4
            zmin = min(int(area[2]),int(area[5]))>>4
            xmax = max(int(area[0]),int(area[3]))>>4
            zmax = max(int(area[2]),int(area[5]))>>4
           
            for i in range(xmax-xmin+1):
                for j in range(zmax-zmin+1):
                    chunkKey = "{}:{}".format(xmin+i,zmin+j)
                    if chunkKey not in area:
                        areas.append(chunkKey)
            

    return areas

def sortChunks(chunks):

    mcaMap = {}
    
    
    for chunk in chunks:
        x = int(chunk.split(":")[0])
        z = int(chunk.split(":")[1])

        mcaKey = "{}.{}".format(x>>5,z>>5)
        if mcaKey in mcaMap.keys():
            mcaMap[mcaKey].append(chunk)
        else:
            mcaMap[mcaKey] = [chunk]
    
    return mcaMap

def saveSeperateChunks(targetServer:Path,targetWorldName:str,targetMcaDir:str,mcaName:str,mcaDic:dict,outPutBaseDir:str):
    regionFile = targetServer/targetWorldName/targetMcaDir/"r.{}.mca".format(mcaName)

    if targetWorldName.startswith("world_nether"):
        regionFile = targetServer/targetWorldName/"DIM-1"/targetMcaDir/"r.{}.mca".format(mcaName)
    elif targetWorldName.startswith("world_the_end"):
        regionFile = targetServer/targetWorldName/"DIM1"/targetMcaDir/"r.{}.mca".format(mcaName)
                
                
                    
    if not regionFile.exists():
        print(regionFile,"path not exists!")
        return
    
    originalRegion = Region(str(regionFile))
    
    if( not originalRegion.isVailableFile()):
        print("\n"+targetMcaDir+"/r.{}.mca".format(mcaName)," Is not a vailable region file.")
        return

    newRegion = EmptyRegion()
    print("MCA:{} WorldName:{}/{}   ".format(mcaName,targetServer.name,targetWorldName),end="\r")

    isEmpty = True

    for strChunk in mcaDic[mcaName]:
        splitStrChunk = strChunk.split(":")

        chunk = originalRegion.getChunk(int(splitStrChunk[0]),int(splitStrChunk[1]))
        
        if(chunk == None):
            continue
        
        isEmpty = False
        newRegion.append(int(splitStrChunk[0]),int(splitStrChunk[1]),chunk)
    
    if(isEmpty):
        return

    newPath = outPutBaseDir+"/"+targetServer.name+"/"+targetWorldName+"/"+targetMcaDir
    outputPath = Path(newPath)
    outputPath.mkdir(parents=True,exist_ok=True)
    newRegion.save(newPath+"/r.{}.mca".format(mcaName))

def main():
    args = getArgs()
    #inputPath = Path("Servers/")
    inputPath = Path(args.input)
    blackList = args.blackList.split(" ")

    worldName = ["world","world_nether","world_the_end"]

    if args.restoreWorld == 1:
        for i in ["world_rs","world_nether_rs","world_the_end_rs"]:
            worldName.append(i)
        
    
    for dirFile in inputPath.iterdir():
        if dirFile.name in blackList:
            continue
        
        residenceFile = dirFile/"plugins/Residence/Save/Worlds"

        if not residenceFile.exists:
            print(residenceFile," not exists Residence file!")
            continue

        for worldResidence in residenceFile.iterdir():
            stripName = worldResidence.name.replace(".yml","").replace("res_","")
            
            if stripName not in worldName:
                continue
            
            chunks = getChunkList(worldResidence)
            mcaMap = sortChunks(chunks)
            

            for mcaName in mcaMap.keys():
                saveSeperateChunks(dirFile,stripName,"region",mcaName,mcaMap,args.output)
                saveSeperateChunks(dirFile,stripName,"entities",mcaName,mcaMap,args.output)
                saveSeperateChunks(dirFile,stripName,"poi",mcaName,mcaMap,args.output)
                     
main()