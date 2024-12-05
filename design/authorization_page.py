import tkinter as tk
from tkinter import messagebox


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Authorization")
        self.geometry("400x300")

        # Ініціалізація сторінок
        self.pages = {}
        for PageClass in (MainPage, UserPage, AdminPage):
            page = PageClass(self)
            self.pages[PageClass] = page
            page.grid(row=0, column=0, sticky="nsew")

        # Відображення головної сторінки
        self.show_page(MainPage)

    def show_page(self, page_class):
        page = self.pages[page_class]
        page.tkraise()


# Головна сторінка
class MainPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Welcome! Choose your role:", font=("Arial", 16)).pack(pady=20)

        tk.Button(self, text="User", command=lambda: parent.show_page(UserPage), width=15).pack(pady=10)
        tk.Button(self, text="Admin", command=lambda: parent.show_page(AdminPage), width=15).pack(pady=10)


# Сторінка для User
class UserPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="User Login", font=("Arial", 14)).pack(pady=10)

        tk.Label(self, text="Login:").pack()
        self.login_entry = tk.Entry(self)
        self.login_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self, text="Login", command=self.login_user).pack(pady=10)
        tk.Button(self, text="Forgot Password", command=self.forgot_password).pack()

        tk.Button(self, text="Back", command=lambda: parent.show_page(MainPage)).pack(pady=10)

    def login_user(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        if login == "user" and password == "password":  # Тимчасова перевірка
            messagebox.showinfo("Success", "User logged in!")
        else:
            messagebox.showerror("Error", "Invalid login or password.")

    def forgot_password(self):
        messagebox.showinfo("Forgot Password", "Password recovery link sent to your email!")


# Сторінка для Admin
class AdminPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Admin Login", font=("Arial", 14)).pack(pady=10)

        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self, text="Login", command=self.login_admin).pack(pady=10)
        tk.Button(self, text="Forgot Password", command=self.forgot_password).pack()

        tk.Button(self, text="Back", command=lambda: parent.show_page(MainPage)).pack(pady=10)

    def login_admin(self):
        password = self.password_entry.get()
        if password == "admin":  # Тимчасова перевірка
            messagebox.showinfo("Success", "Admin logged in!")
        else:
            messagebox.showerror("Error", "Invalid password.")

    def forgot_password(self):
        messagebox.showinfo("Forgot Password", "Admin password recovery link sent to your email!")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
