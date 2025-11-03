import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.locations.models import District, Mandal, Village

class Command(BaseCommand):
    help = "Import/Update Districts, Mandals, and Villages from Admin_codes_AP.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='Admin_codes_AP.csv',
            help='Path to CSV file (default: Admin_codes_AP.csv in same folder)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        clear_first = options['clear']

        # Resolve full path
        cmd_dir = Path(__file__).parent
        csv_path = cmd_dir / file_path if not Path(file_path).is_absolute() else Path(file_path)

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        self.stdout.write(f"Loading data from: {csv_path}")

        # Optional: Clear existing data
        if clear_first:
            self.stdout.write("Clearing existing location data...")
            with transaction.atomic():
                Village.objects.all().delete()
                Mandal.objects.all().delete()
                District.objects.all().delete()
            self.stdout.write("Cleared.")

        created = {'districts': 0, 'mandals': 0, 'villages': 0}
        updated = {'districts': 0, 'mandals': 0, 'villages': 0} # Track updates
        skipped = 0
        processed = 0

        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            # Normalize headers
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            self.stdout.write(f"Headers: {reader.fieldnames}")

            required = {
                'District', 'DstCodeAP',
                'Mandal', 'MndCodeAP',
                'Village', 'VillCodeAP'
            }
            if not required.issubset(set(reader.fieldnames)):
                missing = required - set(reader.fieldnames)
                raise ValueError(f"Missing required columns: {missing}")

            with transaction.atomic():
                for row in reader:
                    processed += 1

                    # === Extract and clean ===
                    district_name = row['District'].strip()
                    dst_code_ap = row['DstCodeAP'].strip()
                    dst_code_ind = row['DstCodeInd'].strip() if row.get('DstCodeInd', '').strip() != 'NA' else None

                    mandal_name = row['Mandal'].strip()
                    mnd_code_ap = row['MndCodeAP'].strip()
                    mnd_code_ind = row['MndCodeInd'].strip() if row.get('MndCodeInd', '').strip() != 'NA' else None

                    village_name = row['Village'].strip().replace('"', '').replace('\n', ' ').strip()
                    vill_code_ap = row['VillCodeAP'].strip()
                    vill_code_ind = row.get('VillCodeIn', '').strip()
                    vill_code_ind = vill_code_ind if vill_code_ind and vill_code_ind != 'NA' else None

                    # === SKIP ONLY IF VILLAGE CODE IS INVALID ===
                    if not vill_code_ap or vill_code_ap == 'NA':
                        skipped += 1
                        continue

                    # Optional: skip if district/mandal codes missing
                    if not dst_code_ap or not mnd_code_ap:
                        skipped += 1
                        continue

                    # === District ===
                    # Use update_or_create: create if not exists, update if exists
                    district, dist_created = District.objects.update_or_create(
                        district_code_ap=dst_code_ap, # This is the lookup field
                        defaults={ # These are the fields to set/update
                            'district_name': district_name,
                            'district_code_ind': dst_code_ind,
                            'is_active': True, # Assuming you want to keep them active
                        }
                    )
                    if dist_created:
                        created['districts'] += 1
                    else:
                        updated['districts'] += 1 # Track updates

                    # === Mandal ===
                    mandal, mndl_created = Mandal.objects.update_or_create(
                        mandal_code_ap=mnd_code_ap, # Lookup field
                        defaults={
                            'mandal_name': mandal_name,
                            'mandal_code_ind': mnd_code_ind,
                            'district': district, # Link to the district just fetched or created
                            'is_active': True,
                        }
                    )
                    if mndl_created:
                        created['mandals'] += 1
                    else:
                        updated['mandals'] += 1

                    # === Village ===
                    village, vill_created = Village.objects.update_or_create(
                        village_code_ap=vill_code_ap, # Lookup field
                        defaults={
                            'village_name': village_name,
                            'village_code_ind': vill_code_ind,
                            'mandal': mandal, # Link to the mandal
                            'district': district, # Link to the district
                            'is_active': True,
                        }
                    )
                    if vill_created:
                        created['villages'] += 1
                    else:
                        updated['villages'] += 1

        # Final Report - Include updates
        self.stdout.write(
            self.style.SUCCESS(
                f"\nIMPORT/UPDATE COMPLETE!\n"
                f"  Processed: {processed} rows\n"
                f"  Skipped: {skipped} invalid rows (NA, urban, etc.)\n"
                f"  Created:\n"
                f"    • {created['districts']} Districts\n"
                f"    • {created['mandals']} Mandals\n"
                f"    • {created['villages']} Villages\n"
                f"  Updated:\n"
                f"    • {updated['districts']} Districts\n"
                f"    • {updated['mandals']} Mandals\n"
                f"    • {updated['villages']} Villages\n" # Added updated counts
            )
        )
        return f"{self.help} completed."