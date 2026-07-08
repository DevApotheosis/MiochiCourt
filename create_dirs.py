import os

dirs = [
    'd:\\Pro\\ai-tools\\games\\city_qes\\src\\core',
    'd:\\Pro\\ai-tools\\games\\city_qes\\src\\gui',
    'd:\\Pro\\ai-tools\\games\\city_qes\\data\\cases',
    'd:\\Pro\\ai-tools\\games\\city_qes\\data\\laws',
    'd:\\Pro\\ai-tools\\games\\city_qes\\data\\evidence',
    'd:\\Pro\\ai-tools\\games\\city_qes\\data\\dialogues',
    'd:\\Pro\\ai-tools\\games\\city_qes\\data\\modules',
    'd:\\Pro\\ai-tools\\games\\city_qes\\data\\saves',
    'd:\\Pro\\ai-tools\\games\\city_qes\\data\\achievements',
    'd:\\Pro\\ai-tools\\games\\city_qes\\data\\dossiers',
    'd:\\Pro\\ai-tools\\games\\city_qes\\tests',
    'd:\\Pro\\ai-tools\\games\\city_qes\\resources',
    'd:\\Pro\\ai-tools\\games\\city_qes\\docs'
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f'Created: {d}')