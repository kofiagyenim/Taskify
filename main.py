#Importing packages
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBody
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.pickers import MDTimePicker



from database import Database
db = Database()

from datetime import datetime


class DialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize both date and time to now
        now = datetime.now()
        self.selected_date = now.strftime("%A %d %B %Y")
        self.selected_time = now.strftime("%H:%M")
        self.update_datetime_text()

    def update_datetime_text(self):
        # Update the UI with both date and time
        self.ids.date_text.text = f"{self.selected_date} at {self.selected_time}"

    def display_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save_date)
        date_dialog.open()

    def on_save_date(self, instance, value, date_range):
        self.selected_date = value.strftime("%A %d %B %Y")
        self.update_datetime_text()

    def display_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_save_time)
        time_dialog.open()

    def on_save_time(self, instance, time):
        self.selected_time = time.strftime('%H:%M')
        self.update_datetime_text()

#Deleting and marking item class
class ListItemWithCheckbox(TwoLineAvatarIconListItem):
    def __init__(self, pk= None, **kwargs):
        super().__init__(**kwargs)
        self.pk = pk

    #Marking item as complete or not
    def mark(self, check, the_list_item):
        if check.active == True:
            the_list_item.text = '[s]' + the_list_item.text + '[/s]'
            db.mark_task_as_complete(the_list_item.pk)
        else:
            the_list_item.text = str(db.mark_task_as_incomplete(the_list_item.pk))

    #Deleting list item
    def delete_item(self, the_list_item):
        self.parent.remove_widget(the_list_item)
        db.delete_task(the_list_item.pk)

class LeftCheckbox(ILeftBody, MDCheckbox):
    pass



#Class for the main application
class MainApp(MDApp):
    task_list_dialog = None
    #Build function for setting the theme
    def build(self):
        self.theme_cls.primary_palette = ("Teal")

    #This is the display task function
    def display_task_dialog(self):
        if not self.task_list_dialog:
            self.task_list_dialog = MDDialog(
                title="Create Task",
                type="custom",
                content_cls=DialogContent(),
            )
        self.task_list_dialog.open()

    def add_task(self, task_text_field, task_date, task_category):
        created_task = db.create_task(task_text_field.text, task_date, task_category)
        self.root.ids.container.add_widget(ListItemWithCheckbox(pk=created_task[0], text='[b]' + created_task[1] + '[/b]', secondary_text=created_task[2] + ' - ' + created_task[3]))
        task_text_field.text = ''  # Reset the text field
        self.task_list_dialog.dismiss()  # Dismiss the dialog
        self.task_list_dialog = None


    def close_dialog(self):
        if self.task_list_dialog:
            self.task_list_dialog.dismiss()


    def on_start(self):
        '''This is to load the saved task and add them to the MDList widget'''
        completed_tasks, incompleted_tasks = db.get_tasks()

        if incompleted_tasks != []:
            for task in incompleted_tasks:
                add_task = ListItemWithCheckbox(pk=task[0], text=task[1], secondary_text=task[2])
                self.root.ids.container.add_widget(add_task)

        if completed_tasks != []:
            for task in completed_tasks:
                add_task = ListItemWithCheckbox(pk = task[0], text = "[s]" + task[1] + "[/s]", secondary_text = task[2])
                add_task.ids.check.active = True
                self.root.ids.container.add_widget(add_task)


    def toggle_theme_style(self):
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"







if __name__=="__main__":
    app = MainApp()
    app.run()