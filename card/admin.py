from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from pyexpat.errors import messages
from .ai_logic import clean_data_with_ai
from .resource import CardResource
from .models import Card
from .forms import ExcelImport
from django.shortcuts import render, redirect
from django.urls import path
import openpyxl
from django.contrib import messages


@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):
    # Подключаем ваш ресурс. Он сам всё распарсит, очистит и сохранит!
    resource_classes = (CardResource, )

    list_display = ['card_number', 'phone', 'balance', 'status', 'expire']
    list_filter = ['status', 'card_number', 'phone']
    search_fields = ['card_number', 'phone'] # Добавил поиск для удобства

    change_list_template = "admin/card/card/change_list.html"
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel, name='import_excel'),
            path('ai-import/', self.admin_site.admin_view(self.ai_import_view), name='ai_import'),

        ]
        return custom_urls + urls



    # 3. Вьюшка, которая откроется при нажатии на кнопку ✨ Magic AI Import
    def ai_import_view(self, request):
        if request.method == "POST":
            file = request.FILES.get("ai_excel_file")

            if not file:
                self.message_user(request, "Файл не выбран!", level=messages.ERROR)
                return redirect("..")

            try:
                # 1. Читаем Excel файл
                wb = openpyxl.load_workbook(file)
                sheet = wb.active

                # 2. Превращаем строки в простой текст для промпта
                raw_data = []
                for row in sheet.iter_rows(values_only=True):
                    raw_data.append(str(row))
                raw_string = "\n".join(raw_data)

                # 3. Отправляем грязный текст в Gemini AI
                print("Отправляю данные в AI... Ждем...") # Это появится в консоли
                clean_json_list = clean_data_with_ai(raw_string)

                # 4. Проверяем ответ и сохраняем в базу
                if clean_json_list and isinstance(clean_json_list, list):
                    created_count = 0
                    created_count = 0
                    for item in clean_json_list:
                        # 1. Достаем значения
                        card = item.get('card_number')
                        expire = item.get('expire')

                        # 2. ЖЕСТКАЯ ПРОВЕРКА: Если нет карты или срока - пропускаем эту строку!
                        if not card or not expire:
                            print(f"Пропущен кривой ряд: {item}") # Выведем в консоль, чтобы знать, что пропустили
                            continue

                            # 3. Сохраняем только хорошие данные
                        try:
                            Card.objects.create(
                                card_number=card,
                                expire=expire,
                                phone=item.get('phone'),
                                status=item.get('status', 'inactive'),
                                balance=item.get('balance', 0.00)
                            )
                            created_count += 1
                        except Exception as e:
                            print(f"Ошибка при сохранении карты {card}: {e}")

                    self.message_user(request, f"✨ AI магия сработала! Сохранено идеальных записей: {created_count}")
                else:
                    self.message_user(request, "AI не смог распознать формат данных.", level=messages.ERROR)

            except Exception as e:
                self.message_user(request, f"Произошла ошибка: {str(e)}", level=messages.ERROR)

            return redirect("..")

        context = dict(
            self.admin_site.each_context(request),
            title="Upload Excel for AI Cleaning",
        )
        return render(request, "admin/ai_upload_form.html", context)

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


