import flet as ft
import sqlite3
from datetime import datetime

DB_NAME = "shop_flet.db"

def init_db():
    """ایجاد جدول دیتابیس"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            model TEXT NOT NULL,
            date_added TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "مدیریت کالا و سفارش‌ها"
    page.rtl = True  # راست‌چین برای زبان فارسی
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    init_db()

    # فیلدهای ورودی فرم
    name_input = ft.TextField(label="نام کالا", hint_text="مثال: لپ‌تاپ", border_color="blue")
    category_input = ft.TextField(label="نوع کالا (دسته‌بندی)", hint_text="مثال: دیجیتال", border_color="blue")
    model_input = ft.TextField(label="مدل کالا", hint_text="مثال: Pro 2026", border_color="blue")
    date_input = ft.TextField(
        label="تاریخ (اختیاری)", 
        hint_text="مثال: ۱۴۰۵-۰۴-۱۲", 
        value=datetime.now().strftime('%Y-%m-%d'),
        border_color="blue"
    )
    
    # فیلد جستجو
    search_input = ft.TextField(label="جستجو در کالاها...", expand=True, border_color="orange")
    
    # لیست نمایش کارتها
    orders_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    def load_orders(search_query=""):
        """بارگذاری و نمایش لیست کالاها از دیتابیس"""
        orders_list.controls.clear()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        if search_query:
            cursor.execute('''
                SELECT * FROM orders 
                WHERE name LIKE ? OR category LIKE ? OR model LIKE ? OR date_added LIKE ?
                ORDER BY id DESC
            ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute("SELECT * FROM orders ORDER BY id DESC")
            
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            order_id, name, cat, model, date = row
            
            # ساخت کارت برای هر جنس
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            title=ft.Text(name, weight=ft.FontWeight.BOLD, size=18),
                            subtitle=ft.Text(f"نوع: {cat} | مدل: {model} | تاریخ: {date}", size=14),
                            trailing=ft.IconButton(
                                icon=ft.icons.DELETE_FOREVER,
                                icon_color="red",
                                data=order_id,
                                on_click=delete_order
                            )
                        )
                    ], spacing=5),
                    padding=10
                )
            )
            orders_list.controls.append(card)
        
        page.update()

    def add_order(e):
        """ثبت کالا جدید"""
        if not name_input.value or not category_input.value or not model_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("لطفاً فیلدهای اجباری را پر کنید!"))
            page.snack_bar.open = True
            page.update()
            return
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (name, category, model, date_added) VALUES (?, ?, ?, ?)",
            (name_input.value, category_input.value, model_input.value, date_input.value)
        )
        conn.commit()
        conn.close()
        
        # خالی کردن فرم بعد از ثبت
        name_input.value = ""
        category_input.value = ""
        model_input.value = ""
        
        page.snack_bar = ft.SnackBar(ft.Text("کالا با موفقیت ثبت شد."))
        page.snack_bar.open = True
        
        load_orders()

    def delete_order(e):
        """حذف کالا"""
        order_id = e.control.data
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()
        
        page.snack_bar = ft.SnackBar(ft.Text("آیتم مورد نظر حذف شد."))
        page.snack_bar.open = True
        
        # بارگذاری مجدد بر اساس متن فعلی جستجو
        load_orders(search_input.value)

    def search_changed(e):
        """اجرای جستجو با تغییر متن"""
        load_orders(search_input.value)

    # دکمه‌ها و رویدادها
    btn_submit = ft.ElevatedButton("ثبت کالا / سفارش", on_click=add_order, bgcolor="blue", color="white")
    search_input.on_change = search_changed

    # چیدمان صفحه (رابط کاربری)
    page.add(
        ft.Text("افزودن جنس جدید", size=20, weight=ft.FontWeight.BOLD, color="blue"),
        name_input,
        category_input,
        model_input,
        date_input,
        btn_submit,
        ft.Divider(),
        ft.Text("جستجو و لیست کالاها", size=20, weight=ft.FontWeight.BOLD, color="orange"),
        ft.Row([search_input]),
        orders_list
    )

    # بارگذاری اولیه کالاها
    load_orders()

ft.app(target=main)
