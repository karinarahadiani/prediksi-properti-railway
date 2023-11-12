from fastapi import APIRouter, HTTPException
from models.properti import Item
import json


with open("/data/properti.json","r") as read_file: 
	data = json.load(read_file)

properti_router = APIRouter(tags=["properti"])
kenaikan_router = APIRouter(tags=["kenaikan"])

@properti_router.get('/properti')
async def read_all_properti():
	return data['properti']

@properti_router.get('/properti/{item_id}')
async def read_properti(item_id: int):
	for properti_item in data['properti']:
		print(properti_item)
		if properti_item['id_properti'] == item_id:
			return properti_item
	raise HTTPException(
		status_code=404, detail=f'properti not found'
	)

@properti_router.post('/properti')
async def add_properti(item: Item):
	item_dict = item.dict()
	item_found = False
	for properti_item in data['properti']:
		if properti_item['id_properti'] == item_dict['id_properti'] and properti_item['wilayah_properti'] == item_dict['wilayah_properti']:
			item_found = True
			return "Properti ID "+str(item_dict['id_properti'])+" exists."
	
	if not item_found:
		data['properti'].routeend(item_dict)
		with open(json_filename,"w") as write_file:
			json.dump(data, write_file)

		return item_dict
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)

@properti_router.put('/properti')
async def update_properti(item: Item):
	item_dict = item.dict()
	item_found = False
	for properti_idx, properti_item in enumerate(data['properti']):
		if properti_item['id_properti'] == item_dict['id_properti']:
			item_found = True
			data['properti'][properti_idx]=item_dict
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not item_found:
		return "Properti ID not found."
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)

@properti_router.delete('/properti/{item_id}')
async def delete_properti(item_id: int):

	item_found = False
	for properti_idx, properti_item in enumerate(data['properti']):
		if properti_item['id_properti'] == item_id:
			item_found = True
			data['properti'].pop(properti_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not item_found:
		return "Properti ID not found."
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)

@kenaikan_router.get('/kenaikan/{item_id}/{jangka_tahun}/{luas_tanah}')
async def read_kenaikan(item_id: int, jangka_tahun: int, luas_tanah: int):
    for properti_item in data['properti']:
        if properti_item['id_properti'] == item_id:
            kenaikan_harga = properti_item.get('kenaikan_harga')
            perhitungan = ((properti_item.get('kenaikan_harga')* luas_tanah * jangka_tahun * 1.03) + (properti_item.get('harga_per_m2')*luas_tanah))
            if kenaikan_harga is not None:
                message = f"harga prediksi properti dalam {jangka_tahun} tahun adalah : {perhitungan:.2f}"
                return message
            else:
                raise HTTPException(status_code=500, detail="Invalid data: kenaikan_harga is None")
    raise HTTPException(status_code=404, detail=f'properti not found')