#!/usr/bin/env python3
"""
Enhanced Mock Data Generator

Generates 1000 luxury fashion products with:
- Accurate Unsplash images matching color and description
- Rich metadata for faceting
- Unique images per color variant
"""

import json
import os
import hashlib
from datetime import datetime, timezone
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


class EnhancedMockGenerator:
    def __init__(self):
        self.products = []
        
        # Curated Unsplash images - each URL is specific to color/style
        # Format: category -> subcategory -> color -> image_url
        self.image_library = {
            'shirts': {
                'dress_shirt': {
                    'white': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800',
                    'blue': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800',
                    'black': 'https://images.unsplash.com/photo-1620012253295-c15cc3e65df4?w=800',
                    'pink': 'https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?w=800',
                    'striped': 'https://images.unsplash.com/photo-1589310243389-96a5483213a8?w=800',
                },
                'casual_shirt': {
                    'white': 'https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=800',
                    'blue': 'https://images.unsplash.com/photo-1603252109303-2751441dd157?w=800',
                    'navy': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800',
                    'gray': 'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=800',
                    'black': 'https://images.unsplash.com/photo-1618354691438-25bc04584c23?w=800',
                },
                'polo_shirt': {
                    'white': 'https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=800',
                    'black': 'https://images.unsplash.com/photo-1581803118522-7b72a50f7e9f?w=800',
                    'navy': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800',
                    'red': 'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800',
                    'green': 'https://images.unsplash.com/photo-1627225924765-552d49cf47ad?w=800',
                },
                't_shirt': {
                    'white': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800',
                    'black': 'https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=800',
                    'gray': 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800',
                    'navy': 'https://images.unsplash.com/photo-1562157873-818bc0726f68?w=800',
                    'red': 'https://images.unsplash.com/photo-1529374255404-311a2a4f1fd0?w=800',
                },
            },
            'pants': {
                'jeans': {
                    'blue': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=800',
                    'black': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800',
                    'light_blue': 'https://images.unsplash.com/photo-1604176354204-9268737828e4?w=800',
                    'gray': 'https://images.unsplash.com/photo-1582552938357-32b906df40cb?w=800',
                    'white': 'https://images.unsplash.com/photo-1584370848010-d7fe6bc767ec?w=800',
                },
                'chinos': {
                    'khaki': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=800',
                    'navy': 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800',
                    'olive': 'https://images.unsplash.com/photo-1517445312882-bc9910d016b7?w=800',
                    'beige': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=800',
                    'black': 'https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=800',
                },
                'dress_pants': {
                    'black': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800',
                    'navy': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800',
                    'gray': 'https://images.unsplash.com/photo-1617137968427-85924c800a22?w=800',
                    'charcoal': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800',
                    'brown': 'https://images.unsplash.com/photo-1560243563-062bfc001d68?w=800',
                },
            },
            'watches': {
                'analog': {
                    'gold': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800',
                    'silver': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800',
                    'black': 'https://images.unsplash.com/photo-1533139502658-0198f920d8e8?w=800',
                    'rose_gold': 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=800',
                    'brown_leather': 'https://images.unsplash.com/photo-1509048191080-d2984bad6ae5?w=800',
                },
                'digital': {
                    'black': 'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800',
                    'white': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800',
                    'blue': 'https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=800',
                    'green': 'https://images.unsplash.com/photo-1544117519-31a4b719223d?w=800',
                    'orange': 'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=800',
                },
                'smart': {
                    'black': 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800',
                    'silver': 'https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=800',
                    'gold': 'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=800',
                    'white': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800',
                    'rose_gold': 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=800',
                },
                'luxury': {
                    'gold': 'https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?w=800',
                    'silver': 'https://images.unsplash.com/photo-1548169874-53e85f753f1e?w=800',
                    'platinum': 'https://images.unsplash.com/photo-1526045431048-f857369baa09?w=800',
                    'rose_gold': 'https://images.unsplash.com/photo-1612817159949-195b6eb9e31a?w=800',
                    'two_tone': 'https://images.unsplash.com/photo-1614164185128-e4ec99c436d7?w=800',
                },
            },
            'shoes': {
                'sneakers': {
                    'white': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800',
                    'black': 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800',
                    'red': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800',
                    'blue': 'https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=800',
                    'gray': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800',
                    'multicolor': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800',
                },
                'loafers': {
                    'brown': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800',
                    'black': 'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800',
                    'tan': 'https://images.unsplash.com/photo-1582897085656-c636d006a246?w=800',
                    'burgundy': 'https://images.unsplash.com/photo-1626379953822-baec19c3accd?w=800',
                    'navy': 'https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=800',
                },
                'boots': {
                    'brown': 'https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=800',
                    'black': 'https://images.unsplash.com/photo-1605812860427-4024433a70fd?w=800',
                    'tan': 'https://images.unsplash.com/photo-1638247025967-b4e38f787b76?w=800',
                    'cognac': 'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=800',
                    'gray': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800',
                },
                'heels': {
                    'black': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800',
                    'red': 'https://images.unsplash.com/photo-1515347619252-60a4bf4fff4f?w=800',
                    'nude': 'https://images.unsplash.com/photo-1518049362265-d5b2a6467637?w=800',
                    'gold': 'https://images.unsplash.com/photo-1596703263926-eb0762ee17e4?w=800',
                    'silver': 'https://images.unsplash.com/photo-1519415943484-9fa1873496d4?w=800',
                },
                'sandals': {
                    'brown': 'https://images.unsplash.com/photo-1603487742131-4160ec999306?w=800',
                    'black': 'https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=800',
                    'white': 'https://images.unsplash.com/photo-1582896911227-c966f6e7fb93?w=800',
                    'tan': 'https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?w=800',
                    'gold': 'https://images.unsplash.com/photo-1603487742131-4160ec999306?w=800',
                },
            },
            'bags': {
                'handbag': {
                    'black': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800',
                    'brown': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800',
                    'tan': 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=800',
                    'red': 'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=800',
                    'white': 'https://images.unsplash.com/photo-1591561954557-26941169b49e?w=800',
                    'navy': 'https://images.unsplash.com/photo-1594223274512-ad4803739b7c?w=800',
                },
                'tote': {
                    'black': 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=800',
                    'brown': 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=800',
                    'canvas': 'https://images.unsplash.com/photo-1597633125097-5a9ae3a22e73?w=800',
                    'navy': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800',
                    'beige': 'https://images.unsplash.com/photo-1614179689702-355944cd0918?w=800',
                },
                'backpack': {
                    'black': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800',
                    'brown': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800',
                    'navy': 'https://images.unsplash.com/photo-1581605405669-fcdf81165afa?w=800',
                    'gray': 'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=800',
                    'green': 'https://images.unsplash.com/photo-1580087256394-dc596e1c8f4f?w=800',
                },
                'clutch': {
                    'black': 'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=800',
                    'gold': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800',
                    'silver': 'https://images.unsplash.com/photo-1591561954557-26941169b49e?w=800',
                    'red': 'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=800',
                    'nude': 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=800',
                },
                'crossbody': {
                    'black': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800',
                    'brown': 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=800',
                    'tan': 'https://images.unsplash.com/photo-1591561954557-26941169b49e?w=800',
                    'red': 'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=800',
                    'navy': 'https://images.unsplash.com/photo-1594223274512-ad4803739b7c?w=800',
                },
            },
            'accessories': {
                'belt': {
                    'black': 'https://images.unsplash.com/photo-1624222247344-550fb60583bb?w=800',
                    'brown': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800',
                    'tan': 'https://images.unsplash.com/photo-1585856331426-d7a22f0ae8c4?w=800',
                    'navy': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800',
                    'reversible': 'https://images.unsplash.com/photo-1624222247344-550fb60583bb?w=800',
                },
                'scarf': {
                    'silk_multi': 'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=800',
                    'cashmere_gray': 'https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=800',
                    'wool_navy': 'https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=800',
                    'silk_orange': 'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=800',
                    'cashmere_camel': 'https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=800',
                },
                'sunglasses': {
                    'black': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800',
                    'tortoise': 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800',
                    'gold': 'https://images.unsplash.com/photo-1577803645773-f96470509666?w=800',
                    'silver': 'https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=800',
                    'brown': 'https://images.unsplash.com/photo-1508296695146-257a814070b4?w=800',
                },
                'wallet': {
                    'black': 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=800',
                    'brown': 'https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=800',
                    'tan': 'https://images.unsplash.com/photo-1612902456551-333ac5afa26e?w=800',
                    'navy': 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=800',
                    'burgundy': 'https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=800',
                },
                'tie': {
                    'navy': 'https://images.unsplash.com/photo-1589756823695-278bc923f962?w=800',
                    'red': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800',
                    'black': 'https://images.unsplash.com/photo-1589756823695-278bc923f962?w=800',
                    'burgundy': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800',
                    'striped': 'https://images.unsplash.com/photo-1589756823695-278bc923f962?w=800',
                },
            },
            'jewelry': {
                'bracelet': {
                    'gold': 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800',
                    'silver': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800',
                    'rose_gold': 'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=800',
                    'leather_black': 'https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=800',
                    'enamel_orange': 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800',
                },
                'necklace': {
                    'gold': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800',
                    'silver': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800',
                    'pearl': 'https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=800',
                    'rose_gold': 'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=800',
                    'diamond': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800',
                },
                'earrings': {
                    'gold': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800',
                    'silver': 'https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800',
                    'pearl': 'https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=800',
                    'diamond': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800',
                    'hoop_gold': 'https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800',
                },
                'ring': {
                    'gold': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800',
                    'silver': 'https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800',
                    'rose_gold': 'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=800',
                    'diamond': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800',
                    'platinum': 'https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800',
                },
            },
        }

        # Product templates with detailed metadata
        self.product_templates = {
            'shirts': {
                'dress_shirt': {
                    'name': '{color} Dress Shirt - {sleeve}',
                    'description': 'Elegant {color} dress shirt in premium cotton with {sleeve} sleeves',
                    'long_description': 'This sophisticated {color} dress shirt is crafted from the finest Egyptian cotton. Features a classic spread collar, mother-of-pearl buttons, and {sleeve} sleeves. Perfect for formal occasions and business settings.',
                    'materials': ['100% Egyptian Cotton'],
                    'styles': ['Formal', 'Business'],
                    'sleeves': ['Full Sleeve', 'Half Sleeve'],
                    'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                    'price_range': '$150-$300',
                    'base_price': 195,
                },
                'casual_shirt': {
                    'name': '{color} Casual Shirt - {sleeve}',
                    'description': 'Relaxed {color} casual shirt in soft cotton blend',
                    'long_description': 'A comfortable {color} casual shirt made from a premium cotton blend. Features a button-down collar, chest pocket, and {sleeve} sleeves. Ideal for weekend outings and casual gatherings.',
                    'materials': ['Cotton Blend'],
                    'styles': ['Casual', 'Weekend'],
                    'sleeves': ['Full Sleeve', 'Half Sleeve', 'Rolled Sleeve'],
                    'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                    'price_range': '$100-$200',
                    'base_price': 145,
                },
                'polo_shirt': {
                    'name': '{color} Polo Shirt',
                    'description': 'Classic {color} polo shirt in premium piqué cotton',
                    'long_description': 'A timeless {color} polo shirt crafted from luxurious piqué cotton. Features a ribbed collar, two-button placket, and signature embroidered logo. Perfect for smart casual occasions.',
                    'materials': ['Piqué Cotton'],
                    'styles': ['Smart Casual', 'Sport'],
                    'sleeves': ['Short Sleeve'],
                    'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                    'price_range': '$120-$180',
                    'base_price': 150,
                },
                't_shirt': {
                    'name': '{color} Premium T-Shirt',
                    'description': 'Essential {color} t-shirt in soft organic cotton',
                    'long_description': 'A wardrobe essential {color} t-shirt made from 100% organic cotton. Features a classic crew neck, relaxed fit, and superior softness. Perfect for everyday wear.',
                    'materials': ['Organic Cotton'],
                    'styles': ['Casual', 'Everyday'],
                    'sleeves': ['Short Sleeve'],
                    'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                    'price_range': '$80-$120',
                    'base_price': 95,
                },
            },
            'pants': {
                'jeans': {
                    'name': '{color} Denim Jeans - {fit}',
                    'description': 'Premium {color} denim jeans with {fit} fit',
                    'long_description': 'Expertly crafted {color} denim jeans featuring a {fit} fit. Made from premium Japanese selvedge denim with classic five-pocket styling. Designed for comfort and durability.',
                    'materials': ['Japanese Selvedge Denim'],
                    'styles': ['Casual', 'Everyday'],
                    'fits': ['Slim Fit', 'Regular Fit', 'Relaxed Fit'],
                    'sizes': ['28', '30', '32', '34', '36', '38'],
                    'price_range': '$200-$350',
                    'base_price': 275,
                },
                'chinos': {
                    'name': '{color} Chino Pants - {fit}',
                    'description': 'Classic {color} chinos with {fit} fit',
                    'long_description': 'Versatile {color} chino pants with a {fit} fit. Crafted from premium stretch cotton twill for all-day comfort. Features a flat front and tapered leg.',
                    'materials': ['Stretch Cotton Twill'],
                    'styles': ['Smart Casual', 'Business Casual'],
                    'fits': ['Slim Fit', 'Regular Fit', 'Tapered'],
                    'sizes': ['28', '30', '32', '34', '36', '38'],
                    'price_range': '$150-$250',
                    'base_price': 195,
                },
                'dress_pants': {
                    'name': '{color} Dress Trousers - {fit}',
                    'description': 'Elegant {color} dress trousers with {fit} fit',
                    'long_description': 'Sophisticated {color} dress trousers featuring a {fit} fit. Made from fine wool blend with a subtle sheen. Perfect for formal occasions and business meetings.',
                    'materials': ['Wool Blend'],
                    'styles': ['Formal', 'Business'],
                    'fits': ['Slim Fit', 'Classic Fit'],
                    'sizes': ['28', '30', '32', '34', '36', '38'],
                    'price_range': '$250-$400',
                    'base_price': 325,
                },
            },
            'watches': {
                'analog': {
                    'name': '{color} Analog Watch - Classic',
                    'description': 'Elegant {color} analog watch with Swiss movement',
                    'long_description': 'A timeless {color} analog watch featuring Swiss automatic movement. Sapphire crystal face, {color} case, and premium leather strap. Water resistant to 50m.',
                    'materials': ['Stainless Steel', 'Sapphire Crystal', 'Leather'],
                    'styles': ['Classic', 'Dress'],
                    'sizes': ['38mm', '40mm', '42mm'],
                    'price_range': '$2,000-$5,000',
                    'base_price': 3500,
                },
                'digital': {
                    'name': '{color} Digital Sport Watch',
                    'description': 'Modern {color} digital watch with advanced features',
                    'long_description': 'A cutting-edge {color} digital watch with multiple functions. Features chronograph, alarm, backlight, and water resistance to 100m. Perfect for active lifestyles.',
                    'materials': ['Titanium', 'Mineral Crystal', 'Silicone'],
                    'styles': ['Sport', 'Active'],
                    'sizes': ['42mm', '44mm', '46mm'],
                    'price_range': '$500-$1,200',
                    'base_price': 850,
                },
                'smart': {
                    'name': '{color} Smart Watch Pro',
                    'description': 'Premium {color} smartwatch with health tracking',
                    'long_description': 'An advanced {color} smartwatch with comprehensive health monitoring. Features heart rate, GPS, sleep tracking, and smartphone notifications. Premium build with all-day battery.',
                    'materials': ['Aluminum', 'Ceramic', 'Fluoroelastomer'],
                    'styles': ['Tech', 'Active', 'Everyday'],
                    'sizes': ['40mm', '44mm'],
                    'price_range': '$800-$1,500',
                    'base_price': 1150,
                },
                'luxury': {
                    'name': '{color} Luxury Chronograph',
                    'description': 'Exquisite {color} luxury chronograph watch',
                    'long_description': 'A masterpiece of horological craftsmanship. This {color} luxury chronograph features an in-house automatic movement, 18k gold accents, and hand-finished details. Limited edition.',
                    'materials': ['18K Gold', 'Sapphire Crystal', 'Alligator Leather'],
                    'styles': ['Luxury', 'Collector'],
                    'sizes': ['40mm', '42mm'],
                    'price_range': '$8,000-$25,000',
                    'base_price': 15000,
                },
            },
            'shoes': {
                'sneakers': {
                    'name': '{color} Leather Sneakers',
                    'description': 'Premium {color} leather sneakers with cushioned sole',
                    'long_description': 'Luxurious {color} sneakers crafted from premium calfskin leather. Features a cushioned insole, rubber outsole, and signature branding. Perfect for elevated casual style.',
                    'materials': ['Calfskin Leather', 'Rubber Sole'],
                    'styles': ['Casual', 'Sport Luxe'],
                    'sizes': ['EU 39', 'EU 40', 'EU 41', 'EU 42', 'EU 43', 'EU 44', 'EU 45'],
                    'price_range': '$500-$900',
                    'base_price': 695,
                },
                'loafers': {
                    'name': '{color} Leather Loafers',
                    'description': 'Classic {color} leather loafers with penny strap',
                    'long_description': 'Timeless {color} penny loafers handcrafted from supple leather. Features a leather sole, hand-stitched details, and classic silhouette. Perfect for business and smart casual.',
                    'materials': ['Full Grain Leather', 'Leather Sole'],
                    'styles': ['Business', 'Smart Casual'],
                    'sizes': ['EU 39', 'EU 40', 'EU 41', 'EU 42', 'EU 43', 'EU 44', 'EU 45'],
                    'price_range': '$600-$1,000',
                    'base_price': 795,
                },
                'boots': {
                    'name': '{color} Leather Boots',
                    'description': 'Refined {color} leather boots with Goodyear welt',
                    'long_description': 'Distinguished {color} boots featuring Goodyear welt construction. Made from premium leather with a durable rubber sole. Perfect for autumn and winter seasons.',
                    'materials': ['Premium Leather', 'Rubber Sole'],
                    'styles': ['Casual', 'Rugged'],
                    'sizes': ['EU 39', 'EU 40', 'EU 41', 'EU 42', 'EU 43', 'EU 44', 'EU 45'],
                    'price_range': '$700-$1,200',
                    'base_price': 950,
                },
                'heels': {
                    'name': '{color} Stiletto Heels',
                    'description': 'Elegant {color} stiletto heels with pointed toe',
                    'long_description': 'Sophisticated {color} stiletto heels crafted from premium materials. Features a pointed toe, 85mm heel, and leather sole. Perfect for evening events and special occasions.',
                    'materials': ['Patent Leather', 'Leather Sole'],
                    'styles': ['Evening', 'Formal'],
                    'sizes': ['EU 35', 'EU 36', 'EU 37', 'EU 38', 'EU 39', 'EU 40', 'EU 41'],
                    'price_range': '$600-$1,100',
                    'base_price': 850,
                },
                'sandals': {
                    'name': '{color} Leather Sandals',
                    'description': 'Comfortable {color} leather sandals with cushioned footbed',
                    'long_description': 'Elegant {color} sandals crafted from soft leather. Features a cushioned footbed, adjustable straps, and durable sole. Perfect for summer and resort wear.',
                    'materials': ['Soft Leather', 'Rubber Sole'],
                    'styles': ['Casual', 'Resort'],
                    'sizes': ['EU 35', 'EU 36', 'EU 37', 'EU 38', 'EU 39', 'EU 40', 'EU 41', 'EU 42', 'EU 43'],
                    'price_range': '$400-$700',
                    'base_price': 550,
                },
            },
            'bags': {
                'handbag': {
                    'name': '{color} Leather Handbag',
                    'description': 'Iconic {color} leather handbag with signature hardware',
                    'long_description': 'A timeless {color} handbag crafted from the finest leather. Features signature gold-tone hardware, interior pockets, and detachable shoulder strap. Handmade by skilled artisans.',
                    'materials': ['Premium Leather', 'Gold Hardware'],
                    'styles': ['Classic', 'Everyday'],
                    'sizes': ['Small', 'Medium', 'Large'],
                    'price_range': '$2,500-$8,000',
                    'base_price': 4500,
                },
                'tote': {
                    'name': '{color} Leather Tote Bag',
                    'description': 'Spacious {color} leather tote for everyday use',
                    'long_description': 'A versatile {color} tote bag made from durable leather. Features a spacious interior, interior zip pocket, and comfortable shoulder straps. Perfect for work and travel.',
                    'materials': ['Full Grain Leather'],
                    'styles': ['Work', 'Travel', 'Everyday'],
                    'sizes': ['Medium', 'Large'],
                    'price_range': '$1,500-$3,500',
                    'base_price': 2500,
                },
                'backpack': {
                    'name': '{color} Leather Backpack',
                    'description': 'Modern {color} leather backpack with laptop compartment',
                    'long_description': 'A contemporary {color} backpack crafted from premium leather. Features a padded laptop compartment, multiple pockets, and adjustable straps. Perfect for urban professionals.',
                    'materials': ['Premium Leather', 'Canvas Lining'],
                    'styles': ['Urban', 'Professional'],
                    'sizes': ['Medium', 'Large'],
                    'price_range': '$1,800-$3,000',
                    'base_price': 2400,
                },
                'clutch': {
                    'name': '{color} Evening Clutch',
                    'description': 'Elegant {color} clutch for special occasions',
                    'long_description': 'A sophisticated {color} clutch perfect for evening events. Features a magnetic closure, interior card slots, and optional chain strap. Handcrafted with attention to detail.',
                    'materials': ['Satin', 'Gold Hardware'],
                    'styles': ['Evening', 'Formal'],
                    'sizes': ['One Size'],
                    'price_range': '$800-$2,000',
                    'base_price': 1400,
                },
                'crossbody': {
                    'name': '{color} Crossbody Bag',
                    'description': 'Compact {color} crossbody bag with adjustable strap',
                    'long_description': 'A practical {color} crossbody bag made from supple leather. Features an adjustable strap, front flap closure, and organized interior. Perfect for hands-free convenience.',
                    'materials': ['Soft Leather', 'Silver Hardware'],
                    'styles': ['Casual', 'Travel'],
                    'sizes': ['Small', 'Medium'],
                    'price_range': '$1,200-$2,500',
                    'base_price': 1850,
                },
            },
            'accessories': {
                'belt': {
                    'name': '{color} Leather Belt with H Buckle',
                    'description': 'Signature {color} leather belt with iconic buckle',
                    'long_description': 'An iconic {color} leather belt featuring the signature H buckle. Crafted from premium reversible leather with polished hardware. A timeless accessory for any wardrobe.',
                    'materials': ['Reversible Leather', 'Palladium Buckle'],
                    'styles': ['Classic', 'Signature'],
                    'sizes': ['80cm', '85cm', '90cm', '95cm', '100cm', '105cm'],
                    'price_range': '$600-$1,000',
                    'base_price': 850,
                },
                'scarf': {
                    'name': '{color} Silk Scarf',
                    'description': 'Luxurious {color} silk scarf with artistic print',
                    'long_description': 'A stunning {color} silk scarf featuring an exclusive artistic print. Hand-rolled edges and vibrant colors. Each piece is a work of art that elevates any outfit.',
                    'materials': ['100% Silk Twill'],
                    'styles': ['Artistic', 'Classic'],
                    'sizes': ['70x70cm', '90x90cm', '140x140cm'],
                    'price_range': '$400-$1,200',
                    'base_price': 650,
                },
                'sunglasses': {
                    'name': '{color} Designer Sunglasses',
                    'description': 'Stylish {color} sunglasses with UV protection',
                    'long_description': 'Premium {color} sunglasses featuring 100% UV protection. Crafted with acetate frames and polarized lenses. Includes signature case and cleaning cloth.',
                    'materials': ['Acetate', 'Polarized Lenses'],
                    'styles': ['Classic', 'Aviator', 'Cat Eye'],
                    'sizes': ['One Size'],
                    'price_range': '$400-$800',
                    'base_price': 595,
                },
                'wallet': {
                    'name': '{color} Leather Wallet',
                    'description': 'Elegant {color} leather wallet with card slots',
                    'long_description': 'A refined {color} wallet crafted from premium leather. Features multiple card slots, bill compartment, and coin pocket. Compact design fits perfectly in any pocket.',
                    'materials': ['Full Grain Leather'],
                    'styles': ['Classic', 'Bifold'],
                    'sizes': ['One Size'],
                    'price_range': '$400-$800',
                    'base_price': 595,
                },
                'tie': {
                    'name': '{color} Silk Tie',
                    'description': 'Classic {color} silk tie with subtle pattern',
                    'long_description': 'A sophisticated {color} silk tie featuring a subtle woven pattern. Hand-finished with a silk lining. The perfect finishing touch for formal attire.',
                    'materials': ['100% Silk'],
                    'styles': ['Formal', 'Business'],
                    'sizes': ['Standard', 'Slim'],
                    'price_range': '$200-$400',
                    'base_price': 295,
                },
            },
            'jewelry': {
                'bracelet': {
                    'name': '{color} Clic Bracelet',
                    'description': 'Iconic {color} enamel bracelet with H clasp',
                    'long_description': 'The signature {color} Clic bracelet featuring vibrant enamel and the iconic H clasp. Crafted with palladium-plated hardware. A statement piece for any occasion.',
                    'materials': ['Enamel', 'Palladium'],
                    'styles': ['Signature', 'Statement'],
                    'sizes': ['PM', 'GM'],
                    'price_range': '$600-$900',
                    'base_price': 750,
                },
                'necklace': {
                    'name': '{color} Chain Necklace',
                    'description': 'Elegant {color} chain necklace with pendant',
                    'long_description': 'A stunning {color} chain necklace featuring a delicate pendant. Crafted from precious metals with expert craftsmanship. Perfect for layering or wearing alone.',
                    'materials': ['18K Gold', 'Sterling Silver'],
                    'styles': ['Delicate', 'Statement'],
                    'sizes': ['40cm', '45cm', '50cm'],
                    'price_range': '$1,500-$4,000',
                    'base_price': 2500,
                },
                'earrings': {
                    'name': '{color} Drop Earrings',
                    'description': 'Sophisticated {color} drop earrings',
                    'long_description': 'Elegant {color} drop earrings featuring exquisite craftsmanship. Made from precious metals with secure closures. Perfect for special occasions and everyday elegance.',
                    'materials': ['18K Gold', 'Sterling Silver'],
                    'styles': ['Drop', 'Stud', 'Hoop'],
                    'sizes': ['One Size'],
                    'price_range': '$800-$3,000',
                    'base_price': 1800,
                },
                'ring': {
                    'name': '{color} Band Ring',
                    'description': 'Classic {color} band ring with signature design',
                    'long_description': 'A timeless {color} band ring featuring the signature design. Crafted from precious metals with expert finishing. Perfect for stacking or wearing alone.',
                    'materials': ['18K Gold', 'Sterling Silver', 'Platinum'],
                    'styles': ['Band', 'Statement'],
                    'sizes': ['5', '6', '7', '8', '9'],
                    'price_range': '$1,000-$5,000',
                    'base_price': 2800,
                },
            },
        }

        # Color display names
        self.color_names = {
            'white': 'White', 'black': 'Black', 'blue': 'Blue', 'navy': 'Navy',
            'gray': 'Gray', 'red': 'Red', 'pink': 'Pink', 'striped': 'Striped',
            'green': 'Green', 'khaki': 'Khaki', 'olive': 'Olive', 'beige': 'Beige',
            'brown': 'Brown', 'tan': 'Tan', 'light_blue': 'Light Blue',
            'charcoal': 'Charcoal', 'gold': 'Gold', 'silver': 'Silver',
            'rose_gold': 'Rose Gold', 'brown_leather': 'Brown Leather',
            'orange': 'Orange', 'platinum': 'Platinum', 'two_tone': 'Two Tone',
            'multicolor': 'Multicolor', 'burgundy': 'Burgundy', 'cognac': 'Cognac',
            'nude': 'Nude', 'canvas': 'Canvas', 'silk_multi': 'Silk Multi',
            'cashmere_gray': 'Cashmere Gray', 'wool_navy': 'Wool Navy',
            'silk_orange': 'Silk Orange', 'cashmere_camel': 'Cashmere Camel',
            'tortoise': 'Tortoise', 'reversible': 'Reversible',
            'leather_black': 'Leather Black', 'enamel_orange': 'Enamel Orange',
            'pearl': 'Pearl', 'diamond': 'Diamond', 'hoop_gold': 'Hoop Gold',
        }
        
        # Gender mapping
        self.gender_mapping = {
            'shirts': 'Unisex',
            'pants': 'Unisex', 
            'watches': 'Unisex',
            'shoes': 'Unisex',
            'bags': 'Women',
            'accessories': 'Unisex',
            'jewelry': 'Women',
        }
        
        # Subcategory gender overrides
        self.subcategory_gender = {
            'heels': 'Women',
            'clutch': 'Women',
            'handbag': 'Women',
            'earrings': 'Women',
            'necklace': 'Women',
        }

    def generate_asset_id(self, category, subcategory, color, variant_idx):
        """Generate unique asset ID"""
        hash_input = f"{category}-{subcategory}-{color}-{variant_idx}"
        url_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"hermes-{url_hash}"
    
    def get_price(self, base_price, color):
        """Calculate price with slight variation"""
        import random
        variation = random.uniform(-0.1, 0.15)
        price = int(base_price * (1 + variation))
        return f"${price:,}"
    
    def get_price_range_bucket(self, base_price):
        """Get price range bucket for faceting"""
        if base_price < 500:
            return '$0 - $500'
        elif base_price < 1000:
            return '$500 - $1,000'
        elif base_price < 2500:
            return '$1,000 - $2,500'
        elif base_price < 5000:
            return '$2,500 - $5,000'
        else:
            return '$5,000+'
    
    def generate_product(self, category, subcategory, color, template, variant_idx):
        """Generate a single product"""
        # Get image URL
        image_url = self.image_library.get(category, {}).get(subcategory, {}).get(color)
        if not image_url:
            return None
        
        color_display = self.color_names.get(color, color.title())
        asset_id = self.generate_asset_id(category, subcategory, color, variant_idx)
        
        # Get sleeve/fit variant if applicable
        sleeve = ''
        fit = ''
        if 'sleeves' in template:
            sleeve = template['sleeves'][variant_idx % len(template['sleeves'])]
        if 'fits' in template:
            fit = template['fits'][variant_idx % len(template['fits'])]
        
        # Generate name and description
        name = template['name'].format(color=color_display, sleeve=sleeve, fit=fit).strip()
        description = template['description'].format(color=color_display, sleeve=sleeve, fit=fit).strip()
        long_desc = template['long_description'].format(color=color_display, sleeve=sleeve, fit=fit).strip()
        
        # Clean up extra spaces
        name = ' '.join(name.split())
        description = ' '.join(description.split())
        
        # Get gender
        gender = self.subcategory_gender.get(subcategory, self.gender_mapping.get(category, 'Unisex'))
        
        # Get size
        sizes = template.get('sizes', ['One Size'])
        size = sizes[variant_idx % len(sizes)]
        
        # Get style
        styles = template.get('styles', ['Classic'])
        style = styles[variant_idx % len(styles)]
        
        base_price = template['base_price']
        
        product = {
            'asset_id': asset_id,
            'title': name,
            'description': description,
            'long_description': long_desc,
            'category': category.title(),
            'subcategory': subcategory.replace('_', ' ').title(),
            'color': color_display,
            'material': template['materials'][0] if template['materials'] else 'Premium Materials',
            'materials': template['materials'],
            'style': style,
            'size': size,
            'gender': gender,
            'brand': 'Hermès',
            'price': self.get_price(base_price, color),
            'price_range': self.get_price_range_bucket(base_price),
            'image_url': image_url,
            'product_url': f"https://www.hermes.com/us/en/product/{asset_id}/",
            's3_key': f"{config.S3_IMAGES_PREFIX}{asset_id}.jpg",
            'product_details': {
                'Material': template['materials'][0] if template['materials'] else 'N/A',
                'Style': style,
                'Size': size,
                'Made in': 'France',
            },
            'product_attributes': {
                'color': color_display,
                'material': template['materials'][0] if template['materials'] else 'N/A',
                'style': style,
                'size': size,
                'gender': gender,
                'sku': asset_id.upper(),
            },
            'scraped_at': datetime.now(timezone.utc).isoformat(),
            'enriched_at': datetime.now(timezone.utc).isoformat(),
            'is_mock_data': True,
        }
        
        return product

    def generate_all_products(self, target_count=1000):
        """Generate all products up to target count"""
        print("\n" + "="*70)
        print("Enhanced Mock Data Generator - Luxury Fashion Products")
        print("="*70)
        print(f"Target: {target_count} products with unique images per variant")
        print("="*70 + "\n")
        
        products = []
        variant_idx = 0
        
        # Iterate through all categories, subcategories, and colors
        while len(products) < target_count:
            for category, subcategories in self.product_templates.items():
                if len(products) >= target_count:
                    break
                    
                for subcategory, template in subcategories.items():
                    if len(products) >= target_count:
                        break
                    
                    # Get available colors for this subcategory
                    colors = self.image_library.get(category, {}).get(subcategory, {}).keys()
                    
                    for color in colors:
                        if len(products) >= target_count:
                            break
                        
                        product = self.generate_product(
                            category, subcategory, color, template, variant_idx
                        )
                        
                        if product:
                            products.append(product)
                            
                            if len(products) % 100 == 0:
                                print(f"Generated {len(products)}/{target_count} products...")
            
            variant_idx += 1
            
            # Safety check to prevent infinite loop
            if variant_idx > 20:
                print(f"Reached maximum variants, stopping at {len(products)} products")
                break
        
        self.products = products
        
        print(f"\n✅ Generated {len(products)} products")
        
        # Print category breakdown
        categories = {}
        for p in products:
            cat = p['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nCategory breakdown:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")
        
        return products
    
    def save_products(self, filename='scraped_products.json'):
        """Save products to JSON file"""
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(config.OUTPUT_DIR, filename)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved to: {output_file}")
        return output_file


def main():
    """Main function"""
    generator = EnhancedMockGenerator()
    
    # Generate 1000 products
    products = generator.generate_all_products(target_count=1000)
    
    # Save to file
    generator.save_products()
    
    print("\n" + "="*70)
    print("Next Steps:")
    print("="*70)
    print("1. Download images to S3:")
    print("   python download_mock_images_to_s3.py")
    print("")
    print("2. Index to Coveo:")
    print("   python coveo_indexer.py")
    print("")
    print("3. Generate embeddings (offline):")
    print("   cd ../backend/embedding_generator && python generate_embeddings.py")
    print("="*70)


if __name__ == '__main__':
    main()
