# repthon/sql_helper/no_log_pms_sql.py

import json
import os

NO_LOG_FILE = "no_log_pms.json"

def load_no_log():
    """تحميل إعدادات عدم تسجيل الخاص من ملف JSON"""
    if os.path.exists(NO_LOG_FILE):
        try:
            with open(NO_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ خطأ في تحميل no_log_pms: {e}")
            return {}
    return {}

def save_no_log(data):
    """حفظ إعدادات عدم تسجيل الخاص إلى ملف JSON"""
    try:
        with open(NO_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"❌ خطأ في حفظ no_log_pms: {e}")
        return False

def is_no_log(chat_id):
    """التحقق إذا كانت المحادثة الخاصة غير مسجلة"""
    data = load_no_log()
    return data.get(str(chat_id), False)

def set_no_log(chat_id, value):
    """تعيين حالة عدم تسجيل المحادثة الخاصة"""
    data = load_no_log()
    data[str(chat_id)] = value
    save_no_log(data)

def enable_no_log(chat_id):
    """تفعيل عدم تسجيل المحادثة الخاصة"""
    return set_no_log(chat_id, True)

def disable_no_log(chat_id):
    """تعطيل عدم تسجيل المحادثة الخاصة (تفعيل التسجيل)"""
    return set_no_log(chat_id, False)

def get_all_no_log():
    """الحصول على جميع المحادثات غير المسجلة"""
    return load_no_log()

def remove_no_log(chat_id):
    """إزالة إعداد عدم تسجيل المحادثة الخاصة"""
    data = load_no_log()
    if str(chat_id) in data:
        del data[str(chat_id)]
        return save_no_log(data)
    return False
