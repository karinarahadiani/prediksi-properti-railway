from fastapi import APIRouter, HTTPException
from models.properti import Item
import json
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.hash import bcrypt
from tortoise import fields 
from tortoise.models import Model 
import jwt

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from tortoise import fields 
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model 

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)
	
User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)

with open("data/properti.json","r") as read_file: 
	data = json.load(read_file)

properti_router = APIRouter(tags=["properti"])
kenaikan_router = APIRouter(tags=["kenaikan"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)
    if not user:
        return False 
    if not user.verify_password(password):
        return False
    return user 

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    return await User_Pydantic.from_tortoise_orm(user)

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

@kenaikan_router.get('/kenaikan/{item_id}/{jangka_tahun}/{luas_tanah}', response_model =User_Pydantic)
async def read_kenaikan(item_id: int, jangka_tahun: int, luas_tanah: int, user: User_Pydantic = Depends(get_current_user)):
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