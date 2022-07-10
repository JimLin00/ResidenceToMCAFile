class Chunk:
    def __init__(self,chunkData:bytes,sectionLength:int) -> None:
        self.chunk = chunkData
        self.sectionLength = sectionLength