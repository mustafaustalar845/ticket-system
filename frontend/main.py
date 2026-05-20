from nicegui import ui, app
import httpx
import os

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api")

ui.add_head_html("""
    <style>
        @media print {
            body * { visibility: hidden; }
            .print-area, .print-area * { visibility: visible; }
            .print-area { position: absolute; left: 0; top: 0; width: 100%; margin: 0; padding: 0; }
            .no-print { display: none !important; }
        }
        .glow-text {
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
            transition: color 0.5s ease, text-shadow 0.5s ease;
        }
        .monitor-bg {
            background: radial-gradient(circle at center, #2d3748 0%, #1a202c 100%);
        }
    </style>
""", shared=True)


# ── LOGIN ────────────────────────────────────────────────────
async def login(username, password):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                app.storage.user['token'] = data.get("access_token")
                app.storage.user['role']  = data.get("user", {}).get("role", "employee")
                ui.notify("Giriş başarılı!", type="positive")
                role = app.storage.user['role']
                if role == "admin":
                    ui.navigate.to("/panel")
                else:
                    ui.navigate.to("/staff")
            else:
                ui.notify("Kullanıcı adı veya şifre hatalı!", type="negative")
        except Exception as e:
            ui.notify(f"Sunucuya bağlanılamadı: {e}", type="negative")


# ── KIOSK: BİLET AL ─────────────────────────────────────────
async def take_ticket(tckn):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_BASE_URL}/tickets/new", json={"tckn": tckn})
            if response.status_code in (200, 201):
                data = response.json()
                ticket_number = data['ticket']['ticket_number']
                ui.notify(f"Biletiniz alındı: {ticket_number}", type="positive")
                with ui.dialog() as dialog, ui.card().classes('print-area flex flex-col items-center p-8 bg-white text-black'):
                    ui.label("SIRA SİSTEMİ").classes('text-2xl font-bold mb-4')
                    ui.label("Bilet Numaranız").classes('text-lg')
                    ui.label(ticket_number).classes('text-6xl font-extrabold my-4 text-blue-700')
                    ui.label("Numaranız çağrılınca lütfen gişeye gidiniz.").classes('text-sm text-gray-500 mb-6')
                    with ui.row().classes('no-print'):
                        ui.button('Yazdır', on_click=lambda: ui.run_javascript('window.print()')).classes('bg-blue-500 text-white mr-2')
                        ui.button('Kapat',  on_click=dialog.close).classes('bg-gray-500 text-white')
                dialog.open()
            else:
                ui.notify(f"Hata: {response.json()}", type="negative")
        except Exception as e:
            ui.notify(f"Sunucuya bağlanılamadı: {e}", type="negative")


# ── STAFF: SONRAKİ BİLETİ ÇAĞIR ─────────────────────────────
async def call_next(counter_val, active_label):
    token = app.storage.user.get('token')
    if not token:
        ui.notify("Oturum açmanız gerekiyor!", type="negative")
        return
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/tickets/call-next?counter={counter_val}",
                headers=headers
            )
            if response.status_code == 200:
                data   = response.json()
                ticket = data.get('ticket', {})
                num    = ticket.get('ticket_number', '?')
                raw_id = ticket.get('id') or ticket.get('_id') or ''
                app.storage.user['active_ticket_id']  = str(raw_id) if raw_id else ''
                app.storage.user['active_ticket_num'] = num
                active_label.set_text(f"Aktif Bilet: {num}")
                ui.notify(f"Çağrıldı: {num}", type="positive")
            else:
                detail = response.json().get('detail', response.text)
                ui.notify(f"Hata: {detail}", type="warning")
        except Exception as e:
            ui.notify(f"Sunucuya bağlanılamadı: {e}", type="negative")


# ── STAFF: AKTİF BİLETİ TAMAMLA ─────────────────────────────
async def complete_ticket(active_label):
    token     = app.storage.user.get('token')
    ticket_id = app.storage.user.get('active_ticket_id', '')
    if not token:
        ui.notify("Oturum açmanız gerekiyor!", type="negative")
        return
    if not ticket_id:
        ui.notify("Tamamlanacak aktif bilet yok!", type="warning")
        return
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/tickets/{ticket_id}/complete",
                headers=headers
            )
            if response.status_code == 200:
                app.storage.user['active_ticket_id']  = ''
                app.storage.user['active_ticket_num'] = ''
                active_label.set_text("Aktif Bilet: —")
                ui.notify("İşlem tamamlandı!", type="positive")
            else:
                detail = response.json().get('detail', response.text)
                ui.notify(f"Hata: {detail}", type="warning")
        except Exception as e:
            ui.notify(f"Sunucuya bağlanılamadı: {e}", type="negative")


# ─────────────────────────────────────────────────────────────
# SAYFALAR
# ─────────────────────────────────────────────────────────────

@ui.page('/')
def index():
    """Kiosk — Müşteri bilet alır."""
    with ui.column().classes('w-full items-center mt-16'):
        ui.label('🎫 Sıra Sistemi').classes('text-4xl font-bold mb-2')
        ui.label('Bilet almak için TCKN numaranızı giriniz.').classes('text-gray-500 mb-8')
        tckn_input = ui.input('11 haneli TCKN').classes('w-72')
        ui.button('Bilet Al', on_click=lambda: take_ticket(tckn_input.value)).classes('w-72 mt-3 bg-blue-600 text-white text-lg py-3')
        ui.separator().classes('my-8 w-72')
        ui.link('Personel Girişi →', '/login').classes('text-blue-500')


@ui.page('/login')
def login_page():
    """Personel giriş sayfası."""
    with ui.column().classes('w-full items-center mt-20'):
        ui.label('👤 Personel Girişi').classes('text-3xl font-bold mb-8')
        username_input = ui.input('Kullanıcı Adı').classes('w-72')
        password_input = ui.input('Şifre', password=True).classes('w-72 mt-2')
        ui.button(
            'Giriş Yap',
            on_click=lambda: login(username_input.value, password_input.value)
        ).classes('w-72 mt-4 bg-green-600 text-white text-lg py-3')
        ui.link('← Ana Sayfa', '/').classes('mt-6 text-gray-500')


@ui.page('/staff')
async def staff_page():
    """Personel (employee) dashboard — bilet çağır ve tamamla."""
    if not app.storage.user.get('token'):
        ui.navigate.to('/login')
        return

    token   = app.storage.user.get('token')
    headers = {"Authorization": f"Bearer {token}"}

    with ui.column().classes('w-full items-center mt-10 gap-4'):
        ui.label('🖥️ Personel Paneli').classes('text-3xl font-bold')

        # Aktif bilet göstergesi
        active_label = ui.label("Aktif Bilet: yükleniyor...").classes('text-xl font-semibold text-orange-600')

        # Sayfa açılışında sunucudan aktif bileti çek
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(f"{API_BASE_URL}/tickets/active", headers=headers)
                if r.status_code == 200:
                    active = r.json().get('active')
                    if active:
                        # Beanie/MongoDB ID alanı 'id' veya '_id' olarak gelebilir
                        raw_id    = active.get('id') or active.get('_id') or ''
                        ticket_id = str(raw_id) if raw_id else ''
                        ticket_num = active.get('ticket_number', '?')
                        app.storage.user['active_ticket_id']  = ticket_id
                        app.storage.user['active_ticket_num'] = ticket_num
                        active_label.set_text(f"Aktif Bilet: {ticket_num}")
                    else:
                        app.storage.user['active_ticket_id']  = ''
                        app.storage.user['active_ticket_num'] = ''
                        active_label.set_text("Aktif Bilet: —")
            except Exception as e:
                active_label.set_text(f"Bağlantı hatası: {e}")

        # Gişe seçimi
        counter_input = ui.number('Gişe No', value=1, min=1, max=99).classes('w-40')

        ui.button(
            '📣 Sıradakini Çağır',
            on_click=lambda: call_next(int(counter_input.value), active_label)
        ).classes('w-64 py-4 text-lg bg-orange-500 text-white')

        ui.button(
            '✅ İşlemi Tamamla',
            on_click=lambda: complete_ticket(active_label)
        ).classes('w-64 py-4 text-lg bg-green-600 text-white')

        ui.separator().classes('w-72 my-4')

        def logout():
            app.storage.user.clear()
            ui.navigate.to('/')
        ui.button('Çıkış Yap', on_click=logout).classes('w-64 bg-gray-500 text-white')



@ui.page('/panel')
async def admin_panel():
    """Admin paneli — kullanıcı yönetimi ve istatistikler."""
    if not app.storage.user.get('token'):
        ui.navigate.to('/login')
        return

    # Sadece admin olanlar girebilir
    if app.storage.user.get('role') != 'admin':
        ui.notify("Bu sayfaya erişim yetkiniz yok!", type="negative")
        ui.navigate.to('/staff')
        return

    token   = app.storage.user.get('token')
    headers = {"Authorization": f"Bearer {token}"}

    with ui.column().classes('w-full items-center mt-8 gap-4'):
        ui.label('⚙️ Admin Paneli').classes('text-3xl font-bold')

        # ── İSTATİSTİKLER (otomatik yüklenir) ─────────────
        ui.label('📊 Bilet İstatistikleri').classes('text-xl font-semibold mt-2')
        stats_row = ui.row().classes('gap-6 my-2')

        async def load_stats():
            async with httpx.AsyncClient() as client:
                try:
                    r = await client.get(f"{API_BASE_URL}/tickets/stats", headers=headers)
                    if r.status_code == 200:
                        d = r.json()
                        stats_row.clear()
                        with stats_row:
                            with ui.card().classes('p-6 text-center min-w-32'):
                                ui.label(str(d.get('waiting', 0))).classes('text-5xl font-bold text-yellow-500')
                                ui.label('Bekleyen').classes('text-gray-500 mt-1')
                            with ui.card().classes('p-6 text-center min-w-32'):
                                ui.label(str(d.get('serving', 0))).classes('text-5xl font-bold text-blue-500')
                                ui.label('Servis Edilen').classes('text-gray-500 mt-1')
                            with ui.card().classes('p-6 text-center min-w-32'):
                                ui.label(str(d.get('completed', 0))).classes('text-5xl font-bold text-green-500')
                                ui.label('Tamamlanan').classes('text-gray-500 mt-1')
                    elif r.status_code in (401, 403):
                        ui.notify("Oturum süresi doldu veya yetkisiz erişim. Lütfen tekrar giriş yapın.", type="negative")
                        app.storage.user.clear()
                        ui.navigate.to('/login')
                    else:
                        ui.notify(f"İstatistik hatası: {r.status_code}", type="negative")
                except Exception as e:
                    ui.notify(f"İstatistik yüklenemedi: {e}", type="negative")

        # Sayfa açılırken otomatik yükle
        await load_stats()
        ui.button('🔄 Yenile', on_click=load_stats).classes('bg-blue-600 text-white')

        ui.separator().classes('w-full max-w-3xl my-2')

        # ── KULLANICI LİSTESİ (otomatik yüklenir) ─────────
        ui.label('👥 Kullanıcı Yönetimi').classes('text-xl font-semibold mt-2')
        users_table = ui.column().classes('w-full max-w-3xl gap-2')

        async def load_users():
            async with httpx.AsyncClient() as client:
                try:
                    r = await client.get(f"{API_BASE_URL}/admin/users", headers=headers)
                    if r.status_code == 200:
                        users_table.clear()
                        users = r.json()
                        if not users:
                            with users_table:
                                ui.label('Henüz kullanıcı yok.').classes('text-gray-400')
                        else:
                            with users_table:
                                for u in users:
                                    with ui.card().classes('w-full p-3'):
                                        with ui.row().classes('w-full justify-between items-center'):
                                            with ui.column().classes('gap-0'):
                                                ui.label(u.get('full_name', '-')).classes('font-semibold')
                                                ui.label(f"@{u.get('username', '-')}").classes('text-sm text-gray-500')
                                            ui.badge(
                                                u.get('role', '-'),
                                                color='red' if u.get('role') == 'admin' else 'teal'
                                            )
                    elif r.status_code in (401, 403):
                        ui.notify("Oturum süresi doldu veya yetkisiz erişim. Lütfen tekrar giriş yapın.", type="negative")
                        app.storage.user.clear()
                        ui.navigate.to('/login')
                    else:
                        ui.notify(f"Kullanıcılar yüklenemedi ({r.status_code})", type="negative")
                except Exception as e:
                    ui.notify(f"Hata: {e}", type="negative")

        # Sayfa açılırken otomatik yükle
        await load_users()
        ui.button('🔄 Listeyi Yenile', on_click=load_users).classes('bg-purple-600 text-white')

        ui.separator().classes('w-full max-w-3xl my-2')

        # ── YENİ KULLANICI EKLE ────────────────────────────
        ui.label('➕ Yeni Kullanıcı Ekle').classes('text-lg font-semibold mt-2')
        with ui.card().classes('w-full max-w-3xl p-4'):
            with ui.row().classes('gap-3 flex-wrap items-end'):
                new_username = ui.input('Kullanıcı Adı').classes('w-44')
                new_password = ui.input('Şifre', password=True).classes('w-44')
                new_fullname = ui.input('Ad Soyad').classes('w-44')
                new_role     = ui.select(['employee', 'admin'], value='employee', label='Rol').classes('w-36')

                async def create_user():
                    if not new_username.value or not new_password.value or not new_fullname.value:
                        ui.notify('Tüm alanları doldurun!', type='warning')
                        return
                    async with httpx.AsyncClient() as client:
                        try:
                            r = await client.post(
                                f"{API_BASE_URL}/admin/users",
                                headers=headers,
                                json={
                                    "username":  new_username.value.strip(),
                                    "password":  new_password.value,
                                    "full_name": new_fullname.value.strip(),
                                    "role":      new_role.value,
                                }
                            )
                            if r.status_code in (200, 201):
                                ui.notify(f"✅ '{new_username.value}' kullanıcısı oluşturuldu!", type="positive")
                                new_username.set_value('')
                                new_password.set_value('')
                                new_fullname.set_value('')
                                await load_users()
                            else:
                                ui.notify(f"Hata: {r.json().get('detail', r.text)}", type="negative")
                        except Exception as e:
                            ui.notify(f"Hata: {e}", type="negative")

                ui.button('Ekle', on_click=create_user).classes('bg-green-600 text-white h-12 px-6')

        ui.separator().classes('w-full max-w-3xl my-4')

        def logout():
            app.storage.user.clear()
            ui.navigate.to('/')
        ui.button('🚪 Çıkış Yap', on_click=logout).classes('bg-gray-500 text-white')


@ui.page('/monitor')
def monitor_page():
    """Ekran — şu an çağrılan numara."""
    with ui.column().classes('w-full h-screen items-center justify-center monitor-bg text-white m-0 p-0 overflow-hidden').style('position: absolute; top: 0; left: 0;'):
        ui.label('ŞU AN SIRASI').classes('text-5xl font-bold text-gray-400 tracking-[0.2em] mb-8')
        current_ticket = ui.label('---').classes('text-[15rem] font-extrabold text-white leading-none mb-12 glow-text')
        current_ticket.props('id="current-ticket"')
        ui.html("""
            <script>
                const host = window.location.hostname;
                const ws = new WebSocket("ws://" + host + ":8000/ws/monitor");
                ws.onmessage = function(event) {
                    const el = document.getElementById("current-ticket");
                    if (el) {
                        let data = event.data;
                        try {
                            const parsed = JSON.parse(event.data);
                            data = parsed.ticket_number || event.data;
                        } catch (e) {}
                        el.innerText = data;
                        el.style.color = '#4ade80';
                        el.style.textShadow = '0 0 40px rgba(74, 222, 128, 0.8)';
                        setTimeout(() => {
                            el.style.color = 'white';
                            el.style.textShadow = '0 0 20px rgba(255, 255, 255, 0.5)';
                        }, 2000);
                    }
                };
            </script>
        """)


ui.run(title="Sıra Sistemi", host="0.0.0.0", port=8080, storage_secret="my-super-secret-key")
