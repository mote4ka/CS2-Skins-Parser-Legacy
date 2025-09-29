import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import io

# Ваши данные
data = [
    (1609459200, 100),
    (1609545600, 105),
    (1609632000, 98),
    (1609718400, 110),
    (1609804800, 95),
    (1609891200, 102)
]

# Создаем DataFrame
df = pd.DataFrame(data, columns=['timestamp', 'price'])
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
df = df.sort_values('datetime')

# Создаем график в памяти
plt.figure(figsize=(10, 5))
plt.plot(df['datetime'], df['price'], marker='o', linewidth=2, markersize=4)
plt.title('История продаж предмета')
plt.xlabel('Дата')
plt.ylabel('Цена')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

# Сохраняем график в буфер памяти
img_buffer = io.BytesIO()
plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
img_buffer.seek(0)

# Создаем Excel файл
wb = Workbook()

# Лист с данными
ws_data = wb.active
ws_data.title = "Данные продаж"

# Заголовки
ws_data['A1'] = 'Дата'
ws_data['B1'] = 'Время (Unix)'
ws_data['C1'] = 'Цена'

# Данные
for i, (index, row) in enumerate(df.iterrows(), start=2):
    ws_data[f'A{i}'] = row['datetime']
    ws_data[f'B{i}'] = row['timestamp']
    ws_data[f'C{i}'] = row['price']

# Лист с графиком
ws_chart = wb.create_sheet("График")

# Добавляем изображение в Excel
img = Image(img_buffer)
img.anchor = 'A1'
ws_chart.add_image(img)

# Сохраняем Excel файл
wb.save('данные_о_продажах.xlsx')
plt.close()

print("Файл 'данные_о_продажах.xlsx' успешно создан!")
print("Содержит два листа: 'Данные продаж' и 'График'")