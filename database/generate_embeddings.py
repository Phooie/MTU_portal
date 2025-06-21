# management/commands/generate_embeddings.py
from django.core.management.base import BaseCommand
from myapp.models import Product
from openai import OpenAI

client = OpenAI(api_key="your-openai-key")

class Command(BaseCommand):
    help = 'Generates OpenAI embeddings for all products'

    def handle(self, *args, **kwargs):
        products = Product.objects.filter(embedding__isnull=True)
        for product in products:
            embedding = client.embeddings.create(
                input=[product.description],
                model="text-embedding-3-small"
            ).data[0].embedding
            product.embedding = embedding
            product.save()
            self.stdout.write(f"Generated embedding for {product.name}")