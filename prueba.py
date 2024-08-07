import requests


randomVerso = "https://fortnite-api.com/v2/shop/br/combined"
response = requests.get(randomVerso)
data = response.json()
#print(data)
#print(data['reference'])
new_skins= data['data']['featured']['entries']

for skin in new_skins:
            try:
                skin_name = skin['items'][0]['name']
                image_url = skin['items'][0]['images']['icon']
                print(f"Skin: {skin_name}, Image URL: {image_url}")
            except KeyError as e:
                print(f"Error al procesar skin: {e}")
