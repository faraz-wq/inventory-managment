# apps/catalogue/management/commands/import_idrn_master.py

import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.catalogue.models import ItemInfo


class Command(BaseCommand):
    help = "Import IDRN Master Items from CSV (S.No, Item Code, Item Name, Activity, Resource Type, Category)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='IDRN_Master_Items.csv',
            help='CSV file path (default: IDRN_Master_Items.csv in same folder)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing ItemInfo before import',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        clear_first = options['clear']

        cmd_dir = Path(__file__).parent
        csv_path = cmd_dir / file_path if not Path(file_path).is_absolute() else Path(file_path)

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        self.stdout.write(f"Importing IDRN master items from: {csv_path}")

        if clear_first:
            self.stdout.write("Clearing existing ItemInfo...")
            with transaction.atomic():
                ItemInfo.objects.all().delete()
            self.stdout.write("Cleared.")

        created = 0
        updated = 0
        skipped = 0

        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            # Normalize headers
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            self.stdout.write(f"Headers: {reader.fieldnames}")

            required = {'S.No', 'Item Code', 'Item Name', 'Activity Name', 'Resource Type', 'Category Name'}
            if not required.issubset(set(reader.fieldnames)):
                missing = required - set(reader.fieldnames)
                raise ValueError(f"Missing required columns: {missing}")

            with transaction.atomic():
                for row in reader:
                    item_code = row['Item Code'].strip()
                    if not item_code:
                        skipped += 1
                        continue

                    defaults = {
                        'item_name': row['Item Name'].strip(),
                        'activity_name': row['Activity Name'].strip(),
                        'resource_type': row['Resource Type'].strip(),
                        'category': row['Category Name'].strip(),
                        'unit': None,
                        'perishability': None,
                        'tags': f"{row['Activity Name'].strip()},{row['Resource Type'].strip()},{row['Category Name'].strip()}",
                        'active': True,
                    }

                    obj, created_flag = ItemInfo.objects.update_or_create(
                        item_code=item_code,
                        defaults=defaults
                    )
                    if created_flag:
                        created += 1
                    else:
                        updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nIDRN MASTER IMPORT COMPLETE!\n"
                f"  Created: {created} items\n"
                f"  Updated: {updated} items\n"
                f"  Skipped: {skipped} rows\n"
            )
        )