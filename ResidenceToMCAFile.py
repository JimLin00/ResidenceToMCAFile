from gettext import install


import argparse
import yaml
import anvil
from pathlib import Path

def getArgs():
    args = argparse.ArgumentParser("ResidenceToMCAFile.py",description="Read the chunks containing Residence and seperate it out")

    args.add_argument("--input","-i",type=str,help="The file contains all the servers")
    args.add_argument("--output","-o",type=str,default="ResidenceServers/",required=False,help="The output file")
    args.add_argument("--blackList","-b",type=str,default="Bungeecord",required=False,help="Black list inside the input file")
    args.add_argument("--restoreWorld","-rs",type=int,default=1,required=False,help="Need to copy the Restore world")

    return args.parse_args()

def getChunkList(worldResidence):
    areas = []

    with open(str(worldResidence).replace("_rs",""),'r') as f:
        data = yaml.load(f,yaml.CLoader)

        for key in data["Residences"].keys():

            area = data["Residences"][key]["Areas"]["main"].split(":")
            
            xmin = int(area[0])>>4
            zmin = int (area[2])>>4
            xmax = int(area[3])>>4
            zmax = int(area[5])>>4
           
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

                regionFile = dirFile/stripName/"region"/"r.{}.mca".format(mcaName)

                if stripName.startswith("world_nether"):
                    regionFile = dirFile/stripName/"DIM-1/region"/"r.{}.mca".format(mcaName)
                elif stripName.startswith("world_the_end"):
                    regionFile = dirFile/stripName/"DIM1/region"/"r.{}.mca".format(mcaName)
                
                
                    
                if not regionFile.exists():
                    print(regionFile,"path not exists!")
                    continue

                splitMcaName = mcaName.split(".")
                
                originalRegion = anvil.Region.from_file(str(regionFile))
                newRegion = anvil.EmptyRegion(int(splitMcaName[0]),int(splitMcaName[1]))
                print("MCA:{} WorldName:{}/{}".format(mcaName,dirFile.name,stripName),end="\r")

                for strChunk in mcaMap[mcaName]:
                    splitStrChunk = strChunk.split(":")

                    
                    try:
                        chunk = anvil.Chunk.from_region(originalRegion,int(splitStrChunk[0]),int(splitStrChunk[1]))
                    except anvil.errors.ChunkNotFound:
                        print("MCA:{} WorldName:{}/{} Chunk at ({},{}) not found".format(mcaName,dirFile.name,stripName,int(splitStrChunk[0]),int(splitStrChunk[1])))
                        continue

                    newRegion.add_chunk(chunk)
                
                newPath = args.output+"/"+dirFile.name+"/"+stripName+"/region"
                outputPath = Path(newPath)
                outputPath.mkdir(parents=True,exist_ok=True)
                newRegion.save(newPath+"/r.{}.mca".format(mcaName))




            
main()