import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
import os
import num2words


class ModernInvoiceGenerator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Générateur de Factures")
        self.window.geometry("800x600")
        self.window.configure(bg="#f9fafb")

        # Variables
        self.client_name = tk.StringVar()
        self.client_ice = tk.StringVar()
        self.items = []
        self.subtotal = 0
        self.vat_rate = 0.20

        # Styles
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12), padding=10)

        # GUI Layout
        self.create_gui()

    def create_gui(self):
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Header Section
        header_frame = ttk.LabelFrame(main_frame, text="En-tête", padding=10)
        header_frame.pack(fill="x", pady=(0, 20))

        self.header_path = tk.StringVar(value="header.png")
        ttk.Label(header_frame, text="Image d'en-tête :").grid(row=0, column=0, sticky="w")
        ttk.Entry(header_frame, textvariable=self.header_path, width=50).grid(row=0, column=1, padx=10)
        ttk.Button(header_frame, text="Parcourir", command=self.browse_header).grid(row=0, column=2)

        # Client Information
        client_frame = ttk.LabelFrame(main_frame, text="Informations du Client", padding=10)
        client_frame.pack(fill="x", pady=10)

        ttk.Label(client_frame, text="Nom du Client :").grid(row=0, column=0, sticky="w")
        ttk.Entry(client_frame, textvariable=self.client_name).grid(row=0, column=1, padx=10)

        ttk.Label(client_frame, text="ICE :").grid(row=1, column=0, sticky="w")
        ttk.Entry(client_frame, textvariable=self.client_ice).grid(row=1, column=1, padx=10)

        # Scrollable Items Table
        items_frame = ttk.LabelFrame(main_frame, text="Articles", padding=10)
        items_frame.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(items_frame, borderwidth=0, background="#f9fafb")
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, padding=10)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        headers = ["N°", "Désignation", "Quantité", "Unité", "Prix Unitaire (DHS)", "Prix Total (DHS)"]
        for i, header in enumerate(headers):
            ttk.Label(self.scrollable_frame, text=header).grid(row=0, column=i, padx=5, pady=5)

        add_button = ttk.Button(items_frame, text="Ajouter Article", command=self.add_item_row)
        add_button.pack(pady=10)

        # Totals
        totals_frame = ttk.Frame(main_frame, padding=10)
        totals_frame.pack(fill="x", pady=10)

        self.subtotal_var = tk.StringVar(value="0.00")
        self.vat_var = tk.StringVar(value="0.00")
        self.total_ttc_var = tk.StringVar(value="0.00")

        ttk.Label(totals_frame, text="HTVA :").grid(row=0, column=0, sticky="e")
        ttk.Label(totals_frame, textvariable=self.subtotal_var).grid(row=0, column=1, sticky="w")

        ttk.Label(totals_frame, text="TVA (20%) :").grid(row=1, column=0, sticky="e")
        ttk.Label(totals_frame, textvariable=self.vat_var).grid(row=1, column=1, sticky="w")

        ttk.Label(totals_frame, text="TTC :").grid(row=2, column=0, sticky="e")
        ttk.Label(totals_frame, textvariable=self.total_ttc_var).grid(row=2, column=1, sticky="w")

        # Footer Section
        footer_frame = ttk.LabelFrame(main_frame, text="Pied de Page", padding=10)
        footer_frame.pack(fill="x", pady=(20, 0))

        self.footer_path = tk.StringVar(value="footer.png")
        ttk.Label(footer_frame, text="Image de pied de page :").grid(row=0, column=0, sticky="w")
        ttk.Entry(footer_frame, textvariable=self.footer_path, width=50).grid(row=0, column=1, padx=10)
        ttk.Button(footer_frame, text="Parcourir", command=self.browse_footer).grid(row=0, column=2)

        # Generate Button
        generate_button = ttk.Button(main_frame, text="Générer PDF", command=self.generate_pdf)
        generate_button.pack(pady=20)

    def browse_header(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            self.header_path.set(path)

    def browse_footer(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            self.footer_path.set(path)

    def add_item_row(self):
        item_frame = ttk.Frame(self.scrollable_frame)
        item_frame.grid(sticky="ew", pady=5)

        designation = tk.StringVar()
        quantity = tk.StringVar()
        unit = tk.StringVar()
        price = tk.StringVar()

        index = len(self.items) + 1
        ttk.Label(item_frame, text=str(index)).grid(row=0, column=0, padx=5)
        ttk.Entry(item_frame, textvariable=designation).grid(row=0, column=1, padx=5)
        ttk.Entry(item_frame, textvariable=quantity).grid(row=0, column=2, padx=5)
        ttk.Entry(item_frame, textvariable=unit).grid(row=0, column=3, padx=5)
        ttk.Entry(item_frame, textvariable=price).grid(row=0, column=4, padx=5)

        total_label = ttk.Label(item_frame, text="0.00")
        total_label.grid(row=0, column=5, padx=5)

        def calculate_total():
            try:
                qty = float(quantity.get())
                prc = float(price.get())
                total = qty * prc
                total_label.config(text=f"{total:.2f}")
                self.update_totals()
            except ValueError:
                pass

        quantity.trace("w", lambda *args: calculate_total())
        price.trace("w", lambda *args: calculate_total())

        delete_button = ttk.Button(item_frame, text="Supprimer", command=lambda: self.delete_item_row(item_frame))
        delete_button.grid(row=0, column=6, padx=5)

        self.items.append((designation, quantity, unit, price, total_label))

    def delete_item_row(self, item_frame):
        index = list(self.scrollable_frame.children.values()).index(item_frame)
        self.items.pop(index)
        item_frame.destroy()
        self.reset_item_numbers()
        self.update_totals()

    def reset_item_numbers(self):
        for i, (_, _, _, _, _) in enumerate(self.items, start=1):
            label = list(self.scrollable_frame.children.values())[i - 1].grid_slaves(row=0, column=0)[0]
            label.config(text=str(i))

    def update_totals(self):
        subtotal = sum(float(label.cget("text")) for _, _, _, _, label in self.items)
        vat = subtotal * self.vat_rate
        total_ttc = subtotal + vat

        self.subtotal_var.set(f"{subtotal:.2f}")
        self.vat_var.set(f"{vat:.2f}")
        self.total_ttc_var.set(f"{total_ttc:.2f}")

    def generate_pdf(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not filename:
            return

        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=30, bottomMargin=30)
        elements = []

        # Header
        try:
            header_image = Image(self.header_path.get(), width=190 * mm, height=20 * mm)
            elements.append(header_image)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image d'en-tête : {e}")

        # Client Info
        client_info = [
            [Paragraph("Nom du Client :", getSampleStyleSheet()["Normal"]), Paragraph(self.client_name.get(), getSampleStyleSheet()["Normal"])],
            [Paragraph("ICE :", getSampleStyleSheet()["Normal"]), Paragraph(self.client_ice.get(), getSampleStyleSheet()["Normal"])]
        ]
        elements.append(Table(client_info, colWidths=[2 * inch, 4 * inch]))
        elements.append(Spacer(1, 20))

        # Items Table
        data = [["N°", "Désignation", "Quantité", "Unité", "Prix Unitaire (DHS)", "Prix Total (DHS)"]]
        for i, (desc, qty, unit, price, total_label) in enumerate(self.items, start=1):
            data.append([str(i), desc.get(), qty.get(), unit.get(), price.get(), total_label.cget("text")])

        table = Table(data, colWidths=[0.7 * inch, 2.5 * inch, 1 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Totals
        totals_data = [
            ["HTVA :", self.subtotal_var.get()],
            ["TVA (20%) :", self.vat_var.get()],
            ["TTC :", self.total_ttc_var.get()]
        ]
        totals_table = Table(totals_data, colWidths=[2 * inch, 2 * inch])
        totals_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 12)
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 20))

        # Amount in Words
        total_ttc = float(self.total_ttc_var.get())
        amount_in_words = num2words.num2words(int(total_ttc), lang="fr") + " dirhams"
        elements.append(Paragraph(f"Montant en lettres : {amount_in_words}", getSampleStyleSheet()["Normal"]))
        elements.append(Spacer(1, 20))

        # Footer
        try:
            footer_image = Image(self.footer_path.get(), width=190 * mm, height=20 * mm)
            elements.append(footer_image)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image de pied de page : {e}")

        # Build PDF
        doc.build(elements)
        messagebox.showinfo("Succès", "Facture générée avec succès !")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = ModernInvoiceGenerator()
    app.run()