from Anvil_Parser.Chunk import Chunk


class Region:
    def __init__(self,filePath:str) -> None:
        with open(filePath,"rb") as f:
            self.inFile = f.read()

    def getChunkHeader(self,x:int,z:int)->int:
        return 4*((x%32)+(z%32)*32)
    
    def getChunkContents(self,x:int,z:int)->list:
        headerPos = self.getChunkHeader(x,z)

        contentBytePos = self.inFile[headerPos:headerPos+3]
        contentLength = self.inFile[headerPos+3]

        contentPos = int.from_bytes(contentBytePos,'big')

        return [contentPos,contentLength]
    
    def getChunk(self,x:int,z:int)->Chunk:
        contentPos = self.getChunkContents(x,z)

        if(contentPos[0]==0 and contentPos[1]==0):
            print("Chunk X:{} Z:{} is empty".format(x,z))
            return None

        chunkData = self.inFile[contentPos[0]*4096:contentPos[0]*4096+contentPos[1]*4096]

        return Chunk(chunkData,contentPos[1])
    
    def isVailableFile(self)->bool:
        return len(self.inFile)>=8192