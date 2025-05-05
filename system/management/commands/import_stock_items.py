from django.core.management.base import BaseCommand
from system.models import StockItem

class Command(BaseCommand):
    help = 'Bulk import stock items extracted from Word document'

    def handle(self, *args, **kwargs):
        stock_data = [
            {"product_name": "Cornflakes", "product_id": "CF001", "available_quantity": 500, "unit_of_measure": "boxes"},
            {"product_name": "Baked Beans", "product_id": "BB002", "available_quantity": 100, "unit_of_measure": "tin"},
            {"product_name": "Eggs", "product_id": "EG003", "available_quantity": 500, "unit_of_measure": "crates"},
            {"product_name": "Liver", "product_id": "LV004", "available_quantity": 10000, "unit_of_measure": "grams"},
            {"product_name": "Sausages", "product_id": "SG005", "available_quantity": 10000, "unit_of_measure": "grams"},
            {"product_name": "Mince", "product_id": "MN006", "available_quantity": 10000, "unit_of_measure": "grams"},
            {"product_name": "Bacon", "product_id": "BC007", "available_quantity": 10000, "unit_of_measure": "grams"},
            {"product_name": "Commercial beef", "product_id": "CB008", "available_quantity": 15000, "unit_of_measure": "grams"},
            {"product_name": "Topside beef/Rump steak", "product_id": "TP009", "available_quantity": 10000, "unit_of_measure": "grams"},
            {"product_name": "Pork Chop", "product_id": "PC010", "available_quantity": 20000, "unit_of_measure": "grams"},
            {"product_name": "Chicken cutlets", "product_id": "CH011", "available_quantity": 5000, "unit_of_measure": "cutlets"},
            {"product_name": "Fish", "product_id": "FS012", "available_quantity": 10000, "unit_of_measure": "grams"},
            {"product_name": "Rice", "product_id": "RC013", "available_quantity": 200000, "unit_of_measure": "grams"},
            {"product_name": "Mealie Meal", "product_id": "MM014", "available_quantity": 100000, "unit_of_measure": "grams"},
            {"product_name": "Spaghetti", "product_id": "SP015", "available_quantity": 1000, "unit_of_measure": "packets"},
            {"product_name": "Cooking oil", "product_id": "CO016", "available_quantity": 15000, "unit_of_measure": "ml"},
            {"product_name": "Biscuits", "product_id": "BS017", "available_quantity": 100, "unit_of_measure": "packets"},
            {"product_name": "Milk", "product_id": "MK018", "available_quantity": 10000, "unit_of_measure": "ml"},
            {"product_name": "Juice", "product_id": "JC019", "available_quantity": 10000, "unit_of_measure": "ml"},
            {"product_name": "Bread", "product_id": "BR020", "available_quantity": 100, "unit_of_measure": "loaves"},
            {"product_name": "Quick brew (Tea bag)", "product_id": "TB021", "available_quantity": 100, "unit_of_measure": "sachets"},
            {"product_name": "Coffee sachet", "product_id": "CF022", "available_quantity": 100, "unit_of_measure": "sachets"},
            {"product_name": "Creamer", "product_id": "CR023", "available_quantity": 300, "unit_of_measure": "sachets"},
            {"product_name": "Sugar sachet", "product_id": "SG024", "available_quantity": 400, "unit_of_measure": "sachets"},
            {"product_name": "Jam Sachet", "product_id": "JM025", "available_quantity": 200, "unit_of_measure": "sachets"},
            {"product_name": "Margarine Sachet", "product_id": "MG026", "available_quantity": 200, "unit_of_measure": "sachets"},
            {"product_name": "Mineral Water", "product_id": "MW027", "available_quantity": 200, "unit_of_measure": "bottles"},
            {"product_name": "Sweets", "product_id": "SW028", "available_quantity": 200, "unit_of_measure": "pieces"},
            {"product_name": "Green vegetables", "product_id": "GV029", "available_quantity": 300, "unit_of_measure": "bundles"},
        ]

        for item in stock_data:
            obj, created = StockItem.objects.get_or_create(
                product_name=item['product_name'],
                product_id=item['product_id'],
                defaults={
                    'available_quantity': item['available_quantity'],
                    'unit_of_measure': item['unit_of_measure']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added: {item['product_name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Skipped (exists): {item['product_name']}"))