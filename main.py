from bs4 import BeautifulSoup
import requests
import pandas as pd
from fpdf import FPDF


headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.\
4692.71 Safari/537.36"}

url = "https://www.parkrun.ie/kilkenny/results/latestresults/"
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')


date = soup.find('span', class_="format-date").text.replace("/", ".")

rows = soup.findAll("tr")
rows = rows[1:]


data = []

for row in rows:
    try:
        position = row.get_attribute_list('data-position')[0]
        name = row.get_attribute_list('data-name')[0]
        club = row.get_attribute_list('data-club')[0]
        if name == "Unknown":
            name = "Unknown"
            club = ""
            time = ""
            PB = ""
        elif row.find('td', class_="Results-table-td Results-table-td--time"):
            time_row = row.find('td', class_="Results-table-td Results-table-td--time").text.split("PB")
            print(time_row)
            PB = time_row[1].strip()
            time = time_row[0].strip()
        elif row.find('td', class_="Results-table-td Results-table-td--time Results-table-td--ft"):
            time = row.find('td', class_="Results-table-td Results-table-td--time Results-table-td--ft").text
            PB = time
        else:
            time = row.find('td', class_="Results-table-td Results-table-td--time Results-table-td--pb").text.split("N")
            time = time[0]
            PB = f"{time} New PB!"

            print(time_row)

        data.append({
            "Position": position,
            "Name": name,
            "Club": club,
            "Time": time,
            "PB": PB
        })

    except Exception as e:
        print(e)

df = pd.DataFrame(data)


html_string = f'''
<html>
  <head><title>HTML Pandas Dataframe with CSS</title></head>
  <link rel="stylesheet" type="text/css" href="df_style.css"/>
  <body>
    {df.to_html(classes='mystyle',index=False)}
  </body>
</html>
'''
with open('myhtml.html', 'w') as f:
    f.write(html_string)

pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(40, 10, f"{date} Park Run Kilkenny Results")
pdf.set_font('Arial', 'B', 9)
th = pdf.font_size + 5
pdf.ln(th)
pdf.ln(th)
pdf.ln(th)
page_width = pdf.w - 2 * pdf.l_margin
col_width = page_width / 5
pdf.set_text_color(255, 255, 255)
pdf.set_fill_color(124, 156, 163)
pdf.set_font('Arial', 'BU', 12)
pdf.set_draw_color(255, 255, 255)
pdf.cell(col_width - 25, th, '#', border=1, fill=True, align='C')
pdf.cell(col_width + 10, th, 'Name', border=1, fill=True, align='C')
pdf.cell(col_width + 15, th, 'Club', border=1, fill=True, align='C')
pdf.cell(col_width, th, 'Time', border=1, fill=True, align='C')
pdf.cell(col_width, th, 'PB', border=1, fill=True, align='C')
pdf.ln(th)
pdf.set_font('Arial', 'B', 9)
for row_index, row in df.iterrows():
    pdf.cell(col_width - 25, th, format(row['Position']), border=1, fill=True, align='C')
    pdf.cell(col_width + 10, th, format(row['Name']), border=1, fill=True, align='C')
    pdf.cell(col_width + 15, th, format(row['Club']), border=1, fill=True, align='C')
    pdf.cell(col_width, th, format(row['Time']), border=1, fill=True, align='C')
    pdf.cell(col_width, th, format(row['PB']), border=1, fill=True, align='C')
    pdf.ln(th)

pdf.output(f'Park Run Kilkenny {date}.pdf', 'F')
df['Position'] = df['Position'].astype(int)
df_date = pd.DataFrame({'Date': date.replace(".", "/")}, index=['Date'])
writer = pd.ExcelWriter(f'Park Run Kilkenny {date}.xlsx')
df_date.to_excel(writer, sheet_name=date, index=False, startrow=0)
df.to_excel(writer, sheet_name=date, index=False, startrow=5)

writer.save()

print(df.head(30))



