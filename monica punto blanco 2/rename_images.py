import os

old_logo = "Gemini_Generated_Image_uum5nkuum5nkuum5.png"
old_avatar = "Gemini_Generated_Image_vuanhzvuanhzvuan.png"

if os.path.exists(old_logo):
    os.rename(old_logo, "logo.png")
    print("Logo renamed")
if os.path.exists(old_avatar):
    os.rename(old_avatar, "avatar.png")
    print("Avatar renamed")
