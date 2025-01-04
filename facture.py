import tkinter as tk
from tkinter import ttk, filedialog
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage
from PIL import ImageTk
import num2words
import os

class ModernInvoiceGenerator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Invoice Generator")
        self.window.geometry("1000x800")
        self.window.configure(bg="#f0f0f0")
        
        # Translations dictionary
        self.translations = {
            "English": {
                "company_details": "Company Details",
                "invoice_details": "Invoice Details",
                "items": "Invoice Items",
                "generate": "Generate PDF",
                "save_template": "Save Template",
                "load_template": "Load Template",
                "company_name": "Company Name",
                "client_name": "Client Name",
                "invoice_number": "Invoice Number",
                "date": "Date",
                "description": "Description",
                "quantity": "Quantity",
                "price": "Price",
                "total": "Total",
                "subtotal": "Subtotal",
                "vat": "VAT",
                "total_ttc": "Total (Inc. VAT)",
                "amount_in_words": "Amount in Words",
                "add_item": "Add Item",
                "signature": "Add Signature"
            },
            "French": {
                "company_details": "Détails de l'entreprise",
                "invoice_details": "Détails de la facture",
                "items": "Articles",
                "generate": "Générer PDF",
                "save_template": "Enregistrer le modèle",
                "load_template": "Charger le modèle",
                "company_name": "Nom de l'entreprise",
                "client_name": "Nom du client",
                "invoice_number": "N° Facture",
                "date": "Date",
                "description": "Description",
                "quantity": "Quantité",
                "price": "Prix",
                "total": "Total",
                "subtotal": "Sous-total",
                "vat": "TVA",
                "total_ttc": "Total TTC",
                "amount_in_words": "Montant en lettres",
                "add_item": "Ajouter un article",
                "signature": "Ajouter une signature"
            }
        }
        
        self.exchange_rates = {
            "USD": 1.0,
            "EUR": 0.92,
            "MAD": 10.2
        }
        
        self.signature_path = None
        self.vat_rate = 0.20  # 20% VAT by default
        self.setup_styles()
        self.create_gui()
        
    def setup_styles(self):
        # Configure modern styles
        style = ttk.Style()
        style.configure('Modern.TFrame', background='#f0f0f0')
        style.configure('Modern.TLabel', background='#f0f0f0', font=('Helvetica', 10))
        style.configure('Modern.TButton', 
                       padding=10,
                       font=('Helvetica', 10),
                       background='#4a90e2',
                       foreground='white')
        style.configure('Title.TLabel',
                       font=('Helvetica', 14, 'bold'),
                       background='#f0f0f0',
                       foreground='#2c3e50')
        
    def create_gui(self):
        main_frame = ttk.Frame(self.window, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Language and currency selection
        controls_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        controls_frame.pack(side='left')
        
        self.language_var = tk.StringVar(value="English")
        ttk.Label(controls_frame, text="Language:", style='Modern.TLabel').pack(side='left', padx=5)
        language_cb = ttk.Combobox(controls_frame, textvariable=self.language_var,
                                 values=["English", "French"])
        language_cb.pack(side='left', padx=5)
        language_cb.bind('<<ComboboxSelected>>', self.update_language)
        
        self.currency_var = tk.StringVar(value="USD")
        ttk.Label(controls_frame, text="Currency:", style='Modern.TLabel').pack(side='left', padx=5)
        ttk.Combobox(controls_frame, textvariable=self.currency_var,
                     values=["USD", "EUR", "MAD"]).pack(side='left', padx=5)
        
        # Company Details
        company_frame = ttk.LabelFrame(main_frame, text=self.get_translation("company_details"),
                                     style='Modern.TFrame')
        company_frame.pack(fill='x', pady=10)
        
        self.company_name = tk.StringVar()
        ttk.Label(company_frame, text=self.get_translation("company_name"),
                 style='Modern.TLabel').pack(pady=5)
        ttk.Entry(company_frame, textvariable=self.company_name).pack(pady=5)
        
        # Invoice Details
        invoice_frame = ttk.LabelFrame(main_frame, text=self.get_translation("invoice_details"),
                                     style='Modern.TFrame')
        invoice_frame.pack(fill='x', pady=10)
        
        details_grid = ttk.Frame(invoice_frame, style='Modern.TFrame')
        details_grid.pack(fill='x', padx=10, pady=5)
        
        self.client_name = tk.StringVar()
        self.invoice_number = tk.StringVar()
        self.invoice_date = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        
        # Grid layout for invoice details
        ttk.Label(details_grid, text=self.get_translation("client_name"),
                 style='Modern.TLabel').grid(row=0, column=0, pady=5, sticky='w')
        ttk.Entry(details_grid, textvariable=self.client_name).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(details_grid, text=self.get_translation("invoice_number"),
                 style='Modern.TLabel').grid(row=1, column=0, pady=5, sticky='w')
        ttk.Entry(details_grid, textvariable=self.invoice_number).grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(details_grid, text=self.get_translation("date"),
                 style='Modern.TLabel').grid(row=2, column=0, pady=5, sticky='w')
        ttk.Entry(details_grid, textvariable=self.invoice_date).grid(row=2, column=1, pady=5, padx=5)
        
        # Items Table
        items_frame = ttk.LabelFrame(main_frame, text=self.get_translation("items"),
                                   style='Modern.TFrame')
        items_frame.pack(fill='both', expand=True, pady=10)
        
        # Table headers
        headers_frame = ttk.Frame(items_frame, style='Modern.TFrame')
        headers_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(headers_frame, text=self.get_translation("description"),
                 style='Modern.TLabel').pack(side='left', padx=(0, 10), expand=True)
        ttk.Label(headers_frame, text=self.get_translation("quantity"),
                 style='Modern.TLabel').pack(side='left', padx=10)
        ttk.Label(headers_frame, text=self.get_translation("price"),
                 style='Modern.TLabel').pack(side='left', padx=10)
        
        # Items container
        self.items_container = ttk.Frame(items_frame, style='Modern.TFrame')
        self.items_container.pack(fill='both', expand=True)
        
        self.items = []
        ttk.Button(items_frame, text=self.get_translation("add_item"),
                  command=self.add_item_row, style='Modern.TButton').pack(pady=10)
        
        # Signature
        signature_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        signature_frame.pack(fill='x', pady=10)
        
        ttk.Button(signature_frame, text=self.get_translation("signature"),
                  command=self.add_signature, style='Modern.TButton').pack(side='left', padx=5)
        
        # Action buttons
        buttons_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        buttons_frame.pack(fill='x', pady=20)
        
        ttk.Button(buttons_frame, text=self.get_translation("generate"),
                  command=self.generate_pdf, style='Modern.TButton').pack(side='left', padx=5)
        ttk.Button(buttons_frame, text=self.get_translation("save_template"),
                  command=self.save_template, style='Modern.TButton').pack(side='left', padx=5)
        ttk.Button(buttons_frame, text=self.get_translation("load_template"),
                  command=self.load_template, style='Modern.TButton').pack(side='left', padx=5)

    def get_translation(self, key):
        return self.translations[self.language_var.get()].get(key, key)

    def update_language(self, event=None):
        # Update all text elements with new language
        self.window.title(self.get_translation("invoice_generator"))
        # Update all other labels and buttons (you'll need to store references to them)
        self.refresh_gui()

    def refresh_gui(self):
        # Recreate the entire GUI with new language
        for widget in self.window.winfo_children():
            widget.destroy()
        self.create_gui()

    def add_item_row(self):
        item_frame = ttk.Frame(self.items_container, style='Modern.TFrame')
        item_frame.pack(fill='x', pady=2)
        
        description = tk.StringVar()
        quantity = tk.StringVar()
        price = tk.StringVar()
        
        ttk.Entry(item_frame, textvariable=description, width=40).pack(side='left', padx=2)
        ttk.Entry(item_frame, textvariable=quantity, width=10).pack(side='left', padx=2)
        ttk.Entry(item_frame, textvariable=price, width=10).pack(side='left', padx=2)
        
        # Delete button
        delete_btn = ttk.Button(item_frame, text="×", width=3,
                              command=lambda: self.delete_item_row(item_frame))
        delete_btn.pack(side='left', padx=2)
        
        self.items.append((description, quantity, price))

    def delete_item_row(self, item_frame):
        index = list(self.items_container.children.values()).index(item_frame)
        self.items.pop(index)
        item_frame.destroy()

    def add_signature(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if file_path:
            self.signature_path = file_path

    def amount_to_words(self, amount):
        language = self.language_var.get().lower()
        if language == "french":
            return num2words.num2words(amount, lang='fr') + " euros"
        return num2words.num2words(amount, lang='en') + " dollars"

    def generate_pdf(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not filename:
            return
            
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CompanyHeader',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        ))
        
        # Company header
        elements.append(Paragraph(self.company_name.get(), styles['CompanyHeader']))
        
        # Invoice details
        elements.append(Paragraph(f"{self.get_translation('invoice_number')}: {self.invoice_number.get()}", styles['Normal']))
        elements.append(Paragraph(f"{self.get_translation('date')}: {self.invoice_date.get()}", styles['Normal']))
        elements.append(Paragraph(f"{self.get_translation('client_name')}: {self.client_name.get()}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Items table
        data = [[
            self.get_translation('description'),
            self.get_translation('quantity'),
            self.get_translation('price'),
            self.get_translation('total')
        ]]
        
        subtotal = 0
        
        for desc, qty, price in self.items:
            try:
                quantity = float(qty.get())
                unit_price = float(price.get())
                item_total = quantity * unit_price
                subtotal += item_total
                data.append([
                    desc.get(),
                    str(quantity),
                    f"{unit_price:.2f} {self.currency_var.get()}",
                    f"{item_total:.2f} {self.currency_var.get()}"
                ])
            except ValueError:
                continue
        
        # Calculate VAT and total
        vat_amount = subtotal * self.vat_rate
        total_ttc = subtotal + vat_amount
        
        # Add totals
        data.extend([
            ['', '', self.get_translation('subtotal'), f"{subtotal:.2f} {self.currency_var.get()}"],
            ['', '', self.get_translation('vat'), f"{vat_amount:.2f} {self.currency_var.get()}"],
            ['', '', self.get_translation('total_ttc'), f"{total_ttc:.2f} {self.currency_var.get()}"]
        ])
        
        # Create and style the table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Add amount in words
        amount_words = self.amount_to_words(total_ttc)
        elements.append(Paragraph(
            f"{self.get_translation('amount_in_words')}: {amount_words}",
            styles['Normal']
        ))
        
        # Add signature if provided
        if self.signature_path:
            try:
                img = Image(self.signature_path, width=2*inch, height=1*inch)
                elements.append(Spacer(1, 20))
                elements.append(Paragraph(self.get_translation("signature"), styles['Normal']))
                elements.append(img)
            except Exception as e:
                print(f"Error adding signature: {e}")
        
        # Build PDF
        doc.build(elements)
        
        # Show success animation
        self.show_success_animation()

    def show_success_animation(self):
        """Show a simple success animation in the GUI"""
        success_window = tk.Toplevel(self.window)
        success_window.geometry("200x100")
        success_window.overrideredirect(True)
        success_window.configure(bg='#4CAF50')
        
        # Center the window
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - 100
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - 50
        success_window.geometry(f"+{x}+{y}")
        
        # Add success message
        label = tk.Label(
            success_window,
            text="✓ PDF Generated!",
            font=('Helvetica', 14, 'bold'),
            bg='#4CAF50',
            fg='white'
        )
        label.pack(expand=True)
        
        # Close animation after 1.5 seconds
        self.window.after(1500, success_window.destroy)

    def save_template(self):
        template = {
            'company_name': self.company_name.get(),
            'language': self.language_var.get(),
            'currency': self.currency_var.get(),
            'vat_rate': self.vat_rate
        }
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            with open(filename, 'w') as f:
                json.dump(template, f)

    def load_template(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, 'r') as f:
                template = json.load(f)
                self.company_name.set(template.get('company_name', ''))
                self.language_var.set(template.get('language', 'English'))
                self.currency_var.set(template.get('currency', 'USD'))
                self.vat_rate = template.get('vat_rate', 0.20)
                self.update_language()

    def run(self):
        # Add some initial animation
        self.window.withdraw()
        self.window.update()
        
        # Fade in effect
        self.window.deiconify()
        alpha = 0
        while alpha < 1:
            alpha += 0.1
            self.window.attributes('-alpha', alpha)
            self.window.update()
            self.window.after(50)
        
        self.window.mainloop()

if __name__ == "__main__":
    app = ModernInvoiceGenerator()
    app.run()