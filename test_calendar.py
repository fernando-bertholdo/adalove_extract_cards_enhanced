import json
from pathlib import Path
from src.adalove_extractor.io.calendar import ICalendarExport

def main():
    with open('output/api_extraction/2026-1A-T13/semanas/semana_06.json', 'r') as f:
        data = json.load(f)
    
    extracao_mock = {
        "semanas": {
            "Semana 06": data
        }
    }
    
    exporter = ICalendarExport(horario_padrao='10:00')
    out_path = Path('test_output.ics')
    success = exporter.gerar_calendario(extracao_mock, out_path)
    if success:
        with open('test_output.ics', 'r') as f:
            for line in f:
                if line.startswith('SUMMARY'):
                    print(line.strip())

if __name__ == '__main__':
    main()
