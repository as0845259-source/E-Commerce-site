import os
from decimal import Decimal

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Category, Product

DOLLAR_RATE = 280


class Command(BaseCommand):
    help = 'Internet se products la kar database mein daalta hai'

    def handle(self, *args, **options):
        url = 'https://dummyjson.com/products?limit=20'
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()

        for item in data['products']:
            cat_name = item['category'].replace('-', ' ').title()
            category, created = Category.objects.get_or_create(
                slug=slugify(cat_name),
                defaults={'name': cat_name},
            )

            slug = slugify(item['title'])
            if Product.objects.filter(slug=slug).exists():
                self.stdout.write(f"Pehle se hai: {item['title']}")
                continue

            try:
                img = requests.get(item['thumbnail'], timeout=20)
                img.raise_for_status()
            except requests.RequestException:
                self.stdout.write(f"Image nahi mili, chhor diya: {item['title']}")
                continue

            ext = os.path.splitext(item['thumbnail'])[1] or '.webp'
            price = round(Decimal(str(item['price'])) * DOLLAR_RATE)

            product = Product(
                category=category,
                name=item['title'][:100],
                slug=slug,
                description=item['description'],
                price=price,
            )
            product.image.save(f'{slug}{ext}', ContentFile(img.content), save=False)
            product.save()

            self.stdout.write(f"Save ho gaya: {product.name} (Rs. {price})")