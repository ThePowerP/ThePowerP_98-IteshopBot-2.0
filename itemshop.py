import json
import logging
from math import ceil
from sys import exit
from time import sleep

import coloredlogs
import twitter
from PIL import Image, ImageDraw

from util import ImageUtil, Utility

log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="[%(asctime)s] %(message)s", datefmt="%I:%M:%S")

class Athena:
    """Fortnite Item Shop Generator."""

    def main(self):
        print("Generador de Tienda de Objetos")
        print("Creado por: ThePowerP_98")

        initialized = Athena.LoadConfiguration(self)

        if initialized is True:
            if self.delay > 0:
                log.info(f"Retrasando ejecución por {self.delay}s...")
                sleep(self.delay)

            itemShop = Utility.GET(
                self,
                "https://fortniteapi.io/v2/shop?lang=es-419",
                {"Authorization": self.apiKey},
               # {"language": self.language},
            )
            if itemShop is not None:
                itemShop2 = json.loads(itemShop)['lastUpdate']
                x = slice(10)
                #print(itemShop2['date'][x])
                itemShop = json.loads(itemShop)["shop"]

                # Strip time from the timestamp, we only need the date
                date = Utility.ISOtoHuman(
                    self, itemShop2["date"][x], self.language
                )
                log.info(f"Encontrado Tienda de Objetos del {date}")

                shopImage = Athena.GenerateImage(self, date, itemShop)

                if shopImage is True:
                    if self.twitterEnabled is True:
                        Athena.Tweet(self, date)
    def LoadConfiguration(self):
        """
        Set the configuration values specified in configuration.json
        
        Return True if configuration sucessfully loaded.
        """

        configuration = json.loads(Utility.ReadFile(self, "settings", "json"))

        try:
            self.delay = configuration["delayStart"]
            self.apiKey = configuration["fortniteAPI"]["apiKey"]
            self.language = configuration["language"]
            self.supportACreator = configuration["supportACreator"]
            self.footer = configuration['footer']
            self.twitterEnabled = configuration["twitter"]["enabled"]
            self.twitterAPIKey = configuration["twitter"]["apiKey"]
            self.twitterAPISecret = configuration["twitter"]["apiSecret"]
            self.twitterAccessToken = configuration["twitter"]["accessToken"]
            self.twitterAccessSecret = configuration["twitter"]["accessSecret"]

            log.info("Loaded configuration")

            return True
        except Exception as e:
            log.critical(f"Failed to load configuration, {e}")
    def GenerateImage(self, date: str, itemShop: dict):
        """
        Generate the Item Shop image using the provided Item Shop.

        Return True if image sucessfully saved.
        """

        try:
        	shop = itemShop
        	if (len(shop) <= 0):
        		raise Exception(f'Shop')
        except Exception as e:
            log.critical(f"Failed to parse Item Shop shop items, {e}")

            return False
            
        rows = max(ceil(len(shop) / 6), ceil(len(shop) / 6))
        shopImage = Image.new("RGBA", (1975, ((545 * rows) + 440)))

        try:
            background = ImageUtil.Open(self, "background.png")
            background = ImageUtil.RatioResize(
                self, background, shopImage.width, shopImage.height
            )
            shopImage.paste(
                background, ImageUtil.CenterX(self, background.width, shopImage.width)
            )
        except FileNotFoundError:
            log.warn("Failed to open background.png, defaulting to dark gray")
            shopImage.paste((18, 18, 18), [0, 0, shopImage.size[0], shopImage.size[1]])

        logo = ImageUtil.Open(self, "logo.png")
        logo = ImageUtil.RatioResize(self, logo, 0, 310)
        shopImage.paste(
            logo, ImageUtil.CenterX(self, logo.width, shopImage.width, 20), logo
        )

        canvas = ImageDraw.Draw(shopImage)
        font = ImageUtil.Font(self, 48)
        textWidth, _ = font.getsize(date)
        canvas.text(
            ImageUtil.CenterX(self, textWidth, shopImage.width, 255),
            date,
            (0, 0, 0),
            font=font,
        )
        canvas.text(
        	ImageUtil.CenterX(self, textWidth, shopImage.width,(shopImage.height - 60)),
        	self.footer,
        	(0, 0, 0),
        	font=font
        )
        i = 0
        
        for item in shop:
        	card = Athena.GenerateCard(self, item)
        	
        	if card is not None:
        		shopImage.paste(
        			card,
        			(
        				(20 + (( i % 6) * (card.width + 5))),
        				(315 + (( i // 6) * (card.height + 5))),
        			),
        			card,
        		)
        		
        		i += 1
        		
        try:
            shopImage.save("itemshop.png")
            log.info("Imagen generada de la Tienda de Objetos")

            return True
        except Exception as e:
            log.critical(f"Failed to save Item Shop image, {e}")
            
    def GenerateCard(self, item: dict):
        """Return the card image for the provided Fortnite Item Shop item."""
        try:
            name = item['displayName']
            rarity = item['rarity']['id']
            mainType = item['mainType']
            category = item['granted'][0]['type']['id']
            price = item['price']['finalPrice']
            icon = item['displayAssets'][0]['url']
        except Exception as e:
            try:
            	name = item['granted'][0]["name"]
            	rarity = item['series']['name']
            	category = item['granted'][0]['type']['id']
            	price = item['price']['finalPrice']
            	if item['granted'][0]['images']['featured']is not None:
            		icon = item['granted'][0]['images']['featured']
            	else:
            		icon = item['granted'][0]['images']['icon']
            except:
            	name = item['granted'][0]["name"]
            	rarity = item['rarity']['id']
            	category = item['granted'][0]['type']['id']
            	price = item['price']['finalPrice']
            	if item['granted'][0]['images']['featured']is not None:
            		icon = item['granted'][0]['images']['featured']
            	else:
            		icon = item['granted'][0]['images']['icon']

            return
        #rarity = rarity.lower()

        if rarity == "frozen":
            blendColor = (148, 223, 255)
        elif rarity == "lava":
            blendColor = (234, 141, 35)
        elif rarity == "legendary":
            blendColor = (211, 120, 65)
        elif rarity == "dark":
            blendColor = (251, 34, 223)
        elif rarity == "starwars":
            blendColor = (231, 196, 19)
        elif rarity == "marvel":
            blendColor = (197, 51, 52)
        elif rarity == "slurp":
            blendColor = (0, 242, 213)
        elif rarity == "dc":
            blendColor = (84, 117, 199)
        elif rarity == "icon":
            blendColor = (54, 183, 183)
        elif rarity == "shadow":
            blendColor = (113, 113, 113)
        elif rarity == "epic":
            blendColor = (177, 91, 226)
        elif rarity == "rare":
            blendColor = (73, 172, 242)
        elif rarity == "uncommon":
            blendColor = (96, 170, 58)
        elif rarity == "common":
            blendColor = (190, 190, 190)
        elif rarity == "gaminglegends":
            blendColor = (42, 0, 168)
        else:
            blendColor = (255, 255, 255)

        card = Image.new("RGBA", (319, 545))
        try:
            layer = ImageUtil.Open(self, f"shopitem_background_{rarity}.png")
        except FileNotFoundError:
            log.warn(f"Failed to open shopitem_background_{rarity}.png, defaulted to Common")
            layer = ImageUtil.Open(self, "shopitem_background_common.png")

        card.paste(layer)

        icon = ImageUtil.Download(self, icon).convert("RGBA")
        if mainType == "bundle":
        	icon = ImageUtil.RatioResize(self, icon, 135, 335)
        elif (category == "outfit") and item['mainType'] != 'bundle' or (category == "emote"):
            icon = ImageUtil.RatioResize(self, icon, 285, 365)
        elif category == "wrap":
            icon = ImageUtil.RatioResize(self, icon, 230, 310)
        else:
            icon = ImageUtil.RatioResize(self, icon, 310, 390)
        if (category == "outfit") and item['mainType'] != 'bundle' or (category == "emote"):
            card.paste(icon, ImageUtil.CenterX(self, icon.width, card.width), icon)
        else:
            card.paste(icon, ImageUtil.CenterX(self, icon.width, card.width, 15), icon)
            
        if item['mainType'] != 'bundle':
            if len(item["granted"]) > 1:
            # Track grid position
            	i = 0

            # Start at position 1 in items array
            	for extra in item["granted"][1:]:
                	try:
                	   extraRarity = extra["rarity"]["id"]
                	   extraIcon = extra["images"]["icon"]
                	except Exception as e:
                		log.error(f"Failed to parse item {name}, {e}")
                		return
                	extraIcon = ImageUtil.Download(self, extraIcon)
                	extraIcon = ImageUtil.RatioResize(self, extraIcon, 95, 95)
                	card.paste (
                		extraIcon,
                		(
                			(card.width - (card.width + 9)),
                			(9 + (i // 1) * (extraIcon.height)),
                		),
                		extraIcon
                	)

                	i += 1

        try:
            layer = ImageUtil.Open(self, f"shopitem_card_{rarity}.png")
        except FileNotFoundError:
            log.warn(f"Failed to open shopitem_card_{rarity}.png, defaulted to Common")
            layer = ImageUtil.Open(self, "cshopitem_card_common.png")

        card.paste(layer, layer)

        # Ahora se traducirá las "values" al Español. Tanto en "rarity" como en "category"
        if rarity == "frozen":
            rarity = "de Hielo"
        elif rarity == "lava":
            rarity = "de Lava"
        elif rarity == "legendary":
            rarity = "Legendario"
        elif rarity == "slurp":
            rarity = "Sorbete"
        elif rarity == "dark":
            rarity = "Oscuro"
        elif rarity == "starwars":
            rarity = "de StarWars"
        elif rarity == "marvel":
            rarity = "de Marvel"
        elif rarity == "dc":
            rarity = "de DC"
        elif rarity == "icon":
            rarity = "de Serie de Iconos"
        elif rarity == "shadow":
            rarity = "Sombra"
        elif rarity == "epic":
            rarity = "Epico"
        elif rarity == "rare":
            rarity = "Raro"
        elif rarity == "uncommon":
            rarity = "Poco Comun"
        elif rarity == "common":
            rarity = "Comun"
        else:
            rarity = "Error"
			
        if category == "outfit":
            category = "Traje"
        elif category == "emote":
            category = "Baile"
        elif category == "wrap":
            category = "Envoltorio"
        elif category == "backpack":
            category = "Mochila"
        elif category == "glider":
            category = "Ala Delta"
        elif category == "banner":
            category = "Estandarte"
        elif category == "pickaxe":
            category = "Pico"
        elif category == "music":
            category = "Musica"
        else:
            category = "Error"
			
        card.paste(layer, layer)

        canvas = ImageDraw.Draw(card)

        font = ImageUtil.Font(self, 33)
        textWidth, _ = font.getsize(f"{category} {rarity}")
        canvas.text(
            ImageUtil.CenterX(self, textWidth, card.width, 385),
            f"",
            blendColor,
            font=font,
        )

        vbucks = ImageUtil.Open(self, "vbucks_card.png")
        vbucks = ImageUtil.RatioResize(self, vbucks, 49, 49)

        price = str(f"{price:,}")
        textWidth, _ = font.getsize(price)
        canvas.text(
            ImageUtil.CenterX(self, ((textWidth + 15) - vbucks.width), card.width, 450),
            price,
            blendColor,
            font=font,
        )

        card.paste(
            vbucks,
            ImageUtil.CenterX(self, (vbucks.width + (textWidth - 290)), card.width, 436),
            vbucks,
        )

        font = ImageUtil.Font(self, 56)
        textWidth, _ = font.getsize(name)
        change = 0
        if textWidth >= 270:
            # Ensure that the item name does not overflow
            font, textWidth, change = ImageUtil.FitTextX(self, name, 56, 260)
        canvas.text(
            ImageUtil.CenterX(self, textWidth, card.width, (380 + (change / 2))),
            name,
            (255, 255, 255),
            font=font,
        )

        return card
    
    def Tweet(self, date: str):
        """
        Tweet the current `itemshop.png` local file to Twitter using the credentials provided
        in `configuration.json`.
        """

        try:
            twitterAPI = twitter.Api(
                consumer_key=self.twitterAPIKey,
                consumer_secret=self.twitterAPISecret,
                access_token_key=self.twitterAccessToken,
                access_token_secret=self.twitterAccessSecret,
            )

            twitterAPI.VerifyCredentials()
        except Exception as e:
            log.critical(f"Error al autentificar con Twitter, {e}")

            return

        body = f"¡Nueva Tienda de Objetos del {date}!"

        if self.supportACreator is not None:
            body = f"{body}\n\nPuedes apoyarme con el código: {self.supportACreator} <3 #Fortnite #ad"

        try:
            with open('itemshop.png', 'rb') as shopImage:
                twitterAPI.PostUpdate(body, media=shopImage)
            log.info('tweet enviado correctamente')
        except:
            foo = Image.open('itemshop.png')
            x, y = foo.size
            x2, y2 = math.floor(x/4), math.floor(y/4)
            foo = foo.resize((x2, y2), Image.ANTIALIAS)
            foo.save('itemshop.png', quality=65)
            with open('itemshop.png', 'rb') as shopImage:
                twitterAPI.PostUpdate(body, media=shopImage)

if __name__ == "__main__":
    try:
        Athena.main(Athena)
    except KeyboardInterrupt:
        log.info("Saliendo...")
        exit()