from Anvil_Parser.Chunk import Chunk


class EmptyRegion:
    def __init__(self):
        self.data = bytearray()

        for i in range(4096*2):
            self.data.append(0)

    def getChunkHeader(self,x:int,z:int)->int:
        return 4*((x%32)+(z%32)*32)
    
    def getChunkContents(self,x:int,z:int)->list:
        headerPos = self.getChunkHeader(x,z)

        contentBytePos = self.data[headerPos:headerPos+3]
        contentLength = self.data[headerPos+3]

        contentPos = int.from_bytes(contentBytePos,'big')

        return [contentPos,contentLength]
    
    def append(self,x:int,z:int,chunkData:Chunk):
        contentPos = self.getChunkContents(x,z)

        if(contentPos[0] != 0 or contentPos[1] !=0 ):
            print("Chunk X:{} Z:{} has been written!".format(x,z))
            return

        headerPos = self.getChunkHeader(x,z)

        self.data[headerPos:headerPos+3] = int.to_bytes(int(len(self.data)/4096),3,'big')
        self.data[headerPos+3] = chunkData.sectionLength

        for i in chunkData.chunk:
            self.data.append(i)

    def save(self,fileName:str):
        with open(fileName,'wb') as f:
            f.write(self.data)