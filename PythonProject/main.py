from PIL import Image

background = Image.open("backgrounds/clear_sky.jpg") #фон
sun_icon = Image.open("icons/sun1.png").convert("RGBA") #иконка солнца
background = background.resize((300,300))
sun_icon = sun_icon.resize((100, 100))

background.paste(sun_icon, (50, 50), sun_icon)

background.save("output/result.png")
