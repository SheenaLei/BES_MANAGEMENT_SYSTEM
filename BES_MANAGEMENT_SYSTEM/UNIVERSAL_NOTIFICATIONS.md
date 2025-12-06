# Universal Notification System 🔔

## ✅ Feature Implemented

I have created a reusable, universal notification system for your application.

### 📂 File Location
`gui/widgets/notification_bar.py`

### 🚀 How to Use

1. **Import it:**
   ```python
   from gui.widgets.notification_bar import NotificationBar
   ```

2. **Initialize it in your Window/Dialog:**
   ```python
   self.notification = NotificationBar(self)
   ```

3. **Show Notifications:**
   ```python
   # Success (Green)
   self.notification.show_success("Operation successful!")

   # Error (Red)
   self.notification.show_error("Something went wrong!")

   # Warning (Orange)
   self.notification.show_warning("Please check your input.")

   # Info (Blue)
   self.notification.show_info("Here is some information.")
   ```

### ✨ Features
- **Full Width:** Spans 95% of the parent window.
- **Smooth Animation:** Slides down from the top.
- **Auto-Hide:** Disappears after 60 seconds (customizable).
- **Manual Close:** Includes a "×" button.
- **Universal:** Can be used in Login, Dashboard, Settings, etc.

## 📝 Test It Now
Run the login screen and try different actions (empty login, correct login) to see the different notification types!
