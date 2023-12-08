from fastapi import APIRouter, Depends, HTTPException, status
from passlib.hash import bcrypt

from routes.auth import get_current_user
from db import conn, cursor
from models.properti import Item
from models.users import UserIn

#define routing 
properti_router = APIRouter(tags=["properti"])
kenaikan_router = APIRouter(tags=["kenaikan"])

friend_url = "http://virtualhoteltourservices.c4aaf6hnfxhhbtb5.southeastasia.azurecontainer.io:8000"

#properti route
#get all the properti list
@properti_router.get('/properti')
async def read_all_properti():
	query = "SELECT * from properti;"
	cursor.execute(query)
	data_properti = cursor.fetchall()

	if not data_properti: 
		raise HTTPException(
		status_code=404, detail=f'Properti not found')
	
	return {
		"success" : True, 
		"message" : "success", 
		"code" : 200, 
		"response" : data_properti
	}

#get properti list with item id
@properti_router.get('/properti/{item_id}')
async def read_properti(item_id: int):
	query = "SELECT * FROM properti WHERE id=%s;"
	cursor.execute(query,(item_id,))
	data_properti = cursor.fetchone()

	if not data_properti: 
		raise HTTPException(
		status_code=404, detail=f'Properti not found')
	
	return {
		"success" : True, 
		"message" : "success", 
		"code" : 200, 
		"response" : data_properti
	}

#add new properti item
@properti_router.post('/properti')
async def add_properti(item: Item):
	query = "INSERT INTO properti (nama_wilayah, harga_per_m2, kenaikan_harga) VALUES (%s, %s, %s)"
	cursor.execute(query, (item.nama_wilayah,item.harga_per_m2, item.kenaikan_harga,))
	conn.commit()
	id = cursor.lastrowid

	return {
		"success" : True, 
		"message" : "success", 
		"code" : 200, 
		"id" : id
	}

# update properti item
@properti_router.put('/properti/{item_id}')
async def update_properti(item_id: int, item: Item):
    query = "SELECT id FROM properti WHERE id = %s"
    cursor.execute(query, (item_id,))
    data_properti = cursor.fetchone()

    if not data_properti:
        raise HTTPException(
            status_code=404, detail=f'Properti not found')

    query = "UPDATE properti SET nama_wilayah=%s, harga_per_m2=%s, kenaikan_harga=%s WHERE id=%s"
    cursor.execute(query, (item.nama_wilayah,item.harga_per_m2, item.kenaikan_harga,item_id,))
    conn.commit()

    return {
        "success": True,
        "message": "success",
        "code": 200,
        "id": item_id
    }


@properti_router.delete('/properti/{item_id}')
async def delete_properti(item_id: int):
	query = "SELECT id FROM properti WHERE id =%s"
	cursor.execute(query, (item_id,))
	data_properti = cursor.fetchone()

	if not data_properti: 
		raise HTTPException(
		status_code=404, detail=f'Properti not found')
	
	query = "DELETE FROM properti WHERE id=%s"
	cursor.execute(query, (item_id,))
	conn.commit()

	return {
		"success" : True, 
		"message" : "success", 
		"code" : 200, 
		"id" : item_id
	}
	

@kenaikan_router.get('/kenaikan/{item_id}/{jangka_tahun}/{luas_tanah}')
async def read_kenaikan(item_id: int, jangka_tahun: int, luas_tanah: int, user: UserIn = Depends(get_current_user)):
    # Assuming you have a table named 'properti' with columns 'id_properti', 'harga_per_m2', 'kenaikan_harga'
    query = "SELECT harga_per_m2, kenaikan_harga FROM properti WHERE id=%s;"
    cursor.execute(query, (item_id,))
    properti_data = cursor.fetchone()

    if not properti_data:
        raise HTTPException(status_code=404, detail=f'properti not found')

    harga_per_m2, kenaikan_harga = properti_data

    if kenaikan_harga is not None:
        perhitungan = ((kenaikan_harga * luas_tanah * jangka_tahun * 1.03) + (harga_per_m2 * luas_tanah))
        message = f"harga prediksi properti dalam {jangka_tahun} tahun adalah : {perhitungan:.2f}"
        return {"success": True, "message": "success", "code": 200, "response": message}
    else:
        raise HTTPException(status_code=500, detail="Invalid data: kenaikan_harga is None")

@kenaikan_router.get('/lihat_properti')
async def gambar_properti(user: UserIn = Depends(get_current_user)): 
	data = {
        "username": "karina",  
        "password": "karinakarina"  
    }
	response = requests.post(f"{friend_url}/token", data=data)
	token = response.json()["access_token"]

	headers = {"Authorization": f"Bearer {token}"}
	response = requests.get(f"{friend_url}/location", headers=headers)

# Error handling for the HTTP request
	try:
		response.raise_for_status()
		return response.json() 
	except requests.exceptions.HTTPError as errh:
		print(f"HTTP Error: {errh}")
	except requests.exceptions.ConnectionError as errc:
		print(f"Error Connecting: {errc}")
	except requests.exceptions.Timeout as errt:
		print(f"Timeout Error: {errt}")
	except requests.exceptions.RequestException as err:
		print(f"Request Exception: {err}")