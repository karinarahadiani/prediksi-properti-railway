from pydantic import BaseModel 

class Item(BaseModel):
	id_properti: int
	wilayah_properti: str
	harga_per_m2: float 
	kenaikan_harga: float