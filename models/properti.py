from pydantic import BaseModel 

class Item(BaseModel):
	id_properti: int
	nama_wilayah: str
	harga_per_m2: float 
	kenaikan_harga: float

class config:
        json_schema_extra = {
            "example": {
                "id": "1",
                "nama_wilayah": "buah batu",
                "harga_per_m2": "170000",
                "kenaikan_harga": "4000"
            }
        }
