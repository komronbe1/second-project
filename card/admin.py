from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resource import CardResource
from .models import Card
from .forms import ExcelImport
from django.shortcuts import render, redirect
from django.urls import path

@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):
    resource_classes = (CardResource, )
    list_display = ['card_number', 'phone', 'balance','status','expire']
    list_filter = ['status', 'card_number', 'phone']


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel, name='import_excel'),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        if request.method == "POST":
            forms = ExcelImport(request.POST, request.FILES)
            if forms.is_valid():
                file = request.FILES("excel_file")
                wb = openpyxl.load_workbook(file)
                sheet = wb.active

                errors = []
                created_count = 0

                for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                    phone, card_number = row[0], row[1]

                    # --- НОРМАЛИЗАЦИЯ И ВАЛИДАЦИЯ ---
                    try:
                        clean_phone = "".join(filter(str.isdigit, str(phone)))
                        if not clean_phone.startswith('998'): # Пример для Узбекистана
                            clean_phone = '998' + clean_phone

                        clean_card = str(card_number).replace(" ", "").replace("-", "")

                        if len(clean_card) != 16:
                            raise ValueError(f"Invalid card length: {len(clean_card)}")

                        Card.objects.create(
                            phone=clean_phone,
                            card_number=clean_card
                        )
                        created_count += 1
                    except Exception as e:
                        errors.append(f"Row {row_idx}: {str(e)}")

                if errors:
                    messages.error(request, f"Hato: {'; '.join(errors)}")
                messages.success(request, f"muvofoqiyatli import bo'ldi : {created_count}")
                return redirect("..")

        form = ExcelImportForm()
        return render(request, "admin/excel_form.html", {"form": form})


