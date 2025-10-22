#!/usr/bin/env python3
import http.server
import socketserver
import os
import io

PORT = 5000
DIRECTORY = "."

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # التأكد من استخدام الملف الصحيح لصفحة الدخول
        if args and args[0] == 'login.html':
            args = ('login.html.txt',) + args[1:]
        
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Cache control headers (للتطوير)
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        
        # Security headers
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        
        super().end_headers()
    
    def send_error(self, code, message=None, explain=None):
        if code == 404:
            # افتراض أن ملف 404.html (أو 404.txt) موجود
            try:
                # محاولة قراءة ملف 404.txt (الاسم الذي استخدمناه)
                with open('404.txt', 'r', encoding='utf-8') as f:
                    error_page = f.read()
            except FileNotFoundError:
                error_page = f"<!DOCTYPE html><html><head><title>404</title></head><body><h1 style='text-align:center;'>404 - {message}</h1></body></html>"
            
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(error_page.encode('utf-8'))
        else:
            super().send_error(code, message, explain)

    def do_GET(self):
        # إعادة توجيه طلب '/' و '/index.html' إلى صفحة الدخول إذا لم يتم تسجيل الدخول
        if self.path in ['/', '/index.html']:
            # هنا نفترض وجود آلية فحص للجلسة في JS داخل index.html
            # لكننا نجعل نقطة البداية دائماً هي صفحة الدخول
            if self.path == '/':
                self.path = '/login.html'
        
        # معالجة طلب ملف login.html.txt على أنه login.html
        if self.path == '/login.html':
            self.path = '/login.html.txt'

        # معالجة ملف favicon.svg (افتراض أن اسمه favicon.txt)
        if self.path == '/favicon.svg':
             self.path = '/favicon.txt'
             self.send_response(200)
             self.send_header("Content-type", "image/svg+xml")
             self.end_headers()
             try:
                 with open(os.getcwd() + self.path, 'rb') as f:
                     self.wfile.write(f.read())
             except FileNotFoundError:
                 self.send_error(404, "File not found: " + self.path)
             return
             
        # إضافة فحص خاص لملف output.css
        if self.path.endswith('.css'):
            self.send_response(200)
            self.send_header("Content-type", "text/css; charset=utf-8")
            self.end_headers()
            try:
                with open(os.getcwd() + self.path, 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, "File not found: " + self.path)
            return

        # إذا كان الطلب على index.html.txt (اسم الملف الفعلي) قم بتخديمه
        if self.path == '/index.html':
            self.path = '/index.txt'

        # لمعالجة ملفات HTML (وغيرها من الملفات الأساسية)
        super().do_GET()


def run_server():
    # التأكد من توفر الملفات الأساسية
    if not os.path.exists('index.html') and not os.path.exists('index.txt'):
        print("⛔ لا يوجد ملف index.html أو index.txt")
        return
    if not os.path.exists('login.html.txt'):
        print("⛔ لا يوجد ملف login.html.txt")
        return
    
    # التأكد من ربط login.html بـ login.html.txt لكي يعمل الخادم بشكل صحيح
    if os.path.exists('login.html'):
        os.remove('login.html') 
    
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"🚀 الخادم يعمل على: http://localhost:{PORT}")
            print("✨ البداية من صفحة تسجيل الدخول.")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
             print(f"❌ خطأ: المنفذ {PORT} مشغول. الرجاء إغلاق البرنامج الذي يستخدمه والمحاولة مرة أخرى.")
        else:
             print(f"❌ حدث خطأ غير متوقع: {e}")

if __name__ == "__main__":
    run_server()