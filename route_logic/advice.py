def get_clothing_advice(uv_index):
	if uv_index is None:
		return "UV data unavailable."
	if uv_index <= 2:
		return "Low UV: Light clothing, no hat needed."
	elif uv_index <= 5:
		return "Moderate UV: Cover shoulders, wear a hat."
	elif uv_index <= 7:
		return "High UV: Hat, sunglasses, long sleeves."
	elif uv_index <= 10:
		return "Very High UV: Avoid midday sun, full coverage."
	else:
		return "Extreme UV: Stay indoors if possible."
