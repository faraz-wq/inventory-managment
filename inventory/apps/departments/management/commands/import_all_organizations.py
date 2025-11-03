import csv
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.departments.models import Department  # UPDATE THIS


class Command(BaseCommand):
    help = "Import ALL organization types (SD, HOD, SU, AO) from CSV files"

    # List all CSV files with their expected ORG_TYPE
    CSV_FILES = [
        {
            "filename": "ORGANISATIONS CODES-01-Sep-2025 05_07_21(SECRETARIAT DEPARTMENTS).csv",
            "org_type": "SD",
        },
        {
            "filename": "ORGANISATIONS CODES-01-Sep-2025 05_07_21(HEADS OF DEPARTMENTS).csv",
            "org_type": "HOD",
        },
        {
            "filename": "ORGANISATIONS CODES-01-Sep-2025 05_07_21(STATE UNITS).csv",
            "org_type": "SU",
        },
        # Special case: AO (Autonomous Organizations) – malformed, handle separately
    ]

    # AO data (from your message) – fixed format
    AO_DATA = [
        ("BCLAO", "AO", "AP Beverages Corporation Ltd", "REV01"),
        ("TODAO", "AO", "AP Toddy Tappers Cooperative Finance Corporation Ltd", "REV01"),
        ("BRAAO", "AO", "AP Brahmin Welfare Corporation", "REV01"),
        ("DMAAO", "AO", "AP State Disaster Management Authority", "REV01"),
        ("TTDAO", "AO", "Tirumala Tirupati Devastanam", "REV01"),
        ("VSDAO", "AO", "Sri Swayambhu Varasiddi Vinayaka Swamy Devasthanam", "REV01"),
        ("SKDAO", "AO", "Sri Kalahastheeswara Swamy Devasthanam", "REV01"),
        ("SSDAO", "AO", "Sri Veera Venkata Satyanarayana Swamy Devastanam", "REV01"),
        ("TADAO", "AO", "Sri Tirupatamma Ammavari Devasthanam", "REV01"),
        ("SDDAO", "AO", "Sri Durgamalleswara Swamy Varla Devatshanam", "REV01"),
        ("SBDAO", "AO", "Sri Bramaramba Mallikarjuna Swamy Devasthanam", "REV01"),
        ("LNDAO", "AO", "Sri Varaha Lakshmi Narasimha Swamy Devasthanam, Simhachalam", "REV01"),
        ("VDDAO", "AO", "Sri Venkateswara Swamy Devasthanam(Dwarakatirumala)", "REV01"),
        ("SMAAO", "AO", "Sri Mavullamma Ammavari Devasthanam", "REV01"),
        ("TLDAO", "AO", "Sri Talupulamma Ammavari Devasthanam", "REV01"),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--folder',
            type=str,
            help='Folder containing the CSV files (default: same as this command)',
        )

    def handle(self, *args, **options):
        folder = options['folder']
        if not folder:
            folder = Path(__file__).parent
        else:
            folder = Path(folder)

        total_created = 0
        total_skipped = 0

        # === 1. Import regular CSV files (SD, HOD, SU) ===
        for file_info in self.CSV_FILES:
            csv_path = folder / file_info["filename"]
            if not csv_path.exists():
                self.stdout.write(self.style.WARNING(f"File not found, skipping: {csv_path}"))
                continue

            created, skipped = self.import_csv(csv_path, file_info["org_type"])
            total_created += created
            total_skipped += skipped

        # === 2. Import AO (Autonomous Organizations) ===
        created, skipped = self.import_ao_data()
        total_created += created
        total_skipped += skipped

        self.stdout.write(
            self.style.SUCCESS(
                f"\nALL IMPORTS COMPLETE!\n"
                f"Total departments inserted/updated: {total_created}\n"
                f"Rows skipped: {total_skipped}"
            )
        )

    def import_csv(self, csv_path, expected_org_type):
        self.stdout.write(f"Importing {csv_path.name} (expected type: {expected_org_type})...")
        created = 0
        skipped = 0
        objs = []

        with open(csv_path, newline='', encoding='utf-8-sig') as f:  # ← 'utf-8-sig' removes BOM
            reader = csv.DictReader(f)

            # Debug: Print actual field names
            self.stdout.write(f"CSV Headers: {list(reader.fieldnames)}")

            # Normalize headers: strip whitespace and BOM
            normalized_fieldnames = [field.strip() for field in reader.fieldnames]
            reader.fieldnames = normalized_fieldnames

            expected_cols = {"ID", "ORG_CODE", "ORG_SHORTNAME", "ORG_TYPE", "ORG_NAME", "REPORT_ORG"}
            if not expected_cols.issubset(set(normalized_fieldnames)):
                missing = expected_cols - set(normalized_fieldnames)
                self.stdout.write(self.style.ERROR(f"Missing columns: {missing}"))
                return 0, 0

            for row in reader:
                # Use normalized keys
                org_code = row.get("ORG_CODE", "").strip()
                if not org_code:
                    skipped += 1
                    continue

                org_type = row.get("ORG_TYPE", "").strip()
                if org_type != expected_org_type:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Type mismatch: {org_code} is {org_type}, expected {expected_org_type}"
                        )
                    )

                objs.append(
                    Department(
                        org_code=org_code,
                        org_shortname=row.get("ORG_SHORTNAME", "").strip(),
                        org_type=org_type,
                        org_name=row.get("ORG_NAME", "").strip(),
                        report_org=row.get("REPORT_ORG", "").strip() or None,
                    )
                )

        if objs:
            with transaction.atomic():
                results = Department.objects.bulk_create(
                    objs,
                    update_conflicts=True,
                    update_fields=["org_shortname", "org_type", "org_name", "report_org"],
                    unique_fields=["org_code"],
                )
                created = len(results)

        self.stdout.write(f"  → {created} inserted/updated, {skipped} skipped")
        return created, skipped

    def import_ao_data(self):
        self.stdout.write("Importing AO (Autonomous Organizations)...")
        objs = []
        skipped = 0

        for org_code, org_type, org_name, report_org in self.AO_DATA:
            if not org_code.strip():
                skipped += 1
                continue
            objs.append(
                Department(
                    org_code=org_code,
                    org_shortname=org_code,  # fallback
                    org_type=org_type,
                    org_name=org_name,
                    report_org=report_org,
                )
            )

        created = 0
        if objs:
            with transaction.atomic():
                results = Department.objects.bulk_create(
                    objs,
                    update_conflicts=True,
                    update_fields=["org_shortname", "org_type", "org_name", "report_org"],
                    unique_fields=["org_code"],
                )
                created = len(results)

        self.stdout.write(f"  → {created} AO entries inserted/updated")
        return created, skipped