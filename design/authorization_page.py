import tkinter as tk
from tkinter import *
import customtkinter as ctk
from PIL import Image, ImageTk


class MainPage:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x600")
        self.root.title("StaffBase")
        self.root.resizable(False, False)
        self.root.configure(bg="#FFFFFF")
        icon = tk.PhotoImage(file="img/icon.png")
        self.root.iconphoto(False, icon)

        self.pages = {}

        self.main_frame = ctk.CTkFrame(self.root, width=800, height=600, fg_color="#FFFFFF")
        self.main_frame.place(x=0, y=0)

        label_title = ctk.CTkLabel(master=self.main_frame, text="Welcome to StaffBase", font=ctk.CTkFont(family="Cooper Black", size=40), text_color="black", bg_color="transparent")
        label_title.place(relx=0.5, rely=0.3, anchor="center")

        label_subtitle = ctk.CTkLabel(master=self.main_frame, text="Please select your role", font=ctk.CTkFont(family="Montserrat Regular", size=24), text_color="black")
        label_subtitle.place(relx=0.5, rely=0.4, anchor="center")

        # image_icon = PhotoImage(file="img/admin.png")

        icon_path = "img/admin.png"
        icon_image = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_image)

        admin_button = ctk.CTkButton(
            master=self.main_frame, text="Admin", width=200, height=60, corner_radius=30, font=ctk.CTkFont(family="Montserrat Medium", size=16), fg_color="#C6DBFE", hover_color="#A5C4E7", text_color="black", border_width=0, image=icon_photo, compound="left", command=lambda: self.show_page("admin"))

        admin_button.place(relx=0.3, rely=0.6, anchor="center")

        employee_button = ctk.CTkButton(master=self.main_frame, text="Employee", width=200, height=60, corner_radius=30, font=ctk.CTkFont(family="Montserrat Medium", size=16), fg_color="#C6DBFE", hover_color="#A5C4E7", text_color="black", border_width=0, command=lambda: self.show_page("employee"))
        employee_button.place(relx=0.7, rely=0.6, anchor="center")

        self.pages["admin"] = AdminPage(self.root, self)
        self.pages["employee"] = EmployeePage(self.root, self)

    def show_page(self, page_name):
        self.main_frame.place_forget()
        self.pages[page_name].show()

    def show_main(self):
        for page in self.pages.values():
            page.hide()
        self.main_frame.place(x=0, y=0)


class AdminPage:
    def __init__(self, root, main_page):
        self.main_page = main_page
        self.frame = ctk.CTkFrame(root, width=800, height=600, fg_color="#FFFFFF")

        self.create_login_screen()

    def create_login_screen(self):
        self.clear_frame()

        label = ctk.CTkLabel(master=self.frame, text="Admin Login", font=ctk.CTkFont(family="Montserrat Medium", size=30), text_color="black")
        label.place(relx=0.5, rely=0.2, anchor="center")

        password_label = ctk.CTkLabel(master=self.frame, text="Password:", font=ctk.CTkFont(size=16))
        password_label.place(relx=0.3, rely=0.4, anchor="center")

        self.password_entry = ctk.CTkEntry(master=self.frame, width=250, show="*", font=ctk.CTkFont(size=14))
        self.password_entry.place(relx=0.5, rely=0.4, anchor="center")

        forgot_password = ctk.CTkButton(master=self.frame, text="Forgot Password?", fg_color="transparent", text_color="#1C73E8", command=self.create_verification_screen)
        forgot_password.place(relx=0.5, rely=0.5, anchor="center")

        login_button = ctk.CTkButton(master=self.frame, text="Log In", width=200, height=40, fg_color="#C6DBFE", text_color="black", command=lambda: print("Admin logged in"))
        login_button.place(relx=0.5, rely=0.6, anchor="center")

        back_button = ctk.CTkButton(master=self.frame, text="Back", width=80, height=30, corner_radius=10, fg_color="#C6DBFE", text_color="black", command=self.main_page.show_main)
        back_button.place(x=10, y=10)

    def create_verification_screen(self):
        self.clear_frame()

        label = ctk.CTkLabel(master=self.frame, text="Verification Code Sent", font=ctk.CTkFont(family="Montserrat Medium", size=24), text_color="black")
        label.place(relx=0.5, rely=0.2, anchor="center")

        instruction = ctk.CTkLabel(master=self.frame, text="Please enter the 6-digit code sent to staff-base@ukr.net.", font=ctk.CTkFont(size=14), text_color="black")
        instruction.place(relx=0.5, rely=0.3, anchor="center")

        # Code entry fields
        self.code_entries = []
        for i in range(6):
            entry = ctk.CTkEntry(master=self.frame, width=40, font=ctk.CTkFont(size=18))
            entry.place(relx=0.4 + (i * 0.05), rely=0.4, anchor="center")
            self.code_entries.append(entry)

        submit_button = ctk.CTkButton(master=self.frame, text="Confirm", width=150, height=40, fg_color="#C6DBFE", text_color="black", command=self.create_new_password_screen)
        submit_button.place(relx=0.5, rely=0.6, anchor="center")

        back_button = ctk.CTkButton(master=self.frame, text="Back", width=80, height=30, corner_radius=10, fg_color="#C6DBFE", text_color="black", command=self.create_login_screen)
        back_button.place(x=10, y=10)

    def create_new_password_screen(self):
        entered_code = "".join(entry.get() for entry in self.code_entries)
        if entered_code == "123456":  # Replace with actual validation logic
            self.clear_frame()

            label = ctk.CTkLabel(master=self.frame, text="Set New Password", font=ctk.CTkFont(family="Montserrat Medium", size=24), text_color="black")
            label.place(relx=0.5, rely=0.2, anchor="center")

            new_password_label = ctk.CTkLabel(master=self.frame, text="New Password:", font=ctk.CTkFont(size=16))
            new_password_label.place(relx=0.3, rely=0.4, anchor="center")

            self.new_password_entry = ctk.CTkEntry(master=self.frame, width=250, show="*", font=ctk.CTkFont(size=14))
            self.new_password_entry.place(relx=0.5, rely=0.4, anchor="center")

            confirm_password_label = ctk.CTkLabel(master=self.frame, text="Confirm Password:", font=ctk.CTkFont(size=16))
            confirm_password_label.place(relx=0.3, rely=0.5, anchor="center")

            self.confirm_password_entry = ctk.CTkEntry(master=self.frame, width=250, show="*", font=ctk.CTkFont(size=14))
            self.confirm_password_entry.place(relx=0.5, rely=0.5, anchor="center")

            submit_button = ctk.CTkButton(master=self.frame, text="Submit", width=150, height=40, fg_color="#C6DBFE", text_color="black", command=self.submit_new_password)
            submit_button.place(relx=0.5, rely=0.7, anchor="center")
        else:
            print("Invalid code!")

    def submit_new_password(self):
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if new_password == confirm_password and new_password:
            print("Password updated successfully!")
            self.create_login_screen()
        else:
            print("Passwords do not match or are empty!")

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show(self):
        self.frame.place(x=0, y=0)

    def hide(self):
        self.frame.place_forget()


class EmployeePage:
    def __init__(self, root, main_page):
        self.main_page = main_page
        self.frame = ctk.CTkFrame(root, width=800, height=600, fg_color="#FFFFFF")

        self.create_login_screen()

    def create_login_screen(self):
        self.clear_frame()

        label = ctk.CTkLabel(master=self.frame, text="Employee Login", font=ctk.CTkFont(family="Montserrat Medium", size=30), text_color="black")
        label.place(relx=0.5, rely=0.2, anchor="center")

        username_label = ctk.CTkLabel(master=self.frame, text="Username:", font=ctk.CTkFont(size=16))
        username_label.place(relx=0.3, rely=0.4, anchor="center")

        self.username_entry = ctk.CTkEntry(master=self.frame, width=250, font=ctk.CTkFont(size=14))
        self.username_entry.place(relx=0.5, rely=0.4, anchor="center")

        password_label = ctk.CTkLabel(master=self.frame, text="Password:", font=ctk.CTkFont(size=16))
        password_label.place(relx=0.3, rely=0.5, anchor="center")

        self.password_entry = ctk.CTkEntry(master=self.frame, width=250, show="*", font=ctk.CTkFont(size=14))
        self.password_entry.place(relx=0.5, rely=0.5, anchor="center")

        forgot_password = ctk.CTkButton(master=self.frame, text="Forgot Password?", fg_color="transparent", text_color="#1C73E8", command=self.create_forgot_password_screen)
        forgot_password.place(relx=0.5, rely=0.6, anchor="center")

        login_button = ctk.CTkButton(master=self.frame, text="Log In", width=200, height=40, fg_color="#C6DBFE", text_color="black", command=self.login_employee)
        login_button.place(relx=0.5, rely=0.7, anchor="center")

        back_button = ctk.CTkButton(master=self.frame, text="Back", width=80, height=30, corner_radius=10, fg_color="#C6DBFE", text_color="black", command=self.main_page.show_main)
        back_button.place(x=10, y=10)

    def create_forgot_password_screen(self):
        self.clear_frame()

        label = ctk.CTkLabel(master=self.frame, text="Enter your login", font=ctk.CTkFont(family="Montserrat Medium", size=24), text_color="black")
        label.place(relx=0.5, rely=0.2, anchor="center")

        login_label = ctk.CTkLabel(master=self.frame, text="Login:", font=ctk.CTkFont(size=16))
        login_label.place(relx=0.3, rely=0.4, anchor="center")

        self.forgot_username_entry = ctk.CTkEntry(master=self.frame, width=250, font=ctk.CTkFont(size=14))
        self.forgot_username_entry.place(relx=0.5, rely=0.4, anchor="center")

        send_code_button = ctk.CTkButton(master=self.frame, text="Send Verification Code", width=200, height=40, fg_color="#C6DBFE", text_color="black", command=self.send_verification_code)
        send_code_button.place(relx=0.5, rely=0.6, anchor="center")

        back_button = ctk.CTkButton(master=self.frame, text="Back", width=80, height=30, corner_radius=10, fg_color="#C6DBFE", text_color="black", command=self.create_login_screen)
        back_button.place(x=10, y=10)

    def send_verification_code(self):
        print("Verification code sent to the email associated with", self.forgot_username_entry.get())
        self.create_verification_code_screen()

    def create_verification_code_screen(self):
        self.clear_frame()

        label = ctk.CTkLabel(master=self.frame, text="Verification Code Sent", font=ctk.CTkFont(family="Montserrat Medium", size=24), text_color="black")
        label.place(relx=0.5, rely=0.2, anchor="center")

        instruction = ctk.CTkLabel(master=self.frame, text="Please enter the 6-digit code sent to your email.", font=ctk.CTkFont(size=14), text_color="black")
        instruction.place(relx=0.5, rely=0.3, anchor="center")

        # Code entry fields
        self.code_entries = []
        for i in range(6):
            entry = ctk.CTkEntry(master=self.frame, width=40, font=ctk.CTkFont(size=18))
            entry.place(relx=0.4 + (i * 0.05), rely=0.4, anchor="center")
            self.code_entries.append(entry)

        submit_button = ctk.CTkButton(master=self.frame, text="Confirm", width=150, height=40, fg_color="#C6DBFE", text_color="black", command=self.create_new_password_screen)
        submit_button.place(relx=0.5, rely=0.6, anchor="center")

        back_button = ctk.CTkButton(master=self.frame, text="Back", width=80, height=30, corner_radius=10, fg_color="#C6DBFE", text_color="black", command=self.create_forgot_password_screen)
        back_button.place(x=10, y=10)

    def create_new_password_screen(self):
        entered_code = "".join(entry.get() for entry in self.code_entries)
        if entered_code == "123456":
            self.clear_frame()

            label = ctk.CTkLabel(master=self.frame, text="Set New Password", font=ctk.CTkFont(family="Montserrat Medium", size=24), text_color="black")
            label.place(relx=0.5, rely=0.2, anchor="center")

            new_password_label = ctk.CTkLabel(master=self.frame, text="New Password:", font=ctk.CTkFont(size=16))
            new_password_label.place(relx=0.3, rely=0.4, anchor="center")

            self.new_password_entry = ctk.CTkEntry(master=self.frame, width=250, show="*", font=ctk.CTkFont(size=14))
            self.new_password_entry.place(relx=0.5, rely=0.4, anchor="center")

            confirm_password_label = ctk.CTkLabel(master=self.frame, text="Confirm Password:", font=ctk.CTkFont(size=16))
            confirm_password_label.place(relx=0.3, rely=0.5, anchor="center")

            self.confirm_password_entry = ctk.CTkEntry(master=self.frame, width=250, show="*", font=ctk.CTkFont(size=14))
            self.confirm_password_entry.place(relx=0.5, rely=0.5, anchor="center")

            submit_button = ctk.CTkButton(master=self.frame, text="Submit", width=150, height=40, fg_color="#C6DBFE", text_color="black", command=self.submit_new_password)
            submit_button.place(relx=0.5, rely=0.7, anchor="center")

        else:
            print("Invalid code!")

    def submit_new_password(self):
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if new_password == confirm_password and new_password:
            print("Password updated successfully!")
            self.create_login_screen()
        else:
            print("Passwords do not match or are empty!")

    def login_employee(self):
        print("Employee logged in with username:", self.username_entry.get())
        self.main_page.show_user_page()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show(self):
        self.frame.place(x=0, y=0)

    def hide(self):
        self.frame.place_forget()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainPage(root)
    root.mainloop()





