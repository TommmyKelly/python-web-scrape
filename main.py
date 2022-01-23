from tkinter import *
from bs4 import BeautifulSoup
import requests
import pandas as pd
from fpdf import FPDF
from tkinter import filedialog
from tkinter import messagebox


YELLOW = "#f7f5dd"


def scrape():



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

    messagebox.showinfo(title="Success", message="Reports saved")


def folder_picker():
    window.filename = filedialog.askdirectory()
    folder_name = window.filename.replace("/", "\\") + "\\"
    entry_folder.delete(0,'end')
    entry_folder.insert(0, folder_name)


def check_folder_input():
    folder_path = entry_folder.get()
    if folder_path == "":
        messagebox.showinfo(title="Selection Required", message='Please select a folder to save results')
    else:
        scrape()


window = Tk()
window.geometry("800x200")
window.title("Kilkenny Parkrun")
window.config(padx=100, pady=50, bg=YELLOW)
entry_folder = Entry(width=100)
entry_folder.grid(column=1, row=1, columnspan=4, pady=5)
scrape_button = Button(text='Run', width=20, cursor="hand2", command=check_folder_input)
scrape_button.grid(column=1, row=2, columnspan=4)
folder_image = PhotoImage(file="folder_image.png")
folder_picker_button = Button(cursor="hand2", command=folder_picker, image=folder_image, height=18, width=20)
folder_picker_button.grid(column=5, row=1, columnspan=1, padx=5)
window.resizable(False, False)
window.mainloop()

