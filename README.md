# 🚀 Budget Management Monitoring Indicators in Odoo Version 13

## This project aims to design and implement relevant indicators that allow effective monitoring of budget management, in line with performance objectives and financial control requirements.

## 📸 Screenshots

### 🖥️ Dashboard

![Dashboard](screenshots/dashboard.png)

---

### 📊 Report 1

- Wizard  
  ![Report1Wizard](screenshots/report1_wizard.png)
- Pivot View  
  ![Report1Pivot](screenshots/report1_pivot.png)

---

### 📊 Report 2

- Wizard  
  ![Report2Wizard](screenshots/report2_wizard.png)
- Pivot View  
  ![Report2Pivot](screenshots/report2_pivot.png)
- PDF Export  
  ![Report2PDF](screenshots/report2_pdf.png)
- XLS Export  
  ![Report2XLS](screenshots/report2_xls.png)

---

### 📊 Report 3

- Wizard  
  ![Report3Wizard](screenshots/report3_wizard.png)
- Graph  
  ![Report3Graph](screenshots/report3_graph.png)

---

### 📊 Report 4

- Wizard  
  ![Report4Wizard](screenshots/report4_wizard.png)
- Graph  
  ![Report4Graph](screenshots/report4_graph.png)

---

### 📊 Report 5

- Wizard  
  ![Report5Wizard](screenshots/report5_wizard.png)
- Graph  
  ![Report5Graph](screenshots/report5_graph.png)

---

### 📊 Report 6

- Wizard  
  ![Report6Wizard](screenshots/report6_wizard.png)
- Pivot View  
  ![Report6Pivot](screenshots/report6_pivot.png)

---

### 📊 Report 7 (Method 1)

- Wizard  
  ![Report71Wizard](screenshots/report7_1_wizard.png)
- Pivot View  
  ![Report71Pivot](screenshots/report7_1_pivot.png)

---

### 📊 Report 7 (Method 2)

- Wizard  
  ![Report72Wizard](screenshots/report7_2_wizard.png)
- PDF Export  
  ![Report72PDF](screenshots/report7_2_pdf.png)
- XLS Export  
  ![Report72XLS](screenshots/report7_2_xls.png)

---

### 📊 Report 8

- Wizard  
  ![Report8Wizard](screenshots/report8_wizard.png)
- Graph  
  ![Report8Graph](screenshots/report8_graph.png)

---

## 🛠️ Technologies Used

- **Backend:** Odoo 13, Python 3.7.9
- **Database:** PostgreSQL 13.21

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/taha3313/odoo-gestion-budgetaire.git
cd pfa-odoo-2025
```

### 2️⃣ Copy the modules into Odoo `custom_addons` directory

```bash
cp -r pfa-odoo-2025/* /odoo/custom_addons/
```

---

## 💾 Database Restoration

Inside the project folder `pfa-odoo-2025/`, you will find two database dump files:

- **`odoo_db_empty.sql`** → An empty database with only the base configuration.
- **`odoo_db_full.sql`** → A full database containing demo data and reports.

### 🔹 Restore the empty database

```bash
createdb internship_empty
psql -U odoo -d internship_empty -f pfa-odoo-2025/odoo_db_empty.sql
```

### 🔹 Restore the full database

```bash
createdb internship_full
psql -U odoo -d internship_full -f pfa-odoo-2025/odoo_db_full.sql
```

> ⚠️ Make sure PostgreSQL is running and your user (`odoo` in this example) has permission to restore databases.  
> You can rename the databases (`internship_empty` / `internship_full`) as you like.

---

## ▶️ Running Odoo

### 3️⃣ Restart Odoo server

```bash
./odoo-bin -c /etc/odoo.conf -u all
```

### 4️⃣ Activate Developer Mode

- Open: **http://localhost:8069/web?debug=assets**

### 5️⃣ Install the modules

- Go to **Apps**
- Update the apps list
- Search and install:
  - `om_account_budget`
  - `ccit_groups_config`
  - `web_pivot_hide_total`

---

## ✅ Usage

After installation, you can access the reports from:  
**`Facturation → Rapports Dépenses`** in Odoo.

Each wizard provides options to export data in different formats, including **Pivot Tables, Graphs, PDF, and Excel**.

---
